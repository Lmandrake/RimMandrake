"""validation.py -- modcheck suite for RimUtinni: Assailant Salvage (mandrake.rut.assailantsalvage).

First north-star script (ASSAILANT_SALVAGE_FIRST_SCRIPT_1, debug_process.md section 2). NEVER RUN LIVE YET.
The mod is 22 owned RUT_ set-dressing ThingDefs (airlocks, turrets, landmine, terminals, heater, black box,
bed, pod ...) replacing the retired Cryptoforge donor props, with the donor's gameplay unchanged. It ships no
C# and no Mod Settings, and is not wired into any map generation yet (ASSAILANT_DUNGEON_BUILD_1 is separate).

WHAT IT PROVES (state reads):
  * defs_resolve: every ThingDef parsed from the mod's own XML resolves live (a def with an unresolvable
    thingClass or comp is silently discarded); a control proves the probe can say absent.
  * fields_match_xml: the live thingClass / fillPercent / size of each def equals what the XML declares
    (a donor or patch override would show here).
  * spawn_all: every placeable prop spawns and is found again on the map.
  * landmine: a hostile pawn walking over a player-owned landmine springs it (mine gone, pawn hurt or dead);
    a control mine off the path is still there.
  * textures_resolve: jawa/texture_audit names no missing texture of ours.
UNMEASURED (reason recorded): turrets firing, the heater's heat/glow, the bed/pod/table functions (each needs
power, a raid or a sealed room), and Mod Settings (the mod has none).

STATIC (offline): `python3 validation.py` runs `static_checks()` with no game.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_NAME = "RimUtinni: Assailant Salvage"
CONTROL_ABSENT = "ThingDef/RUT_NoSuchProp_Control"
MINE = "RUT_AncientLandmine"
# defs that are projectiles or turret guns: they resolve but never spawn on the map
NOT_PLACEABLE_PARENTS = ("BaseBullet", "BaseWeaponTurret")


def read_defs():
    """[{name, parent, thingClass, fillPercent, size, texPaths, placeable}] for every concrete ThingDef in
    Defs/, parsed per element with comments stripped (never a fixed line)."""
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "ThingDefs", "*.xml"))):
        txt = re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)
        for m in re.finditer(r"<ThingDef\b([^>]*)>(.*?)</ThingDef>", txt, re.S):
            attrs, body = m.group(1), m.group(2)
            if re.search(r'Abstract\s*=\s*"[Tt]rue"', attrs):
                continue
            nm = re.search(r"<defName>([^<]+)</defName>", body)
            if not nm:
                continue
            # top-level scalars only: strip nested blocks that reuse tag names
            top = re.sub(r"<(comps|building|graphicData|statBases|verbs|projectile|race|costList|placeWorkers)\b.*?</\1>",
                         "", body, flags=re.S)
            pn = re.search(r'ParentName\s*=\s*"([^"]+)"', attrs)
            d = {"name": nm.group(1).strip(), "parent": pn.group(1) if pn else None, "file": os.path.basename(path)}
            for tag in ("thingClass", "fillPercent", "size"):
                v = re.search(r"<%s>([^<]*)</%s>" % (tag, tag), top)
                d[tag] = v.group(1).strip() if v else None
            d["texPaths"] = re.findall(r"<texPath>([^<]*)</texPath>", body)
            d["placeable"] = d["parent"] not in NOT_PLACEABLE_PARENTS
            out.append(d)
    return out


DEFS = read_defs()
NAMES = [d["name"] for d in DEFS]
PLACEABLE = [d for d in DEFS if d["placeable"]]


def _tex_in_mod(tex):
    base = os.path.join(HERE, "Textures", *tex.split("/"))
    folder = os.path.dirname(base)
    stem = os.path.basename(base)
    if os.path.exists(base + ".png") or os.path.isdir(base):
        return True
    return bool(glob.glob(os.path.join(folder, stem + "_*.png")))


def static_checks():
    """Return a list of failure strings; empty means pass. Needs no game."""
    bad = []
    if not DEFS:       # sanity probe: the parser must find defs or "no findings" means nothing
        return ["def parser found 0 ThingDefs under Defs/ThingDefs: the probe is blind"]
    if len(set(NAMES)) != len(NAMES):
        bad.append("duplicate defNames: %s" % sorted(n for n in set(NAMES) if NAMES.count(n) > 1))
    for d in DEFS:
        if not d["name"].startswith("RUT_"):
            bad.append("%s breaks the RUT_ prefix (shipping-name tiers)" % d["name"])
    raw = "".join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(HERE, "Defs", "ThingDefs", "*.xml")))
    code = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    if "VQE_" in code or "VanillaQuestsExpanded" in code:
        bad.append("a live def still names the retired Cryptoforge donor (VQE_ / VanillaQuestsExpanded)")
    if re.search(r"<Operation[^>]*MayRequire", code):
        bad.append("MayRequire on an Operation (inert)")
    # turret pairs: each turret names a gun def that exists, each gun names a bullet def that exists
    for tag, gun in (("RUT_AncientShieldedTurret", "RUT_AncientShieldedTurret_Gun"),
                     ("RUT_AncientSpacerAutocannon", "RUT_AncientSpacerAutocannon_Gun")):
        if "<turretGunDef>%s</turretGunDef>" % gun not in code:
            bad.append("%s does not name %s as its turretGunDef" % (tag, gun))
        if gun not in NAMES:
            bad.append("gun def %s is missing" % gun)
        if gun.replace("_Gun", "_Bullet") not in NAMES:
            bad.append("bullet def for %s is missing" % gun)
    if MINE not in NAMES:
        bad.append("%s is gone" % MINE)
    # no C#, no Mod Settings: if either appears the script owes a settings round trip
    if os.path.isdir(os.path.join(HERE, "Source")) or glob.glob(os.path.join(HERE, "Assemblies", "*.dll")):
        bad.append("the mod now ships C# or an assembly: add settings_roundtrip (this script says it has no settings)")
    if "mandrake.rut.assailantsalvage" not in open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read():
        bad.append("About.xml packageId drifted")
    walk = os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "AssailantSalvage.md")
    if not os.path.exists(walk):
        bad.append("walk design/validation_walks/RimMandrake/AssailantSalvage.md is missing")
    else:
        w = open(walk, encoding="utf-8").read().split("## must be true", 1)[-1].split("\n## ", 1)[0]
        for ln in w.splitlines():
            if ln.startswith("- ") and "→" not in ln:
                bad.append("walk line has no coverage arrow: %s" % ln[:70])
    return bad


def art_note():
    """texPaths with no png in this mod's own Textures (NOT a finding: a path can resolve from vanilla or
    another mod; the live texture_audit decides). Printed so the owed-art list is visible."""
    out = []
    for d in DEFS:
        for tex in d["texPaths"]:
            if not tex.startswith(("UI/", "Things/Projectile/")) and not _tex_in_mod(tex):
                out.append("%s: %s" % (d["name"], tex))
    return out


# ---------------------------------------------------------------------------------------------- live

def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("AssailantSalvage")
    suite.toggles = []         # the mod ships no Mod Settings
    state = {}

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _live(t):
        return t.session is not None

    def _defs_read(t, names, **kw):
        r = t.bridge_call("jawa/get_defs", defs=";".join("ThingDef/%s" % n for n in names), limit=100, **kw)
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs could not ask: %r" % (r,))
        return r

    def _things(t, defName, rect):
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=50)
        return (r or {}).get("things") or []

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("defs_resolve", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs_read(t, NAMES)
            if r.get("notFound") or int(r.get("foundCount", 0)) != len(NAMES):
                raise ExpectationFailed("%d of %d shipped defs resolved; notFound %r"
                                        % (int(r.get("foundCount", 0)), len(NAMES), r.get("notFound")))
        with t.component("probe_can_say_absent", beyond_toggle=True):
            if not _live(t):
                return
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, limit=5)
            if not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 0 \
                    or CONTROL_ABSENT.split("/")[1] not in " ".join(str(x) for x in (r.get("notFound") or [])):
                raise ExpectationFailed("control: a def that does not exist did not read absent: %r" % (r,))
        with t.component("fields_match_xml", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs_read(t, NAMES, fields="thingClass,fillPercent,size")
            rows = {d.get("defName"): (d.get("fields") or {}) for d in (r.get("defs") or [])}
            wrong, seen = [], 0
            for d in DEFS:
                # LIVE run17 2026-10-03: get_defs answers '(no such field)' for System.Type (thingClass) and IntVec2
                # (size) -- an instrument gap, not a difference. thingClass is re-read from jawa/get_def's extra;
                # size has no other reader and is left unread (never compared against the placeholder).
                f = {k: v for k, v in rows.get(d["name"], {}).items() if "no such field" not in str(v)}
                if d["thingClass"] and f.get("thingClass") is None:
                    g = t.bridge_call("jawa/get_def", defType="ThingDef", defName=d["name"])
                    tc = ((g or {}).get("extra") or {}).get("thingClass") if isinstance(g, dict) else None
                    if tc:
                        f["thingClass"] = tc
                if d["thingClass"] and f.get("thingClass") is not None:
                    seen += 1
                    if str(f["thingClass"]).split(".")[-1] != d["thingClass"].split(".")[-1]:
                        wrong.append("%s thingClass %r != XML %r" % (d["name"], f["thingClass"], d["thingClass"]))
                if d["fillPercent"] is not None and f.get("fillPercent") is not None:
                    seen += 1
                    if abs(float(f["fillPercent"]) - float(d["fillPercent"])) > 1e-6:
                        wrong.append("%s fillPercent %r != XML %r" % (d["name"], f["fillPercent"], d["fillPercent"]))
                if d["size"] is not None and f.get("size") is not None:
                    seen += 1
                    if re.sub(r"[\s()]", "", str(f["size"])) != re.sub(r"[\s()]", "", d["size"]):
                        wrong.append("%s size %r != XML %r" % (d["name"], f["size"], d["size"]))
            if seen == 0:
                _unmeasured(t, "get_defs returned none of thingClass/fillPercent/size as field values: %r"
                            % list(rows.items())[:2])
                return
            if wrong:
                raise ExpectationFailed("live defs differ from the shipped XML: %s" % wrong[:4])

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("no_settings_declared", beyond_toggle=True):
            if not _live(t):
                return
            _unmeasured(t, "this mod ships no C# and declares no Mod Settings, so there is no field to round-trip; "
                           "static_checks fails if a Source folder or assembly ever appears")

    @suite.chain("spawn_all")
    def spawn_all(t):
        x0, z0 = t.anchor
        cells = {}
        with t.component("every_placeable_prop_spawns", beyond_toggle=True):
            if not _live(t):
                return
            t.clear_area(size=44)
            ops = []
            for i, d in enumerate(PLACEABLE):
                cx, cz = x0 - 18 + (i % 6) * 7, z0 - 14 + (i // 6) * 7
                cells[d["name"]] = (cx, cz)
                ops.append("%s:%d,%d" % (d["name"], cx, cz))
            r = t.bridge_call("jawa/spawn_batch", ops=";".join(ops))
            if isinstance(r, dict) and r.get("success") is False:
                raise ExpectationFailed("spawn_batch refused: %r" % (r,))
            rect = "%d,%d,44,44" % (x0 - 22, z0 - 22)
            missing = [n for n in cells if not _things(t, n, rect)]
            state["spawned"] = {n: c for n, c in cells.items() if n not in missing}
            state["rect"] = rect
            if missing:
                raise ExpectationFailed("%d of %d props did not spawn / were not found: %s"
                                        % (len(missing), len(cells), missing))
        with t.component("spawned_props_inspect_clean", beyond_toggle=True):
            if not _live(t) or not state.get("spawned"):
                return
            bad = []
            for n in list(state["spawned"])[:30]:
                rows = _things(t, n, state["rect"])
                if not rows:
                    continue
                r = t.bridge_call("jawa/inspect_string", thingIds=rows[0]["id"])
                row = next((x for x in ((r or {}).get("things") or []) if x.get("id") == rows[0]["id"]), None)
                if row is None or row.get("error"):
                    bad.append("%s: %r" % (n, (row or r)))
            if bad:
                raise ExpectationFailed("inspect_string errored for %d props: %s" % (len(bad), bad[:3]))

    @suite.chain("landmine")
    def landmine(t):
        x0, z0 = t.anchor
        with t.component("hostile_pawn_springs_player_landmine", beyond_toggle=True):
            if not _live(t):
                return
            t.clear_area(size=30)
            rect = "%d,%d,30,30" % (x0 - 15, z0 - 15)
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d;%s:%d,%d" % (MINE, x0 + 4, z0, MINE, x0 + 4, z0 + 9))
            on_path, control = _things(t, MINE, "%d,%d,1,1" % (x0 + 4, z0)), _things(t, MINE, "%d,%d,1,1" % (x0 + 4, z0 + 9))
            if not on_path or not control:
                _unmeasured(t, "the landmines did not spawn (path %r control %r)" % (len(on_path), len(control)))
                return
            for m in (on_path[0], control[0]):
                r = t.bridge_call("jawa/set_thing_props", thing=m["id"], faction="PlayerColony")
                if isinstance(r, dict) and r.get("success") is False:
                    _unmeasured(t, "set_thing_props could not make the landmine player-owned: %r" % (r,))
                    return
            pid = t.spawn_pawn("Colonist", hostile=True)
            if not pid:
                _unmeasured(t, "could not spawn a hostile pawn to step on the mine")
                return
            t.walk_over(pid, [(x0 + 8, z0)], wait_ticks=300)
            t.wait_ticks(120)
            if _things(t, MINE, "%d,%d,1,1" % (x0 + 4, z0 + 9)) == []:
                raise ExpectationFailed("control landmine off the path vanished by itself")
            if _things(t, MINE, "%d,%d,1,1" % (x0 + 4, z0)):
                _unmeasured(t, "the hostile pawn never stepped on the mine (no trigger, no evidence either way)")
                return
            r = t.bridge_call("jawa/list_pawns", rect=rect, includeCorpses=True, includeHealth=True, limit=50)
            row = next((p for p in ((r or {}).get("pawns") or []) if p.get("id") == pid), None)
            hurt = row is not None and (row.get("dead") or ((row.get("health") or {}).get("hediffs") or []))
            if not hurt:
                raise ExpectationFailed("the mine is gone but the pawn beside it is unhurt: the blast did not "
                                        "land (row %r)" % (row,))

    @suite.chain("textures")
    def textures(t):
        with t.component("textures_resolve", beyond_toggle=True):
            if not _live(t):
                return
            r = t.bridge_call("jawa/texture_audit", filter="RUT_Ancient", limit=100)
            if not isinstance(r, dict) or r.get("success") is False:
                _unmeasured(t, "texture_audit could not ask: %r" % (r,))
                return
            ours = {tex for d in DEFS for tex in d["texPaths"]}
            missing = [m for m in (r.get("missing") or []) if any(o in str(m) for o in ours)]
            if missing:
                raise ExpectationFailed("%d of our texture paths are missing in the running game: %s"
                                        % (len(missing), [str(m)[:90] for m in missing[:5]]))

    @suite.chain("unproven_behaviours")
    def unproven_behaviours(t):
        for name, why in (
                ("turrets_fire_when_hostile_in_range",
                 "RUT_AncientShieldedTurret and RUT_AncientSpacerAutocannon firing need power, ownership and a raid"),
                ("floor_heater_heats_and_glows_when_powered",
                 "needs a sealed powered room and a temperature read against a control room"),
                ("airlock_opens_for_pawns",
                 "needs a wall gap, walls both sides and a pawn pathing through (door open state has no reader)"),
                ("bed_pod_table_functions",
                 "ruined hospital bed, frozen pod, wargaming table and blueprints bench need pawns and bills")):
            with t.component(name, beyond_toggle=True):
                if not _live(t):
                    continue
                t.upstream_failed = False
                _unmeasured(t, why)

    return suite


try:
    suite = _build_suite()
except ImportError:      # run outside the modcheck path: the static check below needs no game
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    owed = art_note()
    print("ART NOTE (not a finding; live texture_audit decides): %d of %d texPaths have no png in this mod's "
          "Textures" % (len(owed), sum(len(d["texPaths"]) for d in DEFS)))
    sys.exit(1 if problems else 0)
