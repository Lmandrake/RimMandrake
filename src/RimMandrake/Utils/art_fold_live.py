#!/usr/bin/env python3
"""art_fold_live.py -- the LIVE half of the folded-*ArtOverride family script (ART_OVERRIDE_FAMILY_SCRIPT_1).

art_fold_check.py proves offline that every folded creature's art is on disk and patched in. This proves, in the
running game, that each creature SPAWNS DRAWING THAT ART without a magenta/missing-texture error. Parametrized from
art_fold_manifest.json (one row per creature), never a hand list:

  bind (offline)  manifest row -> the PawnKindDefs that draw its `new` texPath:
                    our Defs XML under src/ whose texPath (own, or an abstract ParentName's) is `new`;
                    our Patches XML whose Operation names PawnKindDef[defName="X"] and carries <texPath>new</texPath>;
                    the donor's own Defs whose texPath is `old`, when the row carries a value-matched `patch`.
  live            per kind: jawa/get_defs (found? its lifeStages/alternateGraphics now name `new`? flyer?);
                  every non-flyer present kind spawned WILD in ONE expectations_l2 batch (spawn readback, ticks, LogTap,
                  one screenshot counted for magenta); texture-error lines (Failed to find any textures / Could not load
                  Texture2D ...) naming a row's `new` path, from the tap AND the whole Player.log.

Per-row status (classified; the allowed ones carry no defect of this family):
  PASS            every present kind found, draws `new`, spawned, stayed, no log line, no texture error  (allowed)
  DEAD            manifest mode "dead": nothing binds the art by design, nothing to spawn                (allowed)
  DONOR-RETIRED   every bound kind is a retired donor's (infrastructure/state/facts/retired_mods.json) and absent
                  from the running game: the fold's patch is inert until DONOR_DEFS_PORT_TO_OURS_1 ports it (allowed)
  FLYER           draws `new` but its race flies: never live-spawned without the owner (standing ruling)  (allowed)
  UNBOUND         a non-dead row binds no kind at all                                                     (defect)
  NOT-LOADED      a bound kind of ours (or of a live donor) is absent from the running game              (defect)
  REPOINTED       present, but no lifeStage/alternate graphic names `new` (patch did not apply)          (defect)
  TEXLOG          a missing-texture line names the row's `new` path                                       (defect)
  NOT-SPAWNED / GONE / LOG   the expectations_l2 verdict for one of its kinds                             (defect)
Batch rows (one-sitting, log, art) come from expectations_l2; LOG-BLIND / ART-BLIND are UNMEASURED.

    python3 src/RimMandrake/Utils/art_fold_live.py --bind        offline binding table; exit 1 on an UNBOUND row
    python3 src/RimMandrake/Utils/art_fold_live.py --selftest    every status reachable, incl. a missing texture
    python.exe src/RimMandrake/Utils/art_fold_live.py --live     the sitting; JSON to Transient/northstar/ArtFold_<ts>.json
Exit: 0 every row allowed and every batch row PASS; 1 a defect; 2 UNMEASURED (no bridge, log/art blind, no rows).
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import art_fold_check as afc  # noqa: E402

REPO = afc.REPO
RETIRED = os.path.join(REPO, "infrastructure", "state", "facts", "retired_mods.json")
OUT_DIR = os.path.join(REPO, "Transient", "northstar")
ALLOWED = ("PASS", "DEAD", "DONOR-RETIRED", "FLYER")
UNMEASURED = ("LOG-BLIND", "ART-BLIND", "UNMEASURED")
TEX_RES = (re.compile(r"Failed to find any textures at (\S+)"),
           re.compile(r"No textures found at (?:path )?(\S+)"),
           re.compile(r"Could not load (?:UnityEngine\.)?Texture2D at '?([^'\s]+)'?"),
           re.compile(r"Could not (?:find|get) texture:?\s*(\S+)"))
XP_KIND = re.compile(r"PawnKindDef\[\s*defName\s*=\s*[\"']([A-Za-z0-9_]+)[\"']\s*\]")


# ---------------------------------------------------------------- offline binding

def _xml_roots(d, sub):
    for f in glob.glob(os.path.join(glob.escape(d), "**", "*.xml"), recursive=True):
        rel = os.path.relpath(f, d).replace(os.sep, "/")
        if "/About/" in "/" + rel or ("/%s/" % sub) not in "/" + rel:
            continue
        try:
            yield f, ET.parse(f).getroot()
        except (ET.ParseError, OSError):
            continue


def kind_texpaths(dirs):
    """{kindDefName: {texPath_lower}} over every PawnKindDef in the Defs/ trees of `dirs`, a ParentName's texPaths
    inherited when the child has no lifeStages of its own."""
    defs, named = {}, {}
    for d in dirs:
        for _, root in _xml_roots(d, "Defs"):
            for e in root.iter("PawnKindDef"):
                own = {(t.text or "").strip().lower() for t in e.iter("texPath") if (t.text or "").strip()}
                rec = (e.findtext("defName"), e.get("ParentName"), own, e.find("lifeStages") is not None)
                if e.get("Name"):
                    named[e.get("Name")] = rec
                if rec[0] and e.get("Abstract", "").lower() != "true":
                    defs[rec[0].strip()] = rec
    out = {}
    for k, (_, parent, own, has_ls) in defs.items():
        paths, seen = set(own), set()
        while parent and parent in named and parent not in seen and not has_ls:
            seen.add(parent)
            _, parent2, pown, has_ls = named[parent]
            paths |= pown
            parent = parent2
        out[k] = paths
    return out


def patch_kinds(d):
    """[(kindDefName, {texPath_lower})] for every WRITING operation under Patches/ of `d` (a direct <xpath> and a direct
    <value>) whose xpath names a PawnKindDef; the texPaths come from its own <value> only, so a Conditional's test
    xpath never inherits its <match>'s payload."""
    out = []
    for _, root in _xml_roots(d, "Patches"):
        for op in root.iter():
            xp, val = op.find("xpath"), op.find("value")
            if xp is None or val is None or not (xp.text or "").strip():
                continue
            ks = XP_KIND.findall(xp.text)
            if not ks:
                continue
            tps = {(t.text or "").strip().lower() for t in val.iter("texPath") if (t.text or "").strip()}
            for k in ks:
                out.append((k, tps))
    return out


