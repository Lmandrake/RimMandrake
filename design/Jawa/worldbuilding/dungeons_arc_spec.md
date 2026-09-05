<!-- status: live -->
# The dungeons arc — Assailant complex + six Forsaken vaults

> 🔶 **BUILD SPEC, not final creative lock-in.** `FUTURE_VECTORS.md` names this arc
> explicitly "Assailant flesh dungeon + Forsaken vault design **with the owner**" —
> full creative lock-in (exact map authoring, dialogue/letters, hand-finish
> set-pieces) stays a bench sitting, not a solo pass. What follows consolidates
> everything already RULED across `ASSAILANT_FLESH_DUNGEON_1` and
> `VAULT_DUNGEON_CONCEPT_1` (both closed 2026-08-30) into one buildable spec, adds
> the technical route (KCSG via the bridge, confirmed available), drafts the safe
> pieces for real, and marks every remaining creative call HELD FOR OWNER.
> Written to resolve the "thin item" flag on `ASSAILANT_DUNGEON_BUILD_1` and
> `VAULT_DUNGEON_BUILD_1` (`infrastructure/state/items/`).

Sources this leans on, not restated in full: `reconciled_lore/03_deep_history.md`
(the canon triad, the Assailant, the vaults), `infrastructure/state/canon.yml`
(`rakata.*`, `assailant_reveal_arc`, `cradle_memory`, `anomaly_content`),
`ANCIENTS_AS_RAKATA_SPEC.md` ("the dark half"), `vault_siting_prep.md` (the six
sites), and `review/assailant_flesh_sheet.decisions.json` +
`review/assailant_flesh_sheet.html` (the 70-def content palette, owner-ruled
keep-for-dungeon 2026-08-30). Register: `Rakata` endonym, **`the Forsaken`**
exonym in all authored player-facing text.

## 0. Ruled vs drafted here vs held for the owner

| | source |
|---|---|
| **RULED** (owner sittings, do not re-litigate) | site families, thaw-gate concept, guardian register, learning chain/endgame, vault count+siting+type mix, concentric grammar doctrine, wake/loot/leave payoff ladder, LARGE maps, template-then-hand-finish authoring route — all cited below with their canon.yml/item-history source |
| **DRAFTED FOR REAL, this pass** | this doc's narrative/site writeup for both dungeons; the content-palette-to-defName assignment (§2.3, §3.4); the map-layout CONCEPTS (§2.4, §3.3); one illustrative KCSG `StructureLayoutDef` skeleton (§3.5); the quicktest-proven verify bar (§3.6) |
| **RULED 2026-09-01** (owner, via BENCH cards) | thaw trigger = QuestNode + map signal; power core = vanilla `AIPersonaCore`; vaults 325×325; V5 gets a new organic landmark; `RUT_` tier for all dungeon defNames; KCSG pawn symbol = `SymbolDef`+`pawnKindDef`; territories mod = Faction Territories (§2.7, §3.8, §3.9) |
| **HELD FOR OWNER** | exact KCSG authoring of all templates and all seven maps; dialogue/letters for the reveal beat, the wake/loot/leave branches, and the ship-claim thread; per-vault hand-finish set-pieces; the territorial-access conflict mechanic (its own item); the bridge placement writes for the seven sites |

## 1. Shared spine

Both dungeons are the same reveal economy wearing two faces (canon.yml
`assailant_reveal_arc`, owner ruling on point 4 of `VAULT_DUNGEON_CONCEPT_1`):
ship memory-fragments triangulate, the Forgotten Arsenal/Free Droid Enclave
(FDE) trust chain gates what the ship will reveal, and both site families sit
in the same deep-Umbra neighborhood (Assailant complex adjacent to tile 20853;
20853 itself is vault V6). **The frozen Rakata and their frozen killer sleep
near each other — one pilgrimage, two revelations.**

- **Register guard** (canon.yml `rakata.victims_and_tyrants`): the Rakata are
  victims AND were themselves tyrants; the Assailant is never named, never
  sympathetic, and its horror is that it could do this even to the Rakata.
  Tyranny is REVEALED content — never ambient in a pre-reveal bio, label or
  tooltip, in either dungeon.
