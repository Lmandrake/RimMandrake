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
import errno
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

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
    unwritable = os.path.join(tmp, "cache_is_a_file")          # fifth GPT review: a cache that cannot be written
    write(unwritable, "x")
    check(B.deployed_hash(d, cache_dir=unwritable) == h1,
          "a cache that cannot be written leaves a readable folder's hash as it is, never None")
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
    # third GPT review (D:\ClaudeWork\rimmandrake\conductor\bm_gpt_review3.md)
    nl_a = os.path.join(tmp, "Nl", "mod")
    nl_b = nl_a + "\n0"
    write(os.path.join(nl_a, "0\n!"), "bytes")
    os.makedirs(nl_b)
    os.link(os.path.join(nl_a, "0\n!"), os.path.join(nl_b, "!"))            # one inode: every stat field the same
    B.deployed_hash(nl_a, cache_dir=cache)
    got_b, true_b = B.deployed_hash(nl_b, cache_dir=cache), B.deployed_hash(nl_b)
    check(got_b == true_b and true_b != B.deployed_hash(nl_a),
          "a folder and file name holding newlines cannot make two folders share a cache entry: %s vs %s"
          % ((got_b or "")[:16], (true_b or "")[:16]))
    odd = os.path.join(tmp, "Odd")
    write(os.path.join(odd, "About", "About.xml"), "x")
    os.symlink("/proc/uptime", os.path.join(odd, "uptime"))              # stat says size 0, a read gives bytes
    check(B.deployed_hash(odd) is None and B.deployed_hash(odd, cache_dir=cache) is None,
          "a file whose read length is not its size (a /proc file) is not hashed: no value to cache or match")
    fifo = os.path.join(tmp, "Fifo")
    write(os.path.join(fifo, "About", "About.xml"), "x")
    os.mkfifo(os.path.join(fifo, "pipe"))
    check(B.deployed_hash(fifo) is None and B.deployed_hash(fifo, cache_dir=cache) is None,
          "a folder holding a pipe is not hashed (and the reading does not wait on it)")
    bad = os.path.join(tmp, "Undecodable")
    write(os.path.join(bad, "About", "About.xml"), "x")
    write(os.path.join(os.fsencode(bad), b"n\xff.xml").decode("utf-8", "surrogateescape"), "y")
    hu = B.deployed_hash(bad, cache_dir=cache)
    check(bool(hu) and hu == B.deployed_hash(bad), "a file name that is not UTF-8 hashes, cached and not: %s"
          % (hu or "")[:20])
    # a link back to an ancestor under another spelling (drvfs folds case; realpath does not) is still a cycle
    ci_base = "/mnt/d/ClaudeWork/rimmandrake/build_match"
    if os.path.isdir(ci_base):
        ci = tempfile.mkdtemp(prefix="bm_case_", dir=ci_base)
        try:
            top = os.path.join(ci, "BmCase")
            write(os.path.join(top, "x"), "x")
            os.symlink(os.path.join(ci, "bmcase"), os.path.join(top, "self"))
            if os.path.isdir(os.path.join(ci, "bmcase")):
                seen = [r for r, _ in B._files(top)]
                check(seen == ["x"], "a link to an ancestor spelt in another case is cut as a cycle: %s" % seen)
            else:
                check(True, "case alias: %s is case-sensitive, not testable here" % ci_base)
        finally:
            shutil.rmtree(ci, ignore_errors=True)
    else:
        check(True, "case alias: no case-folding drive here (%s), not testable" % ci_base)

    # Exercise the same cycle on a case-sensitive test host: realpath can spell the reached directory
    # differently while scandir and stat still see the same inode.
    top = os.path.join(tmp, "BmCase")
    link = os.path.join(top, "self")
    write(os.path.join(top, "x"), "x")
    os.symlink(top, link)
    realpath = os.path.realpath
    with patch.object(os.path, "realpath", side_effect=lambda p: top.lower() if p == link else realpath(p)):
        seen = [r for r, _ in B._files(top)]
    check(seen == ["x"], "a differently spelt path to the same directory inode still ends the cycle: %s" % seen)

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
    shutil.rmtree(os.path.join(mods2, "RimMandrake.Biomes"))
    got3 = B._mod_folder(root2, "Comp", mods2)[1]
    check(got3 is None, "a composed mod whose Biomes folder is not deployed has no folder (never the stale "
          "standalone copy): %s" % got3)
    write(os.path.join(root2, "src", "RimMandrake", "Solo", "About", "About.xml"), ABOUT % "mandrake.rm.solo")
    write(os.path.join(mods2, "Solo", "About", "About.xml"), ABOUT % "mandrake.rm.solo")
    check(B._mod_folder(root2, "Solo", mods2)[1] == os.path.join(mods2, "Solo"),
          "a mod the composition does not name is read from its own folder")
    # Pyrelands visit 2 (2026-11-21): a composed member's DLL stamp is deployed at Biomes/<key>/Assemblies; the shell's
    # own Assemblies holds only the shell's stamp, so reading there owed a deploy forever
    biomes = os.path.join(mods2, "RimMandrake.Biomes")
    write(os.path.join(biomes, "About", "About.xml"), ABOUT % "mandrake.rm.biomes")
    write(os.path.join(biomes, "Assemblies", "RimMandrake.Biomes.dll.srchash"), "# project: shell\n# dll: aa\n")
    write(os.path.join(root2, "src", "RimMandrake", "Comp", "Assemblies", "Comp.dll.srchash"), "# project: comp\n# dll: bb\n")
    write(os.path.join(biomes, "Biomes", "Comp", "Assemblies", "Comp.dll.srchash"), "# project: comp\n# dll: bb\n")
    walk_c = {"deployed_folder": biomes}
    check(B.walk_source(root2, "Comp", walk_c)[0] is None,
          "a composed member whose deployed stamp (Biomes/<key>/Assemblies) equals its source owes no deploy")
    # a stamp copied beside a DLL the running game had locked is no deploy (Explosive Knockback, 2026-11-24)
    write(os.path.join(root2, "src", "RimMandrake", "Comp", "Assemblies", "Comp.dll"), "new build")
    write(os.path.join(biomes, "Biomes", "Comp", "Assemblies", "Comp.dll"), "old build")
    check("Comp.dll" in (B.walk_source(root2, "Comp", walk_c)[0] or ""),
          "the source's stamp beside another build's DLL owes a deploy, named by the DLL")
    write(os.path.join(biomes, "Biomes", "Comp", "Assemblies", "Comp.dll"), "new build")
    check(B.walk_source(root2, "Comp", walk_c)[0] is None, "the source's stamp beside the source's DLL owes nothing")
    write(os.path.join(biomes, "Biomes", "Comp", "Assemblies", "Comp.dll.srchash"), "# project: comp\n# dll: cc\n")
    owed = B.walk_source(root2, "Comp", walk_c)[0]
    check(bool(owed) and "deploy" in owed, "a composed member whose deployed stamp differs owes a deploy: %r" % (owed,))
    # fourth GPT review (D:\ClaudeWork\rimmandrake\conductor\bm_gpt_review4.log, the job's own probes): a composition
    # file that is there but cannot be read must not send a composed mod to its stale standalone copy
    for bad_json in ("{not json", json.dumps({"compose_wave": 1, "entries": ["Comp"]})):
        write(os.path.join(root2, "src", "RimMandrake", "Biomes.compose.json"), bad_json)
        got4 = B._mod_folder(root2, "Comp", mods2)[1]
        check(got4 is None, "an unreadable Biomes.compose.json (%s) gives no folder, never the standalone copy: %s"
              % (bad_json[:12], got4))

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
                      host="Archmagi", mod_sha="abc1234", scan=lambda m: dict.fromkeys(B.norm_list(am)))
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
    # drvfs returned ENOMEM on one 618 kB Biomes texture and read it whole the next time (measured 2026-11-24, on
    # ArchSmall's Mods folder): the walk build then read "Pyrelands is not deployed" and 0 of 39 checks counted.
    png = os.path.join(tmp, "Mods", "DeployedName", "Textures", "t.png")
    real_open, fails = open, {"left": 0}

    def flaky_open(path, *a, **k):
        if os.path.abspath(str(path)) == os.path.abspath(png) and fails["left"]:
            fails["left"] -= 1
            raise OSError(errno.ENOMEM, "Cannot allocate memory", path)
        return real_open(path, *a, **k)
    B.open, B.RETRY_PAUSE_S = flaky_open, 0
    try:
        fails["left"] = 1
        check(B.deployed_hash(d) == h1, "a file that drvfs refuses once with ENOMEM is read again: the same hash")
        fails["left"] = 10 ** 6
        check(B.deployed_hash(d) is None, "a file that never reads gives no hash, never a value")
        fails["left"] = 10 ** 6
        wn = B.walk_build(root, "TestMod", sv, host="Archmagi", mods_dir=os.path.join(tmp, "Mods"), version_txt=vt)
        txt = " ".join(wn["why"])
        check(wn["why"] and "not deployed" not in txt and "could not be read" in txt and "t.png" in txt,
              "a deployed folder that cannot be read says so and names the file, never 'not deployed': %s" % wn["why"])
    finally:
        del B.open
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
    clone = os.path.join(tmp, "poolclone")                  # another checkout of the repo (or its case alias)
    os.makedirs(os.path.join(clone, ".git"))
    os.environ[B.STANDIN_ENV] = stand
    try:
        wc = B.walk_build(clone, "TestMod", sv, host="Archmagi")
    finally:
        os.environ.pop(B.STANDIN_ENV, None)
    check(wc["why"] and B.STANDIN_ENV in " ".join(wc["why"]),
          "a stand-in is refused in any git checkout, not only the one this file sits in: %s" % wc["why"])
    wf = B.walk_build(clone, "TestMod", sv, host="Archmagi")   # fifth GPT review: --root naming another checkout
    check(wf["why"] and "build_match.py" in " ".join(wf["why"]) and not wf.get("mod_hash"),
          "another checkout's walk build is not read with this checkout's modset_builder and readers: %s" % wf["why"])

    # ---- the tier list is built fresh each reading: no on-disk cache can hand back a list the builder now refuses -----
    calls = {"scan": 0}

    class FakeMB:
        refuse = False

        @staticmethod
        def tier_def(t):
            return {} if t in ("bridge", "other") else None

        @staticmethod
        def scan(*a, **k):
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

    # ---- RIMMANDRAKE_READ_TIER_LIST_FROM_EVERY_GAME_INSTALL_HERE: the tier's list on this machine's other install -----
    other = os.path.join(tmp, "b", "Mods")
    os.makedirs(other, exist_ok=True)
    scans = []

    class TwoMB:
        gone = False

        @staticmethod
        def tier_def(t):
            return {} if t == "bridge" else None

        @staticmethod
        def scan(local_mods=None, keep=False):
            scans.append(local_mods)
            return {"where": local_mods}

        @staticmethod
        def resolve_tier(t, installed):
            b = installed["where"] == other
            return (["ludeon.rimworld"] + (["dep.mod"] if b else []), ["gone.mod"] if b and TwoMB.gone else [], [])
    real_dirs = getattr(B, "other_installs", None)
    sys.modules["modset_builder"] = TwoMB
    B.other_installs = lambda: [("ArchSmall", other)]
    walk = dict(WALK, why=[])
    try:
        def judged(mods):
            return B.judge_row("min_t", {}, row("min_t", active_mods=mods), walk, B.tier_lister(walk))
        plain = judged(["ludeon.rimworld"])
        lazy = list(scans)
        alt = judged(["ludeon.rimworld", "dep.mod"])
        bad = judged(["ludeon.rimworld", "dep.mod", "stray.mod"])
        TwoMB.gone = True
        lost = judged(["ludeon.rimworld", "dep.mod"])
    finally:
        B.other_installs = real_dirs
        if real is None:
            sys.modules.pop("modset_builder", None)
        else:
            sys.modules["modset_builder"] = real
    check(plain[0] and lazy == [None], "a row on the default install's list counts and no other install is scanned: %s %s"
          % (plain, lazy))
    check(alt[0] and "ArchSmall" in alt[1], "a row whose list is the tier's on the other install counts, named: %s" % (alt,))
    check(not bad[0] and "list" in bad[1], "a list that is the tier's on no install does not count: %s" % (bad,))
    check(not lost[0] and "ArchSmall" in lost[1], "an install the tier cannot be built on counts nothing, and is named: %s"
          % (lost,))


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
    # RIMMANDRAKE_READ_LIVE_FULL_KIND_AS_FULL_LIST: the test table marks sc_walk by kind live_full with no why_full_list; a
    # check of that kind ran on his full list and must be read as one (FlowWorks visit 2: sc_walk refused as "names no tier")
    check(B.is_full({"kind": "live_full", "stage": "6"}), "a test of kind live_full is a full-list test without why_full_list")
    check(not B.is_full({"kind": "live_minimal", "stage": "6"}), "a test of kind live_minimal is not a full-list test")
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


