"""prove_harmony_patches.py - prove jawa/harmony_patches, and use it to close
WILD_ANIMALS_PADDED_LISTS_1: name the mod whose Harmony patch pads every
biome's wildAnimals list to 1024 records.

READ ONLY. jawa/harmony_patches touches no Map, Pawn or game state - it reads
Harmony's own patch registry - so this needs no pause gate and no cleanup,
unlike prove_new_tools.py.

    python.exe src/RimMandrake/bridgetools/prove_harmony_patches.py
    python3     src/RimMandrake/bridgetools/prove_harmony_patches.py --selftest

Written alongside the tool, before either was ever run against a live game -
see JawaBenchHarmonyInspect.cs and WILD_ANIMALS_PADDED_LISTS_1.md for what
built it and why.
"""
import argparse
import os
import sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_ROOT, "src", "RimMandrake", "Utils"))

OK, BAD, SKIP = "  ok  ", "  FAIL", "  skip"
RESULTS = []


def check(name, cond, detail=""):
    print("%s %s%s" % (OK if cond else BAD, name, ("   " + detail) if detail else ""))
    RESULTS.append((name, bool(cond)))
    return bool(cond)


def skip(name, why):
    print("%s %s   %s" % (SKIP, name, why))
    RESULTS.append((name, None))


def ok(resp):
    return isinstance(resp, dict) and resp.get("success") is True


def prove(s, have):
    if "jawa/harmony_patches" not in have:
        return skip("jawa/harmony_patches",
                     "not registered - deploy first (build.py --apply, game closed)")

    r = s.call("jawa/harmony_patches", typeName="BiomeDef")
    check("jawa/harmony_patches answers for BiomeDef", ok(r),
          "methodCount=%s" % (r or {}).get("methodCount"))

    methods = (r or {}).get("methods") or []
    print("     patched BiomeDef methods: %s" % [m.get("method") for m in methods])

    target = next((m for m in methods if m.get("method") == "CommonalityOfAnimal"), None)
    if target is None:
        # WILD_ANIMALS_PADDED_LISTS_1's own offline half already named this as a
        # live possibility: the padder may act through a DIFFERENT type entirely
        # (a DefGenerator or ResolveReferences transpiler, not a BiomeDef method).
        # A skip here is the correct next-step signal, not a tool failure.
        skip("CommonalityOfAnimal is patched",
             "not found on BiomeDef directly - the padder may act through "
             "DefGenerator/ResolveReferences instead; try typeName=DefGenerator "
             "or a broader survey next")
    else:
        patches = ((target.get("postfixes") or []) + (target.get("prefixes") or [])
                   + (target.get("transpilers") or []))
        check("  ...and a patch on it names an owner and assembly",
              bool(patches) and any(p.get("patchAssembly") for p in patches),
              str([(p.get("owner"), p.get("patchAssembly")) for p in patches]))

    # Second call: filtered to the one method, must be a subset of the first.
    r2 = s.call("jawa/harmony_patches", typeName="BiomeDef",
                methodName="CommonalityOfAnimal")
    check("  ...and the methodName filter narrows the result",
          ok(r2) and (r2 or {}).get("methodCount", 0) <= (r or {}).get("methodCount", 99),
          "methodCount=%s" % (r2 or {}).get("methodCount"))


# ------------------------------------------------------------------- selftest

class _StubBridge(object):
    def __init__(self, tools):
        self._tools = tools

    def list_tools(self):
        return [{"name": n} for n in self._tools]


class _StubSession(object):
    """No game needed. `has_patch=False` exercises the skip path this item's
    own offline half predicted - a real possible outcome, not an error mode."""

    def __init__(self, registered=True, has_patch=True):
        self._rb = _StubBridge(["jawa/harmony_patches"] if registered else [])
        self._has_patch = has_patch

    def call(self, tool, **p):
        if tool != "jawa/harmony_patches":
            return {"success": True}
        if p.get("methodName") == "CommonalityOfAnimal":
            n = 1 if self._has_patch else 0
            methods = [{"method": "CommonalityOfAnimal",
                        "postfixes": [{"owner": "some.mod.id", "patchAssembly": "SomeMod"}],
                        "prefixes": [], "transpilers": [], "finalizers": []}] if n else []
            return {"success": True, "typeName": "BiomeDef",
                    "methodName": "CommonalityOfAnimal", "methodCount": n, "methods": methods}
        if self._has_patch:
            return {"success": True, "typeName": "BiomeDef", "methodCount": 1,
                    "methods": [{"method": "CommonalityOfAnimal",
                                 "postfixes": [{"owner": "some.mod.id",
                                                "patchAssembly": "SomeMod"}],
                                 "prefixes": [], "transpilers": [], "finalizers": []}]}
        return {"success": True, "typeName": "BiomeDef", "methodCount": 0, "methods": []}


def selftest():
    """The good path AND the skip path this item predicted are both exercised,
    so a stub that always says yes cannot hide a broken assertion."""
    global RESULTS
    bad = 0
    for name, kw, want_failures in [
        ("patch found on CommonalityOfAnimal", dict(), 0),
        ("no patch on BiomeDef directly - real possible outcome", dict(has_patch=False), 0),
        ("tool not deployed yet", dict(registered=False), 0),
    ]:
        print("\n" + "=" * 60)
        print("SELFTEST: %s" % name)
        RESULTS = []
        s = _StubSession(**kw)
        have = {t.get("name") for t in s._rb.list_tools()}
        prove(s, have)
        failed = [n for n, v in RESULTS if v is False]
        if bool(failed) != bool(want_failures):
            print("  SELFTEST BUG: expected failures=%s, got %s" % (bool(want_failures), failed))
            bad += 1
        else:
            print("  scenario behaved as intended (%d failure(s))" % len(failed))
    print("\nSELFTEST %s" % ("FAILED" if bad else "OK"))
    return 1 if bad else 0


# -------------------------------------------------------------------- driver

def summarise():
    passed = [n for n, v in RESULTS if v is True]
    failed = [n for n, v in RESULTS if v is False]
    skipped = [n for n, v in RESULTS if v is None]
    print("\n%d passed, %d failed, %d skipped" % (len(passed), len(failed), len(skipped)))
    for n in failed:
        print("  FAILED: %s" % n)
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="run against a stub. No game, no socket.")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    from core import Session                                   # noqa: E402
    with Session() as s:
        have = {t.get("name") for t in s._rb.list_tools()}
        prove(s, have)
    return summarise()


if __name__ == "__main__":
    sys.exit(main())