def _norm_pid(pid):
    """A LoadFolders gate's packageId, minus the `_copy`/`_steam` suffix RimWorld gives a local copy of the same mod."""
    pid = pid.strip().lower()
    for suf in ("_copy", "_steam"):
        if pid.endswith(suf):
            pid = pid[:-len(suf)]
    return pid


def load_gates(d, version="v1.6"):
    """[(folder_rel, kind, {pid})] from `d`/LoadFolders.xml's `version` block (else `default`); kind is "any"
    (IfModActive: loads if any is active), "all" (IfModActiveAll) or None (ungated). None if there is no LoadFolders.xml
    (then the game loads the root and version folder ungated)."""
    try:
        root = ET.parse(os.path.join(d, "LoadFolders.xml")).getroot()
    except (ET.ParseError, OSError):
        return None
    blk = root.find(version)
    if blk is None:
        blk = root.find("default")
    if blk is None:
        return []
    out = []
    for li in blk.findall("li"):
        rel = (li.text or "").strip().replace("\\", "/").strip("/")
        if li.get("IfModActiveAll"):
            out.append((rel, "all", {_norm_pid(x) for x in li.get("IfModActiveAll").split(",") if x.strip()}))
        elif li.get("IfModActive"):
            out.append((rel, "any", {_norm_pid(x) for x in li.get("IfModActive").split(",") if x.strip()}))
        else:
            out.append((rel, None, set()))
    return out


def kind_gates(d, version="v1.6"):
    """{kindDefName: [(kind, {pid})]} for each PawnKindDef of donor `d` that the `version` block loads ONLY through
    gated folders (ART_OVERRIDE_FAMILY_SCRIPT_1: GR_Beetlefleet lives in VGE's 1.6/Mods/AlphaAnimals, gated
    IfModActive=sarg.alphaanimals). A kind with any ungated definition, or no LoadFolders.xml, is absent."""
    gates = load_gates(d, version)
    if not gates:
        return {}
    seen = {}
    for f, root in _xml_roots(d, "Defs"):
        rel = os.path.relpath(f, d).replace(os.sep, "/")
        hits = [(g, ids) for fr, g, ids in gates if rel.startswith((fr + "/" if fr else "") + "Defs/")]
        if not hits:
            continue  # this version does not load the file
        for e in root.iter("PawnKindDef"):
            k = (e.findtext("defName") or "").strip()
            if k and e.get("Abstract", "").lower() != "true":
                seen.setdefault(k, []).extend(hits)
    return {k: hs for k, hs in seen.items() if all(g for g, _ in hs)}


def gate_retired(gates, retired):
    """The retired packageIds that keep a gated kind out: every gate must be dead (an `any` gate with all its mods
    retired, an `all` gate with one retired); [] when some gate could still load it."""
    dead = set()
    for g, ids in gates or []:
        if g == "any" and ids and ids <= retired:
            dead |= ids
        elif g == "all" and ids & retired:
            dead |= ids & retired
        else:
            return []
    return sorted(dead)