def tick_walk_checks(tmp):
    sys.path.insert(0, B.UTILS)
    import deploy_custom_mods as D
    import maturation as M
    import maturation_dispatch as MD

    root = os.path.join(tmp, "tick")
    mod = "Comp"
    vdir = os.path.join(M.mod_dir(root, mod), "version")
    visit = os.path.join(vdir, "in_game", "visit_1")
    src = os.path.join(root, "src", "RimMandrake")
    mods = os.path.join(tmp, "TickMods")
    folder = os.path.join(mods, "RimMandrake.Biomes")
    write(os.path.join(src, mod, "About", "About.xml"), ABOUT % "mandrake.rm.comp")
    write(os.path.join(src, "Biomes.compose.json"), json.dumps({
        "compose_wave": 1, "entries": [{"key": mod, "wave": 1}], "about": {"packageId": "mandrake.rm.biomes"},
        "target": "RimMandrake.Biomes"}))
    write(os.path.join(folder, "About", "About.xml"), ABOUT % "mandrake.rm.biomes")
    for i in range(32):
        write(os.path.join(folder, "Biomes", mod, "Defs", "%d.xml" % i), "<Defs/>")
    ver = os.path.join(tmp, "TickVersion.txt")
    write(ver, "1.6.4871 rev590\n")
    save = os.path.join(tmp, "tick.rws")
    write(save, "<?xml version=\"1.0\"?><savegame><meta><modIds><li>mandrake.rm.biomes</li></modIds></meta></savegame>")
    state = {"stage": "in_game", "version": "0.1.0", "moves": [{"to": "in_game"}]}
    write(os.path.join(M.mod_dir(root, mod), M.RECORD), json.dumps(state))
    write(os.path.join(vdir, "VERSION.json"), json.dumps({"version": "0.1.0"}))
    table = {"tests": {"full_t": {"kind": "live_full", "stage": 6, "why_full_list": "walk test"}}}
    write(os.path.join(vdir, "test_table.json"), json.dumps(table))
    h = B.deployed_hash(folder)
    write(os.path.join(visit, "rows.jsonl"), json.dumps(row(
        "full_t", mod_hash=h, game_build="1.6.4871 rev590", active_mods=["mandrake.rm.biomes"],
        site_checked=True, site="fixture site checked", mod_sha="abc1234")) + "\n")
    write(os.path.join(visit, "strange.jsonl"), "")
    write(os.path.join(visit, "SUMMARY.md"), "## Exit\ningame_rows: {full_t: pass}\nstrange_open: 0\n"
          "savegame: %s\nexit_met: true\n" % save)
    stamp = os.path.join(mods, ".RimMandrake.Biomes.walk-build.json")
    config = os.path.join(tmp, "tick-config.xml")
    write(config, "<ModsConfigData/>")
    applying = []

    def compose_apply(change, apply=True):
        # Run the CLI's orchestration with its writer and staging build replaced. No deployment runs.
        staged = os.path.join(tmp, "staged", "RimMandrake.Biomes")
        os.makedirs(staged, exist_ok=True)

        def run(args, targets, holds, mods_dir, active):
            if args.apply:
                applying.append(not os.path.exists(stamp))
                change()
            return 0

        argv = [D.__file__, "--compose", "biomes"] + (["--apply"] if apply else [])
        with patch.object(sys, "argv", argv), patch.object(D, "_MODS", [mods]), patch.object(D, "_CONFIG", [config]), \
                patch.object(D, "_is_real_game", return_value=False), patch.object(D, "mod_dirs", return_value=[]), \
                patch.object(D, "load_holds", return_value=[]), patch.object(D, "folded_refusal"), \
                patch.object(D.biomes_compose, "folded_ids", return_value=[]), \
                patch.object(D.biomes_compose, "build", return_value=("RimMandrake.Biomes", staged, [])), \
                patch.object(D, "_run", side_effect=run):
            return D.main()

    check(compose_apply(lambda: None, apply=False) == 0 and not os.path.exists(stamp),
          "a compose plan leaves the walk build stamp alone")
    check(compose_apply(lambda: None) == 0 and os.path.isfile(stamp) and
          json.load(open(stamp, encoding="utf-8"))["mod_hash"] == h,
          "a compose apply stamps the bytes of the deployed folder, including its extra files")
    hash_files = B._hash_files
    with patch.dict(os.environ, {"RM_MATURATION_DISPATCH_DIR": os.path.join(tmp, "dispatch")}), \
            patch.object(B.socket, "gethostname", return_value="archmagi"), \
            patch.object(B, "_paths", return_value=(mods, None, ver)), \
            patch.object(B, "_hash_files", side_effect=lambda d, files, cache_dir: hash_files(
                d, files, os.path.join(tmp, "tick_cache") if cache_dir else None)), \
            patch.object(B, "_files", wraps=B._files) as walk, \
            patch.object(M, "certificate", return_value={}), patch.object(MD, "rerun_result", return_value=None):
        def tick_match():
            return MD.add_ingame(root, mod, {"stage": "in_game"}, [])["exit"]["build_match"]

        matches = [tick_match() for _ in range(2)]
        check(walk.call_count == 0 and all(m["count"] == 1 for m in matches),
              "tick-uses-deploy-build-without-walking: %d deployed tree walks on two ticks" % walk.call_count)
        strict = M.read_ingame_exit(root, mod, 1)["build_match"]
        f = os.path.join(folder, "Biomes", mod, "Defs", "0.xml")
        s = os.stat(f)
        write(f, "<Defz/>")
        os.utime(f, ns=(s.st_atime_ns, s.st_mtime_ns))
        fresh = M.read_ingame_exit(root, mod, 1)["build_match"]
        check(strict["count"] == 1 and fresh["count"] == 0 and fresh["walk"]["mod_hash"] != h,
              "the explicit exit reader detects a same-size manual edit with its mtime restored, even with a stamp")
        before = walk.call_count
        check(tick_match()["walk"].get("deploy_stamp") == stamp and walk.call_count == before,
              "the Dispatch forecast identifies the deploy stamp it used")
        check(compose_apply(lambda: write(f, "<Defy/>")) == 0 and all(applying),
              "a second apply invalidates yesterday's stamp before the writer runs")
        before = walk.call_count
        new = tick_match()
        check(new["count"] == 0 and new["walk"]["mod_hash"] not in (h, fresh["walk"]["mod_hash"])
              and walk.call_count == before, "the next tick uses the changed deploy's hash without walking")
        if not os.path.isfile(stamp):
            return  # the stamp-writing check above reports its absence
        old_stamp = os.path.join(mods, ".RimMandrake.Biomes.previous")
        os.rename(stamp, old_stamp)
        check(tick_match()["walk"]["mod_hash"] == new["walk"]["mod_hash"] and walk.call_count == before + 1,
              "a legacy install without a stamp still hashes the deployed files")
        os.rename(old_stamp, stamp)
        os.rename(folder, os.path.join(tmp, "old-biomes"))
        write(os.path.join(folder, "About", "About.xml"), ABOUT % "mandrake.rm.biomes")
        fallback = tick_match()
        check(fallback["walk"]["mod_hash"] != new["walk"]["mod_hash"] and walk.call_count == before + 2,
              "a replacement folder cannot borrow the old folder's stamp")
        write(stamp, "invalid stamp")
        check(tick_match()["walk"]["mod_hash"] == fallback["walk"]["mod_hash"] and walk.call_count == before + 3,
              "an invalid stamp falls back to hashing the deployed files")


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


