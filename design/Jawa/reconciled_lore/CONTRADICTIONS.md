# Contradictions found, and which side won

Every disagreement the 2026-08-29/30 reconciliation pass found between lore
documents, with the settling authority. Where canon.yml already records one, it
is cited rather than re-argued. **Nothing here is newly decided** — this is the
map of decisions already made, so no dead reading comes back.

## World and map

| # | disagreement | winner |
|---|---|---|
| 1 | Water fraction 25% / 22–28% / 8.6% / 8.1% / 6.9% across docs | **5.19% liquid / 6.46% incl. sea ice** — canon.yml, measured 2026-08-22/23. `the_one_map.md:100/130` and meta.json still carry dead values |
| 2 | Habitable ring 34–57 (the evidence) vs 40–57 | **40–57, owner ruling 2026-08-21** — the stronger evidence lost, correctly; design decision, not a finding |
| 3 | "+14 °C is the terminator" (tidally_locked, hydrology) vs the mod curve | **Axis misread**: the mod's curve runs on ARC; its +14 is arc 45°, its terminator −37. Ours (+14 at terminator) is what ships; the mod is worldgen-only and cannot reach the painted save. canon.yml > temperature_curves |
| 4 | Lake biome cut (biome_review) vs keep | **Keep** — The Scald IS the Lake biome; cutting the def deletes a named sea [owner 2026-08-20] |
| 5 | Idyllic Meadows & Gelatinous Superorganism cut (2026-08-04) vs painted map | **Painter wins for Gelatinous + ZBiome_Grasslands** [owner 2026-08-20]; Idyllic stays cut. cut_vs_painted diff run once, closed — no third case |
| 6 | Start colony "The Setdown" at tile 2476 vs none | **Struck** [owner 2026-08-24] — no canon start colony; paint/populate/repair tools still carry stale guards (see GAPS) |
| 7 | Faction count 14 / 13 / 12 / 11 | **13** (canon.yml); Unbound Hive cut as a faction, kept as creatures; 12 = dossiers/settlement-holders |

## History and precursors

| # | disagreement | winner |
|---|---|---|
| 8 | The Rakata released the bioweapon (first R-W3 naming) vs victims | **Victims** — retracted the same day [owner 2026-08-20]; the flesh belongs to the unnamed Assailant |
| 9 | Victims-only vs tyrants | **Both** — victims AND dark-force tyrants; the reversal is the designed player arc [owner 2026-08-29] |
| 10 | `what_the_machines_are.md` chose "the Forsakens" and rejected Rakata (Legends risk) | **Rakata named in full** [owner 2026-08-20]; reconciled by the endonym/exonym ruling — the Forsaken IS what moderns call the Rakata |
| 11 | Sleepers = the builders vs the war generation | **War generation** — grown children of the last great Rakata [owner 2026-08-29] |
| 12 | Mechanoids leave the raid roster (proposed twice) | **They stay, in full** [owner 2026-08-15 and 2026-08-20]; emphasis at the vaults is allowed, deletion is not |

## Factions

| # | disagreement | winner |
|---|---|---|
| 13 | Roster's twelve faith NAMES vs the twelve `<ideoName>` on disk | **faction_religions.md/_spec.md** — eight roster names exist nowhere; roster carries the mapping banner |
| 14 | Empire tech Spacer (roster, world_spec) vs Ultra | **Ultra** — the shipped def, unpatched (canon.yml > empire) |
| 15 | Empire xenotype mixes (roster :711; the 41%-Echani matrix cell) | **The owner's race/faction matrix as corrected** — Baseliner 76.9% (canon.yml) |
| 16 | concept.md "Empire = fused vanilla + Outer Rim Galactic Empire" | **One Empire**: vanilla `Empire` reskinned; OuterRim FactionDef cut once-and-for-all, its MOD stays as gear donor [owner 2026-08-20/28] |
| 17 | Geonosian ↔ Free Droid "Cold / no trade" (roster) vs allied | **Formally ALLIED, with trade** [owner 2026-08-17] |
| 18 | Blackstar as "every pirate" (fixedName leaked to 6 defs) | **One outfit, never a genus** [ruled 2026-08-22]; sibling zeroing must still be proven at worldgen |
| 19 | Salvagers as a separate casket faction | **Folded into Junkers** (canon.yml > ruled); executed in the world save |
| 20 | Miraluka four-role placement vs removal | **Gone, completely, every version** [owner 2026-08-20] |
| 21 | Wildsteam as a steam-tech cult (one brainstorm) | **Spring-mist life-web people** — the name misleads [owner 2026-08-29] |
| 22 | Tusken shortest range *because of water* vs very-low thirst tier | **Doctrinal, not physiological** (W3) — they could range far and choose not to |
| 23 | Deepwater holds "every natural water tile" vs Hutt oases / Wildsteam springs | **Aquifers only** (W6) — surface water belongs to whoever sits on it |
| 24 | Purification "expensive v2 tech" vs Deepwater's cheap desalination | **Expensive for the PLAYER to build** (W5) — the monopoly and the salvage stills stand |

