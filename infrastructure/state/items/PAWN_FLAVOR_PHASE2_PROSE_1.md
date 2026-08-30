## spec
Phase 2 prep per `design/Jawa/pawn_flavor_design.md` § Open questions, item 6: a
lore-prose pass over ThoughtDef/MentalBreakDef/xenotype-title flavor.
**Now covers COMMON + OCCASIONAL — 1,783 rows** (403+1,262=1,665 ThoughtDef +
22+11=33 MentalBreakDef + 72+13=85 XenotypeDef), everything reachable routinely
or occasionally in play on the live 585-mod set per the existing census's own
tiering logic. DORMANT (502 + 11 + 54) stays deliberately OUT — essentially
unreachable on this mod set; still a future item, not dropped, if ever.

**COMMON-tier pass** (original scope, 497 rows) shipped first; the **OCCASIONAL
extension** (below) added the remaining 1,286 rows to the same sheet without
touching the owner's already-saved COMMON decisions.

**Census** (input, sanity-checked against RimSage and the live mod XML on
disk, reused as-is — no re-run needed):
`infrastructure/output/pawn_flavor_phase2_census.csv` (1,784 rows, all tiers).
Methodology record (not directly re-runnable — session-scratch input paths):
`infrastructure/output/pawn_flavor_phase2_census_gen.py`.

**Drafted prose** for all 1,783 COMMON+OCCASIONAL rows:
`infrastructure/output/pawn_flavor_phase2_prose_draft.json`, keyed
`"<defType>::<defName>"`. Field shape follows the real def, not a uniform
template: ThoughtDef/XenotypeDef carry `label`+`description`; MentalBreakDef
carries `label`+`beginLetter`+`recoveryMessage` because that prose actually
lives on the linked MentalStateDef, not on MentalBreakDef itself (confirmed by
reading both def types live via RimSage) — several MentalBreakDefs
(COMMON's `Catatonic`/`RunWild`; OCCASIONAL's
`Turn_MentalBreak_TerrifiedFaintingSpell`) have no linked MentalStateDef and
carry only a label.

**COMMON drafting method** (497 rows): split across 9 parallel Sonnet
subagents (7 ThoughtDef batches grouped by mod, 2 XenotypeDef batches), each
given the same style guide (desert-scavenger-Jawa register per
`pawn_flavor_design.md`'s established voice, mechanical meaning and mood
direction/intensity preserved exactly, first-person present-tense for thought
descriptions, Star Wars proper nouns used sparingly, xenotypes re-voiced as
the clan's own practical bestiary entries rather than Wookieepedia
paraphrase). The 22 MentalBreakDef rows were hand-drafted directly against the
real MentalStateDef XML (RimSage `get_def_details`), not delegated. A
similarity check (`difflib` against the original vanilla text) flagged 15 rows
that came back too structurally close to the source; those were rewritten by
hand afterward.

**OCCASIONAL extension** (1,286 rows, added after the COMMON pass): before
drafting, re-verified census trustworthiness — a 6-row spot-check across
Ideology/Alpha Memes/Core/Vanilla Ideology Expanded against RimSage confirmed
4/6 exact-ish matches; the other 2 fell in mods RimSage doesn't index at all
(same known blind spot as the COMMON pass hit on `RimMandrake - Star Wars
Races`), not fabrications. The 1,262 ThoughtDef rows split across **12**
parallel Sonnet subagents grouped by mod/theme (Ideology split into 2 halves
of 130; remaining ~30 third-party mods grouped into 10 thematic batches —
genes/DLC, bestiary, alien/droid, romance, ISEKAI standalone,
biomes/traits, slave-economy/misc — each ~70-140 rows) against a shared
style-brief file, same voice rules as COMMON plus explicit guidance on
romance/sex-adjacent content (plain register, not coy/graphic) and one debug
"null thought" row (dry in-universe joke, not forced sincerity). All 12
batch outputs verified complete (every input defName present, no empty
label/description) before merging — zero key collisions with the existing 497
COMMON entries. The 11 MentalBreakDef + 13 XenotypeDef rows were hand-drafted
directly, same as COMMON's method: RimSage `get_def_details` where the mod is
indexed (all 9 vanilla Biotech + Odyssey xenotypes, `FireStartingSpree`,
`IdeoChange`), live mod XML on disk under the Steam workshop content tree
where it isn't (VTE, Outer Rim - Droid Depot, Integrated Genes, ABF: Synstructs,
`guy762_debugxenotype_droid`, `VRESaurids_Saurid`).