- **The Anomaly exception** (canon.yml `anomaly_content`): zero ambient Anomaly
  content in v1, except — the Assailant dungeon may use the Anomaly
  fleshmass/entity toolbox, and the sarlacc's own design (separate item) may
  draw on it too. Nothing else touches Anomaly content. The vault dungeons are
  NOT covered by this exception (per `VAULT_DUNGEON_CONCEPT_1`'s sitting brief:
  type-② vaults were describable without it).
- **No-worldgen doctrine** (`CLAUDE.md`, `the_one_map.md`): Ash'karr is the one
  frozen map. Nothing here generates a new planet or a new map layout at
  runtime from a seed — every site below is a FIXED tile on the existing,
  already-painted world, authored in place via the bridge's KCSG tools
  (§3.5) exactly the way every other piece of Ash'karr content is authored.

## 2. `ASSAILANT_DUNGEON_BUILD_1` — the first-impact complex

### 2.1 What it is

**The Assailant's first-impact point** — where its landing struck, "unknown and
undetected at the time, and triangulated far too long after all hope of
response had been lost" (canon.yml `assailant_reveal_arc`, owner verbatim). A
HUGE frozen complex, inert and dormant since the fall — not a routine
map-embedded ancient horror (those already occur on regular maps constantly
per the Arsenal/Rakata/Assailant background hum); this is *the* site, the one
place the whole war traces back to.

### 2.2 Site — deep Umbra

Fixed, deep-nightside, adjacent to tile **20853** (`VAULT_DUNGEON_BUILD_1`'s V6,
held for the frozen-Rakata vault). Region **The Umbra** (arc > 152°, the named
region already on the gazetteer — `ASHKARR_WORLD_DEFINITION.md` §3,
`worldgen_interactive_def.md` line 814 lists it among the 28 named regions; not
a name to invent). Pilgrimage-distance past the FDE's two deep-nightside
refugee seats (Coldfire, The Cracking Station) — "the last waypoint, rumor
carriers" (owner ruling, `ASSAILANT_FLESH_DUNGEON_1` history 2026-08-30). Exact
tile lands from the vault-siting analysis at a down-window placement pass —
**not committed to the world by this doc**; that bridge write is HELD FOR
OWNER/FOUNDRY at the next down-window (`rimworld-world-editing`'s
`world_commit` step, one driver at a time per `rimbridge`).

### 2.3 The thaw-gate

Owner ruling verbatim (`ASSAILANT_FLESH_DUNGEON_1` history, point 4): *"a
really huge complex with meaning and powerful knowledge, weaponry, defenses,
and a reason to have remained. Perhaps utterly frozen in the cold depths until
the players begin to wake/thaw it by bringing an old power core to its hidden
location."*

**Mechanical reading (drafted here, not yet built):**