## The clan, the faith, the ship

| # | disagreement | winner |
|---|---|---|
| 25 | concept.md "Articles of Passage, Nomad+Tunneler" | **The Salvation**, five memes on the tribes / four on the player .rid — corrected in place 2026-08-22 |
| 26 | `VME_Nomad` dropped (2026-08-20) vs kept | **Kept on the NPC tribes** [owner 2026-08-21, reversal]; the player .rid legitimately differs — do not harmonize |
| 27 | Two half-Jawa xenotypes (merge question) | **`MandrakeJawa` outright** [measured 2026-08-19 — it already contains the other's substance] |
| 28 | `Outland_EggLayer` as the egg mechanism | **Does nothing** [measured 2026-08-22]; `SEX_Ovipositor` + `SEX_AlwaysAphrodor` are the working route; Outland gene kept for icon only |
| 29 | Kolyska vs the Utinni as the ship's name | **Not a contradiction — a rename with a register rule** [owner 2026-08-15]: player-facing = The Utinni; only the Cradle-Mind says Kolyska |
| 30 | The ship AI as one plural mind that "believes it is Ohm" (2026-08-08) vs nine tenants | **No integrating self** [owner 2026-08-15] — nine personas + the Cradle's purpose, nothing above them; "schizophrenia as damage" withdrawn; the CREW believe Ohm possesses it |
| 31 | The live LLM Council of Voices vs v1 | **v1 has no talking ship** [owner 2026-08-15] — felt, not heard; the Council is the v2 delivery |
| 32 | Five founders vs six | **Six** — Sekki Vosh ruled in over diluting Tobb [owner 2026-08-15] |
| 33 | Ration-as-sacred austerity (early persona doc) | **Jawas prize delicacies** — `NutrientPasteEating_Disgusting` ships; paste is tolerated, not sanctified [owner 2026-08-15] |

## Arms and machines

| # | disagreement | winner |
|---|---|---|
| 34 | L4 "ion is a warm breeze to flesh" vs LOCKED SPEC D1 | **D1's gradient** [owner 2026-08-08; L4 amended 2026-08-22]: flesh is the weakest tier, not exempt |
| 35 | Ion machine tier "blocked because mechs can't take hediffs" | **Wrong mechanism** — the engine whitelists stun defs by identity; the built route re-issues as vanilla EMP [measured 2026-08-22] |
| 36 | Vanilla firearms as the low-tech floor (audit advice) | **They stay cut** — theme over balance, knowingly [owner 2026-08-22]; mech weapons the one reversal |
| 37 | JDS droids "never taken alive — a feature" (2026-08-13) | **Capturable on the Droidworks port** [owner 2026-08-29] — the old ruling was platform-forced and the platform is dissolving |
| 38 | Droid system "spec then PARK; v1 plays three frameworks raw" (early 2026-08-29) | **Reopened and building the same day** [owner 2026-08-29]: Droidworks, fully independent, packs retire with credit |
| 39 | "Data spike exists in Droid Depot" (droid_ruling §3) vs census | **No data spike ships in any accepted mod** — the census correction stands; the existing verb is the reprogram job; the faction-keyed spike is OURS to author (and now is, in Droidworks) |
| 40 | Turret bands (emplacement 40–200 / artillery 250–600 / turbolaser 800–2000, 2026-08-14) vs (squares)² | **(squares)² doctrine** [owner 2026-08-29] supersedes the three fixed-gun tiers for canon-roster turrets; armoury generator header says so |
| 41 | "The pilot console gates flight" | **False** — the VGE cockpit route needs only BasicGravtech; never write console-gates-flight |
| 42 | Bestiary count 78 vs 108 | **108 named, 0 built** (canon.yml > bestiary) |
| 43 | Early "rogue androids poison the water they hold" (2026-08-04 layer) vs the authored Free Droid Enclaves | **Evolved, not contradicted**: the Enclaves settle un-drinkable ground and crack water for fuel. The Biotech-pollution seeding half was never restated in FACTION_SPEC → carried as a GAP, not silently dropped |
