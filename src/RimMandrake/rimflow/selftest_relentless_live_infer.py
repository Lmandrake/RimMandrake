#!/usr/bin/env python3
"""selftest_relentless_live_infer.py -- every live-proof clause is a testq client, not only live-tier ones
(LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT; design/RimMandrake/lightspeed_2026-11-06.md section 4 row 2).

A clause with no live-tier line goes to SteveDesktop on a tier its mods name (mods__<tokens>: the build's mods and the
file's live-mods), so its verdict is a testq row and no Archmagi staging (no LLM, no bridge, no list swap) touches it.
What must hold, on selftest_relentless_game's fake world:
  routing: inferable() is false for a GREEN-FULL clause, an explicit-tier clause, a file with a live-site or live-without
  line; the round's candidates skip an inferred clause (INFERRED_TIER) only on a build whose modset_builder knows mods__
  names, and run it again once SteveDesktop gave it back (the fallback file, "*" for the whole build);
  the game phase: a plain item on such a build submits ONE testq job of profile tier:mods__..., stages nothing on
  Archmagi; its PASS is verified and lands as a runs.jsonl row (source testq); a FAIL returns the item; after
  steve_tries jobs that measured nothing the clause goes back to Archmagi (fallback written, staging resumes), never a
  hold; a build whose mods name no tier gives every clause back at once; a build older than the mods__ form, or
  steve_infer false, keeps the old Archmagi path; an explicit live-tier clause is still its own tier's;
  GameFx.infer_tier: a folded source is its composed mod, a repo folder its About.xml packageId, a packageId as written;
  a refused name names no tier; the fallback file round-trips through steve_fallback / steve_fell_back / fell_back;
  steve_deploy carries the live-mods trees (folders, never packageIds).
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_game as G            # noqa: E402
import relentless_live_round as LR     # noqa: E402
import relentless_names as N           # noqa: E402
import selftest_relentless_game as T   # noqa: E402
import selftest_relentless_live_tier as TT     # noqa: E402

FAILS = T.FAILS
ok = T.ok
TIER = "mods__mandrake_rm_flowworks"


class IW(T.GW):
    """GW plus the inference half of GameFx: a build that knows mods__ names, its tier, the fallback file."""

    def __init__(self, n=2):
        T.GW.__init__(self, n)
        self.infers, self.infer, self.fb = True, (TIER, None), {}

    def sha_infers(self, sha):
        return self.infers

    def infer_tier(self, item, sha):
        self.events.append("infer:%s" % item)
        return self.infer

    def steve_fell_back(self, item, sha):
        v = self.fb.get(item) or {}
        return list(v.get("clauses") or []) if v.get("sha") == sha else []

    def steve_fallback(self, item, sha, clauses, why):
        self.events.append("fallback:%s:%s" % (item, ",".join(clauses)))
        v = self.fb.setdefault(item, {"sha": sha, "clauses": []})
        v["clauses"] = sorted(set(v["clauses"]) | set(clauses))
        v["why"] = why


def rig(n=1):
    x = T.rig(n)
    x.w = IW(n)
    return x


def submits(x):
    return [e for e in x.w.events if e.startswith("testq_submit")]


def t_inferable():
    ok(LR.inferable(T.PROOF, "A2", "L1"), "a plain clause is inferable")
    ok(not LR.inferable(T.PROOF, "A2", "GREEN-FULL"), "a GREEN-FULL clause is the full list's, never inferred")
    ok(not LR.inferable(TT.MIXED, "A1", "L1") and LR.inferable(TT.MIXED, "A2", "L1"),
       "an explicit-tier clause stays its tier's; its plain sibling is inferable")
    site = "live-site A2: python.exe src/RimMandrake/Utils/live_site.py --calm\n" + T.PROOF
    ok(not LR.inferable(site, "A2", "L1"), "a file with a live-site line stays on Archmagi (its site is staged there)")
    ok(not LR.inferable("live-without: Pits\n" + T.PROOF, "A2", "L1"), "a live-without file stays on Archmagi")


def t_round_skips_inferred():
    it = {"id": "I0", "state": "built", "built_sha": "abc1234567", "outstanding": ["A1", "A2"],
          "criteria": [{"id": "A1", "level": "L1"}, {"id": "A2", "level": "L1"}]}
    root = tempfile.mkdtemp()
    try:
        LR._INFERS["abc1234567"] = True
        at = {"text": TT.MIXED}
        seams = dict(read_at=lambda i, s: at["text"], game_of=lambda i: ["A1", "A2"])
        steve = LR.steve_routes("/books", root, **seams)
        todo, counts = LR.candidates([it], lambda i: TT.MIXED, {}, 0, 0, None, steve)
        ok(not todo and counts.get(LR.EXACT_TIER) == 1 and counts.get(LR.INFERRED_TIER) == 1,
           "Archmagi's round runs neither: A1 its tier's, A2 inferred: %s %s" % (todo, counts))
        out = LR.steve_routes("/books", root, read_at=seams["read_at"], game_of=lambda i: ["A1"])
        todo, counts = LR.candidates([it], lambda i: TT.MIXED, {}, 0, 0, None, out)
        ok([t[1] for t in todo] == ["A2"], "a clause outside the item's game phase stays the round's (steve_sync "
           "never sends it): %s" % counts)
        at["text"] = "live-site A2: python.exe src/RimMandrake/Utils/live_site.py --calm\n" + TT.MIXED
        todo, counts = LR.candidates([it], lambda i: TT.MIXED, {}, 0, 0, None, steve)
        ok([t[1] for t in todo] == ["A2"], "judged on the file AT THE BUILD, as steve_sync reads it (a live-site "
           "there): %s" % counts)
        at["text"] = TT.MIXED
        ok(LR.in_game(root, "NOPE") == [], "no store state: no game clauses")
        os.makedirs(os.path.join(root, "store", "items", "G1"))
        for st, want in (({"status": "game", "game": {"phase": "prove", "clauses": ["A2"]}}, ["A2"]),
                         ({"status": "game", "game": {"phase": "stage", "clauses": ["A2"], "full": True}}, []),
                         ({"status": "built", "game": {"phase": "prove", "clauses": ["A2"]}}, [])):
            with open(os.path.join(root, "store", "items", "G1", "state.json"), "w") as f:
                json.dump(st, f)
            ok(LR.in_game(root, "G1") == want, "in_game %s -> %s" % (st, want))
        ok(LR.steve_routes("/books", root, enabled=False) is None, "steve_infer false: no predicate")
        LR._INFERS["old999"] = False
        old = dict(it, built_sha="old999")
        todo, counts = LR.candidates([old], lambda i: TT.MIXED, {}, 0, 0, None, steve)
        ok([t[1] for t in todo] == ["A2"], "a build older than the mods__ form keeps A2 on Archmagi: %s" % counts)
        ok(LR.sha_infers("/books", "") is False, "no sha infers nothing")
        os.makedirs(os.path.join(root, "live"))
        fx = G.GameFx()
        fx.base = root
        fx.steve_fallback("I0", "abc1234567", ["A2"], "measured nothing")
        steve = LR.steve_routes("/books", root, **seams)
        todo, counts = LR.candidates([it], lambda i: TT.MIXED, {}, 0, 0, None, steve)
        ok([t[1] for t in todo] == ["A2"], "a clause SteveDesktop gave back runs on Archmagi again: %s" % counts)
        ok(fx.steve_fell_back("I0", "abc1234567") == ["A2"] and fx.steve_fell_back("I0", "other") == [],
           "the fallback is per build")
        fx.steve_fallback("I1", "abc1234567", ["*"], "no tier")
        ok(LR.fell_back(LR.read_fallback(root), "I1", "abc1234567", "B7"), "'*' gives back every clause of that build")
    finally:
        shutil.rmtree(root)


def t_plain_item_goes_to_testq():
    x = rig()
    TT.in_stage(x, proof=T.PROOF)
    TT.step(x)
    ok(submits(x) == ["testq_submit:I0:%s:A2" % TIER], "the plain clause is one job on its inferred tier: %s" % x.w.events)
    ok("take" not in x.w.events and not TT.staged(x) and not x.w.enabled,
       "no bridge, no staging, no enable on Archmagi: %s" % x.w.events)
    job = x.w.testq[TT.only_job(x)]["job"]
    ok(job["profile"] == "tier:" + TIER and job["lane"] == "stevedesktop" and job["selector"] == {"proofs": ["A2"]},
       "profile tier:mods__..., lane stevedesktop: %s" % job)
    TT.finish_job(x, TT.only_job(x), {"A2": "PASS"})
    TT.step(x)
    rows = [r for r in x.w.rows if r.get("source") == G.STEVE]
    ok("verify:I0:A2:pass" in x.w.events and len(rows) == 1 and rows[0]["tier"] == TIER and rows[0]["outcome"] == "PASS",
       "the PASS is verified and lands as a testq row: %s" % rows)
    ok("take" not in x.w.events, "still nothing staged")
    x.done()


def t_fail_returns():
    x = rig()
    TT.in_stage(x, proof=T.PROOF)
    TT.step(x)
    TT.finish_job(x, TT.only_job(x), {"A2": "FAIL"}, detail="exit 1: A2 FAIL MOD: the comp is missing")
    TT.step(x)
    ok("verify:I0:A2:fail" in x.w.events and x.st("I0")["status"] != "game", "a FAIL returns the item")
    x.done()


def t_unmeasured_falls_back_not_held():
    x = rig()
    TT.in_stage(x, proof=T.PROOF)
    for _ in range(G.cfg(x.r).get("steve_tries", 3)):
        TT.step(x)
        TT.finish_job(x, TT.only_job(x), {"A2": "UNMEASURED"}, detail="exit 2: UNMEASURED: no save here")
    TT.step(x)
    st = x.st("I0")
    ok("fallback:I0:A2" in x.w.events, "after steve_tries empty jobs the clause goes back to Archmagi: %s" % x.w.events)
    ok(st["status"] == "game" and "held" not in str(st.get("hold") or ""), "never a hold: %s" % st.get("hold"))
    n = len(submits(x))
    TT.step(x)
    ok(len(submits(x)) == n and "take" in x.w.events, "no more jobs; Archmagi stages it: %s" % x.w.events[-6:])
    x.done()


def t_unnameable_gives_all_back():
    x = rig()
    x.w.infer = (None, "no packageId for Mystery")
    TT.in_stage(x, proof=T.PROOF)
    TT.step(x)
    ok("fallback:I0:*" in x.w.events and not submits(x) and "take" in x.w.events,
       "mods that name no tier: every clause back to Archmagi at once: %s" % x.w.events)
    x.done()


def t_old_build_and_switch_keep_archmagi():
    for why, set_ in (("old build", lambda x: setattr(x.w, "infers", False)),
                      ("steve_infer false", lambda x: setattr(x, "r", dict(x.r, game=dict(x.r.get("game") or {}, steve_infer=False))))):
        x = rig()
        set_(x)
        TT.in_stage(x, proof=T.PROOF)
        TT.step(x)
        ok(not submits(x) and "take" in x.w.events and TT.staged(x), "%s: Archmagi stages as before" % why)
        x.done()


def t_explicit_tier_still_its_own():
    x = rig()
    TT.in_stage(x, proof=TT.MIXED, clauses=("A1", "A2"))
    TT.step(x)
    ok(sorted(submits(x)) == ["testq_submit:I0:%s:A2" % TIER, "testq_submit:I0:ratchet_pilot:A1"],
       "A1 on its own tier, A2 on the inferred one: %s" % submits(x))
    ok("take" not in x.w.events, "and nothing staged on Archmagi")
    x.done()


class FakeRound(object):
    def __init__(self, mods, index):
        self._mods, self._index = mods, index

    def mods_of(self, sha):
        return list(self._mods)

    def names_index(self):
        return self._index


def t_infer_tier_names_packages():
    index = N.Index({"FlowWorks", "Graffiti", "RimMandrake.Biomes", "Stillsand"},
                    folded={"Stillsand": ("RimMandrake.Biomes", "Stillsand")}, packages=["7f.alienworlds"],
                    repo_pids={"mandrake.rm.flowworks": "FlowWorks", "mandrake.rut.graffiti": "Graffiti",
                               "mandrake.rm.biomes": "RimMandrake.Biomes"})

    class F(G.GameFx):
        books, base, text = "/books", "/base", "live-mods: Graffiti, Stillsand, 7f.alienworlds\n" + T.PROOF

        def _round_fx(self):
            return FakeRound(["FlowWorks"], index)

        def _mods_text(self, item, sha):
            return self.text

    f = F()
    tier, why = f.infer_tier("I0", "abc")
    ok(tier == "mods__7f_alienworlds__mandrake_rm_biomes__mandrake_rm_flowworks__mandrake_rut_graffiti" and not why,
       "build FlowWorks + live-mods Graffiti, folded Stillsand, a packageId -> %s %s" % (tier, why))
    f.text = "live-mods: NoSuchMod\n" + T.PROOF
    tier, why = f.infer_tier("I0", "abc")
    ok(tier is None and why, "a refused name names no tier: %s" % why)

    class D(F):
        text = "live-mods: Graffiti, 7f.alienworlds\nlive-deploy: Armoury\n" + T.PROOF

    import relentless_live_round as R
    orig = R.item_mods
    R.item_mods = lambda fx, i, s: ["FlowWorks"]
    try:
        got = D().steve_deploy("I0", "abc")
    finally:
        R.item_mods = orig
    ok(got == ["FlowWorks", "Graffiti", "Armoury"], "steve_deploy: the build's mods, then live-mods/deploy trees, no "
       "packageId: %s" % got)


if __name__ == "__main__":
    t_inferable()
    t_round_skips_inferred()
    t_plain_item_goes_to_testq()
    t_fail_returns()
    t_unmeasured_falls_back_not_held()
    t_unnameable_gives_all_back()
    t_old_build_and_switch_keep_archmagi()
    t_explicit_tier_still_its_own()
    t_infer_tier_names_packages()
    print("selftest_relentless_live_infer: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
