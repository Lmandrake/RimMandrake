<!-- status: draft — BENCH synthesis of the three-arm beast fan-out, 2026-08-31. Owner's law: bodySize tracks visual size (spindly exception); mass matches scale; danger matches size — "a bull casually kills someone without intending to." Data: beast_census.csv (1,022 rows) · beast_roster.csv (581 kinds) · vanilla curves (arm 3, quoted here). -->
# Beast Normalization — size, mass, casual lethality, temperature, products

## 1. What the fan-out established (MEASURED, frozen dump `1742630eb6253187`)

1. **Mass is not authored — it is `60 kg × bodySize`.** The Mass StatDef
   carries `StatPart_BodySize` over a flat 60 base; 1,019 of 1,022 animals
   keep the raw 60 (three overrides in 584 mods). So in-game mass DOES scale
   with size already — but on a compressed scale (elephant = 240 kg vs ~4,000
   real). **Consequence: there is no independent mass defect to fix. bodySize
   is the only dial.** (And the Covered Pits mass triggers are already
   calibrated to engine mass — the peer's 240 kg ceiling is exactly
   bodySize 4.0 × 60. Confirmed consistent; no correction needed there.)
2. **Vanilla already normalizes sprites: `drawSize ≈ 1.9·√bodySize`** (115
   vanilla animals, tight fit). The owner's law inverts cleanly:
   **`bodySize ≈ (drawSize / 1.9)²`** — with two sanctioned exemptions:
   the **legibility floor** (critters below bs ≈ 0.5 are drawn oversized on
   purpose) and the **spindly register** (long-limbed, low-mass builds get a
   named exemption row, never a silent one).
3. **The dump cannot see drawSize — field-level coverage gap**, same class as
   the old statBases hole (verified: texPath present, drawSize absent, whole
   population). The bodySize-vs-visual audit is **UNMEASURED until the
   capture is widened** (remedy: extend `measure/dumpdb.py`'s GraphicData
   capture; raw-XML sweeps are a trap — drawSize inherits through ParentName
   chains).
4. **Danger does not track size, and the Star Wars marquee monsters are the
   worst offenders.** Median danger-per-size 4.0 across 1,022; the SW
   bestiary's apex reads: GreaterKraytDragon **1.5** (bs 15, DPS 22.5 —
   three timber wolves), KraytDragon 1.25, JungleRancor 1.33, Horax 1.07,
   Beldon 0.92. Big herbivores generally sit at the bottom (vanilla cow
   k=2.5; the Jurassic herbivore family 0.56–0.69). Vanilla undersells
   bull-class burst by 3–4×.
5. **Scope is one mod.** All 581 spawnable Ash'karr beasts are third-party;
   the SW bestiary (161 defs) comes entirely from
   `mlie.starwarsanimalcollection`, zero are Cherry-Picker cut, and our own
   mods ship no animals. The normalization is a patch mod over known targets.

## 2. The three laws (the normalization itself)

**Law 1 — bodySize from visual:** `bodySize = (drawSize/1.9)²`, exemptions:
legibility floor (bs < 0.5 keeps authored size) and the spindly register
(each exemption a named row with a one-line physical justification). Gated on
finding 3's capture fix.

**Law 2 — mass rides bodySize** (already definitional). DECISION FOR THE
OWNER: leave the engine's compressed 60×bs scale (recommended — every
downstream system is tuned to it: hauling, caravans, pit covers), or override
to realistic masses (a 4-tonne elephant would distort carrying/caravan
balance stack-wide for flavor nobody reads). Recommended: **no override;
close the question.** ✅ RULED (owner card, 2026-08-31): engine scale kept.

**Law 3 — casual lethality, with counterplay** (arm-3 curve, adopted as
draft): for bs ≥ 1, **best-hit damage goes linear: ≈ 12–15 × bodySize**
(muffalo/bull 2.4 → ~30: one hit downs an unarmored pawn; thrumbo-class 4.0
→ 50–60: maims or kills) while **DPS stays sublinear (≈ 8–12·√bs) via 3–4 s
cooldowns on the big hits** — burst lethality, not shredding; fights are
survived by not being hit. **Aggression does NOT rise**: the "casual" half
lives in the revenge knobs (`manhunterOnDamageChance`,
`manhunterOnTameFailChance`) raised on big herbivores — docile until
provoked, catastrophic when provoked. Counterweights that keep the early
game playable: armor honestly absorbs (flak turns 30 blunt survivable),
telegraphs before charges, and the theology already teaches the answer —
hunt from range; the new curve makes Ishko's doctrine mechanically true.

