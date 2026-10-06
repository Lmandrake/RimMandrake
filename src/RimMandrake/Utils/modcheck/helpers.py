"""modcheck.helpers -- repeatable, verified situational helpers for northstar scripts.

Design: design/RimMandrake/northstar_helpers_plan.md section 4, as revised by section 10 (GPT review)
and corrected by section 11 (shapes MEASURED live 2026-10-01). Rules every helper obeys:

  * EXACT-ID. Nothing is killed, resurrected or healed by category or blast radius. The route that
    works on hostiles and wolves is `jawa/pawn_force_incapacitate action=kill` (measured). `jawa/damage
    Cut 500` reported success and left a raider standing, which is why verification is mandatory.
  * VERIFIED BY READ-BACK. `success:true` is never the proof (it is the commonest bridge lie). Every
    helper re-reads the world and returns a `HelperResult`; a helper that cannot show its effect
    raises `HelperUnverified`.
  * CONVERGES, NOT "IDEMPOTENT". Calling a helper twice leaves the world in the same verified
    postcondition; side effects (a corpse, a cleared incident) are recorded in the result.
  * TRANSACTIONAL SETTINGS. Debug/difficulty values are recorded BEFORE the first mutation and
    restored exactly (and verified) in `finally`.
  * BASELINE-DELTA RESTORE. Only hediffs that appeared after the baseline are reversed; nothing
    here wipes memories or "heals to perfect".
  * NO HIDDEN CLOCK. Helpers never step the game; the only tick-moving verb is in clockgate.

`session` is any object with `call(tool, **params) -> dict` (a rimdrive Session, or
`rimdrive.fake.FakeWorld` in the selftest).
"""
import clockgate

# MEASURED 2026-10-01: injuries that a restore may remove. Anything else (implants, addictions,
# immunity, pregnancy, genes) is never touched.
INJURY_DEFS = frozenset(["Cut", "Stab", "Scratch", "Bite", "Gunshot", "Burn", "Frostbite", "Crack",
                         "Bruise", "Shredded", "Crush", "Blunt", "Hypothermia", "Heatstroke",
                         "BloodLoss", "Flu", "Plague", "FoodPoisoning", "Malaria", "Infection",
                         "WoundInfection", "Malnutrition"])
RESTORE_NEEDS = ("Food", "Rest", "Joy")   # Mood is derived; it is never a restore target


class HelperUnverified(RuntimeError):
    """A helper acted but could not show the effect on a re-read."""


class HelperResult(object):
    def __init__(self, name, acted=0, verified=False, residue=None, evidence=None):
        self.name = name
        self.acted = acted
        self.verified = verified
        self.residue = list(residue or [])
        self.evidence = dict(evidence or {})

    def as_dict(self):
        return {"name": self.name, "acted": self.acted, "verified": self.verified,
                "residue": self.residue, "evidence": self.evidence}

    def __repr__(self):
        return "HelperResult(%s acted=%d verified=%s residue=%d)" % (
            self.name, self.acted, self.verified, len(self.residue))


# ------------------------------------------------------------------ reads
def read_pawns(session, health=True):
    """All pawn rows including corpses; raises HelperUnverified if the listing is truncated (a
    truncated list must never be read as 'the pawn is gone')."""
    r = session.call("jawa/list_pawns", includeHealth=health, includeCorpses=True, limit=500)
    if not r.get("success"):
        raise HelperUnverified("list_pawns failed: %s" % r.get("message"))
    if r.get("truncated"):
        raise HelperUnverified("list_pawns truncated (%s beyond the limit): refusing to act on a "
                               "partial roster" % r.get("truncated"))
    return r["pawns"]


def is_colonist(row):
    # MEASURED: the colony Husky has isPlayer=True; a colonist is a humanlike player pawn.
    return bool(row.get("isPlayer")) and row.get("intelligence") == "Humanlike"


def is_hostile(row):
    return bool(row.get("hostile")) and not row.get("dead")


def is_wildlife(row):
    # MEASURED: a factionless wolf reads hostile=False, so predators are found by this, not `hostile`.
    return (row.get("faction") is None and row.get("intelligence") == "Animal"
            and not row.get("dead") and row.get("spawned", True))


def is_stranger(row):
    return (row.get("faction") is None and row.get("intelligence") == "Humanlike"
            and not row.get("dead") and row.get("spawned", True))


def read_settings(session):
    r = session.call("jawa/debug_settings", action="list")
    if not r.get("success"):
        raise HelperUnverified("debug_settings list failed: %s" % r.get("message"))
    return dict((f["name"], f["value"]) for f in r["fields"])


