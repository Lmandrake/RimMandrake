#!/usr/bin/env python3
"""Selftest for leftovers.py: every kind's check, positive (SAFE) and negative (NOT-SAFE / REFUSED), plus the
archive -> verify -> delete round trip and its refusals. Runs entirely in a fixture tree (fake repo with a bare
remote, fake Saves/Config/Mods, fake scratch clones); never touches the live machine."""

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leftovers as L  # noqa: E402

OLD = time.time() - 30 * 86400
FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def w(path, text="x", old=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(text)
    if old:
        os.utime(path, (OLD, OLD))
    return path


def png(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + os.urandom(16))
    return path


def git(cwd, *a):
    subprocess.run(["git", "-C", cwd] + list(a), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def age_git(clone):
    for f in ("HEAD", "index", "logs/HEAD"):
        p = os.path.join(clone, ".git", f)
        if os.path.exists(p):
            os.utime(p, (OLD, OLD))


ABOUT = "<ModMetaData><packageId>%s</packageId></ModMetaData>"
FINDMOD = ('<Patch><Operation Class="PatchOperationFindMod"><mods><li>%s</li></mods>'
           '<match Class="PatchOperationAdd"><xpath>Defs</xpath><value/></match>%s</Operation></Patch>')


def build(t):
    env_git = ["-c", "user.name=t", "-c", "user.email=t@t"]
    repo = os.path.join(t, "repo")
    w(os.path.join(repo, "infrastructure/state/canon.yml"), "planet:\n  start_savegame: CANON_X.rws\n")
    w(os.path.join(repo, "docs/notes.md"), "see RM_referenced_save.rws and mandrake.rm.moda, CANON_X.rws, "
                                          "ModsConfig.xml.bak-named\n")
    m = os.path.join(repo, "src/RimMandrake/ModA")
    w(os.path.join(m, "About/About.xml"), ABOUT % "mandrake.rm.moda")
    w(os.path.join(m, "Defs/a.xml"), "<Defs><ThingDef><graphicData><texPath>Things/Used/Thing</texPath>"
                                     "</graphicData></ThingDef>"
                                     # slashless texPaths name a Textures-root file / Graphic_Random folder
                                     "<ThingDef><graphicData><texPath>rootaxe</texPath></graphicData>"
                                     "<uiIconPath>rooticon</uiIconPath></ThingDef>"
                                     "<ThingDef><graphicData><graphicClass>Graphic_Random</graphicClass>"
                                     "<texPath>rootfolder</texPath></graphicData>"
                                     "<description>things</description><placementMask>Things</placementMask></ThingDef></Defs>")
    w(os.path.join(m, "Source/GoneMod.cs"), 'class GoneMod { string s = "Things/Coded/Icon"; '
                                            'string b = "rootcoded"; '
                                            'string c = "Things/Composed/Debris_" + (ash ? "Ash" : "Char") + i; }')
    png(os.path.join(m, "RimThemes/Shell/Textures/Widgets.ButtonBGAtlas.png"))
    for f in ("Things/Composed/Debris_Ash3.png", "rootaxe.png", "rooticon.png", "rootfolder/a.png", "rootcoded.png",
              "rootorphan.png",
              "Things/Deep/rootaxe.png"):
        png(os.path.join(m, "Textures", f))
    png(os.path.join(m, "Textures/Things/Used/Thing_north.png"))
    png(os.path.join(m, "Textures/Things/Coded/Icon.png"))
    png(os.path.join(m, "Textures/Things/Unused/Orphan.png"))
    png(os.path.join(m, "Textures/UI/Icons/Lone.png"))
    w(os.path.join(m, "Patches/Dead.xml"), FINDMOD % ("sarg.alphabiomes", ""))
    w(os.path.join(m, "Patches/Live.xml"), FINDMOD % ("Ludeon.RimWorld.Odyssey", ""))
    w(os.path.join(m, "Patches/Nomatch.xml"), FINDMOD % ("sarg.alphabiomes", "<nomatch Class=\"PatchOperationAdd\"/>"))
    w(os.path.join(m, "Patches/Mixed.xml"), FINDMOD % ("sarg.alphabiomes</li><li>Ludeon.RimWorld.Odyssey", ""))
    remote = os.path.join(t, "remote.git")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    git(repo, "add", "-A")
    git(repo, *env_git, "commit", "-q", "-m", "init")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], check=True)
    git(repo, "remote", "add", "origin", remote)
    git(repo, "push", "-q", "-u", "origin", "main")
    # an unpushed repo picture
    png(os.path.join(m, "Textures/Things/Unused/Local.png"))
    git(repo, "add", "src/RimMandrake/ModA/Textures/Things/Unused/Local.png")
    git(repo, *env_git, "commit", "-q", "-m", "local")

    ud = os.path.join(t, "userdata")
    saves, config, mods = os.path.join(ud, "Saves"), os.path.join(ud, "Config"), os.path.join(t, "Mods")
    w(os.path.join(saves, "CANON_X.rws"), "<savegame><meta><modIds><li>ludeon.rimworld</li>"
                                          "<li>mandrake.rm.moda</li></modIds></meta></savegame>")
    for n in ("RM_old.rws", "RM_old2.rws", "RM_referenced_save.rws", "RM_x_REVIEW.rws", "PlayerColony.rws",
              "CANONICAL_copy.rws"):
        w(os.path.join(saves, n), "<savegame/>")
    w(os.path.join(saves, "RM_new.rws"), "<savegame/>", old=False)
    w(os.path.join(ud, "Saves_backup_x/RM_a.rws"), "s")
    w(os.path.join(ud, "Saves_backup_canon/CANON_X.rws"), "s")
    w(os.path.join(config, "ModsConfig.xml"), "<ModsConfigData><activeMods><li>ludeon.rimworld</li>"
                                              "<li>mandrake.rm.moda</li></activeMods></ModsConfigData>")
    w(os.path.join(config, "ModsConfig.xml.bak-old"), "<x/>")
    w(os.path.join(config, "ModsConfig.xml.bak-named"), "<x/>")
    w(os.path.join(config, "Mod_ModA_ModAMod.xml"), "<x/>")
    w(os.path.join(config, "Mod_Gone_GoneMod.xml"), "<x/>")
    w(os.path.join(config, "Mod_Foreign_ForeignMod.xml"), "<x/>")
    w(os.path.join(mods, "ModA/About/About.xml"), ABOUT % "mandrake.rm.moda")
    w(os.path.join(mods, "Under_Score/About/About.xml"), ABOUT % "mandrake.rm.under")
    w(os.path.join(config, "Mod_Under_Score_UnderMod.xml"), "<x/>")
    w(os.path.join(mods, "Orphan/About/About.xml"), ABOUT % "mandrake.rm.orphan")
    png(os.path.join(mods, "Orphan/Textures/Things/Gone/Thing.png"))
    w(os.path.join(mods, "Foreign/About/About.xml"), ABOUT % "someone.else.mod")
    png(os.path.join(mods, "Foreign/Textures/Things/Gone/Thing.png"))

    sc = os.path.join(t, "scratch")
    clones = {}
    for name in ("clean", "dirty", "unpushed", "rebased", "foreign"):
        c = os.path.join(sc, "BENCH", name)
        subprocess.run(["git", "clone", "-q", remote, c], check=True)
        clones[name] = c
    w(os.path.join(clones["dirty"], "untracked.txt"), "work")
    w(os.path.join(clones["unpushed"], "new.txt"), "work")
    git(clones["unpushed"], "add", "new.txt")
    git(clones["unpushed"], *env_git, "commit", "-q", "-m", "unpushed")
    # rebased: a local commit whose patch is on origin/main under another sha (publish rebases)
    git(clones["rebased"], "fetch", "-q", repo, "main")
    git(clones["rebased"], *env_git, "cherry-pick", "--allow-empty", "FETCH_HEAD")
    git(clones["foreign"], "remote", "set-url", "origin", "/elsewhere/other.git")
    for c in clones.values():
        age_git(c)
    return repo, saves, config, mods, sc, clones


