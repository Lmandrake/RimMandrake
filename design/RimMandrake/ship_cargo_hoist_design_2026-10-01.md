# Ship cargo hoist — universal vertical cargo device (design, 2026-10-01)

Item: `SHIP_CARGO_HOIST_DESIGN_1`. Status: **RULED** 2026-10-01 (owner cards on design `b30a0032d`; ledger notes on `SHIP_CARGO_HOIST_DESIGN_1`).
Nothing is built. Build items: §5.

## 1. What already exists

**The owner's brief (2026-10-01, typed, verbatim, typos kept):**

> *"Your idea for the hoist should be repurposed. Inhabited locations ijnhutt territories that are slave pits. You can sell any slave to the pit and the characters walk them over and lower them down the pit. Also has slaves already down there in an oubliette that cannot get out. Will also pay for unconscious beasts even if not tamed. Slave put fodder for the arenas. Could also have dungeon entrances that support this joist up and down. Now I'm wondering if we can have a universal cool new mechanic be the ships's houst. A cargo device that is universal for vertical cargo movement. Could be a unique gravship component in this campaign. Reuse it all over the place. Send this idea out for deep planning, then get gpt commentary on how to next it and all the differentnusefulnplot moments it might help in. I named two here. Could we even incorporate a lottery in the hutt trading areas like that cool old catapult idea from the ancients rimworld expansion mod in their vault? Replaced what you sent with items of similar value. Lots of possibilities here. Just have to be careful we don't get caught in endless animation development."*

Origin: GPT's idea 2, "The Veyrline Keel Hoist", in
`design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §5. BENCH judged it
there as *"unique mechanism, thin need ... pawns already carry things through a pocket-map
portal."* The owner's answer is to widen the need rather than drop the mechanism.

### 1a. Our own source

| what | path | what it gives the hoist |
|---|---|---|
| `PlaceWorker_NeedsGravEngine` | `src/RimMandrake/DivingInteraction/Source/PlaceWorker_NeedsGravEngine.cs` | An existing place-worker that limits a building to structures carrying a `GravEngine`. The ship form needs the same rule; **copy it into the hoist mod** rather than referencing it, because it lives in `DivingInteraction` beside the sea dive hatch. (The hatch that used it is a leftover of an earlier build, being retired as `SEA_DIVE_HATCH_RETIRE_1`. Nothing here depends on the hatch.) |
| `RM_LanternDeepMineshaft` (vanilla `MapPortal`, 5×5, PitGate art, `CompProperties_Sealable`) | `src/RimMandrake/LanternDeeps/Defs/ThingDefs_Buildings/RM_LanternDeepMineshaft.xml` | A cave mouth into the Lantern Deeps pocket map. It is where the Keel Hoist was first pictured. |
| `RM_LanternDeepEmergence` | `src/RimMandrake/LanternDeeps/Defs/ThingDefs_Buildings/RM_LanternDeepEmergence.xml` | A second Deeps mouth. |
| `RUT_FoundryTowerEntrance` (vanilla `MapPortal`, 80×80 pocket floor) | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FoundryTowerEntrance.xml` | A dungeon entrance that already works. Its header records *"one deep floor per tower in v1, no multi-floor/portal chaining attempted."* |
| `RUT_HuttCartel_Captives` TraderKindDef | `src/RimUtinni/UtinniPatches/Defs/TraderKindDefs/RUT_HuttCartel_Captives.xml` | A Hutt captive-purchase route exists **today** through caravan trade. Its header says plainly that the Hutt "torture chambers" are **not a visitable site**: `hutt_holding_pens.lua` is district 2 of Gorga's Palace, and v1 composes only district 0. **No `InhabitedCastDef` exists for any Cartel place, so the palace spawns zero cast pawns.** The slave pit has no map to sit on yet. That is the largest prerequisite in this whole design. |
| Hutt district templates | `design/Jawa/templates/hutt_holding_pens.lua`, `hutt_cistern_court.lua`, `hutt_palace_hall.lua`, `hutt_spicehouse.lua` | Where a pit and a lottery would be composed. |
| `RUT_Jawa_HuttCartel` FactionDef | `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml` | The real Hutt faction. |

**Earlier design records that touch this brief:**