# ------------------------------------------------------------------ transaction
class SettingsTransaction(object):
    """Record pre-mutation debug + difficulty values FIRST, change them through `set`, restore exactly
    on exit. The pre-values are read before the first write, so a half-failed prepare still restores
    to what a human had, not to a value this harness wrote."""

    DIFFICULTY_KEYS = ("threatScale", "allowBigThreats")

    def __init__(self, session):
        self.session = session
        self.pre_debug = {}
        self.pre_difficulty = {}
        self.touched_debug = []
        self.touched_difficulty = []
        self.restored = False

    def __enter__(self):
        self.pre_debug = read_settings(self.session)
        r = self.session.call("jawa/difficulty_tune")        # no args == read (measured)
        if r.get("success"):
            self.pre_difficulty = dict((k, r["before"][k]) for k in self.DIFFICULTY_KEYS if k in r["before"])
        return self

    def set_debug(self, field, value):
        if field not in self.pre_debug:
            raise HelperUnverified("debug field %r not present in debug_settings list" % field)
        self.touched_debug.append(field)
        r = self.session.call("jawa/debug_settings", action="set", field=field, value=value)
        now = read_settings(self.session).get(field)
        if now != value:
            raise HelperUnverified("debug_settings %s: asked %r, read back %r (success=%s)"
                                   % (field, value, now, r.get("success")))

    def set_difficulty(self, **kw):
        for k in kw:
            if k not in self.pre_difficulty:
                raise HelperUnverified("difficulty key %r not readable" % k)
        self.touched_difficulty.extend(kw)
        r = self.session.call("jawa/difficulty_tune", **kw)
        after = r.get("after") or {}
        for k, v in kw.items():
            if after.get(k) != v:
                raise HelperUnverified("difficulty_tune %s: asked %r, read back %r" % (k, v, after.get(k)))

    def restore(self):
        problems = []
        for f in set(self.touched_debug):
            want = self.pre_debug[f]
            self.session.call("jawa/debug_settings", action="set", field=f, value=want)
            if read_settings(self.session).get(f) != want:
                problems.append("debug %s not restored to %r" % (f, want))
        if self.touched_difficulty:
            kw = dict((k, self.pre_difficulty[k]) for k in set(self.touched_difficulty))
            r = self.session.call("jawa/difficulty_tune", **kw)
            after = r.get("after") or {}
            for k, v in kw.items():
                if after.get(k) != v:
                    problems.append("difficulty %s not restored to %r" % (k, v))
        self.restored = True
        if problems:
            raise HelperUnverified("; ".join(problems))

    def __exit__(self, et, ev, tb):
        self.restore()
        return False


# ------------------------------------------------------------------ helpers
def companion_available(session):
    """True iff the situational companion answers (jawa/pawn_census with limit=1 succeeds). Probed once per
    Watch; a missing companion DLL means the detectors fall back to inference, never to silence."""
    try:
        r = session.call("jawa/pawn_census", limit=1) or {}
    except Exception:                                           # noqa: BLE001
        return False
    return bool(r.get("success"))


def pause(session):
    clockgate.ensure_paused(session)
    return HelperResult("pause", acted=0, verified=True)


def storyteller_off(session, tx):
    """Stop NEW incidents and clear queued ones. NOT a general event freeze (GPT review, plan section
    10): quests, site logic and mod tickers can still raid. The queue clear is global (no selective
    removal exists yet: gap G6), so it is recorded in evidence."""
    tx.set_debug("enableStoryteller", False)
    tx.set_difficulty(threatScale=0.0, allowBigThreats=False)
    r = session.call("jawa/incident_queue_clear")
    return HelperResult("storyteller_off", acted=1, verified=True,
                        evidence={"cleared_count": r.get("clearedCount"), "cleared": r.get("cleared")})


def random_events_off(session, tx):
    tx.set_debug("enableRandomMentalStates", False)
    tx.set_debug("enableRandomDiseases", False)
    return HelperResult("random_events_off", acted=2, verified=True)


def _kill_ids(session, ids, name, pick, passes=2, action="kill"):
    """Kill exact ids with pawn_force_incapacitate; re-read; retry once; leftovers are residue.
    action="vanish" removes them with no death at all (see kill_hostiles)."""
    acted = 0
    done = set()
    for _ in range(passes):
        rows = [r for r in read_pawns(session, health=False) if r["id"] in ids and pick(r)]
        if not rows:
            break
        for r in rows:
            session.call("jawa/pawn_force_incapacitate", pawn=r["id"], action=action)
            acted += 1
            done.add(r["id"])
    left = [r["id"] for r in read_pawns(session, health=False) if r["id"] in ids and pick(r)]
    return HelperResult(name, acted=acted, verified=not left, residue=left,
                        evidence={"targeted": sorted(done)})