def bind(rows, repo=REPO, donor_roots=afc.DONOR_ROOTS):
    """{creature: {"mode", "news", "kinds": {kind: source}, "gates": {kind: [(kind, {pid})]}}}; source is "ours" or
    "donor:<packageId>"; gates lists a donor kind the donor's LoadFolders.xml loads only behind IfModActive."""
    mods = [os.path.dirname(os.path.dirname(a)) for a in glob.glob(os.path.join(glob.escape(repo), "src", "*", "*",
                                                                                "About", "About.xml"))]
    mods += [d for d in glob.glob(os.path.join(glob.escape(repo), "src", "*", "*")) if os.path.isdir(d)
             and not os.path.isfile(os.path.join(d, "About", "About.xml"))]
    ours = kind_texpaths(sorted(set(mods)))
    ptch = [kp for d in sorted(set(mods)) for kp in patch_kinds(d)]
    donors, dgates = {}, {}
    out = {}
    for r in rows:
        news = sorted({g["new"] for g in r.get("groups", []) if g.get("new")})
        olds = sorted({g["old"] for g in r.get("groups", []) if g.get("old")})
        nl = {n.lower() for n in news}
        kinds = {}
        if r.get("mode") != "dead":
            for k, tps in ours.items():
                if tps & nl:
                    kinds[k] = "ours"
            patched = {k for k, tps in ptch if tps & nl}
            pid = r.get("donor")
            if pid and (r.get("patch") or patched - set(ours)):
                if pid not in donors:
                    dd = afc.donor_dir(pid, r.get("donor_hint"), donor_roots)
                    donors[pid] = kind_texpaths([dd]) if dd else {}
                    dgates[pid] = kind_gates(dd) if dd else {}
                if r.get("patch"):
                    ol = {o.lower() for o in olds} | nl
                    for k, tps in donors[pid].items():
                        if tps & ol:
                            kinds.setdefault(k, "donor:" + pid)
            for k in patched:  # owned by whoever DEFINES the kind, not by whoever patches it
                kinds.setdefault(k, "donor:" + pid if pid and k not in ours and k in donors.get(pid, {}) else "ours")
        gates = {k: dgates[src[6:]][k] for k, src in kinds.items() if src.startswith("donor:")
                 and k in dgates.get(src[6:], {})}
        out[r["creature"]] = {"mode": r.get("mode"), "news": news, "kinds": kinds, "gates": gates}
    return out


def _pid(d):
    try:
        return (ET.parse(os.path.join(d, "About", "About.xml")).getroot().findtext("packageId") or "").strip().lower()
    except (ET.ParseError, OSError):
        return ""


def composed_ids(repo=REPO):
    """{folded packageId: composed packageId}: a mod folded into RimMandrake.Biomes loads as mandrake.rm.biomes, never
    under its own id (ART_OVERRIDE_FAMILY_SCRIPT_1 read 'not in the running load: mandrake.rm.warscar, mandrake.rm.webwork'
    on a load holding the composed mod, 2026-11-05). {} when the repo has no compose manifest."""
    try:
        import biomes_compose
        return biomes_compose.folded_ids(os.path.join(repo, "src"))
    except Exception:       # noqa: BLE001  an unreadable manifest folds nothing: the plain ids are still required
        return {}


def required_mods(rows, binding, retired, repo=REPO, folded=None):
    """{packageId: why} the running load must hold before any row is judged: each live row's owner mod (manifest
    `owner`), the mod of ours that DEFINES each bound kind (RM_Ollathrix is Webwork's, skinned by Shokk), and each live
    (non-retired) donor a kind binds to. Read from the manifest and src/, never a hand list. Run 1 (2026-11-03) judged a
    load without Shokk and read its skin patch as REPOINTED: a tier gap scored as a mod defect."""
    homes = {}
    for a in sorted(glob.glob(os.path.join(glob.escape(repo), "src", "*", "*", "About", "About.xml"))):
        d = os.path.dirname(os.path.dirname(a))
        for k in kind_texpaths([d]):
            homes.setdefault(k, _pid(d) or "?" + os.path.relpath(d, repo))
    need = {}
    for r in rows:
        b = binding.get(r["creature"]) or {}
        if b.get("mode") == "dead" or not b.get("kinds"):
            continue
        if r.get("owner"):
            d = os.path.join(repo, r["owner"])
            need.setdefault(_pid(d) or "?" + r["owner"], "owner of " + r["creature"])
        for k, src in b["kinds"].items():
            if src == "ours" and k in homes:
                need.setdefault(homes[k], "defines " + k)
            elif src.startswith("donor:") and src.split(":", 1)[1].lower() not in retired:
                need.setdefault(src.split(":", 1)[1].lower(), "live donor of " + k)
    fold = composed_ids(repo) if folded is None else folded
    out = {}
    for p, why in need.items():
        out.setdefault(fold.get(p, p), why if p not in fold else "%s, as %s" % (why, p))
    return out


