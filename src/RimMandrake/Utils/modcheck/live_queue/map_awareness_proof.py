"""Live proofs of MAP_AWARENESS_PROVE_ON_A_QUIET_MAP, one clause per call (design/RimMandrake/map_awareness.md):

    python.exe src/RimMandrake/Utils/modcheck/live_queue/map_awareness_proof.py A1 .. A13

Runs on the CURRENT quicktest map through the bridge (Session focus=False: never focuses the game), stages what the
clause needs near the anchor farthest from the colonists, reads the result, removes what it spawned (Vanish: no
death, no corpse) and prints one "<clause> PASS|FAIL|UNMEASURED: ..." line.
Exit 0 = the clause holds, 1 = it answered and something is wrong, 2 = UNMEASURED (no bridge, no map, recorder not
installed, a precondition the map does not meet).

  A1  substituted spawn receipt: a spawn whose kind changes after the tool returned (recruit -> Pawn.SetFaction ->
      ChangeKind, Pawn.cs:2734) gets a receipt whose INDEPENDENT read-back shows requested vs actual; an untouched
      control spawn's receipt stays clean
  A2  bounded condition contract: expect("condition", any, max_count=1) admits the first condition (Eclipse) and
      the second (Aurora) is still reported by condition_unexpected
  A3  player-faction joiner: an undeclared new player pawn -> player_joiner names its id; pawn_arrived and
      pawn_state_changed do not also claim it
  A4  stranger naming: a manhunter Warg and a player joiner -> the detectors name both ids, and scene_report prints
      both with decomposed hostility (no-faction + mental:Manhunter / player) and an origin it does not over-claim
  A5  recruit = state change: a factionless stranger already in the baseline turned player -> pawn_state_changed,
      never player_joiner / pawn_arrived
  A6  old-id arrival via set diff: a colonist taken off the map by caravan, a newer pawn spawned, the colonist
      brought back (JawaBenchAwarenessProof.CaravanBack) -> player_joiner names the OLD id (an id watermark misses it)
  A7  ambiguous thing_explain: two Muffalo, name selector -> resolved false, both ids listed, nothing picked; the id
      selector on one resolves
  A8  incident called-but-failed: a worker that returns false (ShortCircuit / CropBlight / SelfTame on a map with
      no conduit / crop / wild animal) -> journal row called, outer body ran, returned false, no 'fired' wording
  A9  forced raid chain: RaidEnemy via jawa/fire_incident -> journal chain bridge:jawa/fire_incident > incident:
      RaidEnemy, returned true, pawns generated > 0, and those pawns' pawn_origin generation chain says the same
  A10 drop-pod deferred delivery: a Mechanoid RaidEnemy whose pawns were generated during the call but spawned 0
      during it -> after the pods land, the new hostiles read generation chain incident:RaidEnemy (bridge-rooted)
      and spawn ticks later than the call
  A11 first-map mapgen recorded at startup: startedBy bridge-registration, GeneratePawn installed early, and the
      map's wildlife reads a generation chain with mapgen. Precondition at launch: test profile and
      "install.generation-early": true in <SaveData>/JawaBench/tps/awareness_settings.json
  A12 caravan transfer: a colonist out by caravan and back reads spawn observedRespawn or mapTransfer, never
      firstObservedSpawn
  A13 overflow counters: more TryExecute calls than the journal ring holds (512) -> retained stays 512, the
      overwritten counter rises by the overflow, status and journal agree, the oldest retained seq advances

verdict() is pure and is exercised offline by selftest_map_awareness_proof.py.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUSES = tuple("A%d" % i for i in range(1, 14))
RING = 512                                    # JawaBenchAwarenessCore.IncidentCapacity
FAIL_CANDIDATES = ("ShortCircuit", "CropBlight", "SelfTame")   # Core Incidents_Map_Misc.xml; worker returns false
PROBE = "JawaBench.BridgeTools.JawaBenchAwarenessProof"         # on a map with nothing to act on
FORBIDDEN = ("caused by", "created by", "mapgen pawn", "generated before load", "newly created and intentionally",
             "no arrivals occurred", "this mod caused", "vanilla initiated", "intentionally spawned")


# ------------------------------------------------------------------------------------------------ pure verdicts
def _chain_kinds(chain):
    """'bridge:jawa/fire_incident#3 > incident:RaidEnemy#4' -> ['bridge:jawa/fire_incident', 'incident:RaidEnemy']"""
    return [re.sub(r"#\d+$", "", part.strip()) for part in (chain or "").split(">") if part.strip()]


def _num(pid):
    m = re.search(r"(\d+)$", pid or "")
    return int(m.group(1)) if m else None


def _ids(hits, det):
    out = []
    for h in hits or []:
        if h.get("detector") == det:
            out += list(h.get("ids") or [])
    return out


def _over_claims(text):
    t = (text or "").lower()
    return [w for w in FORBIDDEN if w in t]


def v_A1(d):
    sub, ctl = d.get("receipt"), d.get("control")
    if not sub or not ctl:
        return 2, "no receipts: %s" % d.get("why")
    f = []
    if sub.get("toolKinds") != [d["requested"]]:
        f.append("tool reported %s, want [%s] (the tool must not see the later change)" % (sub.get("toolKinds"), d["requested"]))
    rb = sub.get("readBackKinds") or [None]
    if rb[0] is None or rb[0] == d["requested"]:
        f.append("read-back kind %s: the substitution is not visible" % rb)
    if not sub.get("mismatch"):
        f.append("substituted receipt mismatch=False")
    if not any(d["requested"] in p and str(rb[0]) in p for p in d.get("problems") or []):
        f.append("receipt_problems %s do not name requested vs actual" % d.get("problems"))
    if ctl.get("mismatch") or ctl.get("missingOnReadBack") or ctl.get("toolKinds") != [d["requested"]] \
            or ctl.get("readBackKinds") != [d["requested"]]:
        f.append("control receipt not clean: %s" % ctl)
    return (1 if f else 0), "; ".join(f) or "asked %s, tool said %s, map reads %s; control clean" % (
        d["requested"], sub.get("toolKinds"), rb)


def v_A2(d):
    if d.get("why"):
        return 2, d["why"]
    first, second = d.get("first") or [], d.get("second") or []
    f = []
    if "Eclipse" in first or "Eclipse" in second:
        f.append("Eclipse reported although the bounded expectation admitted it (first %s, second %s)" % (first, second))
    if "Aurora" not in second:
        f.append("Aurora not reported once the bound (1) was used: %s" % second)
    return (1 if f else 0), "; ".join(f) or "Eclipse admitted (max_count=1), Aurora reported: %s" % second


def v_A3(d):
    pid, hits = d.get("id"), d.get("hits")
    if not pid or hits is None:
        return 2, "no joiner staged: %s" % d.get("why")
    f = []
    if pid not in _ids(hits, "player_joiner"):
        f.append("player_joiner did not name %s" % pid)
    for det in ("pawn_arrived", "pawn_state_changed"):
        if pid in _ids(hits, det):
            f.append("%s also claims %s" % (det, pid))
    return (1 if f else 0), "; ".join(f) or "player_joiner names %s; no double report" % pid


def v_A4(d):
    w, j, hits, rep = d.get("warg"), d.get("joiner"), d.get("hits"), d.get("rows")
    if not w or not j or hits is None or rep is None:
        return 2, "scene not staged: %s" % d.get("why")
    f = []
    named = set()
    for h in hits:
        named.update(h.get("ids") or [])
    for pid in (w, j):
        if pid not in named:
            f.append("no detector named %s" % pid)
    rows = dict((r["id"], r) for r in rep)
    rw, rj = rows.get(w), rows.get(j)
    if not rw or not rj:
        return 1, "scene_report rows missing (warg %s, joiner %s)" % (bool(rw), bool(rj))
    if rw.get("relation") != "no-faction" or not str(rw.get("aggression") or "").startswith("mental:Manhunter"):
        f.append("warg hostility not decomposed: relation %s aggression %s" % (rw.get("relation"), rw.get("aggression")))
    if rj.get("relation") != "player":
        f.append("joiner relation %s, want player" % rj.get("relation"))
    for r in (rw, rj):
        if r.get("involvement") not in ("unknown", "confirmedIndirectAction"):
            f.append("%s involvement %s" % (r["id"], r.get("involvement")))
        if _over_claims(r.get("statement")):
            f.append("%s statement over-claims %s" % (r["id"], _over_claims(r.get("statement"))))
    text = d.get("text") or ""
    lines = dict((pid, [ln for ln in text.splitlines() if ln.startswith(pid + " ")]) for pid in (w, j))
    for pid, r, need in ((w, rw, ("no-faction", "mental:Manhunter")), (j, rj, ("player",))):
        ln = (lines[pid] or [""])[0]
        if not ln:
            f.append("rendered text has no row for %s" % pid)
        elif not all(n in ln for n in need) or str(r.get("involvement")) not in ln:
            f.append("rendered row for %s lacks %s / involvement: %s" % (pid, need, ln.strip()[:120]))
        elif _over_claims(ln):
            f.append("rendered row for %s over-claims %s" % (pid, _over_claims(ln)))
    return (1 if f else 0), "; ".join(f) or "named %s (manhunter, no-faction) and %s (player joiner)" % (w, j)


def v_A5(d):
    pid, hits = d.get("id"), d.get("hits")
    if not pid or hits is None:
        return 2, "no stranger staged: %s" % d.get("why")
    f = []
    sc = [h for h in hits if h.get("detector") == "pawn_state_changed" and pid in (h.get("ids") or [])]
    if not sc:
        f.append("pawn_state_changed did not report %s" % pid)
    elif sc[0].get("isPlayerAfter") is not True or sc[0].get("isPlayerBefore") is not False:
        f.append("state change %s, want isPlayer False -> True" % sc[0])
    for det in ("player_joiner", "pawn_arrived"):
        if pid in _ids(hits, det):
            f.append("%s reports the recruit %s as an arrival" % (det, pid))
    return (1 if f else 0), "; ".join(f) or "%s recruited: pawn_state_changed only" % pid


def v_A6(d):
    pid, hits = d.get("id"), d.get("hits")
    if not pid or hits is None:
        return 2, "no round trip: %s" % d.get("why")
    if not d.get("back_ok"):
        return 2, "caravan did not come back: %s" % d.get("back")
    f = []
    if pid not in _ids(hits, "player_joiner"):
        f.append("player_joiner did not report the returning colonist %s" % pid)
    mx = d.get("baseline_max")
    if _num(pid) is None or mx is None or not _num(pid) < mx:
        f.append("not an old id: %s vs baseline max %s (the case is vacuous)" % (pid, mx))
    return (1 if f else 0), "; ".join(f) or "old id %s (< %s) reported on return" % (pid, mx)


def v_A7(d):
    amb, one, ids = d.get("ambiguous"), d.get("single"), d.get("ids") or []
    if amb is None or len(ids) < 2:
        return 2, "two muffalo not staged: %s" % d.get("why")
    f = []
    listed = [a.get("id") for a in amb.get("ambiguous") or []]
    if amb.get("resolved") is not False or amb.get("what"):
        f.append("name selector resolved=%s what=%s (picked one?)" % (amb.get("resolved"), amb.get("what")))
    if not set(ids) <= set(listed):
        f.append("ambiguous list %s lacks %s" % (listed, ids))
    if not (one or {}).get("success") or (one or {}).get("resolved") is not True \
            or ((one or {}).get("what") or {}).get("id") != ids[0]:
        f.append("id selector did not resolve: %s" % str(one)[:200])
    return (1 if f else 0), "; ".join(f) or "%d candidates listed, none picked; id resolves" % len(listed)


def v_A8(d):
    row = d.get("row")
    if not row:
        return 2, "no worker-false incident found among %s: %s" % (FAIL_CANDIDATES, d.get("why"))
    f = []
    if str(row.get("returned")).lower() != "false":
        f.append("returned %s" % row.get("returned"))
    if str(row.get("outerBodyRan")).lower() != "true":
        f.append("outerBodyRan %s" % row.get("outerBodyRan"))
    if row.get("called") is not True:
        f.append("called %s" % row.get("called"))
    st = (row.get("statement") or "").lower()
    if "fired" in st or _over_claims(st):
        f.append("statement claims more than a call: %s" % row.get("statement"))
    if (d.get("tool") or {}).get("fired") is not False:
        f.append("tool fired=%s" % (d.get("tool") or {}).get("fired"))
    return (1 if f else 0), "; ".join(f) or "%s called, returned false: %s" % (row.get("def"), row.get("statement"))


def _raid_chain_ok(chain):
    k = _chain_kinds(chain)
    return bool(k) and k[0] == "bridge:jawa/fire_incident" and "incident:RaidEnemy" in k   # bridge-ROOTED


def _same_call(pawn_chain, row_chain):
    """The pawn was generated inside THIS journal row's context: its chain is the row's chain, ids included, or
    nested under it (a different RaidEnemy#n is another call)."""
    pc, rc = (pawn_chain or "").strip(), (row_chain or "").strip()
    return bool(rc) and (pc == rc or pc.startswith(rc + " > "))


def v_A9(d):
    row = d.get("row")
    if not row and (d.get("tool") or {}).get("fired") is True:
        return 1, "the raid fired but the installed recorder journaled no RaidEnemy row"
    if not row:
        return 2, "no RaidEnemy row: %s" % d.get("why")
    if (d.get("tool") or {}).get("blockedByDialog"):
        return 2, "a dialog swallowed the raid (blockedByDialog): not this recorder's case"
    f = []
    if not _raid_chain_ok(row.get("chain")):
        f.append("journal chain %s" % row.get("chain"))
    if str(row.get("returned")).lower() != "true":
        f.append("returned %s" % row.get("returned"))
    if not (row.get("pawnsGeneratedDuring") or 0) > 0:
        f.append("pawnsGeneratedDuring %s" % row.get("pawnsGeneratedDuring"))
    origins = d.get("origins") or []
    bad = [o["id"] for o in origins if not _same_call((o.get("generation") or {}).get("chain"), row.get("chain"))]
    missing = sorted(set(d.get("new") or []) - set(o["id"] for o in origins))
    if missing:
        f.append("no pawn_origin row for raid pawns %s" % missing[:5])
    if not origins:
        f.append("no raid pawn on the map to read")
    elif bad:
        f.append("raid pawns without the chain: %s" % bad[:5])
    return (1 if f else 0), "; ".join(f) or "chain %s, %d pawn(s) carry it" % (row.get("chain"), len(origins))


def v_A10(d):
    row = d.get("row")
    if not row:
        return 2, "no deferred (drop-pod) raid in %s tries: %s" % (d.get("tries"), d.get("why"))
    f = []
    origins = d.get("origins") or []
    missing = sorted(set(d.get("new") or []) - set(o["id"] for o in origins))
    if missing:
        f.append("no pawn_origin row for landed pawns %s" % missing[:5])
    if not _raid_chain_ok(row.get("chain")):
        f.append("journal chain %s" % row.get("chain"))
    if not origins:
        return 1, "pods never delivered a pawn after %s ticks (row %s)" % (d.get("waited"), row.get("aseq"))
    for o in origins:
        g, s = o.get("generation") or {}, o.get("spawn") or {}
        if not _same_call(g.get("chain"), row.get("chain")):
            f.append("%s generation chain %s, not this call's %s" % (o["id"], g.get("chain"), row.get("chain")))
        if not (s.get("tick") or 0) > (row.get("tick") or 0):
            f.append("%s spawned at %s, not after the call at %s" % (o["id"], s.get("tick"), row.get("tick")))
        if o.get("ourInvolvement") != "confirmedIndirectAction":
            f.append("%s involvement %s" % (o["id"], o.get("ourInvolvement")))
    return (1 if f else 0), "; ".join(f[:5]) or "%d pawn(s) landed after tick %s and read %s" % (
        len(origins), row.get("tick"), (origins[0].get("generation") or {}).get("chain"))


def v_A11(d):
    st = d.get("status") or {}
    if not st.get("success"):
        return 2, "no awareness status: %s" % str(st)[:200]
    if not (st.get("options") or {}).get("install.generation-early"):
        return 2, "precondition: awareness_settings.json lacks \"install.generation-early\": true at launch"
    f = []
    if st.get("startedBy") != "bridge-registration":
        f.append("startedBy %s" % st.get("startedBy"))
    if not str(st.get("generationHook") or "").startswith("installed early"):
        f.append("generationHook %s" % st.get("generationHook"))
    animals = d.get("animals") or []
    if not animals:
        return 2, "no factionless animal on the map to read (quiet prep removed them?)"
    mg = [a["id"] for a in animals if "mapgen" in [k.split(":")[0] for k in _chain_kinds((a.get("generation") or {}).get("chain"))]]
    if not mg:
        f.append("none of %d animals reads a mapgen chain (e.g. %s)" % (len(animals), (animals[0].get("generation") or {}).get("chain")))
    return (1 if f else 0), "; ".join(f) or "%d/%d animals read mapgen (%s)" % (
        len(mg), len(animals), [(a.get("generation") or {}).get("chain") for a in animals if a["id"] == mg[0]][0])


def v_A12(d):
    o = d.get("origin")
    if not d.get("back_ok"):
        return 2, "caravan did not come back: %s" % d.get("back")
    if not o:
        return 1, "no pawn_origin row for %s" % d.get("id")
    c = (o.get("spawn") or {}).get("classification")
    if c not in ("observedRespawn", "mapTransfer"):
        return 1, "%s spawn classification %s after the round trip" % (o.get("id"), c)
    return 0, "%s reads %s: %s" % (o.get("id"), c, o.get("statement"))


def v_A13(d):
    b, a = d.get("before") or {}, d.get("after") or {}
    if not b.get("success") or not a.get("success"):
        return 2, "status unreadable: %s" % d.get("why")
    f = []
    over_b = (b.get("evictions") or {}).get("incidents") or 0
    over_a = (a.get("evictions") or {}).get("incidents") or 0
    ret_b = (b.get("retained") or {}).get("incidents") or 0
    ret_a = (a.get("retained") or {}).get("incidents")
    want = max(0, ret_b + d["calls"] - RING)
    if ret_a != RING:
        f.append("retained %s after %d calls, want %d" % (ret_a, d["calls"], RING))
    if over_a - over_b != want:
        f.append("overwritten rose %d, want exactly %d (paused: only our calls)" % (over_a - over_b, want))
    j = d.get("journal") or {}
    if j.get("overwritten") != over_a:
        f.append("journal overwritten %s != status %s" % (j.get("overwritten"), over_a))
    if not (j.get("oldestRetainedSeq") or -1) > (d.get("oldest_before") or -1):
        f.append("oldest retained seq %s did not advance past %s" % (j.get("oldestRetainedSeq"), d.get("oldest_before")))
    return (1 if f else 0), "; ".join(f) or "retained %d, overwritten %d -> %d (+%d == %d)" % (
        ret_a, over_b, over_a, over_a - over_b, want)


VERDICTS = dict(("A%d" % i, globals()["v_A%d" % i]) for i in range(1, 14))


def verdict(clause, d):
    try:
        return VERDICTS[clause](d)
    except Exception as e:                                      # noqa: BLE001 - a malformed read is not a pass
        return 2, "verdict could not read the data: %s: %s" % (type(e).__name__, e)


# ------------------------------------------------------------------------------------------------ live gathering
def _setup_path():
    sys.path.insert(0, HERE)
    import common  # noqa: F401  (puts modcheck, Utils on sys.path)


class Live(object):
    def __init__(self, s):
        from common import call
        self.s, self._call, self.spawned = s, call, []

    def call(self, tool, **p):
        return self._call(self.s, tool, **p)

    def anchor(self):
        import helpers as H
        ax, az, _ = H.safe_anchor(self.s)
        return ax, az

    def spawn(self, kind, faction, x, z, count=1):
        r = self.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=count)
        ids = [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
        self.spawned += ids
        return r, ids

    def rows(self):
        import helpers as H
        return H.read_pawns(self.s, health=False)

    def snap(self):
        import snapshot
        return snapshot.take_snapshot(self.s, tier="full", companion=True)

    def baseline(self):
        import snapshot
        return snapshot.Baseline(self.snap())

    def hits(self, base, exps=None, anchor=None):
        import detectors
        out = []
        for h in detectors.sweep(self.snap(), base, exps, anchor):
            ev = h.evidence or {}
            ids = list(ev.get("ids") or ([ev["id"]] if ev.get("id") else []))
            ids += [q.get("id") for q in ev.get("pawns") or [] if isinstance(q, dict) and q.get("id") not in ids]
            out.append({"detector": h.detector, "summary": h.summary, "ids": ids,
                        "isPlayerBefore": ev.get("isPlayerBefore"), "isPlayerAfter": ev.get("isPlayerAfter"),
                        "def": ev.get("def")})
        return out

    def status(self):
        return self.call("jawa/awareness")

    def origin(self, ids):
        r = self.call("jawa/pawn_origin", ids=",".join(ids))
        return dict((o["id"], o) for o in r.get("pawns") or [])

    def journal_since(self, seq):
        return self.call("jawa/incident_journal", sinceSeq=seq, limit=RING).get("rows") or []

    def advance(self, n):
        import helpers as H
        H.fast_advance(self.s, n, margin=0)

    def cleanup(self):
        import helpers as H
        if self.spawned:
            try:
                H.remove_visitors(self.s, self.spawned)
            except Exception:                                   # noqa: BLE001 - housekeeping, never a verdict
                pass


def g_A1(L):
    ax, az = L.anchor()
    want = "Tribal_Warrior"
    r, ids = L.spawn(want, "none", ax, az)
    rc, cids = L.spawn(want, "none", ax + 3, az)
    if not ids or not cids:
        return {"why": "spawn failed: %s" % r.get("message")}
    L.call("jawa/set_pawn_faction", pawn=ids[0], faction="player")
    import contract
    rows = L.rows()
    sub = contract.spawn_receipt("A1", "jawa/spawn_pawn", want, r, rows)
    ctl = contract.spawn_receipt("A1-control", "jawa/spawn_pawn", want, rc, rows)
    return {"requested": want, "receipt": sub, "control": ctl, "problems": contract.receipt_problems([sub])}


def g_A2(L):
    import detectors
    base = L.baseline()
    if base.snap["sources"].get("weather_get", {}).get("complete") is False:
        return {"why": "weather_get unreadable: conditions cannot be judged"}
    if {"Eclipse", "Aurora"} & base.conditions:
        return {"why": "Eclipse/Aurora already active at baseline: %s" % sorted(base.conditions)}
    exps = detectors.Expectations()
    exps.expect("condition", lambda c: True, max_count=1)
    try:
        L.call("jawa/game_condition", action="start", condition="Eclipse", durationTicks=2500)
        first = [h["def"] for h in L.hits(base, exps) if h["detector"] == "condition_unexpected"]
        L.call("jawa/game_condition", action="start", condition="Aurora", durationTicks=2500)
        second = [h["def"] for h in L.hits(base, exps) if h["detector"] == "condition_unexpected"]
    finally:
        for c in ("Eclipse", "Aurora"):
            L.call("jawa/game_condition", action="end", condition=c)
    return {"first": first, "second": second}


def g_A3(L):
    ax, az = L.anchor()
    base = L.baseline()
    r, ids = L.spawn("Colonist", "player", ax, az)
    if not ids:
        return {"why": r.get("message")}
    return {"id": ids[0], "hits": L.hits(base, anchor=(ax, az))}


def _statement(org):
    return org.get("statement") if isinstance(org, dict) else str(org)


def g_A4(L):
    import scene_report
    ax, az = L.anchor()
    base = L.baseline()
    rw, w = L.spawn("Warg", "none", ax + 5, az)
    rj, j = L.spawn("Colonist", "player", ax - 5, az)
    if not w or not j:
        return {"why": "spawn failed: %s / %s" % (rw.get("message"), rj.get("message"))}
    m = L.call("jawa/pawn_mental", pawn=w[0], action="start", state="Manhunter")
    if not m.get("success"):
        return {"why": "Manhunter did not start: %s" % m.get("message")}
    hits = L.hits(base, anchor=(ax, az))
    rep = scene_report.collect(L.s, anchor=(ax, az))
    rows = [{"id": p["id"], "relation": p["threat"]["factionRelationToPlayer"],
             "aggression": p["threat"]["aggressionReason"], "involvement": p["ourInvolvement"],
             "statement": _statement(p["evidence"]["origin"])} for p in rep["pawns"]]
    return {"warg": w[0], "joiner": j[0], "hits": hits, "rows": rows, "text": scene_report.render_text(rep)}


def g_A5(L):
    ax, az = L.anchor()
    r, ids = L.spawn("Tribal_Warrior", "none", ax, az)
    if not ids:
        return {"why": r.get("message")}
    base = L.baseline()
    f = L.call("jawa/set_pawn_faction", pawn=ids[0], faction="player")
    if not f.get("success"):
        return {"why": "set_pawn_faction: %s" % f.get("message")}
    return {"id": ids[0], "hits": L.hits(base, anchor=(ax, az))}


def _round_trip(L, between=None):
    ax, az = L.anchor()
    r, ids = L.spawn("Colonist", "player", ax, az)
    if not ids:
        return None, {"why": r.get("message")}
    out = L.call("jawa/caravan_create", pawns=ids[0])
    if not out.get("success"):
        return ids[0], {"why": "caravan_create: %s" % out.get("message")}
    extra = between() if between else None
    back = L.call("jawa/static_call", type=PROBE, method="CaravanBack", args=ids[0])
    text = json.dumps(back)
    return ids[0], {"back": text[:300], "back_ok": "AWAREPROOF back ok=True" in text, "extra": extra}


def g_A6(L):
    state = {}

    def between():
        ax, az = L.anchor()
        L.spawn("Tribal_Warrior", "none", ax + 4, az)        # a NEWER id than the travelling colonist
        state["base"] = L.baseline()
    pid, d = _round_trip(L, between)
    if not pid or "base" not in state:
        return d
    base = state["base"]
    d.update({"id": pid, "hits": L.hits(base), "baseline_max": max([_num(i) or 0 for i in base.pawn_ids] or [0])})
    return d


def g_A7(L):
    ax, az = L.anchor()
    r, ids = L.spawn("Muffalo", "none", ax, az, count=2)
    if len(ids) < 2:
        return {"why": r.get("message"), "ids": ids}
    label = (r.get("pawns") or [{}])[0].get("name") or "Muffalo"
    return {"ids": ids, "ambiguous": L.call("jawa/thing_explain", name=label),
            "single": L.call("jawa/thing_explain", id=ids[0])}


def _seq(L):
    return L.status().get("seq") or -1


def g_A8(L):
    tried = []
    for cand in FAIL_CANDIDATES:
        seq = _seq(L)
        t = L.call("jawa/fire_incident", incidentDef=cand)
        tried.append("%s fired=%s" % (cand, t.get("fired")))
        if t.get("fired") is False:
            rows = [r for r in L.journal_since(seq) if r.get("def") == cand]
            if rows:
                return {"row": rows[-1], "tool": t}
            return {"why": "%s did not fire but has no journal row" % cand, "row": None}
    return {"why": "; ".join(tried)}


def _raid(L, faction=None):
    seq = _seq(L)
    p = {"incidentDef": "RaidEnemy", "points": 100.0}
    if faction:
        p["faction"] = faction
    t = L.call("jawa/fire_incident", **p)
    rows = [r for r in L.journal_since(seq) if r.get("def") == "RaidEnemy"]
    return t, (rows[-1] if rows else None)


def _hostiles(L, before):
    return [p["id"] for p in L.rows() if p.get("hostile") and not p.get("dead") and p["id"] not in before]


def g_A9(L):
    before = set(p["id"] for p in L.rows())
    try:
        t, row = _raid(L)
        if row is None:
            return {"why": "no journal row: %s" % t.get("message"), "tool": t}
        if not (row.get("pawnsSpawnedDuring") or 0):
            L.advance(600)                                     # drop pods: let them land before reading
        new = _hostiles(L, before)
        o = L.origin(new) if new else {}
        return {"row": row, "tool": t, "origins": list(o.values()), "new": new}
    finally:
        import helpers as H
        H.kill_hostiles(L.s)


def g_A10(L):
    import helpers as H
    tries = 0
    try:
        for tries in range(1, 4):
            before = set(p["id"] for p in L.rows())
            t, row = _raid(L, "Mechanoid")
            if row and (row.get("pawnsGeneratedDuring") or 0) > 0 and not (row.get("pawnsSpawnedDuring") or 0):
                L.advance(600)
                new = _hostiles(L, before)
                o = L.origin(new) if new else {}
                return {"row": row, "origins": list(o.values()), "new": new, "waited": 600, "tries": tries}
            H.kill_hostiles(L.s)
        return {"tries": tries, "why": "every raid delivered during the call (walk-in)"}
    finally:
        H.kill_hostiles(L.s)


def g_A11(L):
    st = L.status()
    rows = [p for p in L.rows() if p.get("faction") is None and p.get("intelligence") == "Animal"
            and not p.get("dead") and p.get("spawned", True)]
    o = L.origin([p["id"] for p in rows]) if rows else {}
    return {"status": st, "animals": list(o.values())}


def g_A12(L):
    pid, d = _round_trip(L)
    if pid and d.get("back_ok"):
        d["origin"] = L.origin([pid]).get(pid)
    d["id"] = pid
    return d


def g_A13(L):
    cand = None
    for c in FAIL_CANDIDATES:                                   # a call that changes nothing on the map
        if L.call("jawa/fire_incident", incidentDef=c).get("fired") is False:
            cand = c
            break
    if cand is None:
        return {"why": "no worker-false incident to repeat", "before": {}, "after": {}}
    before = L.status()
    j0 = L.call("jawa/incident_journal", limit=1)
    n = RING + 20
    for _ in range(n):
        L.call("jawa/fire_incident", incidentDef=cand)
    return {"before": before, "after": L.status(), "calls": n, "oldest_before": j0.get("oldestRetainedSeq"),
            "journal": L.call("jawa/incident_journal", limit=1), "incident": cand}


def main(argv):
    if len(argv) != 2 or argv[1] not in CLAUSES:
        print(__doc__)
        return 2
    clause = argv[1]
    try:
        _setup_path()
        from rimdrive import Session
    except Exception as e:                                      # noqa: BLE001
        print("%s UNMEASURED: harness import failed: %s" % (clause, e))
        return 2
    try:
        with Session(lock=None, focus=False, strict=False, quiet=True) as s:
            L = Live(s)
            mi = L.call("jawa/map_info")
            if not mi.get("success", True) or mi.get("sizeX") is None:
                print("%s UNMEASURED: no current map: %s" % (clause, str(mi)[:200]))
                return 2
            st = L.status()
            if not st.get("installed"):
                print("%s UNMEASURED: awareness recorder not installed: %s %s" % (
                    clause, st.get("installStatus"), st.get("installDetail") or st.get("message")))
                return 2
            if clause != "A11":
                L.call("jawa/awareness", action="arm", minutes=30)      # GeneratePawn hook (lazy by default)
            import helpers as H
            H.pause(s)
            try:
                d = globals()["g_" + clause](L)
            finally:
                L.cleanup()
    except Exception as e:                                      # noqa: BLE001 - any transport failure: the proof could not see
        print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, str(e)[:300]))
        return 2
    code, why = verdict(clause, d)
    print("%s %s: %s" % (clause, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code], why))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
