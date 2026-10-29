# Species signature mechanics that need C# (XENOTYPE_CANON_CORRECTION_1, Pattern 4)

Status: SPEC ONLY, not built. 2026-10-29, FOUNDRY. The XML halves are built in
`src/RimStarWars/StarWarsRaces/Defs/GeneDefs/RSW_SpeciesSignature.xml`, checked by
`src/RimMandrake/Utils/selftest_species_signature_genes.py` (offline) and
`selftest_species_signature_vanilla.py` (deployed tier). Canon is read from
`design/RimStarWars/canon_references/<species>/description.md`.

Everything below would live in the StarWarsRaces assembly
(`Source/RSW_StarWarsRacesMod.cs` already has a settings class, `RSW_StarWarsRacesSettings`).
Each mechanic gets its own Mod Settings toggle, default on, and a test before it ships.
Owner question Q5 from the SPECIES_TRAITS_OVER_APTITUDES_1 draft (commit 931730da8)
asked whether StarWarsRaces may have its own code library. The assembly now exists for
other reasons, but the owner has not said that species mechanics may go into it.

## 1. Bothan fur that shows mood (Wrendui): the one mechanic with no XML half

Canon (Legends, from the owner): Bothan fur ripples with emotion, so a Bothan who is
upset or lying is easy to read for anyone who knows Bothans.

- Gene `RSW_WrenduiFur` (replaces the stand-in gene `AptitudeStrong_Social`, per the
  "replace the stand-in, don't count it twice" ruling) with a new
  `ConditionalStatAffecter_MoodBand` (min/max mood fraction). Low mood gives a penalty,
  high mood gives a bonus.
- Open owner question Q3: which stats? Either (a) `NegotiationAbility` / `TradePriceImprovement`
  (the Bothan's own dealings), or (b) how other pawns see the Bothan (`SocialImpact`,
  or an opinion `ThoughtDef`). (a) is pure StatWorker: about 40 lines, no Harmony. (b) needs a
  ThoughtWorker.
- Setting `bothanFurMoodEnabled`. When it is off, the affecter returns false (no stat change).
- Test: a unit check of the band edges; a bridge check of a Bothan's stat at mood 0.2 against 0.8.

## 2. Kel Dor oxygen poisoning when unmasked

Canon: oxygen is poison to Kel Dor; off Dorin they wear an antiox mask and goggles.
Built in XML: the mask's benefits (tox gas immunity, ToxicEnvironmentResistance, and vanilla
`VacuumResistance_Partial` for the hide that survives vacuum, which is sourced). Not
built: harm when the mask is gone. The mask is a permanent head attachment
(`RSW_HeadAttachment_keldormask`), not apparel, so in game it can never be removed.

- Option A (no code): leave it as it is. The mask is part of the body, and poisoning never happens.
- Option B: make the mask an apparel item (`RSW_AntioxMask`). A `HediffGiver` on the gene adds a
  growing `RSW_OxygenPoisoning` hediff while the pawn has no mask and is not in vacuum.
  Setting `kelDorOxygenPoisoningEnabled`. This affects art: the mask attachment becomes
  apparel, which needs an art-judge pass. It is an owner call because it adds micromanagement.

## 3. Defel invisibility in darkness and glare from visible light

Canon: Defel absorb visible light and are nearly invisible; visible light dazzles them;
elderly Defel lose the ability.
Built in XML: out of sunlight, `HuntingStealth` +0.25 and `MeleeDodgeChance` +8, both cancelled
exactly by `ConditionalStatAffecter_InSunlight`. The game's sunlight check is "unroofed and
sky glow > 0.1", so a brightly lit room counts as dim.

- True invisibility: a `HediffComp_Invisibility`-style hediff (vanilla Anomaly has one) that
  turns on when `map.glowGrid` at the pawn's cell is below 0.3 and the pawn is not attacking.
  Setting `defelShadowEnabled`.
- Glare from visible light: reuse the CreatureBehaviors `RM_GlareBlind` pattern (Sight penalty in
  bright light, with its own settings toggle) instead of writing a second system. Today
  Defel carry the vanilla `Nearsighted` gene, which may be a stand-in for this.
- Elderly loss: a check on the biological-age life stage inside the same comp.

## Owner calls recorded on the item (not ruled here)

- Umbaran carry `DarkVision` in place of canon UV vision: is this canon or a deliberate change?
- Should Defel also get `RSW_UltravioletVision` (canon says they see UV), and should
  `Nearsighted` be replaced by the glare mechanic?
- Kel Dor metabolism is now 2 lower (the two new genes cost -1 each). Should it be re-balanced?
- Bothan `AptitudeStrong_Social` (and other stand-in aptitudes) stays until #1 is built.
- The numbers (Sight +0.10, stealth +0.25, dodge +8) are first-pass values and the owner can tune them.
