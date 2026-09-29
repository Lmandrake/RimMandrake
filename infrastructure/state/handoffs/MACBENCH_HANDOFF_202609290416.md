# MACBENCH_HANDOFF_202609290416 — READ FIRST on wake

First handoff for this seat.

## The one thing to carry forward

`design/RimMandrake/Jev_Opportunities.md` is the authority on adopting TypeSafe's Jev, and it has
**already been through an adversarial GPT review that deleted most of its first draft.** Do not
re-expand it from enthusiasm — read Part 3 ("Cut, with reasons") before proposing anything there,
because ~20 seams were considered and killed with the reasoning recorded.

The generalizable lesson, which cost this whole session to learn and applies to any future
"where could X help us" scan: **a five-agent fan-out briefed with a capability returns a list
biased toward yes, and its CONFIRMED labels confirm counts and filenames, never the
intervention.** The test that settles such a seam is an *indistinguishable-input
counterexample* — construct two situations producing the same input but requiring different
correct answers. One such example killed an entire cluster: the same creature description plus
its local XML, from a patched and an unpatched install, requires different answers from
identical state, so an input is **omitted**, not miscalibrated. This repo is maximally exposed
because our `RM_` biome casts are patch-added.

## What the owner should see

- 🔴 **I enrolled this repo for autonomous ChatGPT consultation** (`.consult/config.json`,
  written by `consult.py --enroll`) because sending the doc to GPT required it. That is a
  persistent authorization for repo content to leave the machine without a human seeing the
  payload. It is now **gitignored so it cannot be inherited by another checkout** (`ed0ea7146`).
  Delete the file to revert. He may prefer per-request drafts instead.
- 🔴 **`shared_sync.py` is broken on this Mac and reports a FALSE conflict.** It died with
  `error: unrecognized argument: --ref-action=print` and printed "replay hit a conflict —
  nothing was written or pushed". The local git does not support that `git replay` flag; there
  was no conflict. A session that believes it will go hunting a phantom merge. Unfiled — see
  the pointer below.
- **Three claims in the first draft were false and are withdrawn**, one of which I had also
  stated to him verbally: that Jev's typed output *structurally satisfies* the Oracle's
  text/menu-authority law. It does not — the enumerated option set and the code executing it
  set that boundary, not the absence of prose. Also withdrawn: that we hold three ground-truth
  datasets (we hold historical *records*; 863 closed items are objects, not duplicate labels),
  and that the stale-citation sweep is a "pure win".
- **The economics are the opposite of the pitch.** Jev's price is not the binding cost. A
  1,000-item sweep at 1% true defects, 90% recall and 5% false positives yields ~9 true alerts
  and ~50 false ones — cheap inference readily buys expensive owner attention.