def _newline_key(folder, files, cache_dir):
    """the second build's cache key: names joined by newlines, which a name may hold."""
    sig = B.hashlib.sha256(os.path.realpath(folder).encode("utf-8", "surrogateescape") + b"\n")
    for r, p in files:
        st = os.stat(p)
        sig.update(("%s\0%d\0%d\0%d\n" % (r, st.st_size, st.st_mtime_ns, st.st_ctime_ns)).encode(
            "utf-8", "surrogateescape"))
    return os.path.join(cache_dir, "hash_%s.txt" % sig.hexdigest()[:32])


def _any_file_digest(path, h):
    """the second build's file read: any file opened, its stat size trusted (a pipe is opened non-blocking here so the
    mutant fails its check instead of hanging the selftest)."""
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        h.update(b"%d\0" % os.fstat(f.fileno()).st_size)
        for chunk in iter(lambda: f.read(1 << 20) or b"", b""):
            h.update(chunk)


def _path_chain_files(folder):
    """the second build's walk: a cycle known by its real path string, which drvfs case folding defeats."""
    out, top = [], os.path.realpath(folder)
    stack = [(folder, "", top, frozenset((top,)))]
    while stack:
        d, rel, real, chain = stack.pop()
        for e in list(os.scandir(d)):
            if e.is_dir():
                sub = os.path.realpath(e.path) if e.is_symlink() else os.path.join(real, e.name)
                if sub not in chain:
                    stack.append((e.path, rel + e.name + "/", sub, chain | {sub}))
            else:
                out.append((rel + e.name, e.path))
    return sorted(out)


