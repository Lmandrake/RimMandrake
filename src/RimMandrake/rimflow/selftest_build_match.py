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
    # GPT review 2026-11-17 (D:\ClaudeWork\rimmandrake\conductor\bm_gpt_review.md): the cache must not hide a rewrite
    # whose size and mtime were kept, nor lend one folder's hash to another.
    a = os.path.join(d, "Defs", "a.xml")
    B.deployed_hash(d, cache_dir=cache)
    st = os.stat(a)
    write(a, "<Defz/>")                                                     # same size, other bytes
    os.utime(a, ns=(st.st_atime_ns, st.st_mtime_ns))                        # its mtime put back
    check(B.deployed_hash(d, cache_dir=cache) == B.deployed_hash(d) != h1,
          "a same-size rewrite with its mtime put back misses the cache (the key holds the change time)")
    write(a, "<Defs/>")
    twin_a, twin_b = os.path.join(tmp, "TwinA"), os.path.join(tmp, "TwinB")
    write(os.path.join(twin_a, "x"), "A")
    write(os.path.join(twin_b, "x"), "B")
    os.utime(os.path.join(twin_a, "x"), ns=(1, 10 ** 18))
    os.utime(os.path.join(twin_b, "x"), ns=(1, 10 ** 18))
    ha = B.deployed_hash(twin_a, cache_dir=cache)
    check(B.deployed_hash(twin_b, cache_dir=cache) == B.deployed_hash(twin_b) != ha,
          "two folders whose files share names, sizes and mtimes do not share a cache entry")
    ext = os.path.join(tmp, "External")
    write(os.path.join(ext, "e.xml"), "<Defs/>")
    lk = os.path.join(tmp, "Linked")
    write(os.path.join(lk, "About", "About.xml"), "x")
    os.symlink(ext, os.path.join(lk, "Defs"))
    os.symlink(lk, os.path.join(ext, "loop"))                                # a cycle must not hang the walk
    hl = B.deployed_hash(lk)
    write(os.path.join(ext, "e.xml"), "<Defs> </Defs>")
    check(hl and B.deployed_hash(lk) not in (None, hl),
          "a linked directory's files are hashed (the game follows the link), and a cycle ends: %s" % (hl or "")[:20])
    if os.geteuid() != 0:
        locked = os.path.join(d, "Locked")
        write(os.path.join(locked, "l.xml"), "<Defs/>")
        os.chmod(locked, 0)
        try:
            got = B.deployed_hash(d)
        finally:
            os.chmod(locked, 0o755)
        check(got is None, "a folder with an unreadable subfolder hashes to None, never to the readable part: %s" % got)
        shutil.rmtree(locked)
    else:
        check(True, "unreadable subfolder: running as root, not testable here")
    # second GPT review (D:\ClaudeWork\rimmandrake\conductor\bm_gpt_review2.md): two links to one directory are two
    # paths the game loads; dropping either must change the hash (only a cycle is cut, never an alias)
    alias = os.path.join(tmp, "Alias")
    write(os.path.join(alias, "About", "About.xml"), "x")
    os.symlink(ext, os.path.join(alias, "a"))
    os.symlink(ext, os.path.join(alias, "b"))
    hb = B.deployed_hash(alias)
    seen_a = sorted({r.split("/")[0] for r, _ in B._files(alias)})
    os.unlink(os.path.join(alias, "b"))
    check(hb and seen_a == ["About", "a", "b"] and B.deployed_hash(alias) not in (None, hb),
          "two links to one directory are both hashed, and removing one changes the hash: %s" % seen_a)

    # ---- the deployed folder is found by packageId, not by name ------------------------------------------------------
    root = os.path.join(tmp, "repo")
    write(os.path.join(root, "src", "RimMandrake", "TestMod", "About", "About.xml"), ABOUT % "Mandrake.RM.TestMod")
    check(B.mod_package_id(root, "TestMod") == "mandrake.rm.testmod",
          "the mod's packageId is its About.xml's top-level one (a dependency's packageId is not it)")
    check(B.deployed_folder(os.path.join(tmp, "Mods"), "mandrake.rm.testmod", "TestMod") == d,
          "the deployed folder is the one whose About.xml names the packageId (here DeployedName, not TestMod)")
    # a mod composed into Biomes is read from the Biomes folder even when an old standalone copy is still deployed
    root2, mods2 = os.path.join(tmp, "repo2"), os.path.join(tmp, "Mods2")
    write(os.path.join(root2, "src", "RimMandrake", "Comp", "About", "About.xml"), ABOUT % "mandrake.rm.comp")
    write(os.path.join(root2, "src", "RimMandrake", "Biomes.compose.json"), json.dumps({
        "compose_wave": 1, "entries": [{"key": "Comp", "wave": 1}], "about": {"packageId": "Mandrake.RM.Biomes"},
        "target": "RimMandrake.Biomes"}))
    write(os.path.join(mods2, "Comp", "About", "About.xml"), ABOUT % "mandrake.rm.comp")
    write(os.path.join(mods2, "RimMandrake.Biomes", "About", "About.xml"), ABOUT % "mandrake.rm.biomes")
    got2 = B._mod_folder(root2, "Comp", mods2)[1]
    check(got2 == os.path.join(mods2, "RimMandrake.Biomes"),
          "a composed mod is hashed in the Biomes folder, not in a stale standalone copy: %s" % got2)

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
    os.environ[B.STANDIN_ENV] = stand
    try:
        # the repo this selftest sits in, found from its own path, not from build_match
        wr = B.walk_build(os.path.abspath(os.path.join(HERE, "..", "..", "..")), "TestMod", sv, host="Archmagi")
    finally:
        os.environ.pop(B.STANDIN_ENV, None)
    check(wr["why"] and B.STANDIN_ENV in " ".join(wr["why"]),
          "a stand-in left in the environment is refused against the real repo (it cannot pass a live exit): %s"
          % wr["why"])

    # ---- the tier list is built fresh each reading: no on-disk cache can hand back a list the builder now refuses -----
    calls = {"scan": 0}

    class FakeMB:
        refuse = False

        @staticmethod
        def tier_def(t):
            return {} if t in ("bridge", "other") else None

        @staticmethod
        def scan():
            calls["scan"] += 1
            return {}

        @staticmethod
        def resolve_tier(t, installed):
            return (["ludeon.rimworld"], ["gone.mod"] if FakeMB.refuse else [], [])
    real = sys.modules.get("modset_builder")
    sys.modules["modset_builder"] = FakeMB
    try:
        live = {"game": "archmagi", "why": []}
        f1 = B.tier_lister(live)
        first = (f1("bridge"), f1("other"), f1("bridge"))
        FakeMB.refuse = True
        again = B.tier_lister(live)("bridge")
    finally:
        if real is None:
            sys.modules.pop("modset_builder", None)
        else:
            sys.modules["modset_builder"] = real
    check(first[0] == (["ludeon.rimworld"], None) and calls["scan"] == 2 and again[0] is None and "gone.mod" in again[1],
          "one reading scans the installed mods once; the next reading sees a mod gone and refuses the tier "
          "(scans %d, then %s)" % (calls["scan"], again))


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
    ok, why = one("min_t", row("min_t"))
    check("named by the row" in why, "a minimal-list check whose table names no tier says the row named it: %s" % why)
    lr = B.last_rows([row("full_t"), row("unknown_t"), {"verdict": "PASS"}])
    res = B.compare([("full_t", TESTS["full_t"])], lr, WALK, tiers)
    line = B.summary(res)
    check(res["count"] == 1 and res["unmatched"] == 2 and "2 row(s) name no check" in line,
          "rows naming no check in the table, or none at all, are counted and printed, never silently dropped: %s"
          % line)


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


