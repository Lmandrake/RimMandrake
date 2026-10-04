"""Selftest for run_identity (observatory S1): fingerprint states, the proves_fresh gate and modal_sweep.
Each 'proven' case has a paired control that must NOT prove, so a gate that stops gating turns this red.
Run: python3 selftest_run_identity.py"""
import os
import sys
import tempfile
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
import run_identity as R  # noqa: E402
import deploy_custom_mods as real  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


tmp = tempfile.mkdtemp()
src = os.path.join(tmp, "src", "RimMandrake", "Zed")
dst = os.path.join(tmp, "mods", "Zed")


def put(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


for root in (src, dst):
    put(root, "About/About.xml", b"<a/>")
    put(root, "Defs/a.xml", b"<Defs/>")
    put(root, "Assemblies/Zed.dll", b"MZ1")
put(src, "Assemblies/Zed.dll.srchash", b"abc123")
put(dst, "Assemblies/Zed.dll.srchash", b"abc123")
dm = types.SimpleNamespace(mod_dirs=lambda: {"Zed": src}, LOCAL_MODS=os.path.join(tmp, "mods"), ROOT=tmp,
                           tree=real.tree, split_held=real.split_held, load_holds=lambda: [], compare=real.compare)
GIT = {"source": "mirror", "sha": "deadbeef00"}

a = R.mod_fingerprint("Zed", dm)
b = R.mod_fingerprint("Zed", dm)
check("in-sync tree fingerprints in-sync", a["state"] == "in-sync" and a["src_hash"] == a["deployed_hash"], a.get("reason"))
check("dll sha and its .srchash sidecar recorded", a["dlls"][0]["srchash"] == "abc123" and a["dlls"][0]["sha"])
ok, why = R.proves_fresh(a, b, GIT)
check("in-sync at start and end on a mirror proves fresh", ok, why)

# control 1: a changed def file => drift => NOT proven
put(src, "Defs/a.xml", b"<Defs><new/></Defs>")
d = R.mod_fingerprint("Zed", dm)
check("edited def => drift", d["state"] == "drift" and d["drift"]["changed"] == 1, d["drift"])
check("STALE fingerprint (drift) is never proven", not R.proves_fresh(d, d, GIT)[0])
put(dst, "Defs/a.xml", b"<Defs><new/></Defs>")

# control 2: redeploy DURING the run (start in-sync, end in-sync but different content) => not proven
s0 = R.mod_fingerprint("Zed", dm)
put(src, "Defs/a.xml", b"<Defs><newer/></Defs>")
put(dst, "Defs/a.xml", b"<Defs><newer/></Defs>")
s1 = R.mod_fingerprint("Zed", dm)
check("both in-sync but content moved mid-run => not proven", not R.proves_fresh(s0, s1, GIT)[0], R.proves_fresh(s0, s1, GIT)[1])

# control 3: missing end fingerprint / dirty tree / no repo identity / not deployed
check("missing end fingerprint => not proven", not R.proves_fresh(s1, None, GIT)[0])
dirty = dict(s1, src_dirty=True)
check("dirty source tree (does not match HEAD) => not proven", not R.proves_fresh(dirty, dirty, {"source": "git", "sha": "x"})[0])
check("no repo identity => not proven", not R.proves_fresh(s1, s1, {"source": "unknown", "sha": None})[0])
check("git checkout with unknowable dirtiness => not proven", not R.proves_fresh(dict(s1, src_dirty=None), dict(s1, src_dirty=None), {"source": "git", "sha": "x"})[0])
import shutil
shutil.rmtree(dst)
nd = R.mod_fingerprint("Zed", dm)
check("not deployed => state not-deployed, not proven", nd["state"] == "not-deployed" and not R.proves_fresh(nd, nd, GIT)[0])
check("unknown mod => unknown, never raises", R.mod_fingerprint("Nope", dm)["state"] == "unknown")

# held files are excluded from both sides (deploy tool's own hold logic)
put(dst, "About/About.xml", b"<a/>"); put(dst, "Defs/a.xml", b"<Defs><newer/></Defs>"); put(dst, "Assemblies/Zed.dll", b"MZ1"); put(dst, "Assemblies/Zed.dll.srchash", b"abc123")
put(src, "Defs/held.xml", b"<Defs/>")
dm2 = types.SimpleNamespace(**dict(vars(dm), load_holds=lambda: [("Zed/Defs/held.xml", "x")],
                                    split_held=lambda holds, name, rels: ([r for r in rels if r != "Defs/held.xml"], [("Defs/held.xml", "x")])))
h = R.mod_fingerprint("Zed", dm2)
check("a held, undeployed file is not drift", h["state"] == "in-sync" and h["n_held"] == 1, h["drift"])
check("same tree WITHOUT the hold IS drift (control)", R.mod_fingerprint("Zed", dm)["state"] == "drift")

# folded biome mod: fingerprinted as the composed mod (was 'unknown: no source dir' => every pass unproven)
import biomes_compose as _bc
_cdir = os.path.join(tmp, "compose_master")
for _rel, _d in (("About/About.xml", b"<a/>"), ("Biomes/Foo/Defs/a.xml", b"<Defs/>")):
    put(_cdir, _rel, _d)
    put(os.path.join(tmp, "mods", "Comp"), _rel, _d)
_orig_build = _bc.build
import shutil as _sh
def _fake_build(*a, **k):      # the real build hands back a fresh temp dir the caller deletes
    d = tempfile.mkdtemp(); _sh.copytree(_master, os.path.join(d, "Comp")); return ("Comp", os.path.join(d, "Comp"), [])
_master = os.path.join(tmp, "compose_master")
_bc.build = _fake_build
dm3 = types.SimpleNamespace(**dict(vars(dm), mod_dirs=lambda: {}, folded=lambda: {"Foo": ("Comp", "Foo")}, SRC_ROOT=os.path.join(tmp, "src")))
try:
    c = R.mod_fingerprint("Foo", dm3)
    check("folded mod fingerprints the composed folder", c["state"] == "in-sync" and c.get("composed") == "Comp", c.get("reason"))
    put(_cdir, "Biomes/Bar/Defs/b.xml", b"<Defs/>")   # sibling biome only in repo: not Foo's drift
    check("folded mod ignores sibling biome drift", R.mod_fingerprint("Foo", dm3)["state"] == "in-sync")
    put(os.path.join(tmp, "mods", "Comp"), "Biomes/Foo/Defs/a.xml", b"<Defs><x/></Defs>")
    _dd = R.mod_fingerprint("Foo", dm3); check("folded mod: composed drift => drift (control)", _dd["state"] == "drift", _dd.get("drift") or _dd.get("reason"))
    dm4 = types.SimpleNamespace(**dict(vars(dm3), folded=lambda: {}))
    check("not folded and no dir => unknown (control)", R.mod_fingerprint("Foo", dm4)["state"] == "unknown")
finally:
    _bc.build = _orig_build

# modal_sweep records what it found
calls = []
def fake_call(tool, **kw):
    calls.append(kw["typeName"])
    return {"success": True, "closedCount": 1 if "Naming" in kw["typeName"] or "NamePlayer" in kw["typeName"] else 0}
m = R.modal_sweep(fake_call)
check("modal_sweep: found_open true when one dialog closed", m["found_open"] and m["dialogs"]["Dialog_NamePlayerFactionAndSettlement"] == 1 and calls == list(R.MODAL_DIALOGS), m)
m0 = R.modal_sweep(lambda tool, **kw: {"success": True, "closedCount": 0})
check("modal_sweep: nothing open => found_open false (control)", not m0["found_open"] and not m0["errors"])
def raising(tool, **kw):
    raise TimeoutError("t")
me = R.modal_sweep(raising)
check("modal_sweep: a raising call is an error entry, dialog None, never raises", me["errors"] and all(v is None for v in me["dialogs"].values()) and not me["found_open"])
mf = R.modal_sweep(lambda tool, **kw: {"success": False, "message": "no"})
check("modal_sweep: reply success false is an error, not 'closed none'", mf["errors"] and not mf["found_open"])

mn = R.modal_sweep(lambda tool, **kw: {"success": False, "message": "No open window's type name contains '%s'." % kw["typeName"]})
check("modal_sweep: the tool's 'No open window' refusal is a clean read (closed 0), not an error",
      not mn["errors"] and not mn["found_open"] and all(v == 0 for v in mn["dialogs"].values()), mn)
mo = R.modal_sweep(lambda tool, **kw: {"success": False, "message": "No bridge session"})
check("modal_sweep: any OTHER success:false stays an error (control)", mo["errors"] and all(v is None for v in mo["dialogs"].values()))

# git_state is real here
g = R.git_state()
check("git_state resolves this checkout", g["source"] in ("git", "mirror") and g["sha"], g)

if FAILS:
    print("\nFAILED: %s" % FAILS)
    sys.exit(1)
print("\nOK: selftest_run_identity")