| record | path | what it says |
|---|---|---|
| XX3 **Slave pen** | `design/Jawa/worldbuilding/tile_augmentation_matrix.md` | *"the Hutt thing the player cannot unsee; a liberation choice with a price"* (Torment Master `Water Prison`, prisoner cast) |
| XX4 **The casino** | same file | *"a Hutt post whose stock is chance: gamble silver against a crate"*, marked "🆕 small", scripted gamble in C#. **The lottery was already pitched once.** |
| TR3 **Hutt market post** | same file | stalls, plus a slave-block the player can choose not to look at |
| GB29 **Rancor pen, broken** | same file | *"a Hutt arena beast that got out"* |
| Hutt arena and spectacle tier | `design/Jawa/worldbuilding/Livestock_Trade_Utility_Pets_v1.md` §10.2 | Rancor (*"the canonical under-the-trapdoor set-piece"*), Acklay, Reek, Nexu, and the Cartel Beast-Barge |
| Acklay homing | `design/Jawa/worldbuilding/review/round2/move_mapping_v2.md` | *"Hutt arena fodder and territories"*, OPEN |
| Sarlacc pocket-map route | `design/Jawa/worldbuilding/sarlacc_discussion_pack.md` D-1 | `PitGate`-style stacked pocket maps. Measured there: **pocket-map nesting is not enforced, so stacked levels are legal.** |

### 1b. The pit oubliette and the Hutt oubliette — RULED, no conflict

`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` (2026-09-17) cut the pit **fitting** called the
oubliette (*"forget the oubliette/ion thing"*). The Hutt oubliette is a different thing, ruled 2026-10-01:

> *"It is a special map feature you can't go into and don't want to. But your shop winch could reach down and lift up the slaves if you attacked the place and took it over."*

So it is **neither an enterable map nor a pit room.** It is a sealed feature on the Hutt site's map that holds
slaves. **Only the ship's hoist reaches it, and only after the site has been taken by force.**

### 1c. The engine (RimSage, decompiled 1.6, read 2026-10-01)

- **`MapPortal : Building, IThingHolder`** (`RimWorld/MapPortal.cs`). `GetOtherMap()` and
  `GetDestinationLocation()` are **virtual**. The base class generates a pocket map, but a subclass may
  return **any** map. Load-and-send is already built: `leftToLoad`, `Dialog_EnterPortal`,
  `JobDriver_HaulToPortal`, `LordJob_LoadAndEnterPortal`, `ITab_ContentsMapPortal`, and
  `CompProperties_Sealable` for collapse. **VERIFIED.**
- **`Dialog_EnterPortal` already sends downed pawns and secure prisoners.** It calls
  `CaravanFormingUtility.AllSendablePawns(..., allowEvenIfDowned: true, allowEvenIfPrisonerNotSecure:
  false, allowCapturableDownedPawns: false, ...)`. So **colonists, slaves, secure prisoners, tame animals and
  downed colony pawns all go through today.** **A downed wild animal or a downed stranger does not**
  (`allowCapturableDownedPawns: false`). That is the one gap the owner's *"unconscious beasts even if not
  tamed"* hits. **VERIFIED** (`Dialog_EnterPortal.cs:165`).
- Vanilla subclasses: `PitGate`, `AncientHatch`, `InsectLairEntrance`, `PocketMapExit` → `CaveExit`.
  **VERIFIED.**
- **`Building_GravEngine.CanLaunch(CompPilotConsole)` is NOT virtual.** It already refuses on
  `pocketMapProperties.canLaunchGravship == false`, no substructure, disconnected, fuel, thrusters and
  cooldown. A "tethered: reel in first" refusal therefore needs a **Harmony postfix** on it. **VERIFIED**
  (`Building_GravEngine.cs:299`).
- No gravship source file mentions `MapPortal` or `PocketMap`, so a ship that lifts off with its cable down a portal has no engine guard of its own. The tether lock is that guard.

### 1d. Installed mods — prior art sweep

Sweep: every `About.xml` under both `…/common/RimWorld/Mods` and `…/workshop/content/294100`, matching
`<name>` + `<description>`. Case-insensitive mount, so 2,820 paths are about 1,410 mods, double-globbed.
**Sanity probe:** "gravship" hit **84** paths, so the sweep can see things. Mod-list fact: **611 active**
(`ModsConfig.xml` parsed, 2026-10-01).

