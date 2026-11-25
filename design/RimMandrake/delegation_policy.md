# Delegation policy — agents decide nearly everything, art included

*The owner gave his word for this policy on 2026-10-22 (item `DELEGATION_POLICY_BUILD_AGENTS_ASK_AGENTS`). The policy
binds the Conductor, every helper that the pipeline launches, and every subagent. The model tiers are in
`infrastructure/agents/Agent_Policy.md`. This file never restates them.*

## The ruling

Owner, 2026-10-22 ~16:05 PDT, answering *"Which decisions may agents take without asking you?"*:

> *"Nearly everything including art. An agent can absolutely ask another agent for an art ruling based on
> some prose constraints and requirements we can draft. It would catch most of what we look for anyway. Then
> we would do a review from a much stronger place. Art already takes many passes even with a human in the
> loop."*

He took the spirit of one card option, *"Nearly everything, with timeouts — all but art, north-star bars and anything
irreversible"*; he explicitly extended it to art. This replaces the 2026-09-15 rule *"Cosmetic changes need his
permission first"*. The ruling also replaces the habit of putting taste calls to him on a card before an agent acts.

**Why:** his minutes go where only he can judge. He judges from a pre-filtered set, not from raw output.

**What it does NOT change:** his standing rulings. A delegated call of a seat acts *inside* his standing rulings, never
over them. Only the Conductor may change a standing ruling, as its own recorded act (§2, owner 2026-11-19). The
Conductor never changes one of the five acts.

## 1. What agents now decide alone

Agents decide every call that is not one of the five acts of §2. The table below names some classes and examples.
The table is not a complete list: other calls and other classes are also the agents' to decide.

| class (the `<class>` in the log line) | examples |
|---|---|
| `technical` | harness thresholds, test-site choice, refactors inside a mod, MOD/SITE/HARNESS calls with evidence, tool design |
| `scope` | splitting, narrowing, ordering, closing and dropping items; which of several valid routes to build |
| `design` | mechanics detail, numbers (each one already marked PROVISIONAL), roster rows inside the open questions of a biome sheet, prose and labels that a player reads |
| `art` | keep/redo of a render, which candidate goes live, regen briefs, queueing regens (only for NONE/PLACEHOLDER/DONOR destinations, plus the open exceptions over kept art, §2.2) |
| `cosmetic` | gene, head, eye, skin, hair, body, texPath and tint changes; face-part art; building looks; water and terrain tints |

A destination is a texture path. `src/RimMandrake/Utils/art/regen_eligibility.py` confirms the state of each
destination. NONE means no picture. PLACEHOLDER means a placeholder picture. DONOR means a borrowed (donor) picture.

Each taste call (`design`, `art`, `cosmetic`) goes through a judge first (§4). The acting seat takes technical and scope calls
on its own evidence, as before.

**Do not card him about a §1 class.** Two kinds of call are already delegated:

- work order and helper count (`scope`);
- applying a ruling to its twins. A twin is a case that the ruling does not name.

A question card about either kind is a leak, not a courtesy. The evidence is in
`design/RimMandrake/delegation_candidates_2026-10-26.md` §1: 29 ordering cards at 81% agreement, and 9 twin cards at 8
yes. Decide the call. Log it with `--why "delegated: <class>"`. List it in the digest (§5). The check on cards came from
item `CARDS_ENFORCE_DELEGATED_CLASSES_STOP` (the hook `.claude/hooks/block_delegated_cards.py`).

**With timeouts.** When he is present, a seat may still offer a delegable call on a card, if the card is cheap for him.
The seat never waits on the answer. The card can have no answer when the work needs the call, or at the end of his
sitting. Then the seat takes the call as a delegated decision and logs it as one. ⛔ An unanswered card is never his
approval.

**Evidence-for-Ask** (owner, 2026-11-15; CHARTER §Decisions, `standing_rulings.md` §Evidence-for-Ask): an agent can want
to pause for a call that is not one of the five acts of §2. That call belongs to §1. Take the obvious answer and log it
(§3). Pause only on concrete evidence against the obvious answer, and carry that evidence on the ask. Example: the
pipeline locks the first Design Version of a new mod at 0.1.0.

## 2. What still needs him — the five acts

Owner, 2026-11-19 ~7:40 AM PST: *"I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending
money, public publishing. Everything else the Conductor should mindfully be able to do. Of course question cards for me
should get to me, but the Conductor should review them to ensure it can't just do them now and alert me later."* Full
text: `standing_rulings.md` §Only five acts stay his. Code: `src/RimMandrake/rimflow/conductor_acts.py`.

