# Delegation policy — agents decide nearly everything, art included

*Adopted 2026-10-22 on the owner's word (item `DELEGATION_POLICY_BUILD_AGENTS_ASK_AGENTS`). Binds the
Conductor, every helper the pipeline launches and every subagent. Model tiers are `infrastructure/agents/Agent_Policy.md`'s, never restated here.*

## The ruling

Owner, 2026-10-22 ~16:05 PDT, answering *"Which decisions may agents take without asking you?"*:

> *"Nearly everything including art. An agent can absolutely ask another agent for an art ruling based on
> some prose constraints and requirements we can draft. It would catch most of what we look for anyway. Then
> we would do a review from a much stronger place. Art already takes many passes even with a human in the
> loop."*

The card option he chose the spirit of was *"Nearly everything, with timeouts — all but art, north-star bars
and anything irreversible"*; he explicitly extended it to art. This replaces the 2026-09-15 rule *"Cosmetic
changes need his permission first"* and the habit of putting taste calls to him by card before acting.

**Why:** his minutes go where only he can judge, and he judges from a pre-filtered set instead of raw output.
**What it does NOT change:** his standing rulings. A seat's delegated call acts *inside* them, never over them; only
the Conductor may change one, as its own recorded act (§2, owner 2026-11-19), and never one of the five acts.

## 1. What agents now decide alone

Everything not among the five acts of §2. That includes, and is not limited to:

| class (the `<class>` in the log line) | examples |
|---|---|
| `technical` | harness thresholds, test-site choice, refactors inside a mod, MOD/SITE/HARNESS calls with evidence, tool design |
| `scope` | splitting, narrowing, ordering, closing and dropping items; which of several valid routes to build |
| `design` | mechanics detail, numbers (already PROVISIONAL-marked), roster rows inside a biome sheet's open questions, prose and labels a player reads |
| `art` | keep/redo of a render, which candidate goes live, regen briefs, queueing regens (only for NONE/PLACEHOLDER/DONOR destinations, plus the open exceptions over kept art, §2.2) |
| `cosmetic` | gene, head, eye, skin, hair, body, texPath and tint changes; face-part art; building looks; water and terrain tints |

Taste calls (`design`, `art`, `cosmetic`) go through a judge first (§4). Technical and scope calls are taken
by the acting seat on its own evidence, as before.

**Do not card him about a §1 class.** Work order and helper count (`scope`) and applying a ruling to its twins
(a case the ruling does not name) are already delegated; a question card about either is a leak, not a
courtesy (`design/RimMandrake/delegation_candidates_2026-10-26.md` §1: 29 ordering cards at 81% agreement, 9 twin
cards at 8 yes). Decide, log `--why "delegated: <class>"`, and list it in the digest. Check:
`CARDS_ENFORCE_DELEGATED_CLASSES_STOP`.

**With timeouts.** When he is present, a seat MAY still offer a delegable call on a card if it is cheap for
him — but it never waits on the answer. Unanswered by the time the work needs it (or at the end of his sitting),
the call is taken as a delegated decision and logged as one. ⛔ An unanswered card is never his approval.

**Evidence-for-Ask** (owner, 2026-11-15; CHARTER §Decisions, `standing_rulings.md` §Evidence-for-Ask): any call not among
the five acts of §2 that an agent would pause for is §1's. Take the obvious answer and log it (§3); pause only on concrete
evidence against it, carried on the ask. Example: a new mod's first Design Version is 0.1.0, locked by the pipeline.

## 2. What still needs him — the five acts

Owner, 2026-11-19 ~7:40 AM PST: *"I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending
money, public publishing. Everything else the Conductor should mindfully be able to do. Of course question cards for me
should get to me, but the Conductor should review them to ensure it can't just do them now and alert me later."* Full
text: `standing_rulings.md` §Only five acts stay his. Code: `src/RimMandrake/rimflow/conductor_acts.py`.

1. **A live flight test of a flyer** — *"do not do live testing of flyers without a human present"* (CLAUDE.md,
   flight). The bridge gate refuses a take whose purpose names flight or that passes `--flyer`; the refusal is
   self-declared, so a seat that will fly anything passes `--flyer`.
