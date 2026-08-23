# OWNER_DECISIONS.md — the single list of what is waiting on the owner

> 📦 **Swept 2026-08-23 by REP, under this file's own rule.** Four settled ruling sections
> and the two Open rows that declared themselves CLOSED moved to
> `infrastructure/state/OWNER_DECISIONS_ARCHIVE.md`. **185 lines → 109**, against a budget of
> 120 whose stated rationale is that growth past it means the list is not being drained.
> ⚠️ **Three rows are genuinely open — 8, 9 and 12** — and two of those are `[v2]`.

> ✅ **THE MAP IS ADOPTED, AND AUTHORING IS OPEN AGAIN — owner, 2026-08-22.** Verbatim, after
> looking at the four-globe sheet: *"That world, upon examination, really isn't very bad at all…
> we're thinking of trying to adopt it."* ⇒ **Ash'karr as it stands IS the v1 planet**, and work
> on it continues: continuity repairs, landmarks, named places, settlements, terrain detail.
>
> ⛔ **This REPLACES the 2026-08-21 freeze banner**, which said the opposite and is struck. The
> freeze lasted one evening and did its job — it stopped a redraft nobody wanted.
> ⚠️ **What did NOT come back:** re-running `ashkarr_paint.py` to regenerate the bundle, the
> reference-match harness (`refmatch.py` stays cancelled), and worldgen, which is out of every
> version and always was. **The map is edited DIRECTLY, one map, in place** — that is the whole
> method, per `the_one_map.md`.
> 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` stands as history, not as a plan.
> Ruling: `WORLD_ADOPTED_AUTHORING_OPEN_1` · supersedes `WORLD_FROZEN_RETHINK_PLANET_1`.


> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


_Every question only the owner can answer lives here, and nowhere else. Scattered
across five queues and a dozen design docs they rot: two items were re-raised
after already being answered._

## The rule

- **A seat with a question for the owner adds a row here AND says so in its
  report.** One or the other is not enough — the row is the durable record, the
  report is what gets it seen.
- **Do not file a row a seat could answer itself.** "Which of us owns this" and
  "is this on-brand" are owner calls; "how do I build it" is not.
- **This file is swept** and each answered row deleted. Answered rows do not
  stay here struck through.
- ⚠️ **Re-read the source before adding a row.** An already-answered item listed
  here is worse than no list at all — it spends a decision cycle on nothing.
- **Budget: 120 lines.** A list of owner decisions that grows past that is not
  being drained, which is the failure this file exists to prevent.

---

## Open

> ✅ **ALL THREE OPEN ROWS ANSWERED 2026-08-23 — the list is empty.** Rows 8, 9 and 12 were
> put to the owner and ruled in one pass, and under this file's own rule an answered row is
> removed rather than left struck through. Each is now an item carrying his words:
>
> | was | ruling | item |
> |---|---|---|
> | **12** droid raids | ~5 lines of Harmony — the only route that loses nothing | `DROID_RAIDS_HARMONY_RELATIONS_1` |
> | **8** dinosaurs | **v1**, not v2 — the [v2] tag predated his fauna ruling. Folds into the fauna pass | `DINOSAUR_IMAGE_REVIEW_SHEET_1` |
> | **9** xenotypes | **PURE SW** — cut the non-canon, do not reflavor it | `XENOTYPE_ROSTER_PURE_SW_1` |
>
> ⚠️ **An empty Open table is the state this file is supposed to be in.** A row here means a
> seat is blocked on him; if it stays empty, that is the list working, not the list dying.


| # | the ask | why the owner and not a seat | blocked until answered | source |
|---|---|---|---|---|

---

## Checked and NOT listed — so nobody re-adds them

- **#10 the discarded measuring world — CLOSED 2026-08-19, the question dissolved.**
  All in-game worldgen hooks were stripped; the route is the live bridge. There is no sea
  to measure and nothing to iterate, so the owner is not owed this call. ⚠️ A quicktest
  world is still fine to test the IMPORT tools against — that use was never in question.
- **#12 remains OPEN** and is the only technical one of the three: droid raids are broken
  by our own patch and the three routes are a trade between tending, EMP and shipping a
  broken antagonist.
- **#11 `StrandedQuest`, enable or leave inert — CLOSED 2026-08-14 WITHOUT the
  owner, correctly.** v1 gets **one** `QuestScriptDef` that fires and resolves, and **row 3 already
  fills it** (*The Claim*, seen live). ⇒ `StrandedQuest` stays deployed-but-inert
  and is `[v2]`. 📌 **This row should never have reached the owner.** It looked
  like a scope call and was answerable from the scope document — the test in this
  file's own rule. Do not re-file it.

- **#5, the TODO retirement, and #7, the keep-or-delete set** — both ruled by the
  owner 2026-08-13 and **executed the same hour**. Do not re-raise either. The seat
  queues took the four survivors.

- **A hook guarding `git commit` without a pathspec** — described as needing the
  owner because it is config. **Already built and live:**
  `.claude/hooks/block_blanket_git_stage.py` blocks the naked-commit form. What
  remains is confirming the guard matches the intent, which is DECIDE's, not
  yours (`infrastructure/state/queue/DECIDE.md`).
- **Where the seat identity files live** — answered by `infrastructure/agents/` existing.
- **The mines, the Warcasket retune, `MissingArtFixes`** — all ruled.
- **Galactic Empire leader title, "Sector governor" vs `Sector Director`** — a retired seat
  owned design and could rule it. Not escalated.
