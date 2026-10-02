# ROT_WOUND_SHARING_WIRING_1 — real wound-sharing and kin-mending on the Rot creatures whose descriptions promise it

Caused by `ROT_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.therot`, reusing
`mandrake.rm.creaturebehaviors` (already a hard dependency of the Rot). Design:
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §1 (findings in the cast), §3, §4 row 0,
§8; sheet `design/Jawa/worldbuilding/biomes/the_rot.md` (health-sharing in both variants, ruled; *"your herd
bleeds as one"*). Ruling: **build first: land the decided work plus the giant** (decision taken by question
card 2026-10-02 10:20 PDT): *real wound-sharing on the creatures whose descriptions promise it*.

## spec

The parts exist (searched 2026-10-02): `RM_CompWoundLink` + `CompProperties_WoundLink` (true splitting) and
`RM_HediffComp_KinMending` + `CompProperties_KinMending` (the tend-aura), both in
`src/RimMandrake/CreatureBehaviors/Source/`, tuned per race by `RM_WoundLinkExtension` (`tag`, `radius` 12,
`shareFraction` 0.6, `severityGate` 8, `kinMendingMinKin` 2). No Rot creature carries either today.
🔴 Wire, do not build: if a part seems missing, re-read those files first.

1. **Who promises what** (descriptions read 2026-10-02 from
   `src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml`):

   | body (our name) | promise, verbatim | wiring |
   |---|---|---|
   | `AA_Swarmling` (chittik) | *"a single body with a hundred mouths that shares every wound it takes"* | wound-link |
   | `AA_Agaripod` (gromma) | *"feels the wounds of its kin across the grove"* | wound-link |
   | `AA_Agaripawn` (rennok) | *"hurt one and the others in the grove feel it and come"* | wound-link (the "come" is the link's existing call to kin; measure, add a flee-or-converge response only if the comp lacks one) |
   | `AA_Wildpod` (mullgoth) | *"its kin heal faster near it"* | kin-mending, as the source |
   | `AA_Wildpawn` (durrok) | *"heals fastest of anything here — but only in company"* | kin-mending, as a receiver |

   None of the ten ports (`ROT_RM_CAST_MIGRATION_1`) promises sharing; re-read their final descriptions after
   that item lands and wire any that does.
2. **Where the comps go.** These five bodies are Alpha Animals defs wearing our names. Add the comps and the
   extension by a patch in the free mod, `Patches/RotSpecies_WoundSharing.xml`, guarded by
   `PatchOperationFindMod` on `sarg.alphaanimals` (**never** a top-level `MayRequire`, which 1.6 ignores).
   One shared `tag` (`RotNetwork`) so the five share across species, as the sheet's grove does.
3. **Tamed included** (*"your herd bleeds as one"*): the comps act regardless of faction; a tamed gromma
   shares with tamed and wild kin in radius alike (measure the comp's current faction filter; widen it by a
   field on the extension, default "any faction", if it filters).
4. **Gate:** the Rot screen's existing *Health sharing* toggle (`RM_TheRotSettings.healthSharing`, today a
   dead switch) gates both comps for Rot-tagged races. This is the one control
   `ROT_MOD_SETTINGS_WIRING_1` leaves to this item.
5. **Readable signs:** the comps' existing motes/messages; an inspect line on a linked creature (*"Shares
   wounds with its grove."* / *"Heals faster among its kin."*).

Depends on: none hard. Soft: `ROT_RM_CAST_MIGRATION_1` (re-read the ten). Blocks (soft):
`ROT_HWELGRUE_GIANT_BUILD_1` (none of its parts need this, but the giant's map is where it is felt).

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`, through a debug `[Tool]` that lists a spawned
pawn's comps and hediff comps and applies a fixed `DamageInfo`:
- With Alpha Animals loaded: each of `AA_Swarmling`, `AA_Agaripod`, `AA_Agaripawn` carries
  `RM_CompWoundLink`; `AA_Wildpod` and `AA_Wildpawn` carry the kin-mending wiring; all five carry
  `RM_WoundLinkExtension` with the same tag. Without Alpha Animals: the patch applies nothing and the log has
  no error.
- Split: spawn three grommas within 12 cells, deal one a 20-point cut; the target's total injury severity is
  < 20 and the other two's summed new injury severity is > 0 (read before/after). Same test with the toggle
  off: the target takes the full 20, the others 0.
- Tamed: repeat with one gromma set to the player faction; it still receives a share.
- Mending: an injured durrok next to two mullgoths loses injury severity over 10,000 ticks strictly faster
  than an identical durrok alone (two spawned pairs, severity read at start and end).
</content>
</invoke>