| mod | active | what it actually is | relevance |
|---|---|---|---|
| **Vanilla Quests Expanded – Ancients** (`vanillaquestsexpanded.ancients`) | **yes** | `VQEA_PneumaticTubeLaunchPort` (5×5, `Building_PneumaticTubeLaunchPort`, `CompProperties_PneumaticTransporter` with `massCapacity 100`). Description, verbatim: *"used to send supply capsules between distant vaults ... Cargo can still be loaded and launched, and a return capsule may arrive from another vault after some time."* Keyed: *"You may receive some goods from another vault in return."* | **This is almost certainly the owner's "catapult in their vault."** It lives in the vaults, you send cargo, and goods come back. **How the return is valued** (equal value? random?) is in the DLL and **UNVERIFIED**; no decompiler is on this machine. *"Items of similar value"* is the owner's recollection, and it is the rule we will build either way. |
| Vanilla Factions Expanded – Ancients (the "supply slingshot") | **not installed** | Known only from `Dismantle Ancient Junk`'s compatibility note (*"Ancient supply slingshot ... will be dismantleable"*). | Same idea, older mod. Not readable here. |
| **GravTide** (`gravtide.mod`) | **yes** | Ship-to-sea-floor travel, a `GravTide_VesselCrane` deck crane (within-map heavy cargo, pile driving), and a `GravTide_CargoWinch` that is a **damaged quest-site prop** (*"The contracted cases must be hauled home"*). Its docs use a **launch lock** pattern: *"its vessel cannot launch, cast off, dive or crane into another move."* It also has **individual-pawn diving** (helmets, suits). | Prior art for the tether lock and for cranes. **None of it moves cargo map-to-map vertically.** Its pawn diving **contradicts our ship-only ruling**. Our seas are reached by the ship flying to the `RM_SeabedLayer` sea-floor planet layer. |
| Hospitality: Casino (`Adamas.HospitalityCasino`) | installed | Guest gambling | Possible donor for the lottery's *joy/guest* side. Not the device. |
| Dungeon Core (`HaiLuan.Dungeon`) | installed | Dungeon content | Not read further. Outside this design. |
| hoist / winch / elevator / cargo lift / arena | — | **0** hits in names or descriptions | **No installed mod ships a vertical cargo device.** The hoist is genuinely new. |

## 2. The core device (RULED)

**Working name: the keel hoist.** It is a winch, a cable and a cradle that moves cargo **vertically between
two places that walking does not connect.** It is one comp (`RM_CompKeelHoist`) wherever it appears.

### 2a. Two forms: a ship part, and fixed hoists built into sites

Owner ruling: the hoist is **a ship part, plus fixed hoists that come built into sites. Players do not build
fixed hoists.**

| | **ship form** `RM_KeelHoist` | **fixed form** `RM_HoistFrame` (a head-frame) |
|---|---|---|
| where | a gravship fitting, limited by the existing `PlaceWorker_NeedsGravEngine` | **placed only by site gensteps**: the Hutt slave pit, the lottery chute, old vault shafts, mines |
| travels | yes. It flies with the ship and drops its cable onto any mouth, cell or feature the ship parks over | no |
| player-buildable | yes, through ship research | **no**. The player uses it while on the site, and does not designate or build it |
| what makes it special | the only form that reaches a target it was not built over. This is the unique gravship component. | the NPC sites' own machinery |

### 2b. What it moves

| cargo | hoist |
|---|---|
| items, stacks, minified buildings | yes. **Mass per cycle is the capacity.** |
| colonists, **awake** (owner: colonists may ride) | yes. The cradle is an entrance as well as a lift. |
| slaves, secure prisoners, tame animals, downed colony pawns | yes (vanilla portal loading already allows these) |
| **downed strangers and downed wild animals** | yes. **This is the one engine gap** (`allowCapturableDownedPawns: false`, §1c). They arrive **captured** (prisoner / wild-captive status applied on arrival), never silently kidnapped. |
| corpses | yes |

### 2c. Three target kinds