## 2b. Law 4 — the blaster-shrugging hide (owner, 2026-08-31: "the canon had it")

Star Wars canon: big beasts shrug blaster fire. Two mechanizations, one
recommended:
- **Option A — armor absorption — ✅ RULED (owner card, 2026-08-31):**
  `ArmorRating_Heat` on a **thick-hide register** of beasts, scaling with
  bodySize (draft: ~15% × bodySize, capped ~75%). Blasters deal energy/burn
  damage, so "blasters stop working" EMERGES — the bigger the beast, the
  more bolts it eats — with no new mechanics, vanilla-native, savegame-safe.
  Register-based like the spindly list: not every big beast qualifies
  (soft-bodied and spindly exempt).
- **Option B — heat-resist/overheat hediff:** blasters literally degrade
  against a target over time. Flavorful but new C#, invisible until read,
  and double-punishes with Option A.
- **The emergent gift either way:** slugthrowers, bolts, and the primitive
  tier regain a PURPOSE — big game wants physical damage, exactly the
  scavenger answer (and ion wants the machine). Weapon choice becomes prey
  choice.

## 2c. Coupling register (owner, 2026-08-31: "make sure our pit traps come along for the ride")

| Coupled system | The rule |
|---|---|
| **Pit covers** | Calibrated to ENGINE mass (60×bs) — already true (the 240 kg ceiling = bs 4.0). IF Law 2 ever flips to real masses, cover ratings rescale in the SAME manifest, same commit. |
| **Ion stun counts** | Hits-to-stun/drop scales with the NEW bodySize (stun buildup ∝ bs): a normalized Krayt takes proportionally more ion hits; ties VEHICLE_ION_TIER_1 and the oubliette. The ion tier reads bodySize at run-time, so Law 1 corrections propagate free — but the per-hit stun magnitude is tuned once against the POST-normalization sizes, in this manifest. |
| **Law 4 hides vs our armory** | The thick-hide register is the same register the hunting doctrine reads: blasters for raiders, slugs for beasts, ion for machines. |

## 2d. Law 5 — temperature tolerance covers the domain (✅ RULED, owner phone-card sitting 2026-09-11)

Owner: animals get **wide tolerances that let them survive easily in their
domains of choice**. Ruled margin: **domain envelope +15 °C on BOTH sides.**

Stated so a linter can check it — for every rostered animal `A`:

1. **Domain** `B(A)` = the biome keys assigned by
   `review/round2/decisions_propagated.json` (fauna rows `decision: in`) plus
   `review/round2/move_mapping_v2.md` resolved targets (the 114 ruled moves
   landed in `biomes/rosters/*.json` — `ROSTER_MOVE_APPLY_1` closed
   2026-09-11 — so rosters no longer lag the mapping).
2. **Envelope**: per biome key, map to its painted BiomeDef(s) via
   `biomes/_def_bindings_2026-09-09.md` (the painted CSV wins), then over that
   def's tiles in `world/ASHKARR_WORLDMAP_tiles.csv`:
   `envLo = min over B(A) of p05(temp_c)`, `envHi = max over B(A) of p95(temp_c)`.
3. **The law**: `ComfyTemperatureMin(A) ≤ envLo − 15` **AND**
   `ComfyTemperatureMax(A) ≥ envHi + 15`, on FINAL post-patch stat values
   (XML key `ComfyTemperatureMin/Max` in `statBases`; StatDef defaults 0/40
   apply when a race sets neither).
4. **Widening only** — the law never narrows a range already wider than
   required.
5. Biome keys with no painted tiles (`fall_line`, `the_lantern_deeps`,
   `wreck_fields` — injection layers) are **UNMEASURED**: the linter skips and
   flags, never passes them.
6. ⚠️ Tile `temp_c` is the map-gen mean; in-game seasonal/diurnal swing extends
   beyond it. The +15 is the ruled cover for that, not a measured swing — the
   live harvest confirms realized extremes.

**Offline census 2026-09-11** (mod XML, inheritance-resolved, PRE-patch):
**196 of 279 measurable rostered animals violate** (83 OK, 15 env-unmeasured,
3 xml-unmeasured). Full rows and fingerprints:
`design/Jawa/worldbuilding/fauna_tolerance_census_2026-09-11.csv`; summary:
`fauna_tolerance_violations_2026-09-11.md`. (The sitting's "23 flagged narrows"
was a pre-law flag count, not a census under the ruled law.)