def main():
    t = tempfile.mkdtemp(prefix="leftovers_st_")
    try:
        repo, saves, config, mods, sc, clones = build(t)
        # the repo's own origin/main must be the PUSHED state: the 'local' commit is not on it
        subprocess.run(["git", "-C", repo, "fetch", "-q", "origin"], check=True)
        # the rebased clone's cherry-pick is equivalent to the repo's unpushed 'local' commit; push it so it
        # is on origin/main under a different sha than the clone's
        ctx = L.Ctx(repo=repo, saves=saves, config=config, mods=mods, clone_roots=[sc],
                    archive_root=os.path.join(t, "archive"), dump="", retired={"sarg.alphabiomes", "retired.mod"})
        V = lambda p, k=None: L.check(ctx, p, k)  # noqa: E731
        s = lambda p: V(p).status  # noqa: E731

        # ---- save
        ok(s(os.path.join(saves, "RM_old.rws")) == L.SAFE, "save: old unreferenced agent save is SAFE")
        ok(s(os.path.join(saves, "RM_referenced_save.rws")) == L.NOT_SAFE, "save: repo-referenced save is NOT-SAFE")
        ok(s(os.path.join(saves, "RM_new.rws")) == L.NOT_SAFE, "save: young save is NOT-SAFE")
        ok(s(os.path.join(saves, "RM_x_REVIEW.rws")) == L.NOT_SAFE, "save: unjudged review save is NOT-SAFE")
        ok(s(os.path.join(saves, "CANON_X.rws")) == L.REFUSED, "save: canon.yml start_savegame is REFUSED")
        ok(s(os.path.join(saves, "CANONICAL_copy.rws")) == L.REFUSED, "save: CANONICAL* copy is REFUSED")
        ok(s(os.path.join(saves, "PlayerColony.rws")) == L.REFUSED, "save: non-agent name is REFUSED")
        ok(s(os.path.join(os.path.dirname(saves), "Saves_backup_x")) == L.SAFE, "save: old backup folder is SAFE")
        ok(s(os.path.join(os.path.dirname(saves), "Saves_backup_canon")) == L.REFUSED,
           "save: backup folder holding a canonical copy is REFUSED")
        # sanity probe: blind the repo grep -> UNMEASURED, never SAFE
        blind = L.Ctx(repo=repo, saves=saves, config=config, mods=mods, clone_roots=[sc],
                      archive_root=ctx.archive_root, dump="", retired=ctx._retired, canon_saves={"NOPE_ZZ.rws"})
        ok(L.check(blind, os.path.join(saves, "RM_old.rws")).status == L.UNMEASURED,
           "save: a blind reference search reads UNMEASURED")

        # ---- clone
        ok(s(clones["clean"]) == L.SAFE, "clone: clean pushed idle clone is SAFE")
        ok(s(clones["dirty"]) == L.NOT_SAFE, "clone: untracked work is NOT-SAFE")
        ok(s(clones["unpushed"]) == L.NOT_SAFE, "clone: unpushed commit is NOT-SAFE")
        ok(s(clones["foreign"]) == L.REFUSED, "clone: foreign origin is REFUSED")
        ok(s(repo) == L.REFUSED, "clone: a clone outside the scratch roots is REFUSED")
        git(clones["clean"], "stash", "list")
        w(os.path.join(clones["clean"], "f.txt"), "y")
        git(clones["clean"], "-c", "user.name=t", "-c", "user.email=t@t", "stash", "-q", "-u")
        age_git(clones["clean"])
        ok(s(clones["clean"]) == L.NOT_SAFE, "clone: a stash is NOT-SAFE")
        git(clones["clean"], "stash", "drop", "-q")
        age_git(clones["clean"])
        # an ignored file is not in the bundle: NOT-SAFE until it is gone
        w(os.path.join(clones["clean"], ".git", "info", "exclude"), "local.env\n")
        w(os.path.join(clones["clean"], "local.env"), "SECRET=1")
        age_git(clones["clean"])
        ok(s(clones["clean"]) == L.NOT_SAFE, "clone: an ignored file (lost by the bundle) is NOT-SAFE")
        os.remove(os.path.join(clones["clean"], "local.env"))
        # a tag on a commit no remote has is unpushed work
        git(clones["clean"], "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "tagged")
        git(clones["clean"], "tag", "-a", "-m", "t", "v-local")
        git(clones["clean"], "-c", "advice.detachedHead=false", "reset", "-q", "HEAD~1")
        age_git(clones["clean"])
        ok(s(clones["clean"]) == L.NOT_SAFE, "clone: an unpushed annotated tag is NOT-SAFE")
        git(clones["clean"], "tag", "-d", "v-local")
        age_git(clones["clean"])
        ok(s(clones["clean"]) == L.SAFE, "clone: clean again once the ignored file and the tag are gone")
        # rebased: push the repo's local commit, so the clone's cherry-pick is patch-equivalent on origin/main
        subprocess.run(["git", "-C", repo, "push", "-q", "origin", "main"], check=True)
        ctx._cache.pop("origin_main", None)
        ok(s(clones["rebased"]) == L.SAFE, "clone: local sha patch-equivalent on origin/main is SAFE")
        ok(s(clones["unpushed"]) == L.NOT_SAFE, "clone: unpushed stays NOT-SAFE after the push")

        # ---- modfolder
        ok(s(os.path.join(mods, "Orphan")) == L.SAFE, "modfolder: orphan mandrake folder is SAFE")
        ok(s(os.path.join(mods, "ModA")) == L.NOT_SAFE, "modfolder: active/in-repo folder is NOT-SAFE")
        ok(s(os.path.join(mods, "Foreign")) == L.REFUSED, "modfolder: non-mandrake folder is REFUSED")
        ctx._cache.pop("active", None)
        os.rename(os.path.join(config, "ModsConfig.xml"), os.path.join(t, "mc.xml"))
        ok(s(os.path.join(mods, "Orphan")) == L.UNMEASURED, "modfolder: unreadable ModsConfig reads UNMEASURED")
        os.rename(os.path.join(t, "mc.xml"), os.path.join(config, "ModsConfig.xml"))
        ctx._cache.pop("active", None)

        # ---- setting
        ok(s(os.path.join(config, "ModsConfig.xml.bak-old")) == L.SAFE, "setting: unnamed old ModsConfig backup is SAFE")
        ok(s(os.path.join(config, "ModsConfig.xml.bak-named")) == L.NOT_SAFE, "setting: repo-named backup is NOT-SAFE")
        ok(s(os.path.join(config, "Mod_Gone_GoneMod.xml")) == L.SAFE, "setting: settings of a gone mod of ours is SAFE")
        ok(s(os.path.join(config, "Mod_ModA_ModAMod.xml")) == L.NOT_SAFE, "setting: live settings file is NOT-SAFE")
        ok(s(os.path.join(config, "Mod_Under_Score_UnderMod.xml")) == L.NOT_SAFE,
           "setting: live settings of a folder whose name holds '_' is NOT-SAFE")
        ok(s(os.path.join(config, "Mod_Foreign_ForeignMod.xml")) == L.REFUSED, "setting: foreign settings REFUSED")
        ok(s(os.path.join(config, "ModsConfig.xml")) == L.REFUSED, "setting: the live ModsConfig.xml is REFUSED")

        # ---- picture
        tex = os.path.join(repo, "src/RimMandrake/ModA/Textures")
        ok(s(os.path.join(tex, "Things/Unused/Orphan.png")) == L.SAFE, "picture: unreferenced pushed texture is SAFE")
        ok(s(os.path.join(tex, "Things/Used/Thing_north.png")) == L.NOT_SAFE, "picture: texPath _north variant is NOT-SAFE")
        ok(s(os.path.join(tex, "Things/Coded/Icon.png")) == L.NOT_SAFE, "picture: C# literal reference is NOT-SAFE")
        ok(s(os.path.join(tex, "UI/Icons/Lone.png")) == L.NOT_SAFE, "picture: UI/ path cannot be cleared")
        ok(s(os.path.join(mods, "Orphan/Textures/Things/Gone/Thing.png")) == L.SAFE,
           "picture: unreferenced deployed texture of ours is SAFE")
        ok(s(os.path.join(mods, "Foreign/Textures/Things/Gone/Thing.png")) == L.REFUSED,
           "picture: texture in a foreign mod is REFUSED")
        ok(s(os.path.join(tex, "rootaxe.png")) == L.NOT_SAFE, "picture: slashless <texPath> file is NOT-SAFE")
        ok(s(os.path.join(tex, "rooticon.png")) == L.NOT_SAFE, "picture: slashless <uiIconPath> file is NOT-SAFE")
        ok(s(os.path.join(tex, "rootfolder/a.png")) == L.NOT_SAFE,
           "picture: file in a slashless Graphic_Random folder is NOT-SAFE")
        ok(s(os.path.join(tex, "rootcoded.png")) == L.NOT_SAFE, "picture: slashless C# literal file is NOT-SAFE")
        ok(s(os.path.join(tex, "Things/Composed/Debris_Ash3.png")) == L.NOT_SAFE,
           "picture: a C# path composed as \"..._\" + kind + i covers its files")
        ok(s(os.path.join(repo, "src/RimMandrake/ModA/RimThemes/Shell/Textures/Widgets.ButtonBGAtlas.png"))
           == L.NOT_SAFE, "picture: a RimThemes theme texture (read by file name) is NOT-SAFE")
        ok(s(os.path.join(tex, "rootorphan.png")) == L.SAFE, "picture: unreferenced Textures-root file is SAFE")
        ok(s(os.path.join(tex, "Things/Deep/rootaxe.png")) == L.SAFE,
           "picture: a bare word never vouches for a deeper path of the same name")
        ok(s(os.path.join(tex, "Things/Unused/Orphan.png")) == L.SAFE,
           "picture: a non-path element text ('things') does not clear a Textures-root folder")
        png(os.path.join(tex, "Things/Unused/Untracked.png"))
        ok(s(os.path.join(tex, "Things/Unused/Untracked.png")) == L.NOT_SAFE, "picture: untracked repo file is NOT-SAFE")

        # ---- patch
        pat = os.path.join(repo, "src/RimMandrake/ModA/Patches")
        ok(s(os.path.join(pat, "Dead.xml")) == L.SAFE, "patch: FindMod of a retired mod only is SAFE")
        ok(s(os.path.join(pat, "Live.xml")) == L.NOT_SAFE, "patch: FindMod of a live mod is NOT-SAFE")
        ok(s(os.path.join(pat, "Nomatch.xml")) == L.NOT_SAFE, "patch: FindMod with <nomatch> is NOT-SAFE")
        ok(s(os.path.join(pat, "Mixed.xml")) == L.NOT_SAFE, "patch: retired+live mod list is NOT-SAFE")

        # ---- scan sees the fixtures
        c = L.scan(ctx)
        ok(os.path.join(mods, "Orphan") in c["modfolder"] and os.path.join(mods, "ModA") not in c["modfolder"],
           "scan: orphan mod folder found, in-repo one not")
        ok(any(p.endswith("Orphan.png") for p in c["picture"]) and not any(p.endswith("Thing_north.png")
                                                                          for p in c["picture"]),
           "scan: unreferenced picture found, referenced one not")
        ok(any(p.endswith("Dead.xml") for p in c["patch"]), "scan: retired-mod patch found")
        ok(clones["clean"] in c["clone"], "scan: scratch clone found")

        # ---- archive / delete
        old2 = os.path.join(saves, "RM_old2.rws")
        try:
            L.delete(ctx, old2, ledger=False)
            ok(False, "delete: refuses without an archive")
        except SystemExit as e:
            ok("no archive" in str(e), "delete: refuses without an archive")
        try:
            L.delete(ctx, os.path.join(saves, "RM_new.rws"), ledger=False)
            ok(False, "delete: refuses a NOT-SAFE path")
        except SystemExit as e:
            ok("NOT-SAFE" in str(e), "delete: refuses a NOT-SAFE path")
        try:
            L.archive(ctx, os.path.join(saves, "PlayerColony.rws"))
            ok(False, "archive: refuses a path not ours")
        except SystemExit as e:
            ok("REFUSED" in str(e), "archive: refuses a path not ours")
        orphan = os.path.join(tex, "Things/Unused/Orphan.png")
        ok(s(orphan) == L.SAFE, "picture: the orphan is SAFE by references (so only the kind rule can refuse it)")
        try:
            L.delete(ctx, orphan, ledger=False)
            ok(False, "delete: refuses a picture (art ledger only)")
        except SystemExit as e:
            ok("art ledger" in str(e) and os.path.exists(orphan), "delete: refuses a picture (art ledger only)")
        old = os.path.join(saves, "RM_old.rws")
        before = L._sha256(old)
        man = L.archive(ctx, old)
        ok(os.path.exists(man), "archive: manifest written")
        w(old, "<savegame>changed</savegame>")
        try:
            L.delete(ctx, old, ledger=False)
            ok(False, "delete: refuses when the file changed after its archive")
        except SystemExit as e:
            ok("does not verify" in str(e), "delete: refuses when the file changed after its archive")
        man = L.archive(ctx, old)
        before = L._sha256(old)
        L.delete(ctx, old, ledger=False)
        ok(not os.path.exists(old), "delete: SAFE + verified archive deletes")
        arc = json.load(open(man))["archive"]
        with tarfile.open(arc) as tf:
            tf.extractall(os.path.join(t, "restore"))
        ok(L._sha256(os.path.join(t, "restore", "RM_old.rws")) == before, "round trip: restored save is identical")
        acts = [json.loads(l) for l in open(os.path.join(ctx.archive_root, "acts.jsonl"))]
        ok(acts and acts[-1]["path"] == os.path.realpath(old) and acts[-1]["archive"] == arc,
           "digest: act line records path and archive")
        # clone round trip through a bundle
        cl = clones["clean"]
        head = subprocess.run(["git", "-C", cl, "rev-parse", "HEAD"], stdout=subprocess.PIPE).stdout.strip()
        man = L.archive(ctx, cl)
        L.delete(ctx, cl, ledger=False)
        ok(not os.path.exists(cl), "clone: retired after bundling")
        b = json.load(open(man))["archive"]
        rest = os.path.join(t, "restore_clone")
        subprocess.run(["git", "clone", "-q", b, rest], check=True)
        h2 = subprocess.run(["git", "-C", rest, "rev-parse", "HEAD"], stdout=subprocess.PIPE).stdout.strip()
        ok(h2 == head, "round trip: clone restored from bundle at the same HEAD")
    finally:
        shutil.rmtree(t, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