1. **A portal (map-to-map).** The cable pairs with an existing `MapPortal`: a cave mouth, a dungeon entrance.
   Lowering puts cargo beside the portal's exit below. A cradle cell below sends things up. **One pairing per
   hoist.** Stacked dungeons are chains of ordinary pairs, never a portal graph.
2. **A cell (within-map).** A cell nobody can walk to: the floor of a superdeep pit room, a cliff shelf. This is
   how a pit is served from the lip, consistent with *capture down*.
3. **A holder feature (within-map).** A sealed building on the map that **contains** pawns and cannot be entered,
   the **Hutt oubliette**. The hoist lifts its contents out. The ship form may target it **only once the site is
   taken**: its owning faction is defeated, or the site is the player's.

### 2d. Engine route

- `RM_KeelHoist : MapPortal`. Overriding `GetOtherMap()` / `GetDestinationLocation()` (both **virtual**,
  VERIFIED) reuses the whole vanilla load pipeline: `leftToLoad`, `Dialog_EnterPortal`,
  `JobDriver_HaulToPortal`, `ITab_ContentsMapPortal`. A within-map target returns `Map` itself. A holder target
  unloads the holder's `ThingOwner`.
- **Transit is a hidden timer**, not an animation: loaded things sit in the hoist's `ThingOwner` for
  `cycleTicks` (scaled by mass), then spawn at the destination.
- **Downed strangers and wild animals:** a hoist-owned dialog subclass, or a postfix scoped to `RM_KeelHoist`.
  **Never** patch the shared `AllSendablePawns` call that every caravan reads.
- **Tether lock:** a Harmony postfix on `Building_GravEngine.CanLaunch` (non-virtual, VERIFIED) refuses launch
  while any of the ship's hoists has a cable down: *"Reel in the keel hoist first."*
- **Manifest:** every cycle records what went, who it was, from where and to where, readable in an inspect tab.
  This is the record the "nothing vanishes without a sign" rule needs. It is also what Hutt letters and the
  lottery read.
- **Open Line meter (from GPT, adopted):** a per-map counter that rises while a cable is down and raises a
  site-specific consequence (noise, hostile interest, instability, Hutt scrutiny). It costs, and it never limits
  what can be carried. Slice 1 ships the counter and its readout. Consequences are wired per site later.

### 2e. Gating and cost — by cost, never by narrowing scope

- **Research:** one row on the gravship branch. GPT's order is adopted: rigging (within-map) → portal coupler
  → restraint cradle (downed beings) → heavy drum (mass, speed) → manifest logic. The defName of the prerequisite
  is measured, never guessed.
- **Build (ship form):** steel, components, plasteel. **Running:** power while cycling, and time that scales with mass.
- **Exposure:** the ship cannot leave while the cable is down, and the Open Line meter climbs.
- **Mod Settings:** master on/off; tether lock (on by default, labelled as a safety rule); capacity and
  cycle-time multipliers; colonists-may-ride; downed-wild-animals and strangers; the Open Line meter. In the
  RimUtinni layer: Hutt pit trade, pit price multiplier, lottery on/off and odds sliders.

### 2f. Tiers