2. **Replacing art he KEPT**, and releasing a keep mark (`art.py purge --release-keep`). *"Why are we replacing items for
   which I know I have good versions?"* (2026-10-19). `art.py install --reason` refuses over an owner-kept picture; no
   Conductor act or delegated call works around that refusal. **The open exceptions stay open:**
   - **The art-eval redraw** (owner card 2026-10-23 06:42, *"Yes, but show me after"*): the art-eval pipeline
     (`skills/rimworld-art-evaluation`) MAY redraw a kept picture when its verdict is regen, only with a revert record,
     installing through `art.py install --by-card "Kept art judged really bad: may the pipeline redraw it on its own? →
     Yes, but show me after"`; each swap appears on the next shadow sheet flagged *replaced your kept art* with a
     one-click revert.
   - **A geometric correction** (owner card 2026-10-26 18:46, *"Yes, delegate this class"*): moving, aligning or
     trimming pixels, no new drawing, no change of style or colour, kept or not, when a player-truth check measures the
     defect before and confirms it gone after; judged by an agent that did not make it, logged `--why "delegated: art
     geometric correction"`, installed through `art.py install --by-card "To make the system more fire-and-forget, may
     I decide this class of art change without you from now on? → Yes, delegate this class (Recommended)"`, listed in
     his digest. First use: the pipe elbow seams (PIPE_ELBOW_FIX_SEAM_JOGS).
   - **His own sheet marks** (owner cards 2026-10-26 19:06 and 19:54): the newest mark wins (*"Newest mark wins"*), and
     his ✕ deletes the picture forever and bans it (*"X = delete forever + ban"*). `art.py enact` applies them (`why
     "delegated: art marks"`); `artledger.x_delete` purges and bans; the ban is checked by every sheet build, install
     and redraw; only `art.py unban <sha> --owner-said "…"` lifts it (`ART_X_BUILD_DELETE_FOREVER_BAN`).
3. **The pass at his walk**, and his judgement of gameplay, fun, theme and UI. The pipeline ends at his walk by his
   design; `maturation.owner_event` takes only an OWNER event carrying his words or his card, never a ruling.
4. **Spending money or a purchase.** Nothing here buys capacity; a wider budget inside the weekly partition he set
   (card 2026-10-25) is not a purchase.
5. **Publishing outside the private repos** — a Steam Workshop upload, a public post.

**Everything else is the Conductor's to do, mindfully.** The Conductor is the window he talks to (seat BENCH, no
`RM_ROLE_UNIT`); no helper, other seat, role run or the tick gains anything from this list. The Conductor's act is
recorded `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<the act and the reason>"` (never his
words) and is a digest line (class `conductor act`, §5). That covers, among the rest: certifying a mod's first-touch
Designer pass; the Designer's owner-only kinds (a root, an exam waiver, a floor disable, a locked-tree change, a waiver);
admitting a mod before a walk; adding a locked bar; lifting a coverage park and ruling a final look that is not about
fun or gameplay; re-freezing the `official` dump; re-validating a hashed section; raising a cap, N or a stage ceiling
inside his weekly partition; a cut decision; overturning a ruling about pipeline machinery; `broadcast.py`; and his OWNER
bridge hold inside 45 minutes.