**Review sheet** (extended in place — same sheet, same file paths, COMMON's
497 rows untouched):
- Generator: `src/RimMandrake/Utils/gen_pawn_flavor_phase2_register.py`
- Template: `src/RimMandrake/Utils/pawn_flavor_phase2_register_template.html`
- Sheet: `design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.html`
- Decisions: `design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.decisions.json`

Every row shows current (vanilla/mod) prose next to the drafted proposal,
grouped by def type then by mod with sticky group labels (per the
`review-sheets` skill), pre-filled **approve** so the owner only disagrees. A
new **tier** filter (COMMON/OCCASIONAL) lets the owner separate the
already-reviewed-once tier from the newly-added one. Decisions: `approve`
(ship the draft) / `tweak` (right idea, note holds the fix) / `reject` (redo
later) / `skip` (not reviewed — ships as drafted, same effect as approve but
distinguishable in the export). The generator refuses to regenerate over a
decisions file that carries `savedAt` without
`--i-know-this-overwrites-the-owners-decisions` — **exercised for real this
pass**: the owner had already opened the sheet once (`savedAt` stamped,
`decidedBy: owner-sheet`, all 497 rows still at the untouched approve default,
zero notes). The generator was extended to row both COMMON+OCCASIONAL tiers
from the census, then re-run *without* the override flag: it printed the
REFUSED message, left `pawn_flavor_phase2_register.decisions.json` byte-for-
byte unchanged (confirmed: same `savedAt`, same 497-row `rows` dict), and
still regenerated the HTML with all 1,783 rows — the sheet's own per-row merge
(`mergedRow()`) falls back to the embedded prefill for any row id absent from
the on-disk decisions file, so the 1,286 new rows render with a correct
`approve` default with no write to the decisions file required at all. Every
future re-run stays safe by construction: only a row the owner actually
touches (`t` timestamp set) survives being overwritten by a fresh prefill.
Auto-saves to the linked file via File System Access API, debounced ~1s, with
the same truncation guard and per-row touched-merge as the Phase 1 sheet.

## verify
1. Open the sheet, confirm 1,783 rows load, confirm the def-type, tier and
   per-mod filters work.
2. Link the decisions file (path is in the sheet's header, copy-button
   present) and confirm a decision + note round-trips after a reload — for
   both a COMMON row and a newly-added OCCASIONAL row.
3. When the owner is done: `git diff` the decisions file should show real
   content (not byte-identical to the prefill) before treating the pass as
   reviewed — see `review-sheets` skill §11.

## criteria
- [ ] Owner has worked through all 1,783 rows (approve/tweak/reject/skip on
      each, or explicitly left as the approve default) — COMMON's 497 were
      opened once already (`savedAt` 2026-08-30T19:13:16Z) but all still read
      the untouched default, so full review is still owed on both tiers.
- [ ] Any `tweak`/`reject` notes are folded back into
      `pawn_flavor_phase2_prose_draft.json` and the flavor actually shipped
      into XML — that's a follow-on item, not this one; this item's scope is
      the sheet + drafts, not the deploy.
- [ ] DORMANT tier gets its own follow-on item if the owner ever wants it
      (not filed — essentially unreachable on this mod set, flagging here so
      it isn't lost).

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

⚠️ **The OCCASIONAL extension's ThoughtDef pass is deliberately a tighter
effort than COMMON's** (per the owner's own scoping) — 1,262 rows across 12
subagent batches vs COMMON's 403 across 7, roughly triple the rows per batch.
Every row got genuine, non-templated prose (verified: no empty label/
description across any of the 12 batch outputs, spot-checked samples read in
voice), but a second look before shipping to XML is more warranted here than
on COMMON, which already had its 15-row similarity-flagged rewrite pass; the
OCCASIONAL batches did not get an equivalent post-hoc similarity check.