The device is invented, so it goes in **`RM_`** (`mandrake.rm.*`, a small `RimMandrake.KeelHoist` mod).
Everything Hutt (the slave pit, the oubliette, arena hints, the lottery's dressing) is **`RUT_`**. The chute's
*mechanism* (stake cargo, a value-matched crate comes back) is `RM_`. The Hutts own the one the player meets.

## 3. Reuse sites

### 3a. The Hutt slave pit (RUT) — built first, at a small stand-alone test site

Owner: *"Yes for small test site."* Not Gorga's Palace yet.

- **The site.** One small Hutt map with a `RUT_` cast (keeper, guards) and a fixed `RM_HoistFrame` over the pit.
- **Selling, for silver.** The keeper buys **slaves, unenslaved prisoners, and knocked-out beasts, tame or
  not.** The player's own pawns **walk the sold pawn to the fixed hoist and lower them.** Silver comes back up
  the cable. The price is market value times a Hutt pit multiplier (a Mod Settings slider).
- **The oubliette.** A sealed map feature (§2c target 3) holding slaves who cannot get out. Nobody enters it.
  **While the Hutts hold the site, it is just there**: it is seen, it is heard in letters, and its people are
  out of reach. **If the player attacks and takes the site, the ship's hoist can lift them out**, to free,
  recruit or keep. Taking a Hutt site is its own hostile act, with Hutt consequences.
- **The arena is offstage for now.** It shows up only in pit prices ("fighters fetch more this week") and in
  letters about where the sold went. A visitable arena is a separate, later build.
- **Prerequisite the owner named:** *"We need a way for gravship to land properly in settlement and not be seen
  as attacking. That remains to be proven."* Filed as `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1`. The peaceful
  sale needs it. Taking the site by force does not.

### 3b. Dungeon entrances — fixed head-frames built into the sites

| dungeon | item | how the hoist serves it |
|---|---|---|
| Foundry towers | live (`RUT_FoundryTowerEntrance`) | a ruined head-frame beside the tower mouth carries heavy salvage up without carrying |
| Breached vaults V1–V6 | `VAULT_DUNGEON_BUILD_1` | dead vault lifts. The frozen Rakata (V6) come up sealed. |
| Assailant first-impact site | `ASSAILANT_DUNGEON_BUILD_1` | the thaw-gate's *"old power core"* is lowered to its socket, a reason to bring the ship |
| Sarlacc (D-1) | `sarlacc_discussion_pack.md` | feeding the sarlacc by cable, and pulling a swallowed colonist up |

### 3c. Lantern Deeps cave mouths

The ship parks over `RM_LanternDeepMineshaft` and drops its cable. **This is the first test site**, because the
portal exists and the Deeps need logistics.

### 3d. The seas

**No dependency.** The ship flies to the `RM_SeabedLayer` sea-floor planet layer itself. The hoist works there as
it does anywhere (a trench, a wreck shelf), and adds no route of its own to or from the floor.

### 3e. More sites

Our own superdeep pits (serve a pit prison from the lip); fall-zone lost cargo (`FALLZONE_LOST_CARGO_QUESTS_1`);
the sandcrawler (the Jawa canon suction lift, GPT moment 24); rescue of a downed colonist from a hole; ore up a
mine shaft.

## 4. The Hutt lottery — "the chance chute" (RULED)

Prior art: VQE Ancients' `VQEA_PneumaticTubeLaunchPort` (active in his list); XX4 "The casino".

1. At a Hutt site, a fixed chute (`RM_HoistFrame` in chute mode). You load a stake and pay the house.
   **The stake may be goods, slaves or beasts** (owner ruling).
2. It goes down. A timer of hours runs.
3. A crate comes up with items of similar total value, built with vanilla's
   `ThingSetMakerParams.totalMarketValueRange` (VERIFIED field) around a rolled multiplier: mostly 0.7–1.1×,
   rarely 3×, rarely 0.3×. **The house always takes a cut** (owner ruling), so the expected value is below 1.
4. Slaves and beasts staked are recorded in the manifest. Letters may later say where they went.

No new UI, no new generator, and no animation (a fade, then the crate is on the cradle). It lives at the Hutt test
site, so it shares the peaceful-landing prerequisite.

## 5. Build ladder (filed as FOUNDRY items) — animation is optional polish, last

The shipped visual is **a drawn cable line (`GenDraw.DrawLineBetween`, VERIFIED) and two static cradle sprites**
(empty, loaded). Transit is invisible: things vanish, a timer runs, things appear. **No item waits on art or
animation. Art is the last step of each item and may be skipped. A descent animation is never in scope.**

| # | item | what | depends on | size |
|---:|---|---|---|---|
| 1 | `HOIST_SHIP_PART_BUILD_1` | ship form; items, awake colonists, prisoners, downed colonists, **downed strangers and wild animals captured on arrival**; portal and cell targets; tether lock; manifest; Open Line counter stub; research row; Mod Settings. Test: `RM_LanternDeepMineshaft`. | — | M |
| 2 | `HOIST_FIXED_SITE_FRAMES_1` | `RM_HoistFrame` (genstep-placed, not buildable), holder-feature target kind, dungeon head-frames (Foundry tower first) | 1 | S–M |
| 3 | `HUTT_SLAVE_PIT_TEST_SITE_1` | stand-alone Hutt test site, cast, fixed hoist, sell-to-pit for silver (slaves, prisoners, downed beasts), sealed oubliette feature unlocked to the ship's hoist only when the site is taken, arena hinted in prices and letters | 1, 2, `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` | L |
| 4 | `HUTT_LOTTERY_CHUTE_BUILD_1` | chance chute at the test site: stake goods, slaves or beasts; house cut; value-matched crate; odds in Mod Settings | 3 | M |

Later and unfiled: the visitable arena (its own build); vault, assailant and sarlacc head-frames when those
dungeons are built.

## 6. Owner rulings (2026-10-01)

All eight questions are answered. Ledger notes on `SHIP_CARGO_HOIST_DESIGN_1`.

1. **Hutt oubliette:** a sealed map feature nobody enters. The ship's winch lifts the slaves out only after the
   site is attacked and taken. (Verbatim in §1b.)
2. **Colonists may ride the hoist awake.**
3. **Seas:** no hatch. The ship flies to the `RM_SeabedLayer` sea-floor layer (*"the sea hatch might have been
   something from a previous build. Now the ship just flies to a new planetary layer called sea floor."*). The hatch
   retirement is `SEA_DIVE_HATCH_RETIRE_1`.
4. **A ship part, plus fixed hoists built into sites.** Players do not build fixed hoists.
5. **The pit buys** slaves, knocked-out beasts (tame or not) and unenslaved prisoners, **for silver**.
6. **The lottery** takes a house cut, and slaves and beasts may be staked.
7. **The slave pit is built first at a small stand-alone Hutt test site.** Prerequisite: peaceful gravship landing in
   a settlement (`GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1`).
8. **The arena is offstage for now** (pit prices, letters), and visitable later as its own build.

## 7. GPT commentary and assessment

Consult: `Transient/bedazzle_gpt_enrich_2026-10-01/cargo_hoist.md`, prompt beside it
(`cargo_hoist.prompt.md`), run 2026-10-01 via `codex exec` (read-only). The prompt carried the owner's words
verbatim, the binding rules (ship-only seas, cost-not-scope balance, tiers, the hard no-animation visual budget,
the cut oubliette fitting), and the real hooks. It asked for nesting, at least 20 plot moments with three
starred, research lineage, scope traps, and a critique. GPT returned 28 moments.

### 7a. What GPT said (faithful summary)

**Nesting.** The hoist first appears **dead inside the gravship**: cut cable, an empty drum, and a manifest
naming a replacement drum lost in fall-zone wreckage. Recovering it is the tutorial. **The Jawas own its
culture** (tallies painted on the drum, Ohm invoked before opening the line). Growth is **one research row**:
Salvaged Rigging (within-map) → Portal Coupler (map-to-map) → Restraint Cradle (downed beings) → Site Headframe
(placed form) → Heavy Drum (mass, speed) → Manifest Logic (saved loads, lottery, quest cargo). The introduction
order it proposes is: broken fitting, safe salvage lift, rescue, Lantern Deeps, first tethered attack, placed-form
dungeons, Hutt slave pit, chance chute, seas, then the Imperial, Rakatan and Sarlacc finales. The feel it names:
*"throwing a dependable rope into an unknowable dark ... every use declares, 'We are staying here until this
line comes back.'"*

**GPT's three starred moments:**
- ★ **6. The Open-Line Raid (RM).** Raiders arrive while the cable is down and the ship cannot launch: reel in an
  incomplete load, defend a split expedition, or abandon cargo to save people. *"It turns the tether lock from a
  rule into the hoist's signature tactical story."* (Lineage: FTL's fights while the jump drive charges.)
- ★ **11. The Oubliette Answers (RUT).** Voices and marks reveal the slaves already below, feeding Gorga's arenas.
  Pay for access, lower contraband, descend to organise a breakout, or walk away knowing.
- ★ **14. The Chance Chute (RUT).** Load goods plus a stake, and a sealed crate comes up hours later. Choose the
  stake, whether to wait in dangerous territory, and whether to trust the house's manifest.

**Others worth keeping:** 3 *Someone on the Scree* (a stranger on an unreachable ledge, before weather or
enemies arrive) · 9 *The Hidden Socket* (lowering the Assailant's power core costs a core you could have used
to upgrade your own drum) · 10 *The Slave-Pit Sale* (the manifest keeps the sold captive's name, so complicity
can be read and reversed) · 12 *Buy Them Back Up* (a captive you sold reappears on an arena roster) · 15 *The
Clerk's Finger* (repeated duds expose a cheating clerk) · 16 *Droids Listed as Scrap* (the existing Hutt-captive
droids travel as cargo) · 17 *The Cistern Manifest* (hide raiders in palace supply loads) · 21 *The Frozen
Rakata* (hoist the casket intact, or lower a core and thaw it in place) · 22 *Imperial Manifest Inspection* ·
24 *The Sandcrawler Salvage Well* · 25 *The Fever Wood Exit* (the one fixed extraction point in a hive that
rearranges itself) · 26 *The Quarantine Shelf* (isolate an infected body on an unreachable shelf) · 27 *The
Smuggler's Dead Drop* · 28 *The Last Descent* (an elder asks to be lowered into the Deeps with a treasured
machine; a wall mark records it).

