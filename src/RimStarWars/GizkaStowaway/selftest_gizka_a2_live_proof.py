"""Selftest for a2_live_proof.py (GIZKA_STOWAWAY_UNMEASURED_ROWS_1 A2's live judge). Offline, no game.

    python3 src/RimStarWars/GizkaStowaway/selftest_gizka_a2_live_proof.py

A good live result + load + registry passes; each way a result could describe something other than this mod, now, on
its tier, all PASS (the blind checker's probe: every row PASS with validity=invalid and a zeroed mod_hash), fails.
Then a mutation pass: every `out.append(` failure clause in the judge, replaced by `pass`, must turn some case wrong.
"""
import copy
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "a2_live_proof.py")

H = "ab" * 32
TIER = ["ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "brrainz.harmony", "mandrake.rm.gimmesomeslack",
        "mandrake.rm.biomes", "mandrake.rsw.swbestiary", "mandrake.rsw.gizkastowaway", "jawa.bridge"]
OUT = r"D:\ClaudeWork\rimmandrake\scratch\gizka_A2.json"


def load(src=None):
    m = types.ModuleType("a2_live_proof")
    m.__file__ = SRC
    exec(compile(src if src is not None else open(SRC, encoding="utf-8").read(), SRC, "exec"), m.__dict__)
    return m


def good(m):
    ids = list(m.REQUIRED_BARS) + ["filler.row_%02d" % i for i in range(52 - len(m.REQUIRED_BARS))]
    res = {"mod": "GizkaStowaway", "mode": "live", "partial": False, "chains_skipped": [], "all_green": True,
           "mod_hash": H, "bars": [{"id": i, "status": "PASS", "evidence": "x"} for i in ids],
           "components": [{"chain": i.split(".")[0], "name": i.split(".")[1], "verdict": "PASS",
                           "freshness": "fresh", "validity": None} for i in ids],
           "preflight": [{"name": "game_loaded", "status": "PASS", "required": True},
                         {"name": "optional_note", "status": "UNMEASURED", "required": False}]}
    entry = {"hash": H, "status": "DRAFT-CHECKLIST", "refused": None,
             "components": {"counts": {"PASS": 52}, "not_ok": []},
             "source": {"verb": "northstar_driver run", "result": OUT}}
    return {"res": res, "current_hash": H, "running": [p.upper() if i == 0 else p for i, p in enumerate(TIER)],
            "tier_pids": list(TIER), "tier_problems": [], "entry": entry,
            "result_path": "/mnt/d/ClaudeWork/rimmandrake/scratch/gizka_A2.json", "expected_status": "DRAFT-CHECKLIST"}


def _bars(r, f):
    for b in r["res"]["bars"]:
        f(b)