def _old_files(folder):
    """the first build's walk: links not followed, unreadable directories skipped in silence."""
    return sorted((os.path.relpath(os.path.join(d, n), folder).replace(os.sep, "/"), os.path.join(d, n))
                  for d, _, names in os.walk(folder) for n in names)


def _old_key(folder, files, cache_dir):
    """the first build's cache key: each file's path, size and mtime only."""
    sig = B.hashlib.sha256()
    for r, p in files:
        st = os.stat(p)
        sig.update(("%s\0%d\0%d\n" % (r, st.st_size, st.st_mtime_ns)).encode())
    return os.path.join(cache_dir, "hash_%s.txt" % sig.hexdigest()[:32])


def _seen_once_files(folder):
    """the second build's walk: each real directory once, so a second link to one directory was dropped."""
    out, seen, stack = [], set(), [(folder, "")]
    while stack:
        d, rel = stack.pop()
        if os.path.realpath(d) in seen:
            continue
        seen.add(os.path.realpath(d))
        for e in os.scandir(d):
            (stack.append((e.path, rel + e.name + "/")) if e.is_dir() else out.append((rel + e.name, e.path)))
    return sorted(out)


def _standalone_first(root, mod, mods_dir):
    pid, comp = B.mod_package_id(root, mod), B.composed_into(root, mod)
    folder = B.deployed_folder(mods_dir, pid, mod)
    return pid, folder if folder or not comp else B.deployed_folder(mods_dir, comp[0], comp[1] or "")


def _old_last_rows(rows):
    return {r.get("test") or r.get("id"): r for r in rows or [] if r.get("test") or r.get("id")}


MUTANTS = {
    "links_and_errors_skipped": lambda: setattr(B, "_files", _old_files),
    "cache_key_size_mtime": lambda: setattr(B, "_cache_key", _old_key),
    "aliases_cut": lambda: setattr(B, "_files", _seen_once_files),
    "standalone_before_composed": lambda: setattr(B, "_mod_folder", _standalone_first),
    "standin_on_real_repo": lambda: setattr(B, "REPO", "/nonexistent/repo"),
    "idless_rows_dropped": lambda: setattr(B, "last_rows", _old_last_rows),
    "tier_scans_every_tier": lambda: setattr(B, "_resolve_tier", (lambda o: lambda t, i: o(t, []))(B._resolve_tier)),
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
