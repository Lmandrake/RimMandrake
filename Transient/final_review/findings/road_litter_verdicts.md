# Road litter triage — verdicts (46 fragments + 17 stubs), 2026-09-08

Read-only triage against `Transient/final_review/findings/roads_settlements.md` §1.
Rebuilt the same road graph from `links.json` (1,241 edges, 1,279 tiles, 47
components) to recover exact tile membership per fragment/stub — the prior
audit only gave counts and a "worst 10" list. All numbers below reproduce that
audit's totals exactly (46 small components sized 2-9; 17 dead-end chains
landing on a junction, matching its "worst 10" pairs one-for-one).

**Rule used per verdict:**
- **KEEP-AS-RUIN** — the tile(s) unique to this fragment/stub (i.e. excluding a
  stub's junction end, which stays reachable through its other branches
  regardless) carry a ruin-typed landmark/mutator (`Ruins`, `Abandoned*`,
  `Ancient*`, `TerraformingScar`), sit in machine country (biome `Scarlands`,
  `AB_MechanoidIntrusion`, region `Fall Line*`), reach a named natural
  landmark (cave, oasis, chasm — still "deliberately routed," just not
  archaeological — noted as such in the reason), touch a settlement too far
  (>2 hex-hops) to cheaply connect, or — for the 46 fragments — simply carry
  the `AncientAsphaltHighway` def with none of the above (ancient roads are
  ruins by definition; **100% of the 46 fragments are this def**, so none
  qualify for DELETE, which is scoped to dirt/stone litter).
- **CONNECT** — a dead-end sits 1-2 hex-tiles from an **off-road settlement of
  a faction that isn't deliberately roadless** (Deep Desert Tribes never build
  roads; Wildsteam Clan's newest seats were vetted with no road requirement
  per `ASHKARR_WORLD_DEFINITION.md` §7 — proximity to those is written up
  under KEEP-AS-RUIN with a "do not connect" note instead).
- **DELETE** — a dirt/stone stub/fragment whose own unique tiles carry no
  landmark, no ruin mutator, aren't machine country, and reach no settlement
  within 2 hops — litter serving nothing, pointing at nothing, in living
  country.

## Fragments (46, all `AncientAsphaltHighway` — 0 dirt/stone, so 0 DELETE-eligible)