def cases(m):
    """[(name, kwargs, should_pass)]"""
    out = []

    def case(name, mutate, ok=False):
        k = good(m)
        mutate(k)
        out.append((name, k, ok))

    case("good DRAFT-CHECKLIST", lambda k: None, True)
    case("good GREEN", lambda k: (k["entry"].update(status="GREEN"), k.update(expected_status="GREEN")), True)
    case("good PENDING-OWNER-REVIEW", lambda k: (k["entry"].update(status="PENDING-OWNER-REVIEW"),
                                                k.update(expected_status="PENDING-OWNER-REVIEW")), True)
    case("posix registry source", lambda k: k["entry"]["source"].update(
        result="/mnt/d/ClaudeWork/rimmandrake/scratch/gizka_A2.json"), True)
    # the blind checker's probe (11b2d6483d): every row PASS, validity=invalid, mod_hash all zeros
    case("checker probe: invalid rows + zero hash",
         lambda k: (_bars(k, lambda b: b.update(validity="invalid")), k["res"].update(mod_hash="0" * 64)))
    case("bar validity invalid only", lambda k: k["res"]["bars"][3].update(validity="invalid"))
    case("component validity invalid only", lambda k: k["res"]["components"][5].update(validity="invalid"))
    case("component reused", lambda k: k["res"]["components"][5].update(freshness="reused@old.json"))
    case("bar reused", lambda k: k["res"]["bars"][7].update(freshness="reused@old.json"))
    case("zero mod_hash only", lambda k: k["res"].update(mod_hash="0" * 64))
    case("no mod_hash", lambda k: k["res"].pop("mod_hash"))
    case("current hash unread", lambda k: (k.update(current_hash=None), k["res"].update(mod_hash=None),
                                           k["entry"].update(hash=None)))
    case("mock mode", lambda k: k["res"].update(mode="mock"))
    case("other mod", lambda k: k["res"].update(mod="FlowWorks"))
    case("refused", lambda k: k["res"].update(refused="dirty site"))
    case("aborted", lambda k: k["res"].update(aborted="colony died"))
    case("partial", lambda k: k["res"].update(partial=True))
    case("partial missing", lambda k: k["res"].pop("partial"))
    case("chain skipped", lambda k: k["res"].update(chains_skipped=["chewing_live"]))
    case("all_green false", lambda k: k["res"].update(all_green=False))
    case("one UNMEASURED", lambda k: k["res"]["bars"][20].update(status="UNMEASURED"))
    case("one FAIL", lambda k: k["res"]["bars"][0].update(status="FAIL"))
    case("one SKIP", lambda k: k["res"]["bars"][30].update(status="SKIP"))
    case("49 bars", lambda k: k["res"].update(bars=k["res"]["bars"][:49]))   # required rows lead the list
    case("required row absent", lambda k: k["res"]["bars"][9].update(id="filler.renamed"))
    case("required preflight FAIL", lambda k: k["res"]["preflight"][0].update(status="FAIL"))
    case("running extra mod", lambda k: k["running"].append("someone.fullist.mod"))
    case("running missing mod", lambda k: k["running"].remove("mandrake.rsw.swbestiary"))
    case("running unread", lambda k: k.update(running=None))
    case("tier unresolved", lambda k: k.update(tier_pids=None))
    case("tier refused", lambda k: k.update(tier_problems=["forbidden donor in closure"]))
    case("no registry entry", lambda k: k.update(entry=None))
    case("registry RED", lambda k: k["entry"].update(status="RED"))
    case("registry REFUSED", lambda k: k["entry"].update(status="REFUSED"))
    case("registry status not the earned one", lambda k: k.update(expected_status="GREEN"))
    case("registry refused field", lambda k: k["entry"].update(refused="3 bars UNBUILT"))
    case("registry stale hash", lambda k: k["entry"].update(hash="cd" * 32))
    case("registry from another result", lambda k: k["entry"]["source"].update(result="Transient/northstar/old.json"))
    case("registry no source", lambda k: k["entry"].pop("source"))
    case("registry not_ok", lambda k: k["entry"]["components"].update(not_ok=["chewing_live.site_ready"]))
    case("registry no components", lambda k: k["entry"].pop("components"))
    return out


def run(m):
    """-> list of wrong cases (name, should_pass, got_fails)."""
    wrong = []
    for name, k, ok in cases(m):
        fails = m.judge(**copy.deepcopy(k))
        if (not fails) != ok:
            wrong.append((name, ok, fails))
    return wrong


def mutants(src):
    """Each failure clause of the three judges replaced by `pass`, one at a time."""
    lines = src.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if re.match(r"^\s+out\.append\(", ln) or re.match(r"^\s+return \[\"", ln):
            ind = re.match(r"^(\s*)", ln).group(1)
            # a multi-line call: swallow continuation lines until parens balance
            j, depth = i, 0
            while True:
                depth += lines[j].count("(") + lines[j].count("[") - lines[j].count(")") - lines[j].count("]")
                if depth <= 0:
                    break
                j += 1
            repl = ind + ("pass" if "append" in ln else "return []")
            mut = lines[:i] + [repl] + [""] * (j - i) + lines[j + 1:]
            out.append((i + 1, "\n".join(mut)))
    return out


def main():
    m = load()
    wrong = run(m)
    for name, ok, fails in wrong:
        print("WRONG %-40s expected %s, got %s" % (name, "PASS" if ok else "FAIL", fails[:3]))
    print("cases: %d, wrong: %d" % (len(cases(m)), len(wrong)))
    src = open(SRC, encoding="utf-8").read()
    muts = mutants(src)
    survivors = [ln for ln, s in muts if not run(load(s))]
    print("mutation pass: %d failure clauses removed one at a time, %d survived%s"
          % (len(muts), len(survivors), (": lines %s" % survivors) if survivors else ""))
    want = src.count("out.append(") + src.count('return ["')     # an independent count of the clauses
    sane = len(muts) == want and want >= 20
    if not sane:
        print("mutation sanity: mutator found %d clauses, the source holds %d (want equal, >= 20)" % (len(muts), want))
    ok = not wrong and not survivors and sane
    print("selftest_gizka_a2_live_proof: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
