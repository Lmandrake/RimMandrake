# FEVERWOOD_TWO_FRONT_LURE_TUNING_1 — two-front lure numbers, prey-quality gate, and a free-tier second raider

Caused by `FEVERWOOD_TWO_FRONT_LURE_1` (v1 shipped: lure stake, staking flow,
staggered two-raider raid). Owed work the v1 build deliberately did not guess.

## spec

1. **Prey-quality gate — explicitly left UNSET by the design sheet**
   (`fever_wood_deep_and_mud_2026-09-23.md` §7: *"Whether the lure cares
   about the quality of the staked prey"*). ⚠️ **Known exploit**: v1's
   `RM_WorkGiver_StunForStaking`/`RM_WorkGiver_HaulToStake` accept ANY tamed
   animal or prisoner with no quality/species/value floor — a colony can
   breed the cheapest possible animal purely as raid ammunition. Either the
   lure needs to care about prey quality (market value floor? species
   floor? a `RM_LureRaiderOption`-style commonality bonus for a
   higher-value bait?), or the cheap route needs its own cost. Do not
   guess; needs an owner ruling on which axis "quality" means.
2. **All numeric tuning is INVENTED placeholder**, flagged per-field at its
   source (`RM_FeverWoodSettings`: `twoFrontLureRaidMtbHours` 6,
   `twoFrontLureSecondWaveChance` 0.5, `twoFrontLureSecondWaveMinHours`/
   `MaxHours` 2-8; `RM_LureStake.xml`'s cost/HP). A play-test pass should
   retune these against how often a lure actually gets built and used.
3. **The raid's threat-points scaling** (`RM_MapComponent_TwoFrontLure.
   SpawnRaidWave`: `Mathf.Max(80f, StorytellerUtility.DefaultThreatPointsNow(map) * 0.6f)`)
   is an invented multiplier, not a design-sheet number — check it against a
   real colony's threat points once one exists to stake a lure with.
4. **Free-tier second raider.** `RSW_Shokk_FeraliskBrood` (the real Feralisk,
   canon Wyyyschokk, `MayRequire="mlie.starwarsanimalcollection"`) is the
   only feralisk-side raider — absent that mod, a staked lure only ever
   draws the kurreth swarm ("ants only", graceful degradation, not a bug).
   Per Q11a (`biome_mod_architecture.md` §7) the franchise-free `RM_FeverWood`
   mod should look the same without Star Wars content, cast-in inline — this
   needs an INVENTED, non-canon second raider species for that tier.
   **Ruled 2026-09-24** (decision taken by question card,
   `fever_wood_rm_cast_proposal_2026-09-24.md` § Rulings): the **skreth** is
   the free-tier face of the Webwork brood and the two-front war is identical
   in both tiers. **Moved to `FEVERWOOD_RM_CAST_COMPLETION_1`** (spec 2),
   which builds `RM_Skreth` and its brood faction and replaces the
   ants-only fallback; not this item's work any more.
5. **Release-anytime vs. wager-locked-in.** v1's `RM_CompLureStake.ReleaseBait`
   lets the player free a staked pawn at any time, including after a raid is
   already inbound — a real, if minor, deviation from the design sheet's
   "you are hoping the second column shows up" framing (which reads as a
   commitment). Worth an owner check: should release be blocked once the
   first wave has actually been rolled/spawned?

## not built (v1 scope, real gaps)

- Target-preference weighting (raiders preferring the staked bait over the
  colony) — F9's own stated fallback is plain contact-hostility; v1 ships
  that. A LordToil that beelines a raid group at the bait specifically,
  falling back to `LordJob_AssaultColony` once it's dead, is real follow-on
  work if placement-only proximity (spawn near the stake) proves too weak
  in play.
- Live verification that a staked lure's raid actually spawns and behaves as
  designed — this item's build was offline-only (validate_patch.py + a
  clean `dotnet build`), never bridge-tested.

## Progress 2026-09-26 (FOUNDRY) — points 2/3/5 built, points 1/4 skipped

Built and `dotnet build`-verified, commit `96dbbf8e`:
- **Point 3** (threat-points scaling): the hardcoded `Mathf.Max(80f,
  DefaultThreatPointsNow(map) * 0.6f)` is now two Mod Settings sliders
  (`twoFrontLureThreatPointsMultiplier`/`twoFrontLureMinThreatPoints`,
  defaults unchanged at 0.6/80) — "check it against a real colony's threat
  points once one exists" can now happen live, without a rebuild.
- **Point 5** (release-anytime vs. wager-locked-in): added
  `twoFrontLureLockOnceTriggered`, default OFF (shipped behavior
  unchanged). `RM_CompLureStake` now tracks per-stake `raidTriggered`
  (set by `RM_MapComponent_TwoFrontLure` once a raid actually spawns from
  that stake) and disables "Release lure" via `Command.Disable` when the
  toggle is on and this stake has drawn a raid — an opt-in mechanism for a
  question the item itself said was "worth an owner check," not a call
  this pass made for him.
- **Point 2** (existing MTB/second-wave numbers): already exposed as
  sliders from an earlier pass — nothing further to build; retuning the
  defaults still needs a real playtest, out of scope for an offline pass.

**Skipped, per the item's own instruction not to guess:**
- **Point 1** (prey-quality gate) — explicitly needs an owner ruling on
  which axis "quality" means; untouched.
- **Point 4** (free-tier RM-tier second raider species) — "skreth" is
  proposed but not owner-ruled; the item itself says do not invent the
  ruling here. Untouched.

Not closing: points 1 and 4 remain genuinely open and need the owner.

## Cross-references

`FEVERWOOD_TWO_FRONT_LURE_1` (closed) · `fever_wood_deep_and_mud_2026-09-23.md`
§5/§6l/§7 · `the_webwork.md` (Wyyyschokk/Feralisk naming ruling) ·
`WYYYSCHOKK_FERALISK_MERGE_1` (closed — AA_Feralisk already cut from LIVE
Cherry Picker; never reference it) · Q11a, `biome_mod_architecture.md` §7.

## 2026-10-02 additions

`FEVERWOOD_SCORING_SITTING_1` turn 1 (decision taken by question card 2026-10-02 11:12 PDT, build first =
land the decided work plus the giant's story): spec 4 (the free-tier second raider) is owned by
`FEVERWOOD_RM_CAST_COMPLETION_1`. The kurreth front now steals (`FEVERWOOD_ANT_THEFT_RAIDBACK_1` changes the
lure's `LordJob_AssaultColony(… canSteal: false)` call); retune this item's numbers against the theft raid,
not the plain assault. Points 1 and 5 still need owner rulings and are untouched.

## Progress 2026-11-03 (Relentless) — spec 1 and 5 decided and built
Neither is on `delegation_policy.md` §2, so both were decided here (delegated: design), not waited on:
- **Spec 1, prey-quality gate.** "Quality" = the bait's worth as prey: its race's base market value x its
  life stage's `marketValueFactor`, never its wounds (every bait is wounded and chained by design). Bait under
  `twoFrontLureMinBaitValue` (150 silver) draws no raid; above it the first-wave MTB is divided by
  worth / `twoFrontLureFullDrawBaitValue` (500, capped at 1); the map rolls on its best bait. Against vanilla
  Core values: rat 35, chicken 50, duck 60, goose 90, cat 100 never draw (the bred-ammunition route is shut);
  capybara 150 draws 0.3, muffalo 300 at 0.6, a horse or any prisoner (1750) at full. Toggle
  `twoFrontLurePreyQualityGate` (on); the stake's inspect string says when bait is too poor or lean.
  Kernel `Source/Kernel/RM_LureKernel.cs`, fuzz family `lure` (`selftest_feverwood_fuzz.py --fuzz-only lure`).
- **Spec 5, lock the wager.** `twoFrontLureLockOnceTriggered` now defaults ON (§5: the lure is a gamble you
  live inside). Off restores release-anytime.
- **Spec 2/3, retune against real play:** still owed and live-only — filed as
  `FEVERWOOD_LURE_TUNE_AFTER_A_REAL_RAID`; the theft raid it was to be tuned against was cut
  2026-10-23 (`fluff_cuts_2026-10-23.md`), so the retune is against the plain assault.
