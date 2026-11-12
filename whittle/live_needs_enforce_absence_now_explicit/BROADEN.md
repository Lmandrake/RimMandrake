# BROADEN: a second model on what a real user would try

Asked 2026-11-12 ~06:20Z: GPT (`gpt-6.1-sol`, through `src/RimMandrake/Utils/gpt_consult.py --codex wsl`, job
consult-20261111-221909-251288-a8f4b3).

## The question (abridged; the full text went in as the prompt)

I gave it the item (the gate infers needs from CLI args, script home, fixture saves, single-owner types/defNames and
About.xml closure, and adds the sure ones; `live-without:` blocks inference, refuses a conflicting load and splits
batches; absence checks give no need; a stale index only warns), the three statement bullets, and what I had tested:
the replay (17/20, 0 wrong), the negative control against each PASS run's recorded live list (24 held, 0 without, 26
unrecorded, of which 14 were shown held by the proof itself and 12 could not be told), the week-after count (0/209 vs
15/365), the migration (215 proofs, 0 conflicts, absence wording read by hand), and 110 selftests. I asked what a new,
experienced, adversarial or messy-case user would try that I had not, which one or two to try offline now, and whether
my reading of "zero additions" (a mod the passing run did not already hold) is honest or a dodge.

## The answer (key points)

- The biggest risk is calling an association a sure need: a single-owner type, a script's home or a save's modIds
  identify a mod without proving this proof needs it.
- Try 1: a proof that provably passes without a referenced mod (an OR branch, or a clause that can pass without it).
  Does the gate still add it?
- Try 2: **dependency closure × `live-without` × a stale index.** A proof needs `acme.feature` (it hard-depends on
  `acme.lib`) and is `live-without: acme.lib`. It should be refused before the slot. With P and Q (needs acme.lib) in
  one batch, they must split. A stale index must add neither the feature nor its dependency. An explicitly named mod
  must still refuse.
- On "zero additions": measuring against the passing run's actual load is honest, but it is not established. With 12
  unresolved, calling the criterion satisfied would be a dodge; report the narrower finding and let the owner rule. The
  production count is useful, but 0/209 comes from ~23 h of running against 4 observed baseline days, and calendar time
  with the pipeline off adds no exposure.

## What I tried and found

**Try 2 found a real defect, now fixed.** I ran the exact shapes through `relentless_names.needs` on a synthetic index
before the fix:

```
P fresh    | add [('AcmeFeature', 'proof_defname')] | conflict [] | refusal None
named dep  | add [] | conflict [] | refusal None          (live-mods: AcmeFeature, live-without: AcmeLib)
build dep  | add [] | conflict [] | refusal None          (the build's own mod hangs on the live-without mod)
```

All three loads went through. Staging enables a mod together with its About.xml dependencies, so the load would hold
the very mod the proof is meant to run without, or come out broken. And a stale (warning-level) need still pulled its
transitive dependencies in as sure `closure` additions. After the fix (`needs()` now checks the planned load's whole
dependency closure, `dep_closure`; a closure entry whose parent is only a warning is itself only a warning; `batch_gap`
splits on dependencies too):

```
P fresh          | refusal live-without AcmeLib (a hard dependency of AcmeFeature), but the planned load holds it ...
named            | refusal live-without AcmeLib (a hard dependency of AcmeFeature) ...
build            | refusal live-without AcmeLib (a hard dependency of AcmeFeature) ...
transitive stale | add [] | warn [AcmeFeature (index stale), acme.base (the mod that needs it, AcmeFeature, is itself only a warning)]
transitive fresh | add [AcmeFeature, acme.base (closure)]
```

These are now selftests (`t_dependency_conflict` in `src/RimMandrake/rimflow/selftest_relentless_needs.py`, 8 checks
including both batch orders). The migration over the 215 real proofs still finds 0 conflicts, and the replay is
unchanged (`evidence/replay_enforce.txt`, `evidence/migrate.txt`).

**Try 1 is a real case in the data, and it is a limit of the contract rather than a bug.** HORRORS_RAIDING_FACTION_1's
2026-11-03 A3 PASS (dayside: no lair) could pass without AshkarrWeatherSuite. The gate adds it because the same proof
file's A2 needs it (the census R1 repair). The gate plans per proof file, not per clause, as the spec has it. This
entry stays "cannot tell" in `evidence/negative_control_unrecorded.md`.

**On the reading of criterion 2 I agree with the second model.** The measured result is 0 additions shown absent and
38 of 50 shown held. 12 cannot be told because the pre-landing runs recorded no running list. That is not "zero
additions" shown, and DONE.md says so. From this change on, every admitted run row carries its running load
(`env.running`), so this gap cannot recur.