| Frag | Tiles | Def(s) | Verdict | Reason |
|---|---|---|---|---|
| FRAG_1 | [301, 9087] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 9087 (Dilapidated Gotrarobil, Ruins) — deliberate ruin archaeology. |
| FRAG_2 | [938, 12910] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Hanging Wood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_3 | [1528, 16448] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Ammonia Flats — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_4 | [2378, 21548] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in ExtremeDesert/Anvil — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it (1 hex-hop from the network, but nothing it would serve). |
| FRAG_5 | [3147, 8008] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Ammonia Flats — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_6 | [3341, 8200] | AncientAsphaltHighway | KEEP-AS-RUIN | Touches settlement The Revision (tile 8200) but sits 16 road-hex-hops from the network — too remote for a 1-2 tile connect; AncientAsphaltHighway is ruin infrastructure regardless. |
| FRAG_7 | [3398, 17953] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Frostcaps — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_8 | [3943, 21213] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Nightspill — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_9 | [5619, 13735] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/South Crags — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_10 | [6045, 17615] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Stillwood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_11 | [6298, 11159] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in ExtremeDesert/Kiln — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_12 | [7624, 7625] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Stillwood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_13 | [8002, 8003] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Deadstone — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_14 | [8258, 8263] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Stillwood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_15 | [12118, 12119] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in RUT_NightsideIce/Nightspill — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_16 | [14288, 14290] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Ammonia Flats — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_17 | [14463, 14470] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 14470 (Gane Quarry, AncientQuarry) — deliberate ruin archaeology. |
| FRAG_18 | [16420, 16421] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in BiomeGRimond/Deadstone — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_19 | [17906, 17910] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Frostcaps — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_20 | [627, 6182, 11044] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Ammonia Flats — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_21 | [656, 6358, 11218] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in ExtremeDesert/Anvil — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_22 | [939, 12914, 12918] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Hanging Wood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_23 | [2113, 19961, 19963] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 19961 (Icy Ape Stronghold, AncientGarrison) — deliberate ruin archaeology (also only 1 hex-hop from the network, but the reason it exists is the garrison, not a network gap). |
| FRAG_24 | [2133, 9703, 20080] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in RUT_NightsideIce/The Verge — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_25 | [2765, 14152, 14153] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Stillwood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_26 | [3939, 8799, 21196] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Nightspill — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_27 | [5612, 13712, 13713] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 13712 (Goga Town, Ruins) — deliberate ruin archaeology. |
| FRAG_28 | [5622, 10479, 10483] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Hanging Wood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_29 | [6037, 14133, 14134] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in BiomeGRimond/Deadstone — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_30 | [6064, 6065, 16308] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in RUT_NightsideIce/Deadstone — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_31 | [6143, 16409, 16410] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_PropaneLakes/Deadstone — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_32 | [6296, 11156, 14387] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in ExtremeDesert/Dune Sea — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_33 | [7262, 15366, 15371] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Nightspill — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_34 | [10382, 10383, 10386] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 10386 (Toxxada Ruins, Ruins) — deliberate ruin archaeology (also only 1 hex-hop from the network, but the ruin is the point, not a gap to fix). |
| FRAG_35 | [117, 7984, 16310, 16311] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment terminates at/passes tile 117 (Nehistdos Ruins, Ruins) — deliberate ruin archaeology. |
| FRAG_36 | [4909, 4914, 20550, 20551] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in Desert/Kiln — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_37 | [1711, 7271, 17544, 17549, 17550] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_RockyCrags/Twilight Crags — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it (1 hex-hop from the network, but nothing it would serve). |
| FRAG_38 | [3387, 8250, 8251, 17877, 17879] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_RockyCrags/Rimewall — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_39 | [6291, 6317, 11150, 16558, 16560] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in ExtremeDesert/Dune Sea — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_40 | [984, 7464, 7465, 13184, 13189, 21550] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment sits in machine country (tile 7464, biome=Scarlands) — old road surviving hostile terrain. |
| FRAG_41 | [3872, 8734, 8735, 8736, 8737, 20799] | AncientAsphaltHighway | KEEP-AS-RUIN | Terminates at tile 20799 (Brinco City, AncientRuins_Frozen) — deliberate ruin archaeology; also touches settlement The Cracking Station (tile 8735) but sits 51 road-hex-hops from the network, far too remote to connect. |
| FRAG_42 | [6062, 6063, 14160, 14166, 17967, 17971] | AncientAsphaltHighway | KEEP-AS-RUIN | Isolated AncientAsphaltHighway segment in AB_MycoticJungle/Stillwood — no ruin landmark on-tile, but the def itself is a decayed ancient highway, not maintained infrastructure; nothing nearby to justify reconnecting it. |
| FRAG_43 | [6186, 9077, 11047, 16437, 16438, 16439] | AncientAsphaltHighway | KEEP-AS-RUIN | Touches settlement Coldfire (tile 9077) but sits 39 road-hex-hops from the network — too remote for a 1-2 tile connect; AncientAsphaltHighway is ruin infrastructure regardless. |
| FRAG_44 | [61, 2791, 7649, 7651, 11060, 14308, 14309] | AncientAsphaltHighway | KEEP-AS-RUIN | Fragment sits on a TerraformingScar mutator (tile 61) — deliberate ruin archaeology; also the longest-standing "worst 10" entry (7649↔11060, isolated both ends), far (44+ hops) from the network. |
| FRAG_45 | [1908, 17897, 17898, 17899, 17900, 17901, 18732] | AncientAsphaltHighway | KEEP-AS-RUIN | Terminates at tile 17897 (Dilapidated Asussia, Ruins) — deliberate ruin archaeology; also touches settlement Cold Archive (tile 17901, itself lore-flagged as sitting in the Horror Wastes per the worldbuilding doc) but 10 road-hex-hops from the network. |
| FRAG_46 | [3987, 5074, 5075, 9935, 13176, 21482, 21483, 21507, 21508] | AncientAsphaltHighway | KEEP-AS-RUIN | AncientAsphaltHighway fragment sits in machine country (tile 13176, biome=Scarlands) — old road surviving hostile terrain; also reaches Colcrouscu Saline Flats landmark (tile 21507). |