1. **A live flight test of a flyer** — *"do not do live testing of flyers without a human present"*
   (`standing_rulings.md` §If it flies in the fiction, it flies in the game). The bridge gate refuses a take whose
   purpose names flight, or a take that passes `--flyer`. The gate knows only what the seat declares. So a seat that
   will fly anything passes `--flyer`.
2. **Replacing art he KEPT**, and releasing a keep mark (`art.py purge --release-keep`). *"Why are we replacing items for
   which I know I have good versions?"* (2026-10-19). `art.py install --reason` refuses to install over a picture that
   the owner kept. No Conductor act and no delegated call works around that refusal. **The open exceptions stay open:**
   - **The art-eval redraw** (owner card 2026-10-23 06:42, *"Yes, but show me after"*). The art-eval pipeline
     (`skills/rimworld-art-evaluation`) may redraw a kept picture when its verdict is regen. The redraw needs a revert
     record. The redraw installs through `art.py install --by-card "Kept art judged really bad: may the pipeline redraw
     it on its own? → Yes, but show me after"`. Each swap shows on the next shadow sheet, flagged *replaced your kept
     art*, with a one-click revert. A shadow sheet is the review sheet that
     `src/RimMandrake/Utils/art_eval/shadow.py` builds after the pipeline decides, for his quick look.
   - **A geometric correction** (owner card 2026-10-26 18:46, *"Yes, delegate this class"*). A geometric correction
     moves, aligns or trims pixels, on kept art or on other art. The correction makes no new drawing and no change of style or
     colour. A player-truth check must measure the defect before the correction and confirm it gone after. A
     player-truth is a plain property that a player would expect. A player-truth is written as a check on game logic
     or geometry. That check is swept over the whole input space offline
     (`design/RimMandrake/player_truth_testing_pilot_2026-10-26.md`). An agent that did not make
     the correction judges it. Log it `--why "delegated: art geometric correction"`. Install it through `art.py install
     --by-card "To make the system more fire-and-forget, may I decide this class of art change without you from now
     on? → Yes, delegate this class (Recommended)"`. List it in his digest. First use: the pipe elbow seams
     (PIPE_ELBOW_FIX_SEAM_JOGS).
   - **His own sheet marks** (owner cards 2026-10-26 19:06 and 19:54). The newest mark wins (*"Newest mark wins"*).
     His ✕ deletes the picture forever and bans it (*"X = delete forever + ban"*). `art.py enact` applies the marks
     (`why "delegated: art marks"`). `artledger.x_delete` purges and bans. Every sheet build, install and redraw checks
     the ban. Only `art.py unban <sha> --owner-said "…"` lifts a ban (`ART_X_BUILD_DELETE_FOREVER_BAN`).
3. **The pass at his walk**, and his judgement of gameplay, fun, theme and UI. By his design, the pipeline ends at his
   walk. `maturation.owner_event` takes only an OWNER event that carries his words or his card, never a ruling.
4. **Spending money or a purchase.** Nothing here buys capacity. A wider budget inside the account lines
   (the account plan, `./acct plan`) is not a purchase.
5. **Publishing outside the private repos** — a Steam Workshop upload, a public post.

**Everything else is the Conductor's to do, mindfully.** The Conductor is the window that he talks to (seat BENCH, no
`RM_ROLE_UNIT`). No helper, other seat, role run or tick gains anything from this list. Record a Conductor act with
`--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<the act and the reason>"`, never as his
words. Each Conductor act is a digest line (class `conductor act`, §5). Among the rest, the Conductor does these acts:

- certify the first-touch Designer pass of a mod;
- the owner-only kinds of the Designer: a root, an exam waiver, a floor disable, a locked-tree change, a waiver (each
  kind is defined in `src/RimMandrake/rimflow/roles/designer.md` §Authority and provenance);
