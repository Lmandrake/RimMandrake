# Cauldron trunk deposits: scabs and crystal fans on the trees we already have

Item `CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS` (GPT biome art review 2026-10-24, tiles T091-T092).
Status: DESIGN. Built by `CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS`; the flecks defect below by
`CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR`. Checked by
`src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py`.

## 1. The gap

The biome sheet (`design/Jawa/worldbuilding/biomes/cauldron.md` §1): *"The trunks are pale and slick and
weep a grey metallic sweat that hardens into scabs and crystal fans, so an old trunk is part tree, part
slag heap."* The GPT review (T091-T092, both kept) found that coat weakly shown and asked for deposits on
the EXISTING trees or the growth around them, not one more mineral plant.

What the game draws today (measured 2026-11-02 against `src/RimMandrake/Cauldron`):

- T091-T092 are `RM_TwistingThornwood`, the Cauldron's only tree (`RM_TreeMartyr` is cut). Its graphic is
  `Graphic_Random` over ONE texture, `Textures/Things/Plant/RM_TwistingThornwood/TwistingThornwood_a.png`
  (256×256): a dark corkscrew trunk with grey thorns. It has no scab and no crystal painted on it.
- The only deposit visual is the assay-flecks overlay (spec V3 in
  `cauldron_enrichment_audio_visuals_spec_2026-10-02.md`): class `RM_AssayFlecks` in
  `Source/RM_CauldronDewfallVisuals.cs`, a postfix on `Plant.Print`, driven by `RM_AssayFlecksExtension`
  and the tree's assay grade (`RM_CompMetalYield.GradeFraction`). A tree below a third of its lode shows
  nothing, so young and average trees never show the coat.
- The overlay art misses its own spec. V3 asked for glints and scab-plates "weighted to the lower trunk ...
  trunk-centred" in silver-grey, bronze and blue-violet. `Flecks_Light.png` and `Flecks_Heavy.png` are
  loose nuggets spread over the whole canvas, Heavy mostly gold and orange. Measured by §5's instrument:
  **about 31 % of each overlay's pixels lie outside the tree's silhouette (dilated 9 px)**, so they hang
  in the air beside the trunk. Filed as `CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR`.

## 2. The design: a deposit coat painted onto the tree's own silhouette

One new overlay layer on `RM_TwistingThornwood`, drawn by the same `Plant.Print` path the flecks use.
It is not a plant, not a building and not a new def.

- **What it shows.** Grey metallic sweat dried into scabs along the bark splits and the lower trunk
  (wet silver-grey sheen, darker slag edges), plus **crystal fans**: flat, flared fans of 3-6 pale
  translucent blades, the sheet's "bruised blue" (§9 palette), rooted at branch forks and in the
  corkscrew's grooves. No green, no gold.
- **Age, not assay.** The sheet ties the coat to age ("an old trunk is part tree, part slag heap"), and
  the review asks for a forest-wide look. The coat is keyed to the tree's own life, not to its metal:
  - `Growth < 0.5`: no coat (a sapling has not sweated yet).
  - mature (`Growth >= 0.5`, `Age < 0.5 × LifespanTicks`): **Scab** overlay, scabs in the splits and two
    or three small fans.
  - old (`Growth >= 0.5`, `Age >= 0.5 × LifespanTicks`): **Slag** overlay, the lower trunk sheathed in
    scab, larger fans climbing the spiral.
  The thresholds are extension fields (`scabFromGrowth`, `slagFromAgeFraction`), not constants.
- **The flecks stay, on top.** Assay flecks keep their meaning (where the metal is rich) and draw one
  altitude step above the coat; the coat is the forest's look, the flecks the prospector's hint.
  Their art is redrawn to the same registration bar (§5), on spec V3's palette.
- **The kept tree is not replaced.** The thornwood is an owner favourite ("owner favourite, keep",
  `rosters/cauldron.json`). The coat is a separate additive texture, so the base art stays untouched
  and the coat can be switched off: no delegation-policy §2 art call is raised.
