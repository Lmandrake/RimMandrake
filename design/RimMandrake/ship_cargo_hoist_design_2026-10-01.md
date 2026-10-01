# Ship cargo hoist — universal vertical cargo device (design, 2026-10-01)

Item: `SHIP_CARGO_HOIST_DESIGN_1`. Status: DESIGN. Nothing is built. Open questions for the owner are in §6.

## 1. What already exists

**The owner's brief (2026-10-01, typed, verbatim, typos kept):**

> *"Your idea for the hoist should be repurposed. Inhabited locations ijnhutt territories that are slave pits. You can sell any slave to the pit and the characters walk them over and lower them down the pit. Also has slaves already down there in an oubliette that cannot get out. Will also pay for unconscious beasts even if not tamed. Slave put fodder for the arenas. Could also have dungeon entrances that support this joist up and down. Now I'm wondering if we can have a universal cool new mechanic be the ships's houst. A cargo device that is universal for vertical cargo movement. Could be a unique gravship component in this campaign. Reuse it all over the place. Send this idea out for deep planning, then get gpt commentary on how to next it and all the differentnusefulnplot moments it might help in. I named two here. Could we even incorporate a lottery in the hutt trading areas like that cool old catapult idea from the ancients rimworld expansion mod in their vault? Replaced what you sent with items of similar value. Lots of possibilities here. Just have to be careful we don't get caught in endless animation development."*

