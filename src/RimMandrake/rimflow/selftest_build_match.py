#!/usr/bin/env python3
"""Selftest for build_match.py: an in-game verdict counts only on the build he walks (owner, 2026-11-17, approving the
Stage 6 -> Stage 7 change; RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO).

  python3 selftest_build_match.py              every check; exit 0 only when all hold
  python3 selftest_build_match.py --mutant M   the same checks with guard M broken: must exit 1
  python3 selftest_build_match.py --mutants    run every mutant; exit 0 only if each one is caught

Offline: temp folders stand in for the deployed mod, ModsConfig.xml, Version.txt and the savegame. Never reads the live
game. The range it reads, per row: the mod hash same or different, the game build same or different, the list kind
(full or minimal) against its reference (his walk's list, or the tier's list), the list equal, short, reordered or
differing only in case or the `_steam` suffix, a field missing, a tier unresolved, the walk itself unreadable.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_match as B     # noqa: E402

FAILS = []
CASES = [0]


def check(ok, what):
    CASES[0] += 1
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def write(p, text, mode="w"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode) as f:
        f.write(text)


ABOUT = "<?xml version=\"1.0\"?>\n<ModMetaData>\n  <packageId>%s</packageId>\n  <modDependencies><li>" \
        "<packageId>brrainz.harmony</packageId></li></modDependencies>\n</ModMetaData>\n"


def io_checks(tmp):
    # ---- deployed_hash: bytes and names, never timestamps ------------------------------------------------------------
    d = os.path.join(tmp, "Mods", "DeployedName")
    write(os.path.join(d, "About", "About.xml"), ABOUT % "mandrake.rm.testmod")
    write(os.path.join(d, "Defs", "a.xml"), "<Defs/>")
    write(os.path.join(d, "Textures", "t.png"), b"\x89PNG\x00\x01", "wb")
    h1 = B.deployed_hash(d)
    check(bool(h1) and h1.startswith("sha256:"), "a deployed folder hashes to sha256:<hex> (%s)" % (h1 or "")[:20])
    os.utime(os.path.join(d, "Defs", "a.xml"), (1, 1))
    check(B.deployed_hash(d) == h1, "a touched file with the same bytes keeps the hash (bytes decide, not times)")
    write(os.path.join(d, "Defs", "a.xml"), "<Defs> </Defs>")
    h2 = B.deployed_hash(d)
    check(h2 != h1, "one changed byte in one file changes the hash")
    write(os.path.join(d, "Defs", "a.xml"), "<Defs/>")
    check(B.deployed_hash(d) == h1, "the bytes put back give the first hash again")
    os.rename(os.path.join(d, "Defs", "a.xml"), os.path.join(d, "Defs", "b.xml"))
    check(B.deployed_hash(d) != h1, "a renamed file changes the hash (the path is hashed)")
    os.rename(os.path.join(d, "Defs", "b.xml"), os.path.join(d, "Defs", "a.xml"))
    check(B.deployed_hash(os.path.join(tmp, "Mods", "Nothing")) is None, "no folder hashes to None, never a value")
    cache = os.path.join(tmp, "cache")
    check(B.deployed_hash(d, cache_dir=cache) == h1 and B.deployed_hash(d, cache_dir=cache) == h1,
          "the stat-keyed cache returns the same hash, first read and second")
    write(os.path.join(d, "Defs", "a.xml"), "<Defs>!</Defs>")
    check(B.deployed_hash(d, cache_dir=cache) not in (None, h1), "the cache misses when a file's bytes change")
    write(os.path.join(d, "Defs", "a.xml"), "<Defs/>")

    # ---- the deployed folder is found by packageId, not by name ------------------------------------------------------
    root = os.path.join(tmp, "repo")
    write(os.path.join(root, "src", "RimMandrake", "TestMod", "About", "About.xml"), ABOUT % "Mandrake.RM.TestMod")
    check(B.mod_package_id(root, "TestMod") == "mandrake.rm.testmod",
          "the mod's packageId is its About.xml's top-level one (a dependency's packageId is not it)")
    check(B.deployed_folder(os.path.join(tmp, "Mods"), "mandrake.rm.testmod", "TestMod") == d,
          "the deployed folder is the one whose About.xml names the packageId (here DeployedName, not TestMod)")

    # ---- ModsConfig.xml is parsed, in order; a commented-out line is not a mod ---------------------------------------
    cfg = os.path.join(tmp, "ModsConfig.xml")
    write(cfg, "<?xml version=\"1.0\"?>\n<ModsConfigData>\n  <version>1.6</version>\n  <activeMods>\n"
               "    <li>brrainz.harmony</li>\n    <li>ludeon.rimworld</li>\n    <!-- <li>old.mod</li> -->\n"
               "    <li>Mandrake.RM.TestMod_steam</li>\n  </activeMods>\n  <knownExpansions>\n"
               "    <li>ludeon.rimworld.royalty</li>\n  </knownExpansions>\n</ModsConfigData>\n")
    am = B.active_mods(cfg)
    check(am == ["brrainz.harmony", "ludeon.rimworld", "Mandrake.RM.TestMod_steam"],
          "activeMods read in order; the comment and knownExpansions are not mods: %s" % am)
    check(B.norm_list(am) == ["brrainz.harmony", "ludeon.rimworld", "mandrake.rm.testmod"],
          "a packageId compares lower-case with its _steam suffix dropped")
    vt = os.path.join(tmp, "Version.txt")
    write(vt, "1.6.4871 rev590\n")
    check(B.game_build(vt) == "1.6.4871 rev590", "the game build is Version.txt's first line")
    check(B.game_build(os.path.join(tmp, "none.txt")) is None, "no Version.txt reads None")

    # ---- identity: the four things a row records ---------------------------------------------------------------------
    os.environ["RM_ROLE_UNIT"] = "rm-detached-selftest-driver-1"
    try:
        idn = B.identity(root, "TestMod", tier="bridge", mods_dir=os.path.join(tmp, "Mods"), config=cfg,
                         version_txt=vt, host="Archmagi", mod_sha="abc1234")
    finally:
        os.environ.pop("RM_ROLE_UNIT", None)
    check(idn.get("game") == "archmagi" and idn.get("mod_sha") == "abc1234" and idn.get("mod_hash") == h1
          and idn.get("game_build") == "1.6.4871 rev590" and idn.get("active_mods") == am
          and idn.get("tier") == "bridge" and idn.get("unit") == "rm-detached-selftest-driver-1"
          and not idn.get("why"), "identity names the game, sha, deployed hash, build, list, tier and unit: %s"
          % {k: idn.get(k) for k in ("game", "mod_hash", "tier", "why")})
    full = B.identity(root, "TestMod", full=True, mods_dir=os.path.join(tmp, "Mods"), config=cfg, version_txt=vt,
                      host="Archmagi", mod_sha="abc1234")
    check(full.get("full_list") is True and "tier" not in full, "identity --full marks the row full_list, no tier")
    gone = B.identity(root, "TestMod", tier="bridge", mods_dir=os.path.join(tmp, "Nomods"), config=cfg,
                      version_txt=vt, host="Archmagi", mod_sha="abc1234")
    check(gone.get("mod_hash") is None and any("deployed" in w for w in gone.get("why") or []),
          "a mod not deployed: identity says so and gives no hash: %s" % gone.get("why"))

    # ---- the walk build: read on his machine, the list from the labelled savegame ------------------------------------
    sv = os.path.join(tmp, "walk.rws")
    write(sv, "﻿<?xml version=\"1.0\"?>\n<savegame><meta><gameVersion>1.6.4871 rev590</gameVersion><modIds>"
              "<li>brrainz.harmony</li><li>ludeon.rimworld</li><li>mandrake.rm.testmod</li></modIds>"
              "</meta></savegame>\n")
    w = B.walk_build(root, "TestMod", sv, host="Archmagi", mods_dir=os.path.join(tmp, "Mods"), version_txt=vt)
    check(not w["why"] and w["mod_hash"] == h1 and w["game_build"] == "1.6.4871 rev590"
          and w["active_mods"] == ["brrainz.harmony", "ludeon.rimworld", "mandrake.rm.testmod"],
          "the walk build: Archmagi's deployed hash, its Version.txt, the savegame's modIds in order: %s" % w["why"])
    w2 = B.walk_build(root, "TestMod", sv, host="SteveDesktop", mods_dir=os.path.join(tmp, "Mods"), version_txt=vt)
    check(w2["why"] and "archmagi" in " ".join(w2["why"]).lower(),
          "the walk build read on another machine is refused (he walks on Archmagi): %s" % w2["why"])
    write(os.path.join(tmp, "bare.rws"), "<?xml version=\"1.0\"?>\n<savegame><meta/></savegame>\n")
    w3 = B.walk_build(root, "TestMod", os.path.join(tmp, "bare.rws"), host="Archmagi",
                      mods_dir=os.path.join(tmp, "Mods"), version_txt=vt)
    check(w3["why"] and "modIds" in " ".join(w3["why"]), "a savegame with no modIds gives no walk list: %s" % w3["why"])
    stand = os.path.join(tmp, "standin.json")
    write(stand, json.dumps({"mod_hash": "sha256:feed", "game_build": "1.6.1 rev1", "active_mods": ["a", "b"],
                             "tiers": {"t1": ["a"]}}))
    os.environ[B.STANDIN_ENV] = stand
    try:
        ws = B.walk_build(root, "TestMod", sv, host="Elsewhere")
    finally:
        os.environ.pop(B.STANDIN_ENV, None)
    check(not ws["why"] and ws["mod_hash"] == "sha256:feed" and ws.get("standin") == stand,
          "%s stands in for the live machine and is named on the reading" % B.STANDIN_ENV)
    check(B.tier_lister(ws)("t1") == (["a"], None) and B.tier_lister(ws)("t9")[0] is None,
          "a stand-in's tiers answer the tier lists; a tier it lacks resolves to nothing, with a reason")


WALK = {"game": "archmagi", "mod_hash": "sha256:aaaa", "game_build": "1.6.4871 rev590",
        "active_mods": ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "mandrake.rm.testmod",
                        "other.big.mod"], "why": []}
TIER = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "mandrake.rm.testmod"]
TESTS = {"full_t": {"kind": "live", "stage": "6", "why_full_list": "it reads a mod only the full list holds"},
         "min_t": {"kind": "live", "stage": "6"}}


def tiers(name):
    return (list(TIER), None) if name == "bridge" else (None, "no tier %s" % name)


def row(test, **kw):
    r = {"test": test, "verdict": "PASS", "mod_sha": "abc1234", "mod_hash": WALK["mod_hash"],
         "game_build": WALK["game_build"], "game": "archmagi"}
    if test == "full_t":
        r.update(active_mods=list(WALK["active_mods"]), full_list=True)
    else:
        r.update(active_mods=list(TIER), tier="bridge")
    r.update(kw)
    return {k: v for k, v in r.items() if v is not None}


def one(test, r, walk=WALK):
    res = B.compare([(test, TESTS[test])], {test: r}, walk, tiers)
    x = res["rows"][test]
    return x["counts"], x["why"]


def compare_checks():
    ok, why = one("full_t", row("full_t"))
    check(ok, "a full-list row on the walk's hash, build and exact list counts (%s)" % why)
    ok, why = one("min_t", row("min_t"))
    check(ok, "a minimal-list row on the walk's hash and build whose list is its tier's counts (%s)" % why)
    cases = (
        ("full_t", dict(mod_hash="sha256:bbbb"), "mod hash", "the mod hash differs"),
        ("min_t", dict(mod_hash="sha256:bbbb"), "mod hash", "the mod hash differs (minimal list)"),
        ("full_t", dict(game_build="1.6.4633 rev1261"), "game build", "the game build differs"),
        ("min_t", dict(game_build="1.6.4633 rev1261"), "game build", "the game build differs (minimal list)"),
        ("full_t", dict(active_mods=WALK["active_mods"][:-1]), "list", "the full list is one mod short of his walk's"),
        ("full_t", dict(active_mods=[WALK["active_mods"][1], WALK["active_mods"][0]] + WALK["active_mods"][2:]),
         "list", "the full list holds his mods in another order"),
        ("full_t", dict(active_mods=TIER), "list", "a full-list test run on the tier's list (not his walk's)"),
        ("min_t", dict(active_mods=WALK["active_mods"]), "list",
         "a minimal-list test run on his full list (not its tier's)"),
        ("min_t", dict(active_mods=TIER[:-1]), "list", "the minimal list is one mod short of its tier's"),
        ("min_t", dict(tier=None), "tier", "a minimal-list row that names no tier"),
        ("min_t", dict(tier="nosuch"), "tier", "a minimal-list row whose tier modset_builder cannot build"),
        ("full_t", dict(mod_hash=None), "mod_hash", "a row that records no mod_hash"),
        ("min_t", dict(game_build=None), "game_build", "a row that records no game_build"),
        ("full_t", dict(active_mods=None), "active_mods", "a row that records no active_mods"),
        ("full_t", dict(active_mods=[]), "active_mods", "a row whose active_mods is empty"),
    )
    for test, kw, word, what in cases:
        ok, why = one(test, row(test, **kw))
        check(not ok and word in why, "%s: does not count, and says %r: %s" % (what, word, why))
    ok, why = one("full_t", row("full_t", active_mods=[m.upper() + ("_steam" if i == 3 else "")
                                                        for i, m in enumerate(WALK["active_mods"])]))
    check(ok, "the same list in other case, one with the _steam suffix, counts (%s)" % why)
    ok, why = one("full_t", row("full_t", mod_sha="def5678"))
    check(ok, "another source sha on the same deployed bytes counts: the hash decides, as ruled (%s)" % why)
    ok, why = one("full_t", None)
    check(not ok and "no row" in why, "a check with no row does not count: %s" % why)
    bad_walk = dict(WALK, why=["the walk build is read on Archmagi"], mod_hash=None)
    ok, why = one("full_t", row("full_t"), walk=bad_walk)
    check(not ok and "walk build" in why, "the walk unreadable: no row counts, and each says why: %s" % why)
    res = B.compare([(t, TESTS[t]) for t in ("full_t", "min_t")],
                    {"full_t": row("full_t"), "min_t": row("min_t", mod_hash="sha256:bbbb")}, WALK, tiers)
    check(res["read"] == 2 and res["count"] == 1 and res["rerun"] == ["min_t"] and "min_t" in (res["worst"] or ""),
          "the reading prints cases read (2), how many count (1), the re-runs and the worst: %s"
          % {k: res[k] for k in ("read", "count", "rerun", "worst")})
    line = B.summary(res)
    check(all(w in line for w in ("read 2", "1 count", "limit", "worst")),
          "the summary line names the cases read, the count, the limit and the worst: %s" % line)


def cli_checks(tmp):
    stand = os.path.join(tmp, "standin2.json")
    write(stand, json.dumps(dict(WALK, tiers={"bridge": TIER})))
    root = os.path.join(tmp, "repo2")
    mod = "TestMod"
    vdir = os.path.join(root, "design", "concepts", mod, "version")
    write(os.path.join(vdir, "test_table.json"), json.dumps({"version": "0.1.0", "tests": TESTS}))
    write(os.path.join(vdir, "in_game", "visit_1", "rows.jsonl"),
          json.dumps(row("full_t")) + "\n" + json.dumps(row("min_t", game_build="1.0 rev1")) + "\n")
    write(os.path.join(vdir, "in_game", "visit_1", "SUMMARY.md"), "# v\n\n## Exit\nsavegame: %s\n" % os.path.join(
        tmp, "walk.rws"))
    env = dict(os.environ, **{B.STANDIN_ENV: stand})
    r = subprocess.run([sys.executable, os.path.join(HERE, "build_match.py"), "check", "--root", root, "--mod", mod,
                        "--visit", "1"], capture_output=True, text=True, timeout=120, env=env)
    check(r.returncode == 1 and "min_t" in r.stdout and "game build" in r.stdout and "read 2" in r.stdout,
          "`build_match.py check` exits 1 naming the row to re-run and its reason: rc %d %s" % (
              r.returncode, r.stdout.strip().splitlines()[-1:] if r.stdout.strip() else r.stderr[-200:]))


def _regex_active(path):
    return re.findall(r"<li>([^<]*)</li>", open(path).read().split("<activeMods>")[-1].split("</activeMods>")[0])


MUTANTS = {
    "hash_ignored": lambda: setattr(B, "CHECKED", ("game_build",)),
    "build_ignored": lambda: setattr(B, "CHECKED", ("mod_hash",)),
    "list_as_set": lambda: setattr(B, "same_list", lambda a, b: set(B.norm_list(a)) == set(B.norm_list(b))),
    "full_read_as_minimal": lambda: setattr(B, "is_full", lambda test: False),
    "missing_counts": lambda: setattr(B, "REQUIRED", ()),
    "modsconfig_grepped": lambda: setattr(B, "active_mods", _regex_active),
    "hash_names_only": lambda: setattr(B, "_digest_file", lambda p, h: None),
    "any_host_walks": lambda: setattr(B, "WALK_HOST", None),
}


def main():
    if "--mutants" in sys.argv:
        bad = []
        for m in MUTANTS:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True,
                               text=True, timeout=300)
            n = r.stdout.count("\nFAIL") + r.stdout.startswith("FAIL")
            print("%s  mutant %s: exit %d, %d check(s) failed" % ("ok  " if r.returncode == 1 else "FAIL", m,
                                                                   r.returncode, n))
            if r.returncode != 1:
                bad.append(m)
        print("%d of %d mutants caught" % (len(MUTANTS) - len(bad), len(MUTANTS)))
        return 1 if bad else 0
    if "--mutant" in sys.argv:
        MUTANTS[sys.argv[sys.argv.index("--mutant") + 1]]()
    tmp = tempfile.mkdtemp(prefix="build_match_selftest_")
    try:
        io_checks(tmp)
        compare_checks()
        if "--mutant" not in sys.argv:
            cli_checks(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d of %d checks failed" % (len(FAILS), CASES[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