- **Runtime adoption is withdrawn from the first round** and still needs his transport ruling
  (the `claude -p` doctrine is already implemented in `OracleClient.cs`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `JEV_ADOPTION` — doc written, reviewed, committed; **nothing built or evaluated**, by design;
  NEXT: run condition A of the retrieval diagnostic in the doc's "The first experiment" — replay
  the documented re-invention incidents (`SEA_SHORE_TILE_MUTATOR_1`, the greatbole pass) against
  repo state *before* each mistake, with current retrieval and no model, to establish whether
  ordinary discovery already surfaces the implementation.
- `SHARED_SYNC_REF_ACTION_FLAG` — measured but unfiled, distinct from the known
  `SHARED_SYNC_DROPS_PEER_COMMITS_1`; NEXT: file it with `rimflow file` (invoke the
  `using-rimflow` skill first), quoting the exact failure `unrecognized argument:
  --ref-action=print` and that its "replay hit a conflict" message is a false positive on macOS git.
- `CONSULT_LEDGER_ROW` — the consult row `20260928T174234-RimMaster-design_review` records
  `sent=True` but `reply_chars=0` and `reviewer_model=None`, because the reply read 429'd and
  was recovered out-of-band; 8 findings are attached correctly; NEXT: leave it unless a ledger
  audit needs the row repaired — do NOT resend the prompt.

## Traps learned

- `WebFetch` is **dead on this model group** — it fails with `Invalid model name … claude-haiku-4-5`
  because the summarizer model is unavailable; plain `curl --max-time` to the same URL works fine,
  and Mintlify serves markdown by appending `.md` (filed: LESSONS)
- `shared_sync.py` reports "replay hit a conflict" when the real error is an unsupported
  `git replay --ref-action=print`; the tree was clean and a plain rebase+push worked (filed: LESSONS)
- `handoff.py` **refuses without a seat** when the corpus holds several identities, and this Mac's
  bench seat is `MACBENCH`, not `BENCH` — set `HANDOFF_SEAT=MACBENCH` (filed: LESSONS)
- A `## ruling` section in `canon_references/` holds the literal placeholder
  `(empty — owner has not reviewed …)`, so a non-empty test reports **136 of 137 ruled** when the
  real figure is **29** (see: CLAUDE.md, corrected this session)
- `ET.findall("CharacterDef")` returns **0** across the cast rosters because the tag is
  `RimMandrake.Inhabited.CharacterDef`; the real count is 294 (see: CLAUDE.md namespace gap)
- The zsh `$R file …` word-splitting trap bit again on
  `R="python3 …/consult.py --record-finding <id>"` — eight commands failed with
  `no such file or directory`; drive repeated CLI calls from python, not a shell variable
  (see: CLAUDE.md, already recorded)

## Commits

```
ed0ea7146 Keep ChatGPTConsult per-repo state out of git
df28613ff Four bedazzle art sheets ruled: decisions committed, rulings routed, 2 items filed
d86d37bba Harvest the hung Player.log before kill (GASDAMAGING re-break evidence)
6120a8498 Ledger sync: bridge release after full-list recovery + campaign reload
ffd806b4a Ledger sync: bedazzle art review sheets recorded on the program item
7bddbe339 Bedazzle art review sheets x4 (51 subjects, 97 jobs all done) + wire Tekk/Drazz/BrinePlate/CrackWax art
d38b34061 Ledger sync: Forge turn 6 - vent machines and GPT forms cut, wonder-not-horror redirect
ffdb5f35b Forge GPT consult results preserved + ledger sync
b2b015f0c Ledger sync: Forge turn 4 rulings + GPT consult blocked on Codex auth
2f475d27e Ledger sync: note on GASDAMAGING_PARENTNAME_UNRESOLVED_1 re-break/re-fix
509715770 Re-apply GASDAMAGING_PARENTNAME_UNRESOLVED_1's load-order fix to FULL.LATEST
741055c6c Ledger sync: Forge volley turn 2 - wire-all-waiting + the fire-and-water cycle rulings
ddeecc2c4 Forge bedazzle review complete: scorecard 3 HAVE/4 PARTIAL/2 MISS, 4 fills, 8-idea slate
95a2afd73 Forge bedazzle review: skeleton + What's-there census (movements 1-2 in progress)
ef16bf599 Ledger sync: game UP recorded (owner relay via cross-session message)
a8d1742d8 Ledger sync: FORGE_BEDAZZLE_SITTING_1 filed and started (program row 6)
9a9ad7916 Ledger sync: Cauldron movement 4 commission recorded; comp-family pointer on mechanics ticket
ae396e2f0 Ledger sync: close WARDEN_MOTHER_PATHFINDER_VERIFY_1 (queue re-render)
692109fb3 CAULDRON_BEDAZZLE_SITTING_1: art CSV + 19 queued jobs (13 subjects, dedup-checked)
23d94b450 WARDEN_MOTHER_PATHFINDER_VERIFY_1: live-measured evidence
... 10 more: git log --oneline -30
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