## Dead-end stub chains (17, dead-ending at a live junction)

Reasoning is scoped to each stub's own unique tiles (everything except the
junction tile itself, which stays reachable through its other branches
regardless of this stub).

| Stub (leaf→junction) | Tiles | Def(s) | Verdict | Reason |
|---|---|---|---|---|
| 6486→19392 | [6486, 19392] | DirtRoad | **CONNECT** | Dead-end leaf 6486 is 1 hex-tile from off-road Free Droid Enclaves settlement 'No Master' (tile 19350) — lay **6486–19350 (DirtRoad)** to bring it onto the network. |
| 6474→675 | [6474, 11335, 675] | DirtRoad ×2 | KEEP-AS-RUIN | Unique tile 11335 is biome Scarlands (machine country). Passes within 2 tiles of Wildsteam Clan settlement 'Oilpalm' — that faction's newest seats are deliberately roadless per `ASHKARR_WORLD_DEFINITION.md` §7; do not connect. |
| 7228→12087 | [7228, 12086, 12087] | StoneRoad ×2 | KEEP-AS-RUIN | Unique tile 7228 = Bilgua Wall (Cliffs) — a named natural landmark reached only via this branch, not aimless litter (no settlement within 3 hops to connect instead). |
| 5613→5617 | [5613, 10473, 5617] | StoneRoad ×2 | KEEP-AS-RUIN | Unique tiles reach Menba Fracture (Chasm, 5613) and Nedos Cliffs (Cliffs, 10473); junction end 5617 is itself Fort Ram (AncientGarrison ruin), reinforcing the deliberate routing. |
| 21281→10451 | [21281, 10452, 10450, 10451] | DirtRoad ×3 | **DELETE** | Unique tiles 21281/10452/10450 carry no landmark, no ruin mutator, no settlement within 2 hops, in living ExtremeDesert/Long Sand dunes — the oasis at the junction end (10451, White Oasis) stays reachable via its other two branches regardless. Genuine litter. |
| 17232→17243 | [17232, 17233, 17240, 17243] | StoneRoad ×3 | KEEP-AS-RUIN | Leaf tile 17232 = Harshnose Ruins (def `Ruins`) — ruin-flavored, uniquely served only by this branch. |
| 19959→3728 | [19959, 3733, 19928, 3728] | StoneRoad ×3 | KEEP-AS-RUIN | Leaf tile 19959 uniquely reaches Lesatros Cave Network (Cavern) — natural point of interest, not aimless litter (no settlement within 3 hops). |
| 12417→9171 | [12417, 2476, 12393, 852, 12395, 4310, 9171] | DirtRoad ×6 | KEEP-AS-RUIN | Leaf tile 12417 = Hinin Outpost (AbandonedColonyOutlander); passes through region Fall Line Barrens (machine country); tile 4310 carries AncientQuarry/AncientRuins mutators. Triple-signal ruin road. |
| 17266→1665 | [17266, 17267, 9221, 9222, 4363, 17274, 1665] | DirtRoad ×6 | KEEP-AS-RUIN | Leaf tile 17266 = Waspaia Village (AbandonedColonyTribal) — ruin-flavored, uniquely served only by this branch. |
| 21684→9958 | [21684, 6749, 11610, 6750, 21691, 21689, 9958] | DirtRoad ×6 | KEEP-AS-RUIN | Leaf tile 21684 = Ash's Howl (def `TerraformingScar`) — ruin-flavored mutator/landmark, uniquely served only by this branch. |
| 13602→15919 | [13602, 1053, 13600, 5499, 10359, 5498, 15919] | DirtRoad ×6 | KEEP-AS-RUIN | Leaf tile 13602 = Coro Armory (AncientGarrison) — ruin-flavored, uniquely served only by this branch. |
| 15905→4138 | [15905, 15906, 12227, 12228, 8997, 286, 8999, 4138] | DirtRoad ×7 | KEEP-AS-RUIN | Leaf tile 15905 = Dead Sarlacc, mid-chain tile 286 = Wombat Hand Quicksand Pits — both named natural hazard landmarks reached only via this branch, not litter. |
| 20514→20405 | [20514, 4891, 12988, 9751, 9747, 12984, 4886, 20406, 20405] | DirtPath ×8 | KEEP-AS-RUIN | Leaf tile 20514 = Hisan Stronghold (AncientGarrison) — ruin-flavored, uniquely served only by this branch. |
| 10384→10355 | [10384, 5523, 13622, 1057, 13624, 13625, 10352, 10353, 10355] | StoneRoad ×8 | KEEP-AS-RUIN | Unique tile 13622 (Colmea Cavern) and tile 1057 both carry `TerraformingScar`; junction end 10355 is Isaambrei Warehouse (AncientWarehouse ruin). Ruin-flavored throughout. |
| 17276→8147 | [17276, 3284, 17264, 3285, 8149, 144, 8144, 8146, 8147] | StoneRoad ×8 | KEEP-AS-RUIN | Leaf tile 17276 = Oldzebra Village (AbandonedColonyTribal); mid-chain passes 3 more named landmarks (Thierado Ravine, Itoncroitro Dry River, Orangehoof Canyon). Densely authored ruin route. |
| 3384→1024 | [3384, 17865, 3382, 17857, 1762, 17853, 5322, 17861, 5323, 13421, 1023, 13423, 2643, 13431, 2645, 13425, 1024] | StoneRoad ×16 | KEEP-AS-RUIN | 17-tile route (the longest stub) threads 6 named landmarks unique to it (Vexador Cave Network, Farlaistia Cavern, Yoko's Caves, Cairmila Divide, Bamenda Karst Hollows, Omentbum Tunnel) — clearly hand-authored cave/valley touring road, not litter, though natural rather than archaeological. |
| 4000→675 | [4000, 8861, 263, 8862, 4002, 21572, 2382, 21576, 6538, 16746, 1577, 16742, 3196, 16737, 3194, 16729, 6475, 11331, 675] | DirtPath ×7, DirtRoad ×11 | **CONNECT** | Richly ruin-flavored already (Alex's Launch Site, Dilapidated Toxo, Govexasai Scar, Blueclaw Scar — all `Ancient*`/`Ruins`/`TerraformingScar` — and passes through settlements The Godmouth mid-chain and Founder's Kiln at the junction end), but leaf 4000 is also 1 hex-tile from off-road Free Droid Enclaves settlement 'Unbound Exception' (tile 21560) — lay **4000–21560 (DirtPath)** to bring a third settlement onto this road for free. |

## Summary

- **63 items triaged** (46 fragments + 17 stubs).
- **KEEP-AS-RUIN: 60** (46 fragments — all `AncientAsphaltHighway`, ruins by
  def — + 14 stubs carrying a ruin/machine-country/landmark signal on their
  own unique tiles).
- **CONNECT: 2** — both bring a currently-off-road Free Droid Enclaves
  settlement onto the network for the cost of one new tile:
  - **6486–19350 (DirtRoad)** → connects **No Master**
  - **4000–21560 (DirtPath)** → connects **Unbound Exception**
- **DELETE: 1** — stub **21281→10451** (tiles 21281, 10452, 10450; DirtRoad
  ×3): dead spur through empty ExtremeDesert/Long Sand dunes, no landmark, no
  ruin mutator, no settlement within 2 hops; the oasis at its far end (White
  Oasis) stays reachable via two other branches regardless.

Nothing on disk was changed; this is a recommendation table only.