def _fallback_mod_folder(root, mod, mods_dir):
    """the second build: a composed mod whose Biomes folder is missing fell back to its standalone folder."""
    pid, comp = B.mod_package_id(root, mod), B.composed_into(root, mod)
    folder = B.deployed_folder(mods_dir, comp[0], comp[1] or "") if comp else None
    return pid, folder or B.deployed_folder(mods_dir, pid, mod)


def _strict_keep(key, out):
    """the fourth build: a cache write that fails failed the whole hash."""
    os.makedirs(os.path.dirname(key), exist_ok=True)
    with open(key, "w") as f:
        f.write(out + "\n")


def _compose_error_ignored(root, mod):
    """the third build: an unreadable composition file read as composing nothing."""
    try:
        with open(os.path.join(root, "src", "RimMandrake", "Biomes.compose.json"), encoding="utf-8") as f:
            d = json.load(f)
        cw = d.get("compose_wave", 0)
        if any(e.get("key") == mod and e.get("wave", 99) <= cw for e in d.get("entries") or ()):
            return B.norm_pid((d.get("about") or {}).get("packageId")), d.get("target")
    except (OSError, ValueError, AttributeError):
        pass
    return None


def _old_last_rows(rows):
    return {r.get("test") or r.get("id"): r for r in rows or [] if r.get("test") or r.get("id")}