Origin: GPT's idea 2, "The Veyrline Keel Hoist", in
`design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §5. BENCH judged it
there as *"unique mechanism, thin need ... pawns already carry things through a pocket-map
portal."* The owner's answer is to widen the need rather than drop the mechanism.

### 1a. Our own source — four MapPortals already ship, and one is on the gravship

| what | path | what it gives the hoist |
|---|---|---|
| `RM_SeaDiveHatch` (`MapPortal` subclass, 2×2, steel 150 + 4 components) | `src/RimMandrake/DivingInteraction/Source/RM_SeaDiveHatch.cs`, `.../Defs/ThingDefs_Buildings/RM_SeaDiveHatch.xml` | **The gravship-component form already exists.** It is buildable only inside a structure carrying a `GravEngine` (`PlaceWorker_NeedsGravEngine.cs`), picks its pocket-map generator at generate time from the parent tile's biome, and has a master Mod Settings toggle (`RM_DivingSettings.cs`). The hoist is this class generalised. |
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

### 1b. The pit and oubliette conflict — RECONCILE, NOT DECIDED HERE

`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` (owner rulings, 2026-09-17):
- A pit is a **superdeep cell** (depth 4) in FlowWorks terrain, not a building. An enclosed superdeep area
  is a **room**, and a prisoner bed makes it a real prison room. **`capture down` and `convert down`** happen
  **from the lip**: *"nobody who enters can leave."* A ladder near the lip is the way out, and it works *"like
  opening a prison door."*
- ⛔ **The `Oubliette` fitting was CUT.** Verbatim: *"forget the oubliette/ion thing."* That fitting was the
  pit-hardware version: a building with an ion charge, and the only anti-mechanoid fitting.

The owner now describes a **Hutt "oubliette" holding slaves who cannot get out**. That reads as a
*place*: an enclosed superdeep room or a pocket map below a hoist. The cut covered a *fitting*. These are
probably different things, and the 2026-09-17 model (a trapped room, served from the lip) is already
most of a Hutt oubliette. **That is a question for him (§6 Q1), not something decided here.**

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
- No gravship source file mentions `MapPortal` or `PocketMap`. **What happens today when a ship lifts off
  while `RM_SeaDiveHatch`'s pocket map still holds pawns is UNMEASURED.** Nothing in
  `DivingInteraction/Source` mentions launch. The hoist's tether lock closes that hole for the sea hatch as well.

### 1d. Installed mods — prior art sweep

Sweep: every `About.xml` under both `…/common/RimWorld/Mods` and `…/workshop/content/294100`, matching
`<name>` + `<description>`. Case-insensitive mount, so 2,820 paths are about 1,410 mods, double-globbed.
**Sanity probe:** "gravship" hit **84** paths, so the sweep can see things. Mod-list fact: **611 active**
(`ModsConfig.xml` parsed, 2026-10-01).

| mod | active | what it actually is | relevance |
|---|---|---|---|
| **Vanilla Quests Expanded – Ancients** (`vanillaquestsexpanded.ancients`) | **yes** | `VQEA_PneumaticTubeLaunchPort` (5×5, `Building_PneumaticTubeLaunchPort`, `CompProperties_PneumaticTransporter` with `massCapacity 100`). Description, verbatim: *"used to send supply capsules between distant vaults ... Cargo can still be loaded and launched, and a return capsule may arrive from another vault after some time."* Keyed: *"You may receive some goods from another vault in return."* | **This is almost certainly the owner's "catapult in their vault."** It lives in the vaults, you send cargo, and goods come back. **How the return is valued** (equal value? random?) is in the DLL and **UNVERIFIED**; no decompiler is on this machine. *"Items of similar value"* is the owner's recollection, and it is the rule we will build either way. |
| Vanilla Factions Expanded – Ancients (the "supply slingshot") | **not installed** | Known only from `Dismantle Ancient Junk`'s compatibility note (*"Ancient supply slingshot ... will be dismantleable"*). | Same idea, older mod. Not readable here. |
| **GravTide** (`gravtide.mod`) | **yes** | Ship-to-sea-floor travel, a `GravTide_VesselCrane` deck crane (within-map heavy cargo, pile driving), and a `GravTide_CargoWinch` that is a **damaged quest-site prop** (*"The contracted cases must be hauled home"*). Its docs use a **launch lock** pattern: *"its vessel cannot launch, cast off, dive or crane into another move."* It also has **individual-pawn diving** (helmets, suits). | Prior art for the tether lock and for cranes. **None of it moves cargo map-to-map vertically.** Its pawn diving **contradicts our ship-only ruling**, and must not leak into how our seas are reached. |
| Hospitality: Casino (`Adamas.HospitalityCasino`) | installed | Guest gambling | Possible donor for the lottery's *joy/guest* side. Not the device. |
| Dungeon Core (`HaiLuan.Dungeon`) | installed | Dungeon content | Not read further. Outside this design. |
| hoist / winch / elevator / cargo lift / arena | — | **0** hits in names or descriptions | **No installed mod ships a vertical cargo device.** The hoist is genuinely new. |

## 2. The core device

**Working name: the keel hoist.** It is a winch, a cable and a cradle that moves cargo **vertically
between two places that walking does not connect, or connects badly.** It is one mechanism with one
comp, wherever it appears. Every reuse in §3 is the same device pointed at a different target.

### 2a. Two forms, one comp (`RM_CompKeelHoist`)

| | **ship form** `RM_KeelHoist` | **placed form** `RM_HoistFrame` (a head-frame) |
|---|---|---|
| where | a gravship fitting, gated by the existing `PlaceWorker_NeedsGravEngine` exactly as `RM_SeaDiveHatch` is | built on the ground over a mouth, or **pre-placed by gensteps** at Hutt pits, vault shafts, mines |
| travels | **yes**: it flies with the ship, so it reaches any mouth the ship can park over | no |
| what makes it special | the **only** form that can drop a cable from the sky onto a mouth it was not built over. This is the unique gravship component the owner asked for. | cheap, local, the thing NPC sites own |
| player-buildable | yes, ship research tier | **open question (§6 Q4)** |

The ship form is the campaign's signature, so it lands first. The placed form is the same comp on a
different building, with `range` 0: it serves only the mouth it stands on.

### 2b. What it moves

| cargo | today through a vanilla portal? | hoist |
|---|---|---|
| items, stacks, minified buildings | yes (`Dialog_EnterPortal`) | yes. **Mass per cycle is the capacity stat**, not volume. |
| colonists, slaves, secure prisoners, tame animals | yes | yes. **Whether pawns ride the cradle awake is §6 Q2.** |
| **downed colony pawns** | yes (`allowEvenIfDowned: true`) | yes. This is the rescue lift. |
| **downed strangers, downed wild animals** | **no** (`allowCapturableDownedPawns: false`) | **yes, and this is the one engine gap.** The owner's *"unconscious beasts even if not tamed"* needs it. A hauler carries the body to the cradle the way vanilla carries a capture target. |
| corpses | as items | yes (sarlacc feeding, arena disposal) |

### 2c. Two target kinds: map-to-map and within-map

1. **Map-to-map (a portal target).** The cable is paired with an existing `MapPortal`: a cave mouth, the
   sea dive hatch, a dungeon entrance, or a Hutt pit's oubliette mouth. Lowering moves cargo to that
   portal's other side and puts it down beside its `exit`. Raising takes whatever stands on a **cradle cell
   at the bottom** (a small `RM_HoistCradle` dropped beside the exit on first use, or a stockpile-like zone)
   and brings it up beside the hoist. **No pawn has to walk the shaft.** That is the hoist's whole value over a
   plain portal: it turns a dungeon or cave into a supply line rather than a carry.
2. **Within-map (a cell target).** The cable drops onto a cell on the same map that is **unreachable on foot**:
   the floor of a FlowWorks superdeep pit room, a cliff shelf, or a sealed courtyard. Lowering puts the cargo
   on that cell. Raising lifts from it. This is how a pit is **served from the lip**, which matches the
   2026-09-17 *capture down / convert down* model: food down, a prisoner up, a body up.

### 2d. Engine route (VERIFIED where marked, in §1c)

- `RM_KeelHoist : MapPortal`. Overriding `GetOtherMap()` and `GetDestinationLocation()` (both **virtual**,
  VERIFIED) lets the hoist reuse **the whole vanilla load pipeline**: `leftToLoad`, `Dialog_EnterPortal`,
  `JobDriver_HaulToPortal`, `ITab_ContentsMapPortal`. The hoist does not generate a map of its own. It
  **borrows** its target portal's other map. A within-map target returns `Map` itself and the target cell.
- **Transit is a timed hold, not an animation.** Loaded things go into the hoist's `ThingOwner`, a
  `cycleTicks` timer runs (scaled by mass), and then everything spawns at the destination. The pattern is a
  transport pod's (UNVERIFIED as a reuse; it is a few lines either way).
- **Downed strangers and wild animals:** add them to the send list. Prefer a hoist-owned dialog subclass
  (or a postfix scoped to `RM_KeelHoist`) over patching the shared `AllSendablePawns` call, which every
  caravan reads. Capturing a stranger this way should apply vanilla's capture (they arrive as **prisoners**),
  never a silent kidnap.
- **Tether lock:** a Harmony **postfix on `Building_GravEngine.CanLaunch`** (non-virtual, VERIFIED) refuses
  launch while any `RM_KeelHoist` on the ship has a cable deployed. Message: *"Reel in the keel hoist first."*
  This doubles as the long-missing guard on `RM_SeaDiveHatch` (launching with pawns below is UNMEASURED today, §1c).
- **Pairing:** a targeting gizmo, "Drop cable", picks a portal or a cell within `hoistRange` (ship form)
  or the portal underneath (placed form). The pairing is saved by reference. A destroyed or sealed target
  drops the cable automatically.

### 2e. Gating and cost — balance by cost, never by narrowing scope

- **Research:** one project on the gravship branch (defName to be measured, never guessed, as
  `RM_SeaDiveHatch.xml`'s comment already insists).
- **Build:** steel, components, and plasteel for the ship form, which is heavy. The placed form is wood/steel and cheap.
- **Running:** power while cycling. A cycle's time grows with mass, so a one-mass shipment is fast and a
  minified generator is slow.
- **Exposure:** while the cable is deployed **the ship cannot leave.** That is the honest cost, and the
  risk: a raid arrives while your cable is down a hole. Optional later: the cable can be cut (an
  incident), which strands the cradle below.
- **Mod Settings** (every mod, owner 2026-09-12): master on/off; ship form; placed form; tether lock (on
  by default, labelled as a safety rule); capacity multiplier; cycle-time multiplier; pawns-may-ride;
  downed-wild-animals; and, in the RimUtinni layer, the Hutt pit trade and the lottery as separate toggles.

### 2f. Tiers and names

The device is **invented**, so it lives in the free **`RM_`** tier (`mandrake.rm.*`). Suggested home: a
generalisation of `DivingInteraction`, or a new small `RimMandrake.KeelHoist` mod; that is a packaging call.
Everything Hutt (the slave pit, the oubliette, arena fodder, the lottery's Hutt dressing) is canon and goes to
**`RUT_`** under `UtinniPatches`/a RimUtinni mod. The lottery's *mechanism* (send cargo, get value back) can
be an `RM_` building any faction can own; the Hutts just wear it best.

## 3. Reuse sites

Every row below is **the same comp with a different target**. Rows marked **(RUT)** are campaign/canon.

### 3a. The Hutt slave pit (RUT) — the owner's first example

- **The site.** An inhabited Hutt place whose centrepiece is a **pit with a Hutt-owned head-frame**
  (`RM_HoistFrame`, owned by `RUT_Jawa_HuttCartel`) over an oubliette.
- **Selling.** The pit's keeper buys: **any slave** (Ideology slave status), **secure prisoners** (open: §6 Q5),
  and **unconscious beasts, tame or not**. The player's own pawns **walk the sold pawn to the head-frame and
  lower them.** On arrival below, payment comes up the same cable as silver, or as Hutt favour (open).
  The price is the pawn's market value times a Hutt pit multiplier. Wild animals already carry a market value,
  so beasts need no new pricing.
  *Mechanically this is the hoist's load dialog with a sell side.* Vanilla caravan trade already sells
  prisoners; the pit is the version you do with your own hands.
- **The oubliette.** Below the pit, slaves are **already there and cannot get out**: a pocket map, or an
  enclosed superdeep room, with no exit except the cable. Its residents are pawns of a captive/slave faction
  with the Hutt holding-pens cast (`hutt_holding_pens.lua` already names "guard" and "debtor" roles).
  **The player can buy one up** (pay, and the cable brings them up as your slave). They can **go down**
  (pay for the ride, if pawns may ride: §6 Q2) to free or recruit. Or they can **cut a deal** to remove one.
  `RUT_HuttCartel_Captives`' droid debtors belong here too: its header names this exact plug-in point.
- **Arena fodder.** The oubliette is the arena's larder. A Hutt arena event draws fodder from it. Whether the
  arena is a place the player visits and bets at, or an offstage consumer reported by letter, is §6 Q8.
  The hoist's job ends at "fodder goes up to the arena". The arena itself is its own item.
- **Prerequisite (the big one):** no Hutt place spawns cast or composes a holding-pens district today (§1a).
  Two routes: a small **standalone slave-pit site** (one map, one template, its own cast def), or wait for
  Gorga's Palace multi-district composition. §6 Q7.

### 3b. Dungeon entrances — the owner's second example

| dungeon | item | how the hoist serves it |
|---|---|---|
| Foundry towers | live (`RUT_FoundryTowerEntrance`) | a ruined head-frame beside the tower mouth: repair it and heavy salvage comes up without carrying |
| Breached vaults V1–V6 | `VAULT_DUNGEON_BUILD_1` | vault shafts with dead lifts; **the frozen Rakata** (V6) come up on a cable, sealed, rather than being walked out |
| Assailant first-impact site | `ASSAILANT_DUNGEON_BUILD_1` | the thaw-gate's *"old power core"* is too heavy to carry: it has to be **lowered** to its socket. That is a reason to bring the ship |
| Fever Wood ant hives | `FEVERWOOD_ANT_HIVE_DUNGEON_1` | none by default. A hive is a crawl. Listed so nobody forces it |
| Sarlacc (D-1) | `sarlacc_discussion_pack.md` | **feeding the sarlacc** is the hoist lowering a body or offering (`design/Jawa/devotional_sacrifice_catalog.md`), and pulling a swallowed colonist **up** is the rescue |

### 3c. Lantern Deeps cave mouths — where it started

The ship parks over `RM_LanternDeepMineshaft` and drops its cable: crystal and Working-Dead salvage come up,
and supplies and light go down. GPT's original form, unchanged. **It is the best first test site because the
portal already exists and the Deeps already need logistics.**

### 3d. The seas — ship-only rule respected

The owner's rule: *"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."* The keel
hoist **is part of the ship**, so it does not break the rule. A gravship over a sea **drops its cable down its
own sea dive hatch** as the target. Sea-floor salvage, catch and bodies come up by cable while the crew works
below, and the tether lock stops the ship leaving with the crew still on the floor. Whether the hoist then
**replaces** the hatch, **sits beside it**, or **is** the hatch in another mode is §6 Q3.

### 3e. More sites (BENCH's list; GPT's in §7)

- **Our own superdeep pits** (FlowWorks): serve a pit prison from the lip, lift a prisoner out without a
  ladder, and lower a meal. Within-map target. Already consistent with *capture down*.
- **Fall-zone lost cargo** (`FALLZONE_LOST_CARGO_QUESTS_1`): a manifest points at a crate down a crevasse
  or under a wreck. Recovery means bringing the ship.
- **The sandcrawler** (Jawa canon): the Jawa sandcrawler's **canon suction tube/lift pulls droids aboard**.
  The keel hoist is the Jawa identity in device form. That pairing is worth GPT's eyes.
- **Rescue:** a downed colonist at the bottom of a hole, pulled up before the cave-in.
- **Mines and deep drills:** ore up a shaft.

## 4. The Hutt lottery — "the chance chute"

**Prior art:** the owner's *"catapult in their vault"* is, by the evidence, **VQE Ancients'
`VQEA_PneumaticTubeLaunchPort`** (active in his list). Cargo goes into a capsule and down the tube, and *"you
may receive some goods from another vault in return."* Its valuation is UNVERIFIED (in its DLL). The
campaign also pitched the same thing as **XX4 "The casino"**: *"gamble silver against a crate."*

**The design:** a Hutt-owned **chance chute**, the hoist's comp in "send-only" mode, at Hutt trading posts.
1. You load cargo into the cradle (the same dialog) and pay the house a stake.
2. It goes down. A timer runs: hours, not seconds, so it is a decision rather than a slot machine.
3. A crate comes **up** holding items of **similar total market value**, built by vanilla's own
   `ThingSetMakerParams.totalMarketValueRange` (VERIFIED field) around a roll: mostly 0.7 to 1.1 times,
   rarely a 3× jackpot, rarely a 0.3 dud. **The house keeps a cut.** Hutts never run a fair game.
4. **Optional:** slaves and beasts are cargo too. You send a beast and a crate comes back. This connects to §3a.

**Why it is cheap:** no new UI (the portal load dialog), no new item generator (vanilla
`ThingSetMaker` with a value range), and no animation (a fade, then the crate is simply there on the cradle).
**What it must not become:** a free trader. The stake plus the cut keeps its expected value below 1, and a
Mod Settings slider owns the odds.

## 5. Build ladder — smallest shippable slice first, animation last

**The guard against endless animation (owner: *"careful we don't get caught in endless animation
development"*):** the shipped visual is **a line and two static sprites**. The cable is `GenDraw.DrawLineBetween`
(VERIFIED) from the hoist to the mouth while deployed, and the cradle is one static texture with a "loaded"
variant. Transit is invisible: things vanish, a timer runs, and things appear. **No step on this ladder waits on
art or animation.** Art is a final, separate row, and it may never happen.

| # | slice | proves | size |
|---:|---|---|---|
| **0** | **Ship form, items only, one target type.** `RM_KeelHoist : MapPortal` fitting, "Drop cable" onto any `MapPortal` within range, lower and raise items via the vanilla load dialog plus a bottom cradle, cycle timer, **tether lock** postfix, Mod Settings, a placeholder sprite, and a cable line. Test site: `RM_LanternDeepMineshaft`. | the comp, the pairing, the lock | **M** |
| 1 | **Pawns:** colonists, slaves, prisoners, downed colony pawns (vanilla already allows these), plus **downed strangers and wild animals** arriving captured (the engine gap). | the owner's beasts | S–M |
| 2 | **Placed form** `RM_HoistFrame` and **within-map cell targets** (superdeep pit floors). | pit service from the lip | M |
| 3 | **Sea hatch as a target**, after the owner rules on §6 Q3. | ship-only seas get cargo | S |
| 4 | **Chance chute** (RM mechanism, RUT dressing) at existing Hutt **traders/posts**. Needs no Hutt map. | lottery | M |
| 5 | **Hutt slave pit**: sell-to-pit, buy-up, and the oubliette. **Blocked on a Hutt map with cast** (§6 Q7). | the owner's first example | L (+ the site) |
| 6 | Arena fodder hook, dungeon head-frames (vaults, foundry, assailant core), sarlacc feeding. | reuse | S each |
| 7 | **Art, optional:** head-frame and cradle sprites through artpipe (check `artpipe/done/` first). **A cradle descent animation is not on this ladder.** | — | — |

**Recommended first slice: 0 + 1 together**, the ship hoist on the Lantern Deeps mouth moving items and
downed beasts. It exercises everything the Hutt pit will later need, on a portal that already exists.

## 6. Open questions for the owner (plain language)

1. **The oubliette.** On 2026-09-17 you cut the pit "oubliette" fitting (*"forget the oubliette/ion thing"*).
   Now you have described a Hutt oubliette full of slaves who cannot get out. Is the Hutt one a **place** (a
   hole with people in it, reached only by the hoist) while the cut fitting stays cut? And is that place a
   **separate underground map** below the pit, or a **walled superdeep room** on the surface map, like our own pits?
2. **Do people ride the cable?** Should colonists be able to ride the cradle down and up awake, which makes the
   hoist an entrance as well as a lift? Or should it carry only goods, plus people who are carried (prisoners,
   the downed, the sold)?
3. **The seas.** Your ship already has a dive hatch. Should the hoist **replace** it, **sit beside it** as the
   cargo route, or should the hatch simply **become** the hoist's sea mode?
4. **Only on the ship?** Should players also be able to build a cheaper fixed head-frame on the ground, or is the
   hoist the ship's alone, with fixed ones appearing only at Hutt pits and old dungeons?
5. **What the pit buys.** You said "any slave" and unconscious beasts. Should it also buy **prisoners who are not
   yet slaves**, and does it pay in **silver** or in **Hutt favour**?
6. **The lottery's odds.** Should the house always take a cut (on average you lose a little)? Can you send
   **slaves and beasts** down the chute, or only goods?
7. **Where the pit lives.** No Hutt place has people or a holding-pens area yet. Should we build **one small,
   stand-alone slave-pit site** first, or wait until Gorga's Palace is built out properly?
8. **The arena.** Is the arena a place you **visit and bet at**, or something offstage that the pit feeds, which you
   only hear about?

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
- **Correct: moment 18 (the seas)** assumes the whole ship sinks to the floor, which is GravTide's model. **Our
  shipped mechanism is different:** `RM_SeaDiveHatch` sits in the ship while it rides the sea tile, and its pocket
  map *is* the floor. Under ours, the hoist's sea target is that hatch. GPT's version is stricter than the
  owner's rule requires. It feeds §6 Q3 and changes nothing until he rules.
- **Correct: moment 23 gives Ozzik a *liberation* rite.** Ozzik is the god who always seeks to enslave and
  always fails. A rite of his belongs at the **sale**, as the clan's temptation, and his *failure* is the
  breakout. Any rite here goes to the owner through the usual rites card. None is adopted.
- **Decline: the "Drumkeepers" RM_ cultural layer.** It is an invented tradition the free tier does not need.
  The device stands alone without lore.
- **Scope traps:** all five agree with §5. Trap 3 (one pairing per hoist, dungeons as chains of pairs) becomes
  a design rule here, as does trap 4's "capture status applied on arrival".
- **What GPT did not catch:** the downed-stranger and wild-animal gap is a real engine change
  (`allowCapturableDownedPawns: false`, §1c). The tether lock also has to cover the existing sea hatch, whose
  behaviour on launch is UNMEASURED today.

**Revised first slice:** ladder 0 + 1 (the ship hoist on the Lantern Deeps mouth; items, pawns and downed
beasts), **plus the manifest and an Open Line counter stub.** That stays size M, and it is the whole skeleton
every later moment hangs on.