- **Pre-thaw state**: the complex is inert on arrival — dormant fleshmass
  terrain/growths present as set-dressing (no guardian spawns, no hostile
  faction), the frozen witness scene visible but unreachable/sealed, a single
  legible objective (a socket, altar, or console requiring "an old power
  core") sited at or near the complex's hidden inner point.
- **Trigger**: the player HAULS/DELIVERS a power-core item (an existing salvage
  tier item, not a new artifact — candidate: whatever the campaign's highest
  scavenged power cell/AI persona core already is; confirm the exact def at
  build time rather than invent one) to that socket.
- **Thaw = activation**: delivering the core flips the complex from dormant to
  hostile — guardian spawns come online (Anomaly entities + the pale Geonosian
  turret reskin, §2.5), previously-sealed passages open, and the reveal beat
  (§2.6) becomes reachable. This is a one-way state change, authored as a quest
  signal/map event (rides `rimworld-quests` at build time — the "custom C# node
  needed?" call is HELD FOR OWNER, most likely answerable as "no, a QuestNode +
  map trigger suffices" but not proven this pass).
- Gating context: entry itself is mid-campaign, after the sleeper-sympathy arc
  is established (owner ruling point 5, `ASSAILANT_FLESH_DUNGEON_1`) — the
  quest chain that leads a crew here is downstream of droid trust → Cathedral
  trust (§2.6), not an early-game find.

### 2.4 Layout concept (drafted, not authored)

One dungeon, not six — no concentric-grammar requirement here (that's the
vault doctrine, §3.3). Proposed three-band structure keyed to the thaw state:

1. **Approach / outer galleries** — frozen, inert, dressed in dormant fabric
   (Floor/wall-fabric + Growths groups, §2.5): the complex reads as ancient and
   sealed, not yet dangerous. The socket/altar for the power core sits at the
   transition into band 2, so delivering it is a deliberate, irreversible step
   inward, not something a crew stumbles into by accident.
2. **Interior — the digested works** — post-thaw, guardians online. Set-pieces
   built from the `VFEI2_InfestedShip{Chunk,Module,Part}` family: "a Rakatan
   structure being DIGESTED — the only place tyranny and victimhood are shown
   in one image" (owner ruling point 4). This band carries the bulk of the
   Guardians group.
3. **Core** — the embedded witness + `FleshmassHeart`/`FleshmassNucleus` as the
   reveal-beat centerpiece; ship memory-fragment loot lives here (canon.yml
   `assailant_reveal_arc`: "loot recovered here triggers ship memory-surfacings
   — the dungeon feeds the ship its own past").

### 2.5 Content palette (drafted for real — the actual 70-row sheet, not invented content)

Owner ruling (`ASSAILANT_FLESH_DUNGEON_1` history, 2026-08-30, point 2): **ALL
70 rows of `assailant_flesh_sheet.html`** are the fabric/guardian roster,
frozen in `assailant_flesh_sheet.decisions.json` (`blanket: keep-for-dungeon`,
`decidedCount: 70`). Three rows get a **site-only exception** to their
campaign-wide cut (un-cut for this dungeon's placement only, cut everywhere
else): `DeadColumnMod`, `Trispike`, `Metalhorror`.

| group | count | representative defNames | role |
|---|---|---|---|
| Floor / wall fabric | 8 | `Flesh` (terrain — the dungeon floor), `Fleshmass` (corner-linked wall/floor atlas), `AA_BlackJellyWall`, `HorrorHive`, `VFEI2_HiveDoor`, `VFEI2_InsectJellyWall`, `VFEI2_KemianHive`, `AA_BlackCreep` (terrain) | the complex's own substance |
| Growths | 16 | `FleshmassHeart` (reveal-beat centerpiece candidate), `Fleshbulb`, `FleshSack`, `HorrorCrysalisVisceral`, `VFEI2_Hivenode`, `VFEI2_Jellyspreader`, glow-pod family | ambient life/set-dressing between bands |
| Guardians | 35 | Anomaly entities (`Bulbfreak`, `Chimera`, `Devourer`, `Dreadmeld`, `Fingerspike`, `FleshmassNucleus`, `FleshmassSpitter`, `Ghoul`, `Gorehulk`, `Noctol`, `Revenant`, Shambler family, `Sightstealer`, `Toughspike`, `Metalhorror`⚑, `Trispike`⚑) + Black Hive family (`AA_BlackDefiler`⭐, `AA_BlackScarab`, `AA_BlackSpelopede`, `AA_BlackSpider`, `AA_AcanthamoebaGiganteaHuge`, `AA_FoamBelcher`) + VFEI2 apex insectoids (`VFEI2_Empress`, `VFEI2_Patriarch`, `VFEI2_Gigalocust`, `VFEI2_Gigamite`, `VFEI2_Ironclad`, `VFEI2_Hellbeetle`, `VFEI2_Megawasp`, `VFEI2_Acidspitter`) + Horrors bonus find (`BroodLord`, `Terrorworm`, `Visceral`) | the body-horror core. ⭐ `AA_BlackDefiler` is already canon-assigned "The Assailant's flesh" on the turret register — the first hardware of this register. ⚑ site-only exceptions |
| Set-dressing | 11 | `VFEI2_InfestedShip{Chunk,Module,Part}` (★ direct match for the digested-Rakatan-works image), `AA_BlackCreeper`, `AA_BlackHiveMound`, `TrapIED_Deadlife`, `DeadColumnMod`⚑, `VFEI2_{Creeper,JellyFarm,LargeBurrow,Petroglypher}` | the reveal-beat set-pieces + hazard dressing |

**Guardian register split** (owner ruling point 3): Anomaly fleshmass/entity
toolbox = the body-horror core; **ONE sickly-pale reskin pass** over the
Geonosian living turrets (thornspitter/worm/vilelobber) = the Assailant's OWN
emplacements, visually distinct from the Hive so a player never confuses
Assailant guardians with ordinary Geonosian ones. The reskin pass itself is
new art work, not scoped/drafted here — a `generating-rimworld-sprites` job
for a future build session.

### 2.6 Learning chain / endgame (restated, RULED — not re-litigated)

Owner ruling verbatim (canon.yml `assailant_reveal_arc`): the ship "remembers
how to talk to the Rust Cathedral, only to discover it's been talking to the
FDE and no longer trusts the Cradle." Chain: **earn droid trust → earn
Cathedral trust → Cathedral reveals "Where the infection started... and
remains to this day" (this dungeon's location) → thaw-gate strike → the
Cathedral wants the Cradle as its pyrrhic surgical strike against the
Assailant → releasing that knowledge to the Hutts requires a deal protecting
the Cathedral's "beautiful young children," the droids.** Register: the Rust
Cathedral SPEAKS (has a voice, treats the droids as its children); FDE
nightside refugees are the last waypoint before the site. Quest-chain authoring
for this arc rides `rimworld-quests` and is HELD FOR OWNER/build.

### 2.7 Rulings landed 2026-09-01, and what is still held

**RULED (owner, 2026-09-01, via BENCH cards):**
- **Thaw trigger = QuestNode + map-trigger signal.** Delivering the power-core
  item to the marked point flips the map state. Vanilla quest vocabulary, no
  custom C#. If at build time a node is genuinely missing, that is a finding
  to file, not a licence to write a DLL.
- **The power core = vanilla `AIPersonaCore`.** No new item, no new art. It is
  already in the campaign's salvage set (`design/Jawa/art/salvage_palette.tsv`);
  the fiction is that only an archotech core runs hot enough.
- **The tile adjacent to 20853 is chosen by PROCEDURE, not picked offline:** at
  the bridge pass, take `Find.WorldGrid` neighbours of 20853, keep inside
  Umbra and off the 121-tile settlement-free set (`vault_siting_prep.md`
  method), then `world_commit`.
- **Naming tier: `RUT_`.** Every StructureLayoutDef / QuestScriptDef for this
  complex is campaign content (`design/NAMING_SCHEME_PLAN.md` tier test).

**Still held for the owner:**
- The actual KCSG `StructureLayoutDef`(s) for all three bands, authored and
  placed via `jawa/kcsg_place`.
- The pale-Geonosian-turret reskin art.
- All dialogue/letters for the reveal beat and the Hutt-knowledge-deal thread.

## 3. `VAULT_DUNGEON_BUILD_1` — the six Forsaken vaults

### 3.1 What they are

The "breached vaults" `03_deep_history.md` already names as containing the
self-replicating flesh — plus the other two triad members. Canon triad
(`03_deep_history.md` "The vaults — three things inside"): **① mechanoid
garrisons** (the vault held, everything still switched on), **② the enemy's
flesh weapons loose** (the vault was breached and lost), **③ frozen Rakata**
(the rare emotional scene).

### 3.2 The six sites — RULED, restated from `vault_siting_prep.md`

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 1): **all six candidates
as proposed.** `vault_siting_prep.md`'s own header called every row a
PROPOSAL — that flag is now stale; the table below is the accepted siting.

| id | tile | region | type | landmark | siting notes |
|---|---|---|---|---|---|
| V1 | 678 | Rust Cathedral (core) | ① garrison | `AncientGarrison` | inside the 236-tile Cathedral biome, Arsenal's densest ground; 9.4° from **No Owner** (FDE) — desecration risk |
| V2 | 4000 | Scorch (Cathedral halo) | ① outer works | `AncientLaunchSite` | pollution-halo ring; 3.1° from **No Owner** — the vault the Enclaves actively contest; pairs with V1 as an outer-works/core demo if wanted |
| V3 | 9167 | Fall Line | ① garrison, route-spread | `AncientGarrison` | 49° of arc from V1, independent of the Cathedral trip; sits on the Empire's Ashgarrison chokepoint — Imperial patrol territory |
| V4 | 17461 | Deadstone | ② flesh loose | `AncientWarehouse` | `HorrorWastes` bioweapon-class ground, warm edge of the band (−35.5 °C) — reachable without a deep-nightside trip; 15.0° from the Ascendant Helix's Specimen Hall |
| V5 | 37 | Slough | ② flesh loose, second instance | none pre-placed | `AB_GelatinousSuperorganism`, exactly on the terminator (arc 90.0°) — a second ② from the opposite play route; 10.4° from Dripstone (Homestead Defense League); needs a landmark authored |
| V6 | 20853 | **Umbra** | ③ frozen Rakata (the one) | `AncientWarehouse` | deepest nightside of all six (−70.2 °C, arc 159.7°); farthest from any road/settlement (20.3°) — the rare scene is not a stop on the way to anywhere. Adjacent to the Assailant complex (§2.2) |

Mix: ①×3 (V1–V3), ②×2 (V4–V5), ③×1 (V6). All six independently verified
settlement-free by tile id against the live 121-tile settlement set
(`vault_siting_prep.md`). **Bridge placement not yet done** — same down-window
pass as the Assailant complex, HELD FOR the actual write.

### 3.3 Structure — one concentric grammar, varied per type (RULED)

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 2): **ONE concentric
grammar, varied per type** — outer ring states the vault's condition at a
glance, then a garrison ring, then the core payoff. Partial raids are viable
(a crew can hit the outer ring and leave); the core always costs. Players
learn the vault language across all six.

| ring | type ① (garrison held) | type ② (flesh loose) | type ③ (frozen Rakata) |
|---|---|---|---|
| **outer** (state warns) | disciplined, powered — walls intact, lights on, patrol routes legible | torn open from inside — breach visible, wreckage, the thing that got out left a trail | dark, frost-locked — cold-damage terrain, silence, no power |
| **garrison** | the fight — Arsenal mechanoids at density, doctrine turrets (grav-rail artillery, Singularity Cannon class per the canon turret roster — vault doors guarded by world-enders, which IS the promise of the loot) | Anomaly-adjacent bioweapon guardians per the §6c contamination/bioweapon split — **not** the Assailant dungeon's Anomaly exception; use the campaign's existing bioweapon-class roster (`HorrorWastes`/`AB_GelatinousSuperorganism` native threats), confirm exact roster at build time | thin — this ring is mostly silence, a handful of dormant Arsenal units on standby, not a fight |
| **core** | tech/parts payoff — Forgotten Arsenal materials/weapons (never chassis: mechanoid tech is canonically incompatible with droid parts, `03_deep_history.md`) | survival + the route to ③ knowledge — no direct loot ladder of its own | **the scene**: wake / loot / leave (§3.4) |

### 3.4 Payoff ladder — RULED, restated

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 3): ① = Forsaken
matter/weapons; ② = survival + the route to knowledge; ③ offers three real,
authored-consequence choices:

- **WAKE** — sleepers join the world, believing the war is still on (ties to
  the VQE Rakata sleeper backstories). Owner ruling on the consequence
  (canon.yml `rakata.woken_brutality`, verbatim): *"The brutality of the Rakata
  should be very plainly visible when they wake... they have no gratitude for
  the Jawa and consider them lesser beings... 'And hey... isn't that a
  colonizer ship you're riding in?! What are you doing with that?'"* Woken
  sleepers are the tyranny made present in dialogue, and waking them opens a
  **claim-conflict thread over the Utinni itself** (`VAULT_DUNGEON_BUILD_1`
  history: "the 3-vault wake branch carries this in its authored
  dialogue/letters and opens the ship-claim thread" — the "3-vault" reference
  is V6, the one ③ site).
- **LOOT** — kills them, the game says so plainly, Rakatan tech as the reward.
- **LEAVE** — the Narrator remembers the choice (ties to the Narrator's
  cross-session memory register, `cradle_memory`/Narrator voice doctrine).

All three real, all three HELD FOR OWNER on the actual dialogue/letters.

### 3.5 KCSG technical route — confirmed available

Checked against the vendored source, not assumed: **KCSG ships bundled inside
`VanillaExpandedFramework-main`** (vendored at
`vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/`), and the
bridge already exposes it —
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchKcsgTools.cs`,
tool `jawa/kcsg_place`. `layoutType='structure'` fills a `rect` with a named
`KCSG.StructureLayoutDef` via the exact call sequence KCSG's own debug menu
uses (`GetAllMineableIn` → `CleanRect` → `Generate`). Real precedent for the
grid format exists in the mod list itself:
`vendor/mod_sources/DragonsDescent_src/1.6/Defs/Custom Structure
Generation/Structures/StructureLayoutDef_Dragon_lair_1.xml` — a
`StructureLayoutDef` is `layouts: List<List<string>>` (a list of full-grid
*variants*, KCSG picks one at random; each variant is a list of comma-joined
rows; each cell is a bare ThingDef/TerrainDef defName, or `.` for empty),
plus separate `terrainGrid`/`foundationGrid`/`roofGrid` fields for floor/roof.
**This is the answer to the "does a ring-layout framework already exist"
question — yes, and it is already wired into this project's bridge tooling.**
No new C# is needed to place a template; the parameterized-template authoring
itself is the FOUNDRY build work.

### 3.6 Draft skeleton (drafted for real — illustrative, not a finished vault)

A first-draft fragment of a type-② ("torn open") outer-ring segment, to prove
the grid format against the approved content palette before FOUNDRY commits to
full templates. 12×8 cells, `Flesh` terrain underfoot, `Fleshmass` breach
scarring through a broken `AA_BlackJellyWall` perimeter, `VFEI2_InfestedShipPart`
wreckage where the thing got out:

```xml
<Defs>
  <KCSG.StructureLayoutDef>
    <defName>RUT_VaultType2_OuterRing_Skeleton</defName>
    <spawnConduits>false</spawnConduits>
    <terrainGrid>
      <li>Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh</li>
    </terrainGrid>
    <layouts>
      <li>
        <li>AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,.,.,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall</li>
        <li>AA_BlackJellyWall,.,.,.,.,.,.,.,.,.,.,AA_BlackJellyWall</li>
        <li>.,.,.,VFEI2_InfestedShipPart,.,.,.,.,.,.,.,.</li>
        <li>.,.,Fleshmass,Fleshmass,Fleshmass,.,.,.,.,.,.,.</li>
        <li>.,.,Fleshmass,.,Fleshmass,.,.,.,.,.,.,.</li>
        <li>.,.,.,VFEI2_InfestedShipChunk,.,.,.,.,.,.,.,.</li>
        <li>AA_BlackJellyWall,.,.,.,.,.,.,.,.,.,.,AA_BlackJellyWall</li>
        <li>AA_BlackJellyWall,AA_BlackJellyWall,.,.,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall</li>
      </li>
    </layouts>
  </KCSG.StructureLayoutDef>