def kill_hostiles(session, expected_ids=()):
    """Remove hostiles WITHOUT a death. MEASURED 2026-10-05 (FlowWorks extensions, 4 chains UNMEASURED on
    "hostile_pawns: Fingerspike x3"): killing an Anomaly Toughspike/Trispike runs DeathActionWorker_Divide,
    which launches smaller fleshbeasts as flyers that LAND after the bland check, inside the next chain --
    the harness bred the surprise it then reported. Same family as the boomalope (kill_wildlife)."""
    exp = set(expected_ids)
    ids = set(r["id"] for r in read_pawns(session, health=False) if is_hostile(r) and r["id"] not in exp)
    return _kill_ids(session, ids, "kill_hostiles", is_hostile, action="vanish")


def kill_wildlife(session, expected_ids=()):
    """Remove wild animals WITHOUT killing them. MEASURED 2026-10-01: one dead Boomalope made 25 fires in 5
    ticks (39 by 30), and a fresh quicktest map carries explosive wildlife -- the harness's own kill was the
    source of the scattered fires, the "122 fires in 120 ticks" reading and a Droidworks fire surprise, all
    previously "unknown why". `jawa/destroy_bulk filter=factionlessAnimals` removes them with no death, no
    corpse and no detonation (fires stayed 0). It has no exclusion list, so it is used only when no expected
    animal is on the map; otherwise animals are killed per exact id and the caller MUST extinguish afterwards
    (prepare_bland_map orders it so)."""
    exp = set(expected_ids)
    rows = [r for r in read_pawns(session, health=False) if is_wildlife(r)]
    ids = set(r["id"] for r in rows if r["id"] not in exp)
    if not ids:
        return HelperResult("kill_wildlife", acted=0, verified=True, evidence={"route": "none-needed"})
    if not any(r["id"] in exp for r in rows):
        r = session.call("jawa/destroy_bulk", filter="factionlessAnimals", dryRun=False)
        left = [x["id"] for x in read_pawns(session, health=False) if x["id"] in ids and is_wildlife(x)]
        return HelperResult("kill_wildlife", acted=int(r.get("matchedCount") or 0), verified=not left,
                            residue=left, evidence={"route": "destroy_bulk"})
    res = _kill_ids(session, ids, "kill_wildlife", is_wildlife)
    res.evidence["route"] = "kill-per-id (an expected animal is present): explosion risk, extinguish after"
    return res


def clear_strangers(session, expected_ids=()):
    exp = set(expected_ids)
    ids = set(r["id"] for r in read_pawns(session, health=False) if is_stranger(r) and r["id"] not in exp)
    return _kill_ids(session, ids, "clear_strangers", is_stranger)


def extinguish(session):
    info = session.call("jawa/map_info")
    n = int(info.get("sizeX", 250))
    m = int(info.get("sizeZ", n))
    r = session.call("jawa/map_fire", action="extinguish", rect="0,0,%d,%d" % (n, m))
    fires = session.call("jawa/list_things", defName="Fire")
    if not fires.get("isCompleteList", False):
        raise HelperUnverified("fire list incomplete after extinguish")
    left = [f["id"] for f in fires.get("things", [])]
    return HelperResult("extinguish", acted=int(r.get("firesExtinguished") or 0), verified=not left,
                        residue=left)


def hediff_key(h):
    return (h.get("def"), h.get("part"))


def colonist_baseline(session):
    """Per-colonist hediff (def, part) set. Taken AFTER prepare, so the delta means 'since the test
    began'."""
    return dict((r["id"], set(hediff_key(h) for h in r["health"]["hediffs"]))
                for r in read_pawns(session) if is_colonist(r) and not r["dead"])


def calm_colonists(session, ids):
    ended = []
    for pid in ids:
        st = session.call("jawa/pawn_mental", pawn=pid, action="list").get("currentState")
        if st:
            session.call("jawa/pawn_mental", pawn=pid, action="end")
            ended.append(pid)
    left = [pid for pid in ids if session.call("jawa/pawn_mental", pawn=pid, action="list").get("currentState")]
    return HelperResult("calm_colonists", acted=len(ended), verified=not left, residue=left)