def load_gap(need, running):
    """-> why the running load cannot be judged, or None. running: lower-case packageIds, None when unreadable."""
    if running is None:
        return "jawa/running_mods unreadable: the load is unknown"
    miss = sorted(p for p in need if p not in running)
    if miss:
        return "not in the running load: " + ", ".join("%s (%s)" % (p, need[p]) for p in miss)
    return None


def retired_ids(path=RETIRED):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {str(x.get("packageId", "")).lower() for x in d.get("retired") or [] if isinstance(x, dict)}


# ---------------------------------------------------------------- pure verdict

def tex_hits(messages, news_by_row):
    """{creature: [message]} for texture-error lines whose path is (case-insensitively) a row's `new` or a facing of it."""
    out = {}
    for m in messages:
        for rx in TEX_RES:
            for p in rx.findall(m):
                p = p.strip().strip("'\".,").lower()
                for c, news in news_by_row.items():
                    for n in news:
                        n = n.lower()
                        if p == n or (p.startswith(n + "_") and len(p) - len(n) <= 8):
                            out.setdefault(c, []).append(m)
    return out


def texpaths_of(fields):
    """Every texPath string anywhere in a get_defs fields payload, lowercased (whole values, never substrings)."""
    out, stack = set(), [fields]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "texPath" and isinstance(v, str):
                    out.add(v.strip().lower())
                else:
                    stack.append(v)
        elif isinstance(x, list):
            stack.extend(x)
    return out


def draws(fields, news):
    return bool(texpaths_of(fields) & {n.lower() for n in news})


def is_flyer(race_fields):
    stats = (race_fields or {}).get("statBases")
    if not isinstance(stats, list):
        return None
    return any((st.get("value") or 0) > 0 for st in stats if isinstance(st, dict) and st.get("stat") == "MaxFlightTime")


def classify(binding, retired, live_defs, flyers, l2_status, texlog):
    """-> [row dict] one per creature. live_defs {kind: fields|None}; flyers {kind: bool|None};
    l2_status {kind: (status, detail)} for spawned kinds; texlog {creature: [msg]}."""
    rows = []
    for c in sorted(binding):
        b = binding[c]
        st, why, kinds = None, [], {}
        if b["mode"] == "dead":
            st = "DEAD"
            why.append("manifest mode dead: nothing binds the art")
        elif not b["kinds"]:
            st = "UNBOUND"
            why.append("no PawnKindDef of ours, our patches or the donor draws %s" % b["news"])
        else:
            bad, retired_absent, flyer_n, present = [], 0, 0, 0
            for k, src in sorted(b["kinds"].items()):
                f = live_defs.get(k)
                if f is None:
                    pid = src.split(":", 1)[1].lower() if src.startswith("donor:") else None
                    if pid and pid in retired:
                        kinds[k] = "absent (retired donor %s)" % pid
                        retired_absent += 1
                    elif pid and gate_retired(b.get("gates", {}).get(k), retired):
                        kinds[k] = "absent (donor %s loads it only if %s, retired)" % (
                            pid, "/".join(gate_retired(b["gates"][k], retired)))
                        retired_absent += 1
                    else:
                        kinds[k] = "NOT-LOADED"
                        bad.append(("NOT-LOADED", "%s (%s) absent from the running game" % (k, src)))
                    continue
                present += 1
                tps = texpaths_of(f)
                if not tps:
                    kinds[k] = "UNMEASURED"
                    bad.append(("UNMEASURED", "%s: no texPath readable in its get_defs fields" % k))
                    continue
                if not draws(f, b["news"]):
                    kinds[k] = "REPOINTED"
                    bad.append(("REPOINTED", "%s draws %s, none of %s" % (k, sorted(tps)[:3], b["news"])))
                    continue
                if flyers.get(k) is None:
                    kinds[k] = "UNMEASURED"
                    bad.append(("UNMEASURED", "%s race flight unreadable: not spawned" % k))
                    continue
                if flyers[k]:
                    kinds[k] = "FLYER"
                    flyer_n += 1
                    continue
                s, d = l2_status.get(k, ("UNMEASURED", "not in the spawn batch"))
                kinds[k] = s
                if s != "PASS":
                    bad.append((s, "%s: %s" % (k, d)))
            if texlog.get(c):
                bad.append(("TEXLOG", " | ".join(texlog[c][:2])))
            if bad:
                bad.sort(key=lambda x: x[0] in UNMEASURED)  # a definite defect outranks an unmeasured kind
                st = bad[0][0]
                why += [d for _, d in bad]
            elif present == 0:
                st = "DONOR-RETIRED"
                why.append("every bound kind is a retired donor's; port owed by DONOR_DEFS_PORT_TO_OURS_1")
            elif flyer_n == present:
                st = "FLYER"
                why.append("draws %s; flyer, never live-spawned without the owner" % b["news"])
            else:
                st = "PASS"
        rows.append({"creature": c, "status": st, "kinds": kinds or {k: "-" for k in b["kinds"]},
                     "news": b["news"], "detail": "; ".join(why)})
    return rows


