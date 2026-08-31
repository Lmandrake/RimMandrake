<!-- status: draft — BENCH synthesis of the three-arm beast fan-out, 2026-08-31. Owner's law: bodySize tracks visual size (spindly exception); mass matches scale; danger matches size — "a bull casually kills someone without intending to." Data: beast_census.csv (1,022 rows) · beast_roster.csv (581 kinds) · vanilla curves (arm 3, quoted here). -->
# Beast Normalization — size, mass, and casual lethality

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
