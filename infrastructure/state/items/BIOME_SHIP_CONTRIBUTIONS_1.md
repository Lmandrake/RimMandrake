# BIOME_SHIP_CONTRIBUTIONS_1 — what each biome uniquely gives the ship

Owner, 2026-09-24, typed in chat during the Sump sitting, verbatim:

> "Another every biome pass: let's ask the question 'how can this biome uniquely
> add something to the ship?' Like the slippery bitumen surface might be used. Or
> the burning statues. What can they take and improve their ships environment
> with?"

The campaign is about the ship (his ruling the same sitting, on the asphalt/road
question: *"this one is about the ship"*). So every biome owes an answer: something
a player can take from it and build INTO the gravship — a floor, a light, a larder,
a machine — that no other biome provides.

## the pattern

Third of the every-biome passes, same shape as `BIOME_NUISANCE_NORMALIZATION_1`
and `INDIGENOUS_TECH_REVISIT_1`: **each biome sitting from now on records its
ship contribution in the running list below; the normalization/consistency sweep
runs at the end of the last biome detailing.** No sweeping cross-biome edits
before then.

## running list

Normalized 2026-11-11 (CLAUDE_STEVEDESKTOP_OFFLINE2, Whittle). One row per biome composed into Baroque Biomes
(`src/RimMandrake/Biomes.compose.json`). The `defs` column is the claim: every def named there is checked by
`python3 src/RimMandrake/Utils/ship_contributions.py` (exit 0 = every biome covered, every named def exists and can
stand on a gravship deck the way the engine decides it, and each row's gift is the biome's own). "built" = from the
architect menu on the deck; "installed" = a minifiable thing the player acquires and installs aboard. Rows marked
*delegated* were chosen by an agent under `delegation_policy.md` §2 (owner, 2026-10-22: agents decide nearly
everything), not ruled by him; the four new builds of this pass are marked *new*. A fresh design judge (opus) read every
row against the alternatives each biome ships (`whittle/biome_ship_contributions_1/evidence/design_judge.json`); its three
changes are applied (Greentide's sealed floor dropped, the hexplate rebalanced, Terminal Biomes led by the sun-sphere).

| biome | ship contribution | defs | source |
|---|---|---|---|
| The Abyss | **the summ great bone**: set aboard, a summ egg hatched on the ship imprints on the crew; plus the fold lamp's warm air lane | `RM_SummGreatBone` `RM_FoldLamp` | Abyss mod; *delegated* |
| Blue Desert | **the cold hold**: a blue-ice cold-sink rack keeps a hold cold through a blackout with no power | `RM_ColdSinkRack` | owner by card 2026-09-24 (`the_blue_desert.md` §7) |
| The Cauldron | **the hull liner rig**: one rig glazes the whole ship's skin against acid, from ground vexxith plate | `RM_HullLinerRig` | Cauldron mod; *delegated* |
| The Contagion | **the ship-mounted cloud repulsor**: the Helix field device as a gravship hardpoint, bought or won, installed on substructure | `RM_CloudRepulsorShip` | `the_contagion.md` (devices ruled); Helix trader/quest owner by card 2026-10-15 |
| The Cracked Lands | **the fossil case**: a whole fossil skeleton from the skeleton seams, cased for the bulkhead (beauty 14) | `RM_FossilCase` | *new*, *delegated*, from the cast doc's bulkhead fossil |
| Fever Wood | **the sekkulaath tank**: the swamp's captive producer carried as ship stock | `RM_SekkulaathTank` | FeverWood mod; *delegated* |
| Gelatinous Slime | **the archive vat**: grows a dead colonist back from the slime's last reading of them, anywhere the ship goes | `RM_ArchiveVat` | `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1`; *delegated* |
| Greentide | **the dry-air blower**: cools a cabin without dumping heat into any room, and holds back the wet at its threshold | `RM_DryAirBlower` | Greentide mod; *delegated* |
| Lantern Deeps | **lanternstone aboard**: floor and wall that glow forever and need no lamp | `RM_LanternstoneFloorConstructed` `RM_BuiltLanternstoneWall` | LanternDeeps mod; *delegated* |
| Leaning Scrub | **the wind vaporator**: combs a thin, reliable margin of water out of the passing wind | `RM_WindVaporator` | LeaningScrub mod; *delegated* |
| Long Shade | **the shade awning**: real shade on an open deck under the Direct Sun | `RM_LureAwning` | `long_shade_bedazzle_2026-09-27.md` §6 (shade awning); *delegated* |
| The Miasma | **the decay cell**: power from rot, in a bed of delta loam, silt and salt | `RM_DecayCell` | Miasma mod; *delegated* |
| Pyrelands | **the furnace-hide heat bank**: furnace-beast hide gives back banked sun, a heater with no fuel and no power | `RM_FurnaceHideBank` | *new*, *delegated* |
| The Rust Cathedral | **pattern hull**: hull seeded with live pattern metal that mends itself (120 HP a day) | `RM_PatternHull` | *new*, *delegated* |
| The Sleeping Ice | **tellurox hexplate**: a deck floor of the tellurox's permanent shell plates | `RM_TelluroxHexplate` | *new*, *delegated* |
| Stillsand | **the precision-lens kit**: the lens-glass solar still and sun lance, fuel-free on an open deck (the earlier "ship lens array" row named a part that was never built; this is what ships) | `RM_SolarStill` `RM_SunLance` | `STILLSAND_GLASS_LENS_CHAIN_1` §11 (owner-typed lens chain) |
| Terminal Biomes | **the sun-sphere**: a cultured ollumin that grows into its own small sun, lighting and growing crops with no power or lamp; and the **cryoponics vat**, the Chill's deep-bed plants raised anywhere | `RM_SunSphere` `RM_ChillCryoponicsVat` | TerminalBiomes mod; *delegated* |
| The Forge | **spunstone hull and floatstone door**: airtight floatstone ship parts | `RM_SpunstoneHull` `RM_FloatstoneDoor` | owner by card 2026-10-03 (`FORGE_SPUNSTONE_SOURCES_1`) |
| The Rot | **the swallowed drive core** (multiplies the ship's range) and **the living mat root** (a warm creeping deck mat) | `RM_SwallowedDriveCore` `RM_LivingMatRoot` | TheRot mod; *delegated* |
| The Sump | **glasswalk** flooring, **gaslight lamps** and the **tar vault** larder | `RM_Glasswalk` `RM_GaslightLamp` `RM_TarVault` | owner 2026-09-24 (his own examples); `SUMP_WALKWAYS_1`, `SUMP_GASLIGHT_1`, `SUMP_TAR_VAULT_1` |
| Warscar | **the aerosol screen** (a clean-air dome over the ship in any polluted biome) and the **glower shield panel** | `RM_AerosolScreen` `RM_GlowerShieldPanel` | `WARSCAR_AEROSOL_SCREEN_1` (owner turn 4, 2026-09-30) |
| The Wastes | **the waste cask bay**: a shielded, powered rack that lets a ship carry waste casks safely | `RM_WasteCaskBay` | `wastes.md` (the waste run by gravship); *delegated* |
| Webwork | **the traction lance**: a crewed tether emplacement that reels a target or a downed colonist in | `RM_TractionLance` | Webwork mod; *delegated* |
| Weeping Stones | **the ancient condenser plant**: the oldest gorrask's air-water machine, installed on the ship | `RM_AncientCondenserPlant` | WeepingStones mod (its own text: "install it on a ship") |

## spec

Per biome at its sitting: name the contribution(s), make the relevant defs
ship-placeable (gravship-buildable floors/furniture where the mechanics allow),
and record the row here. At the end: sweep for gaps, balance the set so every
biome's gift is distinct and worth landing for, and card the matrix to the owner.

## verify

Every shipped biome mod has at least one ship-buildable contribution or an
owner-ruled exemption; the list here matches what the mods actually ship.

## criteria

Landing in a biome changes your ship, not just your stores — the gravship becomes
a scrapbook of everywhere it has been.