## 2e. Law 3 scope extension + Law 6 products (✅ RULED, same sitting 2026-09-11)

- **Law 3 now covers the FULL rostered set** (~297 biome-assigned animals as of
  the 2026-09-11 census), not just the 161 SW beasts `BeastNorm_Law3.xml`
  shipped: one K = 12–15 × bodySize band, grazers rise too, AA_/BMT_/GR_/DA_/
  vanilla kinds in play. Above-band outliers come INTO the band — no exemption
  list now; per-beast diversification is a later art+lore round
  (FAUNA_LORE_DIVERSIFICATION_1, done 2026-11-02: 28 ruled divergences in
  `data/fauna_lore_divergence_manifest.csv`, record in
  `fauna_lore_divergence_2026-11-02/README.md`). bodySize itself does not change (ceiling-
  fields lesson: each parameter its own law).
- **Law 6 — products ∝ bodySize**: meat/leather amounts get bodySize-
  proportional defaults NOW; re-checked against live engine values when
  FAUNA_STATS_BRIDGE_TOOL_1 lands (owner accepted it may be redone on real
  numbers). No target curve beyond proportionality is pre-agreed — the constant
  is set at the plot sitting.
- Both manifests ride the POST-restore live harvest (the 2026-09-11
  CherryPicker restore changed the live def set); the offline census above is
  the pre-patch baseline, not the execution input.

## 2f. Execution — Laws 3, 5, 6 over the whole roster (FAUNA_TOLERANCE_NORMALIZATION_1, 2026-11-02)

One generator, `src/RimMandrake/Utils/fauna_normalization.py` (`snapshot` / `generate` / `check` / `plot`),
proven by `selftest_fauna_normalization.py`. Inputs: `data/fauna_norm_input.csv` (+ `.meta.json`: every
animal on an `RM_`/`RUT_` biome roster — BiomeDef `wildAnimals` plus our src patch adds — resolved from the
316-mod `ModsConfig.FULL.LATEST.xml` load set, PRE-patch, with its load-set fingerprint), the tile record and
the divergence manifest. Decision record: **`data/fauna_norm_manifest.csv`** (defName · law · field · old ·
new · rule · note; `6x` rows are exemptions). Patches: `src/RimUtinni/UtinniPatches/Patches/FaunaNorm_Law3_Damage.xml`,
`FaunaNorm_Law5_Tolerance.xml`, `FaunaNorm_Law6_Products.xml`. `check` lints every law on simulated post-patch
values (snapshot + the earlier patches on the same fields + ours) and requires the outputs to regenerate
byte-identical.

- **Law 5** — the envelope of an `RM_` biome (0 tiles today, expected) is its painted twin's tiles, joined
  through `design/RimMandrake/biome_mod_architecture.md` §2a/§2b; a painted name the record no longer spells
  is matched by its unique tile count (`RUT_Wastes` = record `RUT_Wasteland`, 1853). A pocket biome whose
  BiomeDef sets `constantOutdoorTemperature` takes that one value (the Lantern Deeps, 17 °C). Every
  rostered animal is measured. Ops are widen-only and order-proof: an existing value is replaced only
  behind an xpath `number(.)` guard, so they compose with `AnimalTolerances_*.xml`.
- **Law 3** — out-of-band best hits go to K = 15 (the quicktested SW coefficient); in-band animals stay as
  authored; all bodySizes (the SW pass's bs < 1 exemption is superseded by "one band, whole roster"), floor
  1. The other tools scale by the same ratio; a cooldown only lengthens, to DPS ≤ 10·√bs. The 28
  divergences take K_ruled × bodySize, off-roster ones included. `mandrake.rut.patches` loads BEFORE
  `mandrake.rsw.swbestiary` in the full list (`MODLIST_ORDER_FIX_LOADAFTER_WAS_A_SUGGESTION`), so a
  `BeastNorm_Law3.xml` value wins over the generator: the generator skips the defs that file still sets,
  and the seven whose values had gone off target (four divergences, three whose bodySize moved) were deleted
  from it and handed over.
- **Law 6** — the 2026-09-11 card said "meat/leather ∝ bodySize"; the owner's earlier rule (2026-08-11,
  `src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py`: *"a truly enormous kill should leave you swimming in
  meat"*, meat ∝ bodySize² above 1, leather linear) still ships in `MegafaunaYield.xml`. Read together, products
  are a function of bodySize alone: leather base 40 (linear yield), meat base 140 for bs ≤ 1 and 140 × bs
  above it. Explicit per-animal overrides that deviate are reset; a 0 (meatless or hideless creature) is
  kept and listed as an exemption. If he means strictly linear meat, delete `MegafaunaYield*.xml` and set
  `MEAT_BASE × bs` → `MEAT_BASE` in the generator.
- Graphs (`plot`): `Transient/fauna_normalization/` — damage, DPS, tolerance-vs-envelope, products, each
  titled with its load-set fingerprint.

## 3. Execution shape

- **One patch mod, tier RimStarWars** (the lethality of SW beasts is
  any-SW-scenario content): working id `mandrake.rsw.beastnorm`, per the
  naming scheme. Ash'karr roster priorities (the 15 campaign-relevant kinds,
  Krayt family first) come from the RimUtinni-side roster data but the
  patches are SW-general.