- admit a mod before a walk;
- add a locked bar;
- lift a coverage park (the stop of a concept at the coverage judge's second refusal while he is away, `designer.md`),
  and rule a final look that is not about fun or gameplay;
- re-freeze the `official` dump;
- re-validate a hashed section;
- raise a cap, N (the helper slots of a seat, `slot_allocator.py`) or a stage ceiling (the spend limit of one stage) inside the account lines. No
  capacity is kept for his evenings (`standing_rulings.md` §Account and capacity budget);
- move a change to a mod's Polish list, and decide whether a change goes in the current Design Version or the next
  (owner, card 2026-11-23, `standing_rulings.md` §Mod Design Versions);
- a cut decision;
- overturn a ruling about pipeline machinery;
- `broadcast.py`;
- cut his OWNER bridge hold inside 45 minutes.

**A Conductor instruction carries his authority.** A seat or helper that receives a Conductor instruction acts on it.
The receiver does not re-open this list against the instruction (owner, 2026-10-30, ledger
`CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`: *"No more "I need the user to confirm."*). Tool gates that take his words
also take that ruling (`src/RimMandrake/Utils/conductor_authority.py`). The record carries the ruling and the text of
the Conductor, tagged, never as his sentence. The Conductor cannot pass on more than it holds: the five acts stay his.

**Four of those must say what is lost and how it is undone.** The four acts are these:

- a cut of his OWNER bridge hold inside 45 minutes;
- a change to the account order or to the leave line of the shared account;
- a deletion or overwrite of work that is not ours;
- a looser bar, or a bar removed.

The `--why` of each of these acts carries `lost: <what is lost if the act is wrong>` and `undo: <how it is undone>`.
Each part has at least three words. The gate refuses an empty or one-word why. A deletion of our own leftovers keeps its own
route (owner card 2026-10-26 19:06, *"Archive then delete, in digest (Recommended)"*): archive first,
`LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE`.

**Not changed here:**

- his user-level instructions (`~/.claude/CLAUDE.md`, which bans `push --force` and history rewrites for every agent),
  and other repos;
- physical acts (an interactive login, a screen that he must look at). Ask him for these acts in words;
- `--owner-said` and `--by-card`. These two flags only ever carry his words and his cards.

**His cards.** The Conductor first reviews every question card for him. The Conductor checks two things: the act of
the card, and any concrete evidence against the obvious answer (Evidence-for-Ask, §1). If the act is not one of the
five, and no such evidence exists, the Conductor acts now. Then the Conductor alerts him after, with one digest line
that holds the undo. Only two kinds of card reach him:

- a card about one of the five acts;
- a card that carries its evidence against the obvious answer.

Such a card never times out into a decision. Its ask says what he must see to decide.

## 3. How a delegated decision is recorded

- **Ledger:** `rimflow note <ID> --why "delegated: <class>" --text "<the decision; judge verdict file if any>"`. The
  same `--why` also works on `close`/`drop`/`supersede`/`file`. ⛔ Never use `--owner-said` or `--by-card`. Use no
  `--per-ruling` for a §1 class. Those flags name his authority. This ruling authorises the *class*; the call itself is
  ours. The one exception is an Evidence-for-Ask call, which cites its ruling: `--per-ruling
  RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: <the call and why>"`.
  The `delegated:` why keeps the call ours in the digest, never his approval.
- **Commit:** put a body line `Delegated: <class> — <one-line decision>` in the commit. Then
  `git log --grep '^Delegated:'` finds it.
- **Art install:** `art.py install … --why "delegated: art <verdict file>"`. The `--why` grants no owner authority. So
  the mechanical guards apply, and the install never displaces a kept, purged or rejected picture. `--reason` takes
  only mechanical tags and refuses this text. The pre-push `art_guard` accepts the install when the verdict file exists
  in the clone (`ART_GUARD_FIX_REFUSES_THE_DELEGATE`).
- **Verdicts:** commit the output of the judge (§4) as
  `infrastructure/state/delegated/<YYYY-MM-DD>/<subject-or-item>.json`. Cite the verdict by path.
- **Numbers and rosters in `canon.yml`:** a delegated value carries `src: delegated:<class> (<item>)`, never a
  quote of his.

## 4. Asking another agent — the judge protocol

1. **A different agent decides.** The maker never judges its own output. The judge is a fresh subagent, spawned for
   the call, with no maker context. The judge sees only the artifact(s), the written constraints and the question.
2. **Model per `Agent_Policy.md`.** Art, the world, and any call that no later check catches use the opus rows of
   `Agent_Policy.md`.
3. **The brief is written, not remembered.** For art and cosmetic calls, the brief is
   `design/RimMandrake/art_judge_brief.md`. If the subject has a canon entry, add it (`## Must show`, `## Engine
   limits`). For design calls, the brief holds the criteria of the item and the design doc that governs it. The brief
   also quotes every standing ruling that the call touches.
4. **The judge returns keep/redo with reasons** — `KEEP` or `REDO` for each artifact. Each REDO quotes the violated
   constraint and its source. The judge returns `UNSURE` when the written constraints do not decide an artifact (the
   format of the brief).
5. **The maker does not overrule a REDO.** The maker may ask a *new* judge once more, with a written rebuttal. The
   second verdict stands. Two UNSUREs, or a subject still REDO after three rounds, go to his set, flagged (§6).
6. **Every REDO or refusal is a refusal record** (owner, 2026-11-12: *"ANY refusals must be as detailed as the
   evidence they are rejecting and include the fixes and paths towards passing"*). A refusal record holds the evidence,
   `would_pass`, `smallest_fix` and a verdict on the criterion. The record is checked by `refusal_contract.py submit`
   before it sends anything back. Only the refusal of a CALIBRATED brief has a consequence. Full text:
   `standing_rulings.md` §A refusal carries its path to pass.
7. **A judge's miss is a brief defect.** When he overturns a KEEP, his reason becomes a new line in the brief, the same
   day. The line has his words as its source.

Item 7 was item 6 before 2026-11-12. On that date, the refusal-record item became item 6. A citation of §4.6 from before that date
means item 7.

## 5. How he audits and overturns cheaply — the daily digest

Once a day, before the first scheduled check of the Conductor, a program writes
`Transient/delegated_digest_<YYYY-MM-DD>.md`. The Conductor gives him its full native path. The digest has one line for
each delegated call since the last digest: item, class, decision and judge verdict file. The newest line comes first.
The digest groups art by subject.

The program is `src/RimMandrake/rimflow/delegated_digest.py`, the scheduled pre-step of the Conductor. The page is
token-blind by allow-list. Only fields on an allow-list reach the page. The page refuses a money word. The program
builds the digest from these sources:

- the ledger (`why` starting `delegated:`);
- `git log --grep '^Delegated:'`;
- the judge records in `infrastructure/state/delegated/`;
- the delegated installs and marks of the art ledger;
- the leftovers acts log;
- the maturation ceiling releases (`maturation_dispatch.py release`, class `ceiling release`: mod, stage and who).
  `maturation_dispatch.py releases` lists the spend. The spend is never on the token-blind page. The Conductor adds the
  spend when it delivers the digest.

Before anyone reports a zero-line digest as zero, check the digest against a known delegated event.

Every act under the card delegations of 2026-10-26 is a digest line:

- each newest-mark enactment, ✕ delete + ban, ban lifted, and redraw that a ban discarded (§2.2, class `art marks`).
  `art.py marks-digest` lists them;
- each bridge take, deploy and restart (class `bridge idle`);
- each leftover deleted, with its archive or bundle path (§2, class `leftovers`).

Log each of these acts with `--why "delegated: <class>"`, so that the digest finds it.

The same page lists every open item on the OWNER seat at its cut, oldest first. The cut is the moment of the page's
snapshot. Each item shows its age since filing, and how many open items wait on it. An item waits directly when a live block names
it. An item waits by chain when a chain of live blocks reaches it. This list is visibility only. The page applies or
recommends no default (D4(a), `OWNER_ASKS_MEASURE_AGE_IN_DIGEST`). D4(a) is option (a) of decision D4 in
`design/RimMandrake/dispatcher_risk_response_2026-10-29.md`. The Conductor ruled it on 2026-11-01. Revisit a
default only after two weeks of age data.

To overturn a call, he says so, in any words. Then the seat does three things:

- record his words with `--owner-said` on the item;
- undo the call;
- add the reason to the brief (§4.7).

Silence on a digest line is not his approval: the call stays logged as delegated.

## 6. What reaches him — the review "from a much stronger place"

He reviews a **curated, pre-judged set**, never raw output. Nothing reaches him unread (`standing_rulings.md`
§Nothing reaches the owner unread, owner 2026-10-22). A sheet carries its `<stem>.prereview.json`. The set holds only
these:

- judge-KEEP art, with the verdict lines beside each picture;
- rows flagged *split* (two UNSUREs), *stuck* (three REDO rounds), *kept-but-flagged* or *replaced your kept art*
  (§2.2).

The set reaches him in the ways that he already reviews:

- a review sheet that is truly new and passes its gates (`rimworld-review-sheets`);
- a phone set (full-res alone, true scale, facings);
- an in-game review map, for visuals that a look decides.

Never send him a sheet of REDOs. A seat may install delegated art before his review. Biome art never blocks
(`standing_rulings.md`, 2026-10-18). Record his ruling at the review as his (`--owner-said`). That ruling makes the
picture owner-kept.
