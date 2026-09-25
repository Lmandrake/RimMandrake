# FORCE_DISTURBANCE_REFLAVOR_1 — psychic storms become disturbances in the Force

Owner directive, typed 2026-09-24: "Make a ticket in the background to convert
the psychic assault storms event that frequent rimworld sound be converted to
disturbances in the force in rim star wars."

## spec

The vanilla psychic event family — psychic drone (the planetary/map condition
in both sexes), psychic soothe, the psychic-ship crash chain, and any DLC
psychic-storm conditions active in our list — get reflavored as **disturbances
in the Force** at the **RimStarWars tier** (`RSW_`, `mandrake.rsw.*`; per the
tier grammar this is Star Wars flavour usable by any Star Wars scenario, NOT
campaign-specific — the Utinni layer only adds campaign-specific text if any).

- Rename/retext by patch, not by replacing the incident defs: labels, letter
  text, condition descriptions, alert strings. Mechanics unchanged — this is
  flavour, not a rebalance.
- Survey first: enumerate every live incident/condition def whose label or
  text says "psychic" (vanilla + DLC + donors in the active list) before
  patching; patch what the campaign will actually see.
- Wording direction: a drone is "a disturbance in the Force" pressing on
  minds; a soothe is the Force at peace; a psychic ship is a dark-side
  artifact. Draft text goes past the owner (BENCH card) before shipping —
  flavour text he will read constantly.

## Watch out

- `PatchOperationConditional`/`FindMod` return true on no match — a text patch
  that misses its xpath fails silently. Validate with validate_patch.py
  against both --defs and --live.
- Psychic sensitivity stats/hediffs keep their names ("psychically deaf" etc.)
  unless the owner rules wider — scope creep here touches Biotech genes and
  Royalty psycasts; this ticket is the STORM/EVENT family only.
- Donor mods may carry their own psychic events; a vanilla-only xpath sweep
  undercounts what the player sees.

## verify

Every surveyed psychic storm/condition event shows Force-flavoured label +
letter text in a live quicktest; no vanilla "psychic drone" string reaches the
player from the patched set.

## criteria

Owner has seen and approved the replacement text; mechanics measurably
unchanged (same incident defs fire, same conditions apply).

## FOUNDRY progress, 2026-09-24

Claimed, started, survey done, draft patch written and structurally
validated — **not deployed, not closed**. The remaining step (his sign-off on
the exact wording, then deploy + close) needs the owner, so this item's
`needs` is set to `owner`.

**Survey** (live def dump `2026-09-24T22-19-22Z`, 626-mod active list —
IncidentDef/GameConditionDef labels or text containing "psychic"):

- CORE (`ludeon.rimworld`): IncidentDef `PsychicDrone`, `PsychicSoothe`,
  `PsychicEmanatorShipPartCrash`; GameConditionDef `PsychicDrone`,
  `PsychicSoothe`, `PsychicDroner`.
- DLC Royalty: GameConditionDef `PsychicSuppression` (mechanoid cluster
  defense field — the DLC's own psychic-family condition, not literally a
  "storm"; included in the draft, flagged for an owner call on scope).
- Donor, active in our list: Vanilla Events Expanded — IncidentDef
  `VEE_PsychicStimulation/Overdrive/Hum/Bloom/Rain`; GameConditionDef same
  four plus `PsychicRain` (that one def's own name has no `VEE_` prefix).
  Vanilla Races Expanded - Archon — IncidentDef + GameConditionDef
  `VREA_PsychicStorm`.
- Surveyed but left OUT of the draft: Anomaly's `PsychicRitualSiege`
  (IncidentDef, Horax cult ritual siege) and `HateChantDrone`
  (GameConditionDef, label is "hate chanting" — only its description says
  "psychically tuned"). Both are established Anomaly cult flavour, not the
  vanilla storm/mood family the item names. Owner call whether to fold them
  in too.
- Out of scope, per the item's own Watch-out, and NOT touched anywhere in
  the draft: the "Psychic Sensitivity" stat, "psychically deaf/dull" hediffs
  and traits, Biotech genes, Royalty psycasts. Two lines in the draft
  (Royalty's suppression field, VRE Archon's storm) name that real stat in
  their flavour text and keep the phrase "psychic sensitivity" verbatim on
  purpose.

**Draft patch**: `src/RimStarWars/StarWarsPatches/Patches/PsychicToForceDisturbance.xml`
(new file, `mandrake.rsw.patches`), label/description/letterText/endMessage
only via `PatchOperationReplace`, `PatchOperationConditional`-gated for
core/DLC and `PatchOperationFindMod`-gated for the two donor mods. Follows
the item's own wording direction verbatim (drone → "a disturbance in the
Force"; soothe → "the Force at peace"; the ship-crash persona → a dark-side
artifact; the droner machine → a "dark-side droner"). Every xpath validated
against the real 626-mod file set with `validate_patch.py --live <dump>
--defs <Data> --defs <Workshop> --defs <Mods>`: **34/34 operations hit
exactly 1 match, 0 errors** — no silent-fail zero-match xpaths.
`About/About.xml` got the two new `loadAfter` entries
(`vanillaexpanded.vee`, `vanillaracesexpanded.archon`) the new
`PatchOperationFindMod` blocks need.

🔴 **This file is source-only.** It has not been run through
`deploy_custom_mods.py` (apply mode) and is not in the live Mods folder —
the owner has not seen this wording yet. Ran `run_selftests.py`: 73/75 pass;
the 2 failures (`selftest_live_prep.py` on RotSporeKit,
`selftest_deployed_biome_refs.py` on `RUT_Vorrel`) are pre-existing and
unrelated to this change — confirmed by reading their output before this
patch touched anything they check.

**Next step, for BENCH**: card the drafted label/letter text above (or read
it straight from the patch file's comment block, which lists every line) to
the owner. On approval: deploy with `deploy_custom_mods.py --mod
"RimStarWars Patches" --apply` (or the equivalent invocation for this mod's
folder), validate `--live` once more against a fresh dump, then close this
item against that deploy commit.