def _field_ignored(field, real=B.judge_row):
    """judge_row that never compares one field: the row is given the walk's own (a missing field stays missing)."""
    def f(test, spec, r, walk, tiers, relation=None):
        r = dict(r, **{field: walk.get(field)}) if r and r.get(field) else r
        return real(test, spec, r, walk, tiers, relation)
    return f


MUTANTS = {
    "links_and_errors_skipped": lambda: setattr(B, "_files", _old_files),
    "cache_key_size_mtime": lambda: setattr(B, "_cache_key", _old_key),
    "aliases_cut": lambda: setattr(B, "_files", _seen_once_files),
    "standalone_before_composed": lambda: setattr(B, "_mod_folder", _standalone_first),
    "key_newline_ambiguous": lambda: setattr(B, "_cache_key", _newline_key),
    "any_file_read": lambda: setattr(B, "_digest_file", _any_file_digest),
    "cycle_by_path_string": lambda: setattr(B, "_files", _path_chain_files),
    "composed_falls_back": lambda: setattr(B, "_mod_folder", _fallback_mod_folder),
    "standin_on_real_repo": lambda: setattr(B, "_standin_refused", lambda root: False),
    "standin_by_path_only": lambda: setattr(
        B, "_standin_refused", lambda root: os.path.realpath(root) == os.path.realpath(B.REPO)),
    "compose_error_ignored": lambda: setattr(B, "composed_into", _compose_error_ignored),
    "cache_write_strict": lambda: setattr(B, "_keep", _strict_keep),
    "foreign_checkout_read": lambda: setattr(B, "_foreign_checkout", lambda root: False),
    "idless_rows_dropped": lambda: setattr(B, "last_rows", _old_last_rows),
    "tier_scans_every_tier": lambda: setattr(B, "_resolve_tier", (lambda o: lambda t, i: o(t, []))(B._resolve_tier)),
    "other_installs_ignored": lambda: setattr(B, "other_tier_match", lambda *a: (None, "")),
    "other_installs_always_match": lambda: setattr(B, "other_tier_match", lambda *a: ("ArchSmall", "")),
    "hash_ignored": lambda: setattr(B, "judge_row", _field_ignored("mod_hash")),
    "build_ignored": lambda: setattr(B, "judge_row", _field_ignored("game_build")),
    "list_as_set": lambda: setattr(B, "same_list", lambda a, b: set(B.norm_list(a)) == set(B.norm_list(b))),
    "full_read_as_minimal": lambda: setattr(B, "is_full", lambda test: False),
    "missing_counts": lambda: setattr(B, "REQUIRED", ()),
    "modsconfig_grepped": lambda: setattr(B, "active_mods", _regex_active),
    "hash_names_only": lambda: setattr(B, "_digest_file", lambda p, h: None),
    "any_host_walks": lambda: setattr(B, "WALK_HOST", None),
    "walk_stamp_ignored": lambda: setattr(B, "_stamped_hash", lambda folder: None),
    "transient_read_not_retried": lambda: setattr(B, "READ_TRIES", 1),
    "unreadable_as_not_deployed": lambda: setattr(
        B, "deployed_hash_why", (lambda o: lambda f, cache_dir=None: (o(f, cache_dir)[0], "no folder"))(B.deployed_hash_why)),
}