- **Manifest-driven** (`beast_norm_manifest.csv`: defName · new tools rows ·
  cooldowns · revenge chances · bodySize when Law 1 unlocks · exemption
  flag) — patch a curated artifact, never re-derive; the census CSVs are the
  input, the manifest is the decision record.
- **Order:** (1) danger pass on the SW 161 — buildable NOW from the census;
  (2) `dumpdb.py` GraphicData widening (small tooling fix) → then (3) the
  bodySize-visual pass. The three-arm data stays current only against
  fingerprint `1742630eb6253187` — re-verify before executing.
- Non-SW offenders (Jurassic herbivores, `Titan` the unidentified 1.0-
  commonality beast) get a second manifest wave after the SW pass proves the
  curve in play.

## 4. Open for the owner

1. Law 2: confirm no real-mass override (recommended).
2. Law 3 numbers: ✅ RULED (owner card, 2026-08-31) — QUICKTEST FIRST: the
   coefficient is tuned by a muffalo-vs-unarmored-pawn quicktest (MEASURED
   outcomes) at the next game window before the manifest freezes.
   **QUICKTESTED 2026-08-31 (FOUNDRY, BEAST_DANGER_NORMALIZATION_1):** a
   single `jawa/damage` Blunt hit at K x bodySize for K in {12, 13.5, 15},
   bodySize 2.4 (muffalo class, unarmored colonist, apparel stripped) —
   **never produced a clean single-hit "down"** at any tested location.
   Torso absorbed 29-44 raw damage with no down at any K (painTotal ~0.4,
   Moving ~0.46 at the top of that range — well under the down threshold).
   Head hits at the same K killed outright (skull HP is low). A follow-up
   sweep at Torso found the transition is **bimodal, not smooth**: 44-48
   damage still survived clean, 50-70 killed outright, with no clear
   "downed, not dead" middle band observed. **Conclusion: "one hit downs"
   is not literally achievable via a single TakeDamage instance at any K
   in the ruled 12-15 range — RimWorld's downed state does not scale
   smoothly with raw damage.** Shipped with **K=15** (top of the ruled
   band, maximizes casual lethality within it) on the understanding that
   the design's real threat model is a short flurry (2+ hits inside the
   sublinear-DPS cooldown window, or a multi-tool creature landing more
   than one tool per round), not one atomic strike. Full manifest and
   patch: `mandrake.rsw.beastnorm`, `data/beast_norm_manifest.csv`.
3. The empty seas (zero marine fauna in Ocean/Lake biomes — MEASURED): out
   of scope here, but the three seas holding nothing alive is a
   worldbuilding hole worth its own item.

## 5. Execution note (FOUNDRY, 2026-08-31)

The frozen fingerprint `1742630eb6253187` this doc cites for
`beast_census.csv`/`beast_roster.csv` no longer matches the live mod set
(`refresh.py --fingerprint` now reads `0245d9fd5f108808`, 585 mods). The
SW-animal content itself was unaffected (spot-checked Acklay's XML against
its census row: exact match), but the shipped `mandrake.rsw.beastnorm`
manifest was built by parsing `mlie.starwarsanimalcollection`'s own
`Races_Animal_SW.xml` directly (all 160 SW beast `ThingDef`s live in that
one file) rather than trusting the stale CSV, which sidesteps the
staleness question entirely for this mod. The two roster CSVs still need
a re-harvest before anything else leans on them.