def restore_needs(session, ids):
    """Refill Food/Rest/Joy for pawns that HAVE those needs (MEASURED: a droid has no Food need, and
    demanding it made a bland map 'unestablishable'). Verified against the pawn's own need list, by `pct` (fraction of
    the pawn's OWN maximum): LIVE 2026-10-03 these colonists' Food tops out at level 0.9 (pct 1.0), so a level < 0.95
    test read every freshly fed colonist as unrestored and made every later suite's bland map 'unestablishable'."""
    acted = 0
    low = []
    # LIVE 2026-10-03: pawn_need(list) answered with no "needs" key for a pawn (BlueDesert: KeyError 'needs' aborted the
    # whole suite); a pawn with no readable need list simply has nothing to restore.
    for pid in ids:
        lv = dict((x["need"], x.get("pct", x["level"])) for x in (session.call("jawa/pawn_need", pawn=pid, action="list") or {}).get("needs") or [])
        have = [n for n in RESTORE_NEEDS if n in lv]
        for need in have:
            session.call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
            acted += 1
        lv2 = dict((x["need"], x.get("pct", x["level"])) for x in (session.call("jawa/pawn_need", pawn=pid, action="list") or {}).get("needs") or [])
        low.extend((pid, n) for n in have if lv2.get(n, 0) < 0.95)
    return HelperResult("restore_needs", acted=acted, verified=not low, residue=low)


def restore_colonists(session, baseline, resurrect=False):
    """Reverse ONLY post-baseline injuries on baseline colonists; end mental states; refill needs.
    `resurrect` is False by default: a death during a test invalidates the component and the harness
    aborts instead (plan section 10.1); pass True only for a deliberate reset between chains."""
    acted = 0
    residue = []
    rows = dict((r["id"], r) for r in read_pawns(session))
    for pid, base in baseline.items():
        row = rows.get(pid)
        if row is None:
            residue.append((pid, "missing"))
            continue
        if row["dead"]:
            if resurrect:
                session.call("jawa/pawn_resurrect", pawn=pid, restoreMissingParts=True, removeDiedThoughts=True)
                acted += 1
            else:
                residue.append((pid, "dead"))
            continue
        for h in row["health"]["hediffs"]:
            if hediff_key(h) in base or h["def"] not in INJURY_DEFS:
                continue
            r = session.call("jawa/pawn_health", pawn=pid, action="remove", hediff=h["def"], bodyPart=h.get("part") or "")
            acted += 1
            # MEASURED 2026-10-01: a chronic start-of-game wound ("old gunshot (aching)") was listed on part
            # "Leg" but remove(bodyPart="Leg") answered "Pawn has no hediff 'Gunshot' on Leg"; removing by def
            # alone worked. Fall back ONLY when no baseline instance of that def exists to be swept up too.
            if (not r.get("success") and "no hediff" in str(r.get("message", "")).lower()
                    and not any(k[0] == h["def"] for k in base)):
                session.call("jawa/pawn_health", pawn=pid, action="remove", hediff=h["def"])
    after = dict((r["id"], r) for r in read_pawns(session))
    live = [pid for pid in baseline if pid in after and not after[pid]["dead"]]
    # MEASURED live 2026-10-01 (abort_proof predator case): 'Gunshot/Shoulder' on a colonist read back as unremoved right
    # after a part-qualified remove, yet the pawn was clean minutes later. One retry by def alone, then re-read.
    for pid in live:
        for h in after[pid]["health"]["hediffs"]:
            if (hediff_key(h) not in baseline[pid] and h["def"] in INJURY_DEFS
                    and not any(k[0] == h["def"] for k in baseline[pid])):     # never sweep up a baseline instance
                session.call("jawa/pawn_health", pawn=pid, action="remove", hediff=h["def"])
                acted += 1
    after = dict((r["id"], r) for r in read_pawns(session))
    live = [pid for pid in baseline if pid in after and not after[pid]["dead"]]
    for pid in live:
        for h in after[pid]["health"]["hediffs"]:
            if hediff_key(h) not in baseline[pid] and h["def"] in INJURY_DEFS:
                residue.append((pid, "hediff %s/%s" % hediff_key(h)))
    c = calm_colonists(session, live)
    n = restore_needs(session, live)
    residue.extend(c.residue)
    residue.extend(n.residue)
    return HelperResult("restore_colonists", acted=acted + c.acted + n.acted, verified=not residue,
                        residue=residue)


# ------------------------------------------------------------------ bland map
class BlandReport(object):
    def __init__(self):
        self.steps = []
        self.problems = []
        self.notes = []
        self.baseline = None

    @property
    def bland(self):
        return not self.problems

    def as_dict(self):
        return {"bland": self.bland, "problems": self.problems, "notes": self.notes,
                "steps": [s.as_dict() for s in self.steps]}