**Scope traps and the stand-ins it proposes:**
1. Rope, body, cage and pulley animation → one drawn cable, two cradle sprites, a sound, a fade.
2. Simulating living cargo between maps → a hidden `ThingOwner`, a timer, an inspectable manifest.
3. A universal portal graph → one pairing per hoist; stacked dungeons are chains of ordinary pairs.
4. Every hauling and ownership edge case → reuse vanilla's dialog and jobs, and apply capture status on arrival.
5. The lottery as an underground economy → snapshot the stake, seed the result, a timer, value bands, a per-site cooldown.

**Critique.** Universality can flatten distinct places into one loading dialog, and the lottery risks becoming a
value-reroll machine. Its one change is an **Open Line pressure meter**: the longer a cable is down, the more a
context-specific consequence builds (noise, hostile interest, instability, contamination, Hutt scrutiny), with no
limit on what can be carried.

### 7b. BENCH assessment

- **Adopt: the Open Line meter.** It is the strongest single idea in the reply. It is exactly the owner's
  *"balance by cost, never by narrowing"* rule, it gives every site its own flavour of risk through one counter,
  and it makes ★6 (the open-line raid) an emergent outcome rather than a scripted event. It is cheap: a
  `MapComponent` counter, an inspect string, and an incident weight. **Add it to ladder slice 0 as a stub (the
  counter and its readout), and wire consequences per site later.**