def exit_code(rows, batch):
    if not rows:
        return 2
    if any(r["status"] not in ALLOWED and r["status"] not in UNMEASURED for r in rows) or \
            any(b["status"] not in ("PASS",) + UNMEASURED for b in batch):
        return 1
    if any(r["status"] in UNMEASURED for r in rows) or any(b["status"] != "PASS" for b in batch):
        return 2
    return 0


# ---------------------------------------------------------------- live (python.exe only)

class _M(object):
    """The shape expectations_l2 reads off a manifest: .item and .l2."""

    def __init__(self, item, kinds, ticks):
        import expectations_l2 as l2
        self.item = item
        self.l2 = l2.L2Spec([l2.Spawn("pawn", k, 1) for k in kinds], ticks)


def _player_log_lines():
    try:
        import game_paths
        with open(game_paths.PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            return [ln for ln in fh if any(rx.search(ln) for rx in TEX_RES)]
    except Exception:  # noqa: BLE001  an unreadable log is the tap's job to cover
        return []


def run_live(rows, ticks=300, log=print):
    import expectations_l2 as l2
    import validation_core as vc
    if not 1 <= int(ticks) <= l2.MAX_TICKS:
        raise ValueError("ticks must be 1..%d" % l2.MAX_TICKS)
    binding = bind(rows)
    retired = retired_ids()
    kinds = sorted({k for b in binding.values() for k in b["kinds"]})
    B = vc.Bridge()
    import live_def_check
    gap = load_gap(required_mods(rows, binding, retired), live_def_check.running_ids(
        B.call("jawa/running_mods", details=False, assembly="")))
    if gap:
        raise RuntimeError(gap)  # main: UNMEASURED, exit 2 -- the round restages the tier, nothing is judged
    if B.call("rimworld/get_ui_state").get("programState") != "Playing":
        log("no game in progress: starting a quicktest map")
        try:
            B.call("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
        except Exception as e:  # noqa: BLE001
            log("quicktest call ended: %s" % str(e))
            B = vc.Bridge()
    live_defs = {}
    for i in range(0, len(kinds), 40):
        live_defs.update(l2._get_defs(B, "PawnKindDef", kinds[i:i + 40], "race,lifeStages,alternateGraphics"))
    races = sorted({(f or {}).get("race") for f in live_defs.values() if f} - {None})
    race_f = {}
    for i in range(0, len(races), 40):
        race_f.update(l2._get_defs(B, "ThingDef", races[i:i + 40], "statBases"))
    flyers = {k: is_flyer(race_f.get((f or {}).get("race"))) for k, f in live_defs.items() if f}
    spawn = []
    for c, b in sorted(binding.items()):
        ks = [k for k in sorted(b["kinds"]) if live_defs.get(k) and flyers.get(k) is False and draws(live_defs[k], b["news"])]
        if ks:
            spawn.append(_M(c, ks, ticks))
    l2_status, batch = {}, []
    if spawn:
        out = l2.run_l2_live(spawn, shot_name="artfold_l2", log=log)
        for r in out:
            if r.scope == "BATCH":
                batch.append({"subject": r.subject, "status": r.status, "detail": r.detail})
            else:
                l2_status[r.subject.split(":", 1)[1]] = (r.status, r.detail)
    else:
        batch.append({"subject": "spawn", "status": "UNMEASURED", "detail": "no kind present to spawn"})
    msgs = [str(e.get("Message", "")) for e in (vc.TAP[0].since() if vc.TAP else [])] + _player_log_lines()
    texlog = tex_hits(msgs, {c: b["news"] for c, b in binding.items()})
    res = classify(binding, retired, live_defs, flyers, l2_status, texlog)
    return res, batch


# ---------------------------------------------------------------- selftest

def selftest():
    fails = []
    with tempfile.TemporaryDirectory() as td:
        def w(rel, text):
            p = os.path.join(td, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(text)
        w("src/A/Own/About/About.xml", "<ModMetaData><packageId>t.own</packageId></ModMetaData>")
        w("src/A/Own/Defs/k.xml", "<Defs><PawnKindDef Name=\"Base\" Abstract=\"True\"><lifeStages><li><bodyGraphicData>"
          "<texPath>Ours/Inh/Inh</texPath></bodyGraphicData></li></lifeStages></PawnKindDef>"
          "<PawnKindDef ParentName=\"Base\"><defName>K_Inh</defName></PawnKindDef>"
          "<PawnKindDef><defName>K_Own</defName><lifeStages><li><bodyGraphicData><texPath>Ours/Own/Own</texPath>"
          "</bodyGraphicData></li></lifeStages></PawnKindDef></Defs>")
        w("src/A/Own/Patches/p.xml", "<Patch><Operation Class=\"PatchOperationReplace\"><xpath>/Defs/PawnKindDef"
          "[defName=\"K_Pat\"]/lifeStages/li[1]/bodyGraphicData/texPath</xpath><value><texPath>Ours/Pat/Pat</texPath>"
          "</value></Operation><Operation Class=\"PatchOperationConditional\"><xpath>/Defs/PawnKindDef"
          "[defName=\"K_Gate\"]/label</xpath><match Class=\"PatchOperationReplace\"><xpath>/Defs/PawnKindDef"
          "[defName=\"K_Don2\"]/lifeStages/li[1]/bodyGraphicData/texPath</xpath><value><texPath>Ours/Don2/Don2"
          "</texPath></value></match></Operation></Patch>")
        w("donor/D/About/About.xml", "<ModMetaData><packageId>d.old</packageId></ModMetaData>")
        w("donor/D/Defs/k.xml", "<Defs><PawnKindDef><defName>K_Don</defName><lifeStages><li><bodyGraphicData>"
          "<texPath>Don/Old</texPath></bodyGraphicData></li></lifeStages></PawnKindDef>"
          "<PawnKindDef><defName>K_Don2</defName><lifeStages><li><bodyGraphicData><texPath>Don/Other</texPath>"
          "</bodyGraphicData></li></lifeStages></PawnKindDef></Defs>")
        rows = [{"creature": "Inh", "groups": [{"old": "x", "new": "Ours/Inh/Inh"}]},
                {"creature": "Own", "groups": [{"old": "x", "new": "Ours/Own/Own"}]},
                {"creature": "Pat", "groups": [{"old": "x", "new": "Ours/Pat/Pat"}]},
                {"creature": "Don", "groups": [{"old": "Don/Old", "new": "Ours/Don/Don"}], "patch": "p.xml",
                 "donor": "d.old", "donor_hint": os.path.join(td, "donor", "D")},
                {"creature": "Don2", "groups": [{"old": "Don/Other", "new": "Ours/Don2/Don2", "donor_literal": False}],
                 "donor": "d.old", "donor_hint": os.path.join(td, "donor", "D")},
                {"creature": "Dead", "mode": "dead", "groups": []},
                {"creature": "Loose", "groups": [{"old": "x", "new": "Ours/None/None"}]}]
        b = bind(rows, repo=td, donor_roots=(os.path.join(td, "donor"),))
        want = {"Inh": {"K_Inh": "ours"}, "Own": {"K_Own": "ours"}, "Pat": {"K_Pat": "ours"},
                "Don": {"K_Don": "donor:d.old"}, "Don2": {"K_Don2": "donor:d.old"}, "Dead": {}, "Loose": {}}
        for c, k in want.items():
            if b[c]["kinds"] != k:
                fails.append("bind %s: %r != %r" % (c, b[c]["kinds"], k))

        def fd(path):
            return {"race": "R", "lifeStages": [{"bodyGraphicData": {"texPath": path}}]}
        good = {"K_Inh": fd("Ours/Inh/Inh"), "K_Own": fd("Ours/Own/Own"), "K_Pat": fd("Ours/Pat/Pat"), "K_Don": None,
                "K_Don2": None}
        fl = {"K_Inh": False, "K_Own": False, "K_Pat": False}
        l2s = {k: ("PASS", "") for k in fl}

        def st(res):
            return {r["creature"]: r["status"] for r in res}
        base = st(classify(b, {"d.old"}, good, fl, l2s, {}))
        exp = {"Inh": "PASS", "Own": "PASS", "Pat": "PASS", "Don": "DONOR-RETIRED", "Don2": "DONOR-RETIRED",
               "Dead": "DEAD", "Loose": "UNBOUND"}
        if base != exp:
            fails.append("baseline %r" % base)
        cases = [  # (name, mutate -> (retired, live_defs, flyers, l2s, texlog), creature, want)
            ("donor live absent, not retired", lambda: (set(), good, fl, l2s, {}), "Don", "NOT-LOADED"),
            ("our kind not loaded", lambda: ({"d.old"}, dict(good, K_Own=None), fl, l2s, {}), "Own", "NOT-LOADED"),
            ("patch did not apply", lambda: ({"d.old"}, dict(good, K_Pat=fd("Elsewhere/X")), fl, l2s, {}), "Pat",
             "REPOINTED"),
            ("prefix is not the path", lambda: ({"d.old"}, dict(good, K_Own=fd("Ours/Own/OwnBackup")), fl, l2s, {}),
             "Own", "REPOINTED"),
            ("no texPath readable", lambda: ({"d.old"}, dict(good, K_Own={"race": "R"}), fl, l2s, {}), "Own",
             "UNMEASURED"),
            ("defect outranks unmeasured", lambda: ({"d.old"}, good, dict(fl, K_Own=None), l2s,
                                                    tex_hits(["Failed to find any textures at Ours/Own/Own"],
                                                             {c: v["news"] for c, v in b.items()})), "Own", "TEXLOG"),
            ("native unquoted texture line", lambda: ({"d.old"}, good, fl, l2s,
                                                      tex_hits(["Could not load UnityEngine.Texture2D at Ours/Inh/Inh_east"
                                                                " in any active mod or in base resources."],
                                                               {c: v["news"] for c, v in b.items()})), "Inh", "TEXLOG"),
            ("flyer", lambda: ({"d.old"}, good, dict(fl, K_Inh=True), l2s, {}), "Inh", "FLYER"),
            ("flight unreadable", lambda: ({"d.old"}, good, dict(fl, K_Inh=None), l2s, {}), "Inh", "UNMEASURED"),
            ("spawn failed", lambda: ({"d.old"}, good, fl, dict(l2s, K_Own=("NOT-SPAWNED", "x")), {}), "Own",
             "NOT-SPAWNED"),
            ("missing texture", lambda: ({"d.old"}, good, fl, l2s,
                                         tex_hits(["Failed to find any textures at ours/own/own while constructing"],
                                                  {c: v["news"] for c, v in b.items()})), "Own", "TEXLOG"),
            ("missing facing", lambda: ({"d.old"}, good, fl, l2s,
                                        tex_hits(["Could not load Texture2D at 'Ours/Pat/Pat_north'"],
                                                 {c: v["news"] for c, v in b.items()})), "Pat", "TEXLOG"),
        ]
        for name, mk, c, wnt in cases:
            got = st(classify(b, *mk()))[c]
            if got != wnt:
                fails.append("%s: %s -> %s, want %s" % (name, c, got, wnt))
        ok_rows = [r for r in classify(b, {"d.old"}, good, fl, l2s, {}) if r["creature"] != "Loose"]
        pb = [{"subject": "log", "status": "PASS"}]
        for name, rr, bb, wnt in [("all allowed", ok_rows, pb, 0), ("a defect", classify(b, {"d.old"}, good, fl, l2s, {}),
                                                                       pb, 1),
                                  ("log blind", ok_rows, [{"subject": "log", "status": "LOG-BLIND"}], 2),
                                  ("magenta", ok_rows, [{"subject": "art", "status": "ART"}], 1),
                                  ("no rows", [], pb, 2)]:
            if exit_code(rr, bb) != wnt:
                fails.append("exit %s: %s != %s" % (name, exit_code(rr, bb), wnt))
        # ARTFOLD_LOADFOLDER_FIX_BEETLE_BEHIND_DOOR: a live donor whose kind sits only in a LoadFolders folder gated on a
        # retired mod (VGE's 1.6/Mods/AlphaAnimals behind sarg.alphaanimals and its _copy alias)
        kd = "<Defs><PawnKindDef><defName>%s</defName><lifeStages><li><bodyGraphicData><texPath>%s</texPath>" \
             "</bodyGraphicData></li></lifeStages></PawnKindDef></Defs>"
        w("donor/G/About/About.xml", "<ModMetaData><packageId>d.live</packageId></ModMetaData>")
        w("donor/G/LoadFolders.xml", "<loadFolders><v1.6><li>/</li><li>1.6</li>"
          "<li IfModActive=\"d.gone\">1.6/Mods/Gone</li><li IfModActive=\"d.gone_copy\">1.6/Mods/Gone</li>"
          "<li IfModActive=\"d.other\">1.6/Mods/Other</li></v1.6></loadFolders>")
        w("donor/G/1.6/Mods/Gone/Defs/k.xml", kd % ("K_Gated", "Don/Gated"))
        w("donor/G/1.6/Defs/k.xml", kd % ("K_Open", "Don/Open"))
        w("donor/G/1.5/Mods/Gone/Defs/k.xml", kd % ("K_Open", "Don/Open"))  # another version's gate is not ours
        grows = [{"creature": c, "groups": [{"old": "Don/" + c, "new": "Ours/%s/%s" % (c, c)}], "patch": "p.xml",
                  "donor": "d.live", "donor_hint": os.path.join(td, "donor", "G")} for c in ("Gated", "Open")]
        gb = bind(grows, repo=td, donor_roots=(os.path.join(td, "donor"),))
        absent = {"K_Gated": None, "K_Open": None}
        gcases = [("gated kind bound to the live donor", gb["Gated"]["kinds"] == {"K_Gated": "donor:d.live"}),
                  ("gate read, _copy alias folded", gb["Gated"]["gates"].get("K_Gated") == [("any", {"d.gone"})] * 2),
                  ("ungated kind has no gate", gb["Open"]["gates"] == {}),
                  ("gate on a retired mod -> DONOR-RETIRED",
                   st(classify(gb, {"d.gone"}, absent, {}, {}, {}))["Gated"] == "DONOR-RETIRED"),
                  ("same absence with no gate -> NOT-LOADED",
                   st(classify(gb, {"d.gone"}, absent, {}, {}, {}))["Open"] == "NOT-LOADED"),
                  ("gate on a live mod -> NOT-LOADED", st(classify(gb, set(), absent, {}, {}, {}))["Gated"] == "NOT-LOADED"),
                  ("an all-gate with one retired is dead", gate_retired([("all", {"a", "b"})], {"b"}) == ["b"]),
                  ("one live gate keeps it loadable", gate_retired([("any", {"a"}), ("any", {"b"})], {"a"}) == [])]
        fails += ["gate %s" % g for g, ok in gcases if not ok]
        rows[0]["owner"] = "src/A/Own"
        need = required_mods(rows, b, set(), repo=td)
        gaps = [("owner and donor named", sorted(need) == ["d.old", "t.own"]),
                ("retired donor not required", sorted(required_mods(rows, b, {"d.old"}, repo=td)) == ["t.own"]),
                ("full load judged", load_gap(need, {"t.own", "d.old", "x"}) is None),
                ("owner absent refuses", "t.own" in (load_gap(need, {"d.old"}) or "")),
                ("unreadable load refuses", load_gap(need, None) is not None),
                ("a folded owner is its composed mod",
                 load_gap(required_mods(rows, b, set(), repo=td, folded={"t.own": "t.comp"}), {"t.comp", "d.old"}) is None)]
        fails += ["load %s" % g for g, ok in gaps if not ok]
    n = len(want) + 1 + len(cases) + 5 + len(gaps) + len(gcases)
    for f in fails:
        print("FAIL " + f)
    print("selftest %d/%d" % (n - len(fails), n))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bind", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--live", action="store_true")
    ap.add_argument("--ticks", type=int, default=300)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rows = json.load(open(afc.MANIFEST, encoding="utf-8"))["rows"]
    if a.bind:
        b = bind(rows)
        unb = [c for c, v in b.items() if v["mode"] != "dead" and not v["kinds"]]
        for c in sorted(b):
            print("%-28s %-6s %s" % (c, b[c]["mode"] or "-", ", ".join("%s(%s)" % kv for kv in sorted(b[c]["kinds"].items()))
                                      or "-"))
        print("BIND: %d rows, %d dead, %d bound, %d UNBOUND%s" % (
            len(b), sum(v["mode"] == "dead" for v in b.values()), sum(bool(v["kinds"]) for v in b.values()), len(unb),
            (" " + ",".join(unb)) if unb else ""))
        return 1 if unb else 0
    try:
        res, batch = run_live(rows, ticks=a.ticks)
    except Exception as e:  # noqa: BLE001  no bridge / socket drop: nothing was measured
        print("UNMEASURED: %s" % str(e))
        return 2
    code = exit_code(res, batch)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "ArtFold_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    json.dump({"item": "ART_OVERRIDE_FAMILY_SCRIPT_1", "exit": code, "rows": res, "batch": batch}, open(out, "w"),
              indent=1)
    for r in res:
        print("  %-14s %-28s %s" % (r["status"], r["creature"], r["detail"]))
    for bb in batch:
        print("  %-14s BATCH %-22s %s" % (bb["status"], bb["subject"], (bb.get("detail") or "")))
    tally = {}
    for r in res:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print("ARTFOLD LIVE exit=%d %s -> %s" % (code, json.dumps(tally, sort_keys=True), out))
    return code


if __name__ == "__main__":
    sys.exit(main())