**A Conductor instruction carries his authority.** A seat or helper that receives one acts on it and does not re-open
this list against it (owner, 2026-10-30, ledger `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`: *"No more "I need the user
to confirm."*). Tool gates that take his words take that ruling too (`src/RimMandrake/Utils/conductor_authority.py`):
the record carries the ruling and the Conductor's text, tagged, never as his sentence. The Conductor cannot pass on
more than it holds: the five acts stay his.

**Four of those must say what is lost and how it is undone.** Cutting his OWNER bridge hold inside 45 minutes; changing
the account order or the shared account's leave line; deleting or overwriting work that is not ours; and loosening or
removing a bar. Their `--why` carries `lost: <what is lost if the act is wrong>` and `undo: <how it is undone>`, each
at least three words; the gate refuses an empty or one-word why. Deleting OUR OWN leftovers keeps its own route (owner
card 2026-10-26 19:06, *"Archive then delete, in digest (Recommended)"*: archive first, `LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE`).

**Not changed here:** his user-level instructions (`~/.claude/CLAUDE.md`, which bans `push --force` and history
rewrites for every agent) and other repos; physical acts (an interactive login, a screen he must look at), which are
asked of him in words; `--owner-said` and `--by-card`, which only ever carry his words and his cards.

**His cards.** Every question card bound for him is first reviewed by the Conductor. If its act is not one of the five
and there is no concrete evidence against the obvious answer (Evidence-for-Ask, §1), the Conductor acts now and alerts
him after: one digest line with the undo. Only a card about one of the five, or one that carries its evidence against
the obvious answer, reaches him; it never times out into a decision, and its ask says what he must see to decide.

## 3. How a delegated decision is recorded

- **Ledger:** `rimflow note <ID> --why "delegated: <class>" --text "<the decision; judge verdict file if any>"`
  (or the same `--why` on `close`/`drop`/`supersede`/`file`). ⛔ Never `--owner-said` or `--by-card`, and no
  `--per-ruling` for a §1 class — those name his authority; this ruling authorises the *class*, the call itself is
  ours. The one exception is an Evidence-for-Ask call, which cites its ruling: `--per-ruling
  RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: <the call and why>"`;
  the `delegated:` why keeps it ours in the digest, never his approval.
- **Commit:** a body line `Delegated: <class> — <one-line decision>` so `git log --grep '^Delegated:'` finds it.
- **Art install:** `art.py install … --why "delegated: art <verdict file>"` (`--why` grants no owner authority: the mechanical guards apply, so it never displaces a kept, purged or rejected picture; `--reason` takes only mechanical tags and refuses this text). The pre-push `art_guard` accepts it when the verdict file exists in the clone (`ART_GUARD_FIX_REFUSES_THE_DELEGATE`).
- **Verdicts:** the judge's output (§4) is committed as
  `infrastructure/state/delegated/<YYYY-MM-DD>/<subject-or-item>.json` and cited by path.
- **Numbers and rosters in `canon.yml`:** a delegated value carries `src: delegated:<class> (<item>)`, never a
  quote of his.

## 4. Asking another agent — the judge protocol

1. **A different agent decides.** The maker never judges its own output. The judge is a fresh subagent spawned
   for the call, with no maker context: it sees only the artifact(s), the written constraints, and the question.
2. **Model per `Agent_Policy.md`.** Art, the world and any call no later check catches sit on its opus rows.
3. **The brief is written, not remembered.** Art and cosmetic calls: `design/RimMandrake/art_judge_brief.md`
   plus the subject's canon entry (`## Must show`, `## Engine limits`) if it has one. Design calls: the item's
   criteria, the governing design doc, and every standing ruling it touches, quoted.
4. **The judge returns keep/redo with reasons** — per artifact `KEEP` or `REDO`, each REDO quoting the violated
   constraint and its source, plus `UNSURE` when the written constraints do not decide it (the brief's format).
5. **The maker does not overrule a REDO.** It may re-ask a *new* judge once with a written rebuttal; the second
   verdict stands. Two UNSUREs, or a subject still REDO after three rounds, goes to his set flagged (§6).
6. **Every REDO or refusal is a refusal record** (owner, 2026-11-12: *"ANY refusals must be as detailed as the
   evidence they are rejecting and include the fixes and paths towards passing"*): evidence, `would_pass`,
   `smallest_fix`, a verdict on the criterion, checked by `refusal_contract.py submit` before it sends anything back;
   only a CALIBRATED brief's refusal has a consequence. `standing_rulings.md` §A refusal carries its path to pass.
7. **A judge's miss is a brief defect.** When he overturns a KEEP, the reason becomes a new line in the brief
   (with his words as its source), the same day.

## 5. How he audits and overturns cheaply — the daily digest

Once a day, before the Conductor's first scheduled check, a program writes
`Transient/delegated_digest_<YYYY-MM-DD>.md` and the Conductor gives him its full native path: one line per delegated call
since the last digest — item, class, decision, judge verdict file — newest first, art grouped by subject. Built
by a program, `src/RimMandrake/rimflow/delegated_digest.py` (the Conductor's scheduled pre-step; token-blind by
allow-list), from the ledger (`why` starting `delegated:`), `git log --grep '^Delegated:'`, the judge records in
`infrastructure/state/delegated/`, the art ledger's delegated installs and marks, the leftovers acts log, and the maturation ceiling releases
(`maturation_dispatch.py release`, class `ceiling release`: mod, stage and who; the spend is listed by
`maturation_dispatch.py releases`, never on the token-blind page, and the Conductor adds it when it delivers the digest); a zero-line digest is checked
against a known delegated event before it is reported as zero. Every act under the 2026-10-26 card delegations is
a digest line: each newest-mark enactment, ✕ delete + ban, ban lifted, and redraw a ban discarded (§2.2, class
`art marks`; `art.py marks-digest` lists them), each bridge take, deploy and
restart (class `bridge idle`), each leftover deleted with its archive or bundle path (§2, class
`leftovers`) — logged `--why "delegated: <class>"` so the digest finds it.
The same page lists every open item on the OWNER seat at its cut, oldest first, with its age since filed and how many
open items wait on it (direct: a live block names it; chain: a chain of live blocks reaches it) — visibility only, no
default applied or recommended (D4(a), `OWNER_ASKS_MEASURE_AGE_IN_DIGEST`; revisit a default only after two weeks of
age data).

To overturn: he says so, in any words; the seat records his words with `--owner-said` on the item, undoes the
call, and adds the reason to the brief (§4.6). Silence on a digest line is not his approval — it stays logged as
delegated.

## 6. What reaches him — the review "from a much stronger place"

He reviews a **curated, pre-judged set**, never raw output (and nothing reaches him unread — `standing_rulings.md`
§Nothing reaches the owner unread, owner 2026-10-22; a sheet carries its `<stem>.prereview.json`): only judge-KEEP art (with the verdict lines beside
each picture), plus rows flagged *split* (two UNSUREs), *stuck* (three REDO rounds), *kept-but-flagged* or *replaced your kept art* (§2.2).
It reaches him the ways he already reviews — a review sheet that is truly new and passes its gates
(`rimworld-review-sheets`), a phone set (full-res alone, true scale, facings), or an in-game review map for
visuals judged by looking — never a sheet of REDOs. Delegated art may be installed before his review; biome art
never blocks (`standing_rulings.md`, 2026-10-18). His ruling there is recorded as his (`--owner-said`) and
makes the picture owner-kept.