</Defs>
```

⚠️ **Skeleton, not shippable.** Guardian PAWN placement (not a `ThingDef`) may
need a `SymbolDef` indirection rather than a bare defName in the grid — the
Dragon lair precedent only demonstrates buildings/terrain/items, not a live
pawn spawn in the grid itself. Confirm the pawn-spawn symbol shape against
`KCSG.SymbolDef`/`SymbolUtils.Generate` before FOUNDRY builds the real
templates; not resolved this pass.

### 3.7 LARGE maps and the quicktest-proven bar

Owner ruling verbatim (`VAULT_DUNGEON_CONCEPT_1` history, point 3): *"those
vault maps should be LARGE, to add to their impressiveness (in terms of X Y
size)."* This project's standard site map is **250×250** (`row8_build_order.md`
— the ship-origin convention assumes it, verified via `mapSize` off the game,
never off a note). **Proposed LARGE floor for the six vaults: 300×300
minimum**, custom dimensions per site if a specific vault's layout wants
bigger — exact number HELD FOR OWNER, this is a floor proposal only.

**"Quicktest-proven" as a verify step (drafted here, per
`rimworld-debug-testing`):**

1. Each of the three parameterized templates (type ①/②/③) is placed via
   `jawa/kcsg_place` on a throwaway quicktest map at the proposed LARGE
   dimensions — ~30 seconds, belongs to nobody, no cold load needed.
2. **Judged by LOOKING**: `take_screenshot`, read the image (never trust a
   clean log alone). Pass bar, per `rimworld-layout-layers`: power/roof
   circuits sane if any exist, no floating/unreachable guardians, the core
   room is reachable exactly through the ring (not skippable by a straight
   line), no gaps letting a raider path around the garrison ring entirely.
3. Only after a template clears step 2 does it get hand-finished and placed on
   one of the six real sites (`world_commit`, one bridge driver at a time).
4. This bar is what `VAULT_DUNGEON_BUILD_1`'s eventual `verify` section should
   cite — it is not run this pass (no build has happened yet to test).

### 3.8 Territorial access — the mod is identified; the mechanic is still open

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 4), verbatim: *"We must
look back into the territories mod that introduced custom raids in proportion
to settlements!"* — for the conflict/negotiation layer where a vault sits
inside an existing faction's ground (V1/V2 on Cathedral-FDE ground, V3 on the
Empire's Ashgarrison chokepoint).

**The mod is Faction Territories (`jaeger972.factionterritories`)** — active in
the live `ModsConfig.xml`, vendored at
`vendor/mod_sources/FactionTerritories_decompiled`; its
`ForcedAmbushFactionScope` / `TerritoryOwnershipCache` machinery is the
"raids in proportion to settlements" behaviour. Assessing it for the
conflict layer is its own item, not part of either dungeon build.

### 3.9 Rulings landed 2026-09-01, and what is still held

**RULED (owner, 2026-09-01, via BENCH cards):**
- **All six vaults are 325×325** — the vanilla `initialMapSize` ceiling, still
  warning-free (`SCENARIO_SETTINGS_SPEC.md` §B12; `MapSizePerformanceWarning`
  fires only above 325).
- **V5 gets a NEW organic landmark** (working name `RUT_Slough_GelatinousBreach`),
  not a reused garrison landmark — V5 is the second type-② vault and must
  read as a breach, distinct from V4.
- **Pawn-spawn symbol (§3.6) = `KCSG.SymbolDef` with `<pawnKindDef>`**, never a
  bare ThingDef in the grid (precedent:
  `vendor/mod_sources/DragonsDescent_src/1.6/Defs/Custom Structure Generation/Structures/SymbolDef.xml`).
- **Naming tier: `RUT_`** for every vault StructureLayoutDef; the §3.6 skeleton
  `RUT_VaultType2_OuterRing_Skeleton` is renamed `RUT_VaultType2_OuterRing_Skeleton`.

**Still held for the owner:**
- Per-vault hand-finish pass (set-pieces, the casket hall for V6) — "every
  vault then gets a bench hand-finish pass with the owner" (owner ruling,
  point 5).
- All wake/loot/leave dialogue and letters, and the ship-claim thread that
  opens from waking V6.
- The six bridge placement writes.

## 4. Cross-links

- **The quest layer on top of §3 is `vault_thaw_quest_family.md`**
  (`VAULT_THAW_QUEST_FAMILY_1`, 2026-09-05): reveal via CARTOGRAPHY, the six
  vaults as quest Sites at the fixed tiles (so §3.9's six `world_commit`
  placements are now only for V5's landmark and hand-finish), the V6 thaw as a
  vanilla refuelable heart taking the same `AIPersonaCore` as §2.3, the
  wake/loot/leave branches, the ship-claim thread and the Reclamation.
- `design/Jawa/reconciled_lore/FUTURE_VECTORS.md` — "the dungeons arc" bullet
  now points here.
- `infrastructure/state/items/ASSAILANT_DUNGEON_BUILD_1.md` — spec/verify point
  here.
- `infrastructure/state/items/VAULT_DUNGEON_BUILD_1.md` — spec/verify point
  here.