- **Setting.** `trunkDepositsEnabled`, default on, in the Cauldron Mod Settings beside
  `assayFlecksEnabled`. It does not ride the metal-yield or assay toggles: the coat is how the biome
  looks, not part of its economy. Turning it off and on remeshes like the flecks do
  (`RemeshAllMaps`).

### Why not the alternatives

| alternative | why not |
|---|---|
| A new mineral or crystal plant | The review rules it out; `RM_Fexxil` (cobalt glass spines) and `RM_CrystalFlower` already carry ground crystal. |
| More `Graphic_Random` variants of the tree with the coat painted in | Variant choice is random per tree, not age; it would replace the kept look on part of the forest; it multiplies with every future art pass. |
| Repaint the base texture | Replaces art the owner kept (delegation policy §2). |
| Keep using the flecks | Gated on assay grade, so most trees show nothing; the art floats off the trunk (§1). |

## 3. Mechanism (for the build)

Generalise `RM_AssayFlecks` into one print postfix that draws up to two planes:

1. `RM_TrunkDepositsExtension` (new `DefModExtension` on the tree): `scabTexPath`, `slagTexPath`,
   `scabFromGrowth = 0.5`, `slagFromAgeFraction = 0.5`; `ConfigErrors` as the flecks extension has.
2. The tier choice is a pure function in the kernel beside `RM_YieldKernel.FleckBand`
   (`DepositTier(growth, ageFraction, scabFrom, slagFrom, hasScab, hasSlag)`), mirrored in a Python
   selftest that sweeps the whole input grid, as the yield kernel is.
3. The print postfix reuses the flecks' registration replay (same `Rand.Seed`, same offset and flip
   draws), so coat, flecks and trunk share one origin. Coat at `OverlayYOffset`, flecks at twice it.
4. **Re-print on ageing.** Vanilla re-prints a plant when its growth stage changes, not when it ages.
   A full-grown tree crossing `slagFromAgeFraction` must dirty its cell once (a `CompTickLong` check:
   `Plant` ticks only `TickLong()`). A load remeshes everything anyway.
5. Dormant without art, as the flecks are: with neither texture on disk the patch is not installed.

UNMEASURED, for the build to read before relying on it: how wild-plant mapgen seeds `Age` on full-grown
trees (if it leaves `Age` at 0 the old tier never shows on a fresh map, and the key needs a per-position
hash instead).

## 4. Art brief

Two 256×256 RGBA overlays at `Textures/Things/Plant/RM_TrunkDeposits/Deposits_Scab.png` and
`Deposits_Slag.png`, plus the redrawn `RM_AssayFlecks/Flecks_Light.png` and `Flecks_Heavy.png`.

- **Make them by editing the tree, then subtracting it.** Feed `TwistingThornwood_a.png` to the
  `editing-images` skill with the §2 description, keep the trunk fixed, and take the overlay as the
  changed pixels only (alpha where the edit differs from the base). This registers the coat to the
  trunk by construction, because the tree has exactly one texture.
- Painterly vanilla RimWorld style, readable at play zoom: scabs as a few broad plates, fans as clear
  flared shapes, not noise. Palette: silver-grey and slag-dark scab, pale bruised-blue glass.
- Judged by the art-eval pipeline (`rimworld-art-evaluation`) against this brief and the sheet before
  install; installed through the art ledger only.

## 5. Acceptance

- **Registration (offline, every overlay):** at least 95 % of the overlay's pixels with alpha > 16 lie
  inside the tree's alpha > 16 mask dilated by 9 px. The same instrument measures today's flecks at
  about 69 % inside, so it can see a miss. `selftest_cauldron_trunk_deposits.py` holds the instrument.
- **Coverage (offline):** Scab covers 8-25 % of the tree's own pixels, Slag 20-45 %, so the coat reads
  without burying the kept tree.
- **Tier function (offline):** the Python mirror of `DepositTier` agrees with the C# on the full grid.
- **In game (L2, quicktest map):** a mature and an old thornwood show their coats; with
  `trunkDepositsEnabled` off, neither does after the remesh. A capture of each is judged before anyone
  shows it to the owner.
