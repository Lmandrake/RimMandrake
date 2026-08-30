## spec
Phase 2 prep per `design/Jawa/pawn_flavor_design.md` § Open questions, item 6: a
lore-prose pass over ThoughtDef/MentalBreakDef/xenotype-title flavor, for the
**COMMON tier only** — 497 rows (403 ThoughtDef + 22 MentalBreakDef + 72
XenotypeDef), reachable in ordinary play on the live 585-mod set per the
existing census's own tiering logic. OCCASIONAL (1,262 + 11 + 13) and DORMANT
(502 + 11 + 54) are deliberately deferred — a future item, not dropped; the
item's own title says "prep," not "ship."

**Census** (input, sanity-checked against RimSage and the live mod XML on
disk, reused as-is — no re-run needed):
`infrastructure/output/pawn_flavor_phase2_census.csv` (1,784 rows, all tiers).
Methodology record (not directly re-runnable — session-scratch input paths):
`infrastructure/output/pawn_flavor_phase2_census_gen.py`.

**Drafted prose** for all 497 COMMON rows:
`infrastructure/output/pawn_flavor_phase2_prose_draft.json`, keyed
`"<defType>::<defName>"`. Field shape follows the real def, not a uniform
template: ThoughtDef/XenotypeDef carry `label`+`description`; MentalBreakDef
carries `label`+`beginLetter`+`recoveryMessage` because that prose actually
lives on the linked MentalStateDef, not on MentalBreakDef itself (confirmed by
reading both def types live via RimSage) — two MentalBreakDefs
(`Catatonic`, `RunWild`) have no linked MentalStateDef and carry only a label.

Drafting method: split across 9 parallel Sonnet subagents (7 ThoughtDef
batches grouped by mod, 2 XenotypeDef batches), each given the same style
guide (desert-scavenger-Jawa register per `pawn_flavor_design.md`'s
established voice, mechanical meaning and mood direction/intensity preserved
exactly, first-person present-tense for thought descriptions, Star Wars proper
nouns used sparingly, xenotypes re-voiced as the clan's own practical bestiary
entries rather than Wookieepedia paraphrase). The 22 MentalBreakDef rows were
hand-drafted directly against the real MentalStateDef XML (RimSage
`get_def_details`), not delegated. A similarity check (`difflib` against the
original vanilla text) flagged 15 rows that came back too structurally close
to the source; those were rewritten by hand afterward.

**Review sheet** (new, parallel to the Phase 1 sheet — does not touch it):
- Generator: `src/RimMandrake/Utils/gen_pawn_flavor_phase2_register.py`
- Template: `src/RimMandrake/Utils/pawn_flavor_phase2_register_template.html`
- Sheet: `design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.html`
- Decisions: `design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.decisions.json`

Every row shows current (vanilla/mod) prose next to the drafted proposal,
grouped by def type then by mod with sticky group labels (per the
`review-sheets` skill), pre-filled **approve** so the owner only disagrees.
Decisions: `approve` (ship the draft) / `tweak` (right idea, note holds the
fix) / `reject` (redo later) / `skip` (not reviewed — ships as drafted, same
effect as approve but distinguishable in the export). The generator refuses to
regenerate over a decisions file that carries `savedAt` without
`--i-know-this-overwrites-the-owners-decisions` (tested: confirmed it refuses).
Auto-saves to the linked file via File System Access API, debounced ~1s, with
the same truncation guard and per-row touched-merge as the Phase 1 sheet.

## verify
1. Open the sheet, confirm 497 rows load, confirm the three def-type filters
   and per-mod grouping work.
2. Link the decisions file (path is in the sheet's header, copy-button
   present) and confirm a decision + note round-trips after a reload.
3. When the owner is done: `git diff` the decisions file should show real
   content (not byte-identical to the prefill) before treating the pass as
   reviewed — see `review-sheets` skill §11.

## criteria
- [ ] Owner has worked through the 497 rows (approve/tweak/reject/skip on each,
      or explicitly left as the approve default).
- [ ] Any `tweak`/`reject` notes are folded back into
      `pawn_flavor_phase2_prose_draft.json` and the flavor actually shipped
      into XML — that's a follow-on item, not this one; this item's scope is
      the sheet + drafts, not the deploy.
- [ ] OCCASIONAL/DORMANT tiers get their own follow-on item when the owner
      wants them (not filed yet — flagging here so it isn't lost).

## Watch out
🔴 **This item does NOT close on `rimflow close`** — like the Phase 1 sheet,
it's an owner-facing decision artifact that stays open until worked through.
Progress is tracked via `rimflow note`, not by closing the queue item.

⚠️ **The XenotypeDef COMMON set is not "the vanilla xenotypes"** — it's
almost entirely (70 of 72) this campaign's own shipped 71-species Star Wars
roster (`RimMandrake - Star Wars Races` + `Jawa_Xeno_Gamorrean`), which
already carry real Star Wars descriptions (Wookieepedia-style). The prose work
there is re-voicing an encyclopedia paragraph into the Jawa clan's own
practical bestiary register, not writing Star Wars flavor from scratch — do
not mistake "already Star Wars" for "already done."

⚠️ **RimSage's def index does not cover `RimMandrake - Star Wars Races`
XenotypeDefs at all** — `search_defs`/`get_def_details` return not-found for
every one of the 70 (confirmed: `MandrakeJawa`, `RimMandrakeBothan`, etc. all
missed). The census's `currentLabelOrText` for that mod was verified instead
by reading the live game-folder XML directly
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimMandrake_StarWarsRaces\Defs\XenotypeDefs\RimMandrakeXenotypes.xml`)
— 69 xenotypes there, matching the census exactly. Don't trust RimSage's
silence on this mod as "doesn't exist."

🔑 **`.tmp_census_summary.json` was moved to `Transient/` (not committed)** —
it's a one-time human-readable tier-count sanity check, fully re-derivable
from the committed CSV; nothing cites it as a source.
