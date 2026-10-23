# Delegation policy — agents decide nearly everything, art included

*Adopted 2026-10-22 on the owner's word (item `DELEGATION_POLICY_BUILD_AGENTS_ASK_AGENTS`). Binds BENCH,
FOUNDRY and every subagent. Model tiers are `infrastructure/agents/Agent_Policy.md`'s, never restated here.*

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
**What it does NOT change:** his standing rulings. Delegation acts *inside* them, never over them (§2.4).

## 1. What agents now decide alone

Everything not on the §2 list. That includes, and is not limited to:

| class (the `<class>` in the log line) | examples |
|---|---|
| `technical` | harness thresholds, test-site choice, refactors inside a mod, MOD/SITE/HARNESS calls with evidence, tool design |
| `scope` | splitting, narrowing, ordering, closing and dropping items; which of several valid routes to build |
| `design` | mechanics detail, numbers (already PROVISIONAL-marked per FOUNDRY.md), roster rows inside a biome sheet's open questions, prose and labels a player reads |
| `art` | keep/redo of a render, which candidate goes live, regen briefs, queueing regens (only for NONE/PLACEHOLDER/DONOR destinations, plus the art-eval pipeline's redraws of kept art under §2.3's exception) |
| `cosmetic` | gene, head, eye, skin, hair, body, texPath and tint changes; face-part art; building looks; water and terrain tints |

Taste calls (`design`, `art`, `cosmetic`) go through a judge first (§4). Technical and scope calls are taken
by the acting seat on its own evidence, as before.

**With timeouts.** When he is present, a seat MAY still offer a delegable call on a card if it is cheap for
him — but it never waits on the answer. Unanswered by the time the work needs it (or at the end of his sitting),
the call is taken as a delegated decision and logged as one. ⛔ An unanswered card is never his approval.

## 2. What still needs him — the short list

Each line is reserved by a ruling of his that says so; nothing else is.

1. **North-star bars.** The `## north star` sections are hash-bound and his: agents write and approve the
   functional scripts, *"the owner's hash-bound `## north star` bars stay his"* (CHARTER, How we debug;
   CLAUDE.md, North-star validation, 2026-09-17). The 2026-09-16 carve-out stands: a model's `must read` YES
   greens a line (Agent_Policy.md). Criteria tagged **L4** are his by definition (FOUNDRY.md).
2. **Irreversible acts on work that is not ours.** Force-push, `reset --hard` over work you did not make,
   deleting work not yours — *"only with the owner's word"* (CHARTER, expensive list #5). Re-freezing the
   frozen `official` dump — *"only the owner re-freezes it"* (CHARTER, Instruments). Purging a picture from the
   art store — `art.py purge` takes `--owner-said` only.
3. **Replacing art he KEPT** — with ONE exception. *"Why are we replacing items for which I know I have good
   versions?"* (2026-10-19). `art.py install --reason` refuses over an owner-kept picture; a delegated call never
   works around that refusal. **Exception (owner card 2026-10-23 06:42, *"Yes, but show me after"*):** the art-eval
   pipeline (`skills/rimworld-art-evaluation`) MAY redraw a kept picture when its verdict is regen (Opus really
   bad, or a weak one GPT did not strong-accept), only with a revert record, installing through
   `art.py install --by-card "Kept art judged really bad: may the pipeline redraw it on its own? → Yes, but show me after"`; every such swap appears on the next shadow sheet flagged
   *replaced your kept art* with a one-click revert to the kept version through the art ledger. Any other
   replacement of kept art is still his.
4. **Overturning or reinterpreting a standing ruling of his** — CLAUDE.md, `standing_rulings.md`,
   `biome_rulings.md`, a canon entry's `## ruling` (*"The ruling is his, never yours"*, `AGENT_BRIEF.md`), and
   deliberate departures from canon. Applying a ruling to a case it does not name is delegated; changing what
   it says is not.
5. **Outward and paid acts.** Spending money, publishing outside our private repos and artifacts (a Steam
   Workshop upload, a public post), and the acts his global instructions call his: an interactive login, a
   GUI he must look at, a purchase (`~/.claude/CLAUDE.md`, "RUN IT YOURSELF" ③).
6. **Presence-bound acts his rulings name.** Live flight tests of a flyer — *"do not do live testing of flyers
   without a human present"* (CLAUDE.md, flight); `./bridge bench|foundry|free` and `broadcast.py` are his.

A reserved call is asked as a card (the `question-card` skill) or filed `--for OWNER --kind decision`, and the
work waits on it. It never times out into a decision.

## 3. How a delegated decision is recorded

- **Ledger:** `rimflow note <ID> --why "delegated: <class>" --text "<the decision; judge verdict file if any>"`
  (or the same `--why` on `close`/`drop`/`supersede`/`file`). ⛔ Never `--owner-said`, `--by-card` or
  `--per-ruling` — those name his authority; this ruling authorises the *class*, the call itself is ours.
- **Commit:** a body line `Delegated: <class> — <one-line decision>` so `git log --grep '^Delegated:'` finds it.
- **Art install:** `art.py install … --why "delegated: art <verdict file>"` (`--why` grants no owner authority: the mechanical guards apply, so it never displaces a kept, purged or rejected picture; `--reason` takes only mechanical tags and refuses this text). ⚠️ Today the pre-push `art_guard` refuses an install whose only reason is `--why` (MEASURED 2026-10-23); script-made art also passes `--reason script:<repo path of the writer>` (`ART_GUARD_FIX_REFUSES_THE_DELEGATE`).
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
6. **A judge's miss is a brief defect.** When he overturns a KEEP, the reason becomes a new line in the brief
   (with his words as its source), the same day.

## 5. How he audits and overturns cheaply — the daily digest

Once a day, at his first sitting (BENCH) or with the nightly run (FOUNDRY), the seat writes
`Transient/delegated_digest_<YYYY-MM-DD>.md` and gives him its full native path: one line per delegated call
since the last digest — item, class, decision, judge verdict file — newest first, art grouped by subject. Built
from the ledger (`why` starting `delegated:`) and `git log --grep '^Delegated:'`; a zero-line digest is checked
against a known delegated event before it is reported as zero.

To overturn: he says so, in any words; the seat records his words with `--owner-said` on the item, undoes the
call, and adds the reason to the brief (§4.6). Silence on a digest line is not his approval — it stays logged as
delegated.

## 6. What reaches him — the review "from a much stronger place"

He reviews a **curated, pre-judged set**, never raw output (and nothing reaches him unread — `standing_rulings.md`
§Nothing reaches the owner unread, owner 2026-10-22; a sheet carries its `<stem>.prereview.json`): only judge-KEEP art (with the verdict lines beside
each picture), plus rows flagged *split* (two UNSUREs), *stuck* (three REDO rounds), *kept-but-flagged* or *replaced your kept art* (§2.3).
It reaches him the ways he already reviews — a review sheet that is truly new and passes its gates
(`rimworld-review-sheets`), a phone set (full-res alone, true scale, facings), or an in-game review map for
visuals judged by looking — never a sheet of REDOs. Delegated art may be installed before his review; biome art
never blocks (`standing_rulings.md`, 2026-10-18). His ruling there is recorded as his (`--owner-said`) and
makes the picture owner-kept.