- **Adopt: the manifest as the readable record.** Moments 10, 12, 15, 17 and 22 all hang on one thing: a saved
  list of what went down, who it was, and where. It also satisfies the "nothing vanishes without a sign" rule for
  free. It belongs in slice 0 as data, with an inspect-tab readout. No new UI art.
- **Adopt: the single research row,** in GPT's order. It matches ladder slices 0 → 2 well. Its "Heavy Drum" is
  where cost scales.
- **Adopt with a check: "found dead in the ship" as the first meeting.** It is a strong opening, but the
  campaign starts from a **fixed shipped save**, so a pre-installed broken fitting must be placed in that start
  save's ship (`rimworld-savegame` / `gravship-layout`). That is a RUT_ scenario edit, not a mechanic. The RM_
  tier simply researches and builds it.
- **Moot: moment 18 (the seas).** The owner has since ruled the ship flies to the `RM_SeabedLayer` sea-floor layer, so the hoist has no sea route to provide (§3d).
- **Correct: moment 23 gives Ozzik a *liberation* rite.** Ozzik is the god who always seeks to enslave and
  always fails. A rite of his belongs at the **sale**, as the clan's temptation, and his *failure* is the
  breakout. Any rite here goes to the owner through the usual rites card. None is adopted.
- **Decline: the "Drumkeepers" RM_ cultural layer.** It is an invented tradition the free tier does not need.
  The device stands alone without lore.
- **Scope traps:** all five agree with §5. Trap 3 (one pairing per hoist, dungeons as chains of pairs) becomes
  a design rule here, as does trap 4's "capture status applied on arrival".
- **What GPT did not catch:** the downed-stranger and wild-animal gap is a real engine change
  (`allowCapturableDownedPawns: false`, §1c).

**First slice (ruled):** `HOIST_SHIP_PART_BUILD_1` (§5 row 1). That is the ship hoist on the Lantern Deeps mouth, carrying items, pawns and downed beasts, with the manifest and an Open Line counter stub. Size M.