def assert_bland(session, expected_ids=()):
    """Verification only: returns a list of problems (empty == bland). Counts come from the pawn
    roster and the fire list, never from an LLM."""
    exp = set(expected_ids)
    problems = []
    rows = read_pawns(session)
    hostile = [r["id"] for r in rows if is_hostile(r) and r["id"] not in exp]
    wild = [r["id"] for r in rows if is_wildlife(r) and r["id"] not in exp]
    strangers = [r["id"] for r in rows if is_stranger(r) and r["id"] not in exp]
    if hostile:
        problems.append("hostiles present: %s" % hostile)
    if wild:
        problems.append("wildlife present: %d" % len(wild))
    if strangers:
        problems.append("strangers present: %s" % strangers)
    fires = session.call("jawa/list_things", defName="Fire")
    if fires.get("countMatched"):
        problems.append("fires burning: %d" % fires["countMatched"])
    # A dead colonist that is one of the session's OWN fixtures (a test walker the litter teardown killed)
    # is not contamination: MEASURED 2026-10-01, that teardown is what made earlier "everyone is dead"
    # reports (E1) -- the harness killed its own spawns and the next suite read them as casualties.
    dead_col = [r["id"] for r in rows if is_colonist(r) and r["dead"] and r["id"] not in exp]
    if dead_col:
        problems.append("dead colonists: %s" % dead_col)
    return problems


def safe_anchor(session, expected_ids=(), margin=20):
    """The test anchor FARTHEST from every living colonist (Chebyshev), on a coarse grid. MEASURED
    2026-10-01: the default anchor is the map centre, where the colony spawns, and a droid-detonation test
    there killed two starting colonists. Returns (x, z, min_distance); falls back to the centre."""
    info = session.call("jawa/map_info")
    n, m = int(info.get("sizeX", 250)), int(info.get("sizeZ", info.get("sizeX", 250)))
    cols = [(r["x"], r["z"]) for r in read_pawns(session, health=False)
            if is_colonist(r) and not r["dead"] and r["spawned"] and r["id"] not in set(expected_ids)]
    best = (n // 2, m // 2, -1)
    for fx in (0.2, 0.35, 0.5, 0.65, 0.8):
        for fz in (0.2, 0.35, 0.5, 0.65, 0.8):
            x, z = int(n * fx), int(m * fz)
            if x < margin or z < margin or x > n - margin or z > m - margin:
                continue
            d = min([max(abs(x - cx), abs(z - cz)) for cx, cz in cols] or [10 ** 6])
            if d > best[2]:
                best = (x, z, d)
    return best


def prepare_bland_map(session, tx, expected_ids=(), kill=True, resurrect=False):
    """Fixed order, each step protecting the next (plan section 4): pause, stop new causes, remove
    present ones, restore colonists, baseline, verify. `kill=False` makes it a pure VERIFIER that
    refuses with problems instead of erasing anything (plan section 10.7 prefers that on a pristine
    checkpoint). Returns a BlandReport; `report.bland` False means 'could not establish a bland map'
    and the chain must be UNMEASURED, never FAIL against the mod."""
    rep = BlandReport()
    rep.steps.append(pause(session))
    if kill:
        rep.steps.append(storyteller_off(session, tx))
        rep.steps.append(random_events_off(session, tx))
        for h in (kill_hostiles, kill_wildlife, clear_strangers):
            rep.steps.append(h(session, expected_ids))
        rep.steps.append(extinguish(session))      # AFTER removals: a death can detonate and ignite
        # At START every injury on a colonist is contamination (measured: Frostbite within 60 ticks of a
        # fresh swamp map), so the restore baseline is the empty set; the real baseline is taken after.
        start = dict((r["id"], set()) for r in read_pawns(session, health=False)
                     if is_colonist(r) and (resurrect or not r["dead"]) and r["id"] not in set(expected_ids))
        rep.steps.append(restore_colonists(session, start, resurrect=resurrect))
        if resurrect and rep.steps[-1].acted:
            rep.notes.append("restore_colonists acted %d time(s) incl. resurrections of colonists a previous "
                             "chain lost: those deaths belong to THAT chain's evidence, not this one"
                             % rep.steps[-1].acted)
    rep.baseline = colonist_baseline(session)
    for s in rep.steps:
        if not s.verified:
            rep.problems.append("%s unverified: %s" % (s.name, s.residue))
    rep.problems.extend(assert_bland(session, expected_ids))
    return rep