def main():
    if "--mutants" in sys.argv:
        bad = []
        for m in MUTANTS:
            try:
                r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True,
                                   text=True, timeout=120)
            except subprocess.TimeoutExpired:                   # a mutant that hangs the reading is caught too
                print("ok    mutant %s: hung past 120 s, caught" % m)
                continue
            n = r.stdout.count("\nFAIL") + r.stdout.startswith("FAIL")
            print("%s  mutant %s: exit %d, %d check(s) failed" % ("ok  " if r.returncode == 1 else "FAIL", m,
                                                                   r.returncode, n))
            if r.returncode != 1:
                bad.append(m)
        print("%d of %d mutants caught" % (len(MUTANTS) - len(bad), len(MUTANTS)))
        return 1 if bad else 0
    if "--mutant" in sys.argv:
        MUTANTS[sys.argv[sys.argv.index("--mutant") + 1]]()
    mutants_rc = 0
    if "--mutant" not in sys.argv and "--default" not in sys.argv:
        # the door runs this file bare: the bare run also runs the mutants (RIMMANDRAKE_RUN_SELFTEST_MODES_AT_THE_DOOR)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutants"], capture_output=True, text=True,
                           timeout=900)
        print((r.stdout.strip().splitlines() or ["(no output)"])[-1])
        mutants_rc = 0 if r.returncode == 0 else 1
        if mutants_rc:
            print("FAIL mutants did not all die (exit %d)\n%s" % (r.returncode, r.stdout[-1500:] + r.stderr[-500:]))
    tmp = tempfile.mkdtemp(prefix="build_match_selftest_")
    try:
        io_checks(tmp)
        compare_checks()
        if "--mutant" not in sys.argv:
            cli_checks(tmp)
        if "--mutant" not in sys.argv or "walk_stamp_ignored" in sys.argv:
            tick_walk_checks(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d of %d checks failed" % (len(FAILS), CASES[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
