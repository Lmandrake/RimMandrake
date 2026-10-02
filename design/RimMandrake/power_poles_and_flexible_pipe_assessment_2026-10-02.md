# Power Poles Extended, suspended wires and flexible piping — assessment (2026-10-02)

Status: assessment for FOUNDRY, written 2026-10-02 at the owner's ask. Not a ruling; nothing built.

Owner, verbatim: *"At the same time, evaluate the subscribed but inactive mod Power Poles Extended. Perhaps it wouldn't be much more to add suspended wires of similar graphic that allow players to string out power over larger distances? Perhaps to their theft-based pumping equipment? BTW, we're likely going to repurpose all this to make what looks like "flexible piping" that can quickly be installed and de-installed to steal someone's liquids into tanks on the ship. So maybe that's actually part of this mod too? Your advice welcome."*

## 1. Power Poles Extended — what it is

**MEASURED 2026-10-02** (About.xml sweep of both roots, 1,411 About.xml files; sanity probe: 53 mention
"gravship"; exactly one hit for "power pole").

| field | value |
|---|---|
| name / packageId | Power Poles Extended / `gy.ppextend` |
| workshop id | 3339142899 (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3339142899`) |
| author | `gloriousyuri` (no URL, no licence file, no source) |
| supportedVersions | 1.4, 1.5, 1.6 |
| description | *"Retexture the power pole mod and add some extra variant."* |
| subscribed | yes (folder on disk, mtime 2026-10-02 12:28 — subscribed today) |
| active | **no** — absent from `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (610 active, parsed with ElementTree) and from the live `ModsConfig.xml` (which currently holds a 9-mod test tier) |
| contents | 65 files: 3 ThingDefs (`1.5/Defs` and `1.6/Defs` byte-identical), 2 patch files, ~30 PNG+DDS textures. **No DLL, no C#, no source, no Docs.** |

### It is a retexture, not a mechanism

Every def it adds carries `MayRequire="co.uk.epicguru.rimforgepoles"` and
`<thingClass>RimForge.Buildings.Building_PowerPole</thingClass>` plus
`RimForge.Buildings.PlaceWorker_ShowConnectRadius`. Its `Patches/PowerPole.xml` retextures
`RF_PowerPole` / `RF_WallConnector`; its `ModPatches/FortificationIndustrial` patches
`FT_PowerPole` / `FT_PowerPole_Lamp` (Aoba's Fortifications – Industrial, which is active, and
whose own `FT_PowerPole` is ALSO `MayRequire="co.uk.epicguru.rimforgepoles"`).

**The mechanism lives entirely in Epicguru's "RimForge" power-poles mod
(`co.uk.epicguru.rimforgepoles`), which is NOT installed** — MEASURED: no About.xml in either
root carries that packageId (the sweep found four other `co.uk.epicguru.*` mods, so it can see
that author). Consequences, read off the files:

- With the mod active today, its three ThingDefs are **dropped at load** (MayRequire unmet),
  its two `RF_*` patch operations match nothing (and a patch that matches nothing logs
  nothing), and the Fortifications patches target defs that were themselves dropped.
  **Activating Power Poles Extended alone adds nothing to the game.**
- Its `LoadFolders.xml` declares only a `<v1.5>` block. **MEASURED (RimSage, `ModContentPack.InitLoadFolders`, 1.6):**
  with no 1.6 entry the engine takes the highest defined version not above the current one, so on 1.6
  it loads `/`, `1.5` (byte-identical to `1.6`) and, if Fortifications – Industrial is active,
  `ModPatches/FortificationIndustrial`. The `1.6` folder itself is never read. Harmless, but it means
  the author's 1.6 support is accidental.
- The defs show what the RimForge model looks like from the outside: a 1×1 `BuildingBase`,
  `CompPowerTransmitter` (`transmitsPower`), `PassThroughOnly`, `altitudeLayer PawnUnused`,
  `drawerType RealtimeOnly`, `drawOffscreen true` (the wire is drawn by the building in realtime
  and must draw when the pole is off screen — i.e. the wire spans beyond the pole's cell),
  `PlaceWorker_NotUnderRoof` (poles must be outdoors), a "link" gizmo and an "auto-link" gizmo
  over a multi-selection, and a connect-radius place worker. Costs 15–35 steel (+10 wood for the
  lamp pole), 150–250 HP, 750 work, minifiable, Electricity research. Two variants carry a
  `CompPowerTrader` + `CompGlower` (a 100 W street lamp).
### The mechanism it needs: Epicguru's "Power Poles" (`co.uk.epicguru.rimforgepoles`)

Not installed, but its **source is public** — `github.com/Epicguru/Power-Poles` (1.2–1.6 assemblies,
last push 2025-06-25; About.xml supportedVersions 1.4/1.5/1.6, depends on Harmony). Read 2026-10-02
from the repo (not decompiled; source as published, which may differ from the shipped DLL — §4):

- **Real power across distance is ONE Harmony postfix**: `Patch_GenAdj_CellsAdjacentCardinal`
  postfixes `GenAdj.CellsAdjacentCardinal(Thing)` and, when the thing is a
  `Building_LongDistancePower`, appends the `Position` of every pole it is linked to.
  **VERIFIED against decompiled 1.6** (RimSage): `PowerNetMaker.ContiguousPowerBuildings` builds a
  PowerNet by flood-filling exactly `GenAdj.CellsAdjacentCardinal(building)` over buildings with
  `TransmitsPowerNow`. So a linked pole is, to the net builder, "adjacent". No custom PowerNet, no
  custom transmitter comp; the defs use vanilla `CompPowerTransmitter`. On link add/remove it calls
  `Map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(PowerComp)` (sic, vanilla's
  spelling) to force a net rebuild, and dirties the `PowerGrid` map-mesh section.
- **Links**: `Building_LongDistancePower` keeps `HashSet` `connectedTo` / `connectsToMe`, saved with
  `Scribe_Collections.Look(..., LookMode.Reference)` (`ldp_connectedTo`, `ldp_connectsToMe`).
  `CanLinkTo` checks max connections, squared distance vs `MaxLinkDistance`, and roofs. Gizmos:
  Link (target), Unlink (dropdown), Unlink all, Auto-link a selection (a greedy nearest-neighbour
  spanning pass). Roof built over a pole later → its links are cut with a message.
- **Range**: `MaxLinkDistance => PolesModSettings.CableMaxDistance`, default **20 cells**
  (Mod Settings; also segments per cell, default 6, and thickness, default 0.2).
- **Wire drawing**: purely cosmetic. Points from a cubic Bezier between the two poles'
  `GetFlatConnectionPoint()` (per-rotation offsets to the crossarm), control points pulled down by
  `sag = slack * -1.2` (a per-pole "slack" gizmo, "a visual change only"); 10–100 segments; drawn
  every frame in `DynamicDrawPhaseAt(DrawPhase.Draw)` with `GenDraw.DrawLineBetween` at
  `AltitudeLayer.Skyfaller` altitude (above pawns and buildings) with one tinted cutout texture
  (`RF/Buildings/PowerPoleCable`). Saved per pole: `cableColor`, `slack`.
- **No cable entity**: the wire has no HP, cannot be cut, is not a Thing, blocks nothing; a destroyed
  pole simply drops its links. The broken-down overlay is Harmony-prefixed to show a custom
  "under roof" icon.
- **Licence**: the GitHub API reports **no licence** for either `Epicguru/Power-Poles` or
  `Epicguru/RimForge` (no LICENSE file). Default copyright applies: we may read it and depend on it,
  not copy its code or art into our mods. The *technique* (a postfix on a public engine method) is
  not protectable and is the obvious one; reimplementing it ourselves is clean.

### Verdict on the mod

- **Do not depend on it.** It needs a second, uninstalled mod with a C# assembly to do anything,
  carries no licence, and is pure art. Depending on Epicguru's Power Poles instead is possible
  (public, maintained to 1.6) but buys only ~300 lines we would rewrite anyway to get our cord
  look, cuttable wires and theft hooks — and makes a shipped mod hostage to a third party's Harmony
  patch. Recommended: **replace**, reimplementing the postfix technique in our own framework. Depending on it would add two mods to the 630 for a skin.
- **Do not bundle its art.** No licence is stated; "all rights reserved" is the default. Its
  pole textures are also a modern-utility look, not the matte-black Jawa scrap look already
  approved for Messy Conduit (`06_sprawl_jawa.png`).
- **Borrow the idea only**: the UX it advertises (link button, auto-link a selection, a connect
  radius drawn while placing, outdoor-only, a lamp variant) is the right UX and is cheap to
  reimplement on our own cord framework. Leave it subscribed-inactive or unsubscribe; it costs
  nothing either way.

## 2A. Suspended wires

**Overall verdict: MODERATE** — the power half is EASY because the engine trick is proven
(one postfix); the cost is in the cut/drop behaviour and the theft hooks, not in carrying power.

Context the verdict depends on: Messy Conduit is a **visual overlay on vanilla conduits** (a custom
`SectionLayer` printer, saves nothing, changes no power behaviour; planned
`mandrake.rm.messyconduit`), and its doc rates "overhead spans between poles" **NOT ADVISABLE for
phase 1-3** because a span over walls and furniture has no correct occlusion. Epicguru's mod is the
counter-evidence: it draws every span at `AltitudeLayer.Skyfaller`, **on top of everything**, and has
shipped that way since 1.2. For a wire that really is overhead, "above everything except weather"
is the *correct* occlusion, not a compromise — the doc's objection applies to wires lying on or
draped over the floor, which is where Messy Conduit lives. Aerial spans should therefore be a
different render path from floor cords (always-on-top dynamic draw), sharing the curve and art.

| part | verdict | DETECT / TREAT / LOOK / RISK |
|---|---|---|
| Real power across distance | **EASY** | DETECT: linked poles are in one `PowerNet` (`powerNetGrid.TransmittedPowerNetAt` at both ends). TREAT: postfix `GenAdj.CellsAdjacentCardinal(Thing)` for our anchor class, append linked anchors' positions; `Notfiy_TransmitterTransmitsPowerNowChanged` on link change. LOOK: none — invisible. RISK: low; that overload is also used by other callers (e.g. anything enumerating a pole's cardinal neighbours), so the extra "neighbour" leaks to them — Epicguru has lived with it since 1.2. Guard with a `[ThreadStatic]` flag set only inside `PowerNetMaker` if a caller misbehaves. |
| Sagging span drawing | **EASY** | DETECT: visual. TREAT: one cubic/catenary polyline per span, built once on link and cached, drawn per frame (or printed into a per-map dynamic mesh) at Skyfaller altitude with the Messy Conduit strand material (matte black, ribbed). LOOK: matches `06_sprawl_jawa.png` cords, lifted. RISK: hundreds of spans × per-frame `DrawLineBetween` is the one perf trap; batch into one mesh per map, rebuild on link change. |
| Jawa pole / anchor art | **EASY** (art) | Scrap mast, a bent pipe with a crossarm, tape and clamps; a **wall anchor** variant (span starts at a wall bracket) and a **lamp-post** variant. 3 facings. Needs `generating-rimworld-sprites`. |
| Spans over walls/rooms | **EASY** | Allowed; only the *anchors* must be unroofed (`PlaceWorker_NotUnderRoof`), as in Epicguru. A roof built later over an anchor cuts its spans with a message. |
| Build / dismantle UX | **EASY** | Link gizmo (target), unlink, auto-link a selection, range ring while placing; max span from Mod Settings (default ~20 cells — a playtest number, not measured). Link costs a small amount of cable/components, refunded on unlink. |
| Cutting and the downed live wire | **MODERATE** | DETECT: a span is not a Thing, so nothing can shoot it. TREAT: model each span as data on the anchor (endpoints, HP), cut it (a) when an anchor dies — the span falls to the ground as a **floor cord** owned by the surviving anchor, live end sparking (Messy Conduit's break readout), (b) by an explosion/fire whose radius crosses the span's ground projection (`GenExplosion` postfix or a map-component sweep of damage events), (c) by a pawn job "cut cable" on a span (target: the anchor + span picker). A fallen live wire shocks a pawn who steps on it (small burn, stun) — optional. LOOK: the dropped span reuses floor-cord slack physics. RISK: medium — hit-testing a polyline against damage is new code; keep it at "explosions and fire only" for v1. |
| Raids cutting cables | **MODERATE** | A raid lord job that targets anchors (they are buildings — vanilla sappers/breachers already hit them if they are in the way). A deliberate "cut the power" raider duty is new AI; defer. |
| Theft: tapping someone else's grid | **MODERATE** (as a game loop: **HARD**) | Mechanically trivial: link our anchor to *any* transmitter-bearing building (their conduit, their pole) and the nets merge — vanilla ignores faction when flood-filling. That is exactly the risk: on a **settlement map** the hostile base's batteries and generators would start feeding the player's ship equipment, and the player's batteries would feed them. TREAT: a "tap" (clamp) anchor that must be installed adjacent to a foreign conduit by a pawn job (time on the ground, noise), draws power **one way** (a `CompPowerTrader` on our side with negative consumption = the tapped amount, backed by debiting their net's stored energy each `PowerNetTick` via a map component) rather than merging nets. DETECT/LOOK: their lights brown out; our draw readout. RISK: one-way theft is new code (~1 day); merging nets is free but wrong. |
| Running power to the ship's pumping gear | **EASY** once anchors exist | It is just a long span from the gravship's grid to a portable pump on the far bank. The gravship's own power is vanilla `PowerNet` on its map, so nothing special. |

**What vanilla gives (VERIFIED in decompiled 1.6 via RimSage):**
- Nets are built by `PowerNetMaker.ContiguousPowerBuildings`: a flood-fill over
  `GenAdj.CellsAdjacentCardinal(building)` among buildings with `TransmitsPowerNow`. Adjacency is the
  only way transmitters join.
- Non-transmitting consumers/producers attach to the best transmitter within
  `PowerConnectionMaker.ConnectMaxDist = 6` cells (`CompPower.ConnectToTransmitter`, the hookup
  wire). That is the only distance behaviour vanilla has, and it is a fixed 6.
- No vanilla 1.6 def is a power pole (Messy Conduit doc, RimSage search).

## 2B. Flexible piping (liquid theft)

**Overall verdict: MODERATE** for a working hose + pump + ship tank loop on FlowWorks' built stock
API; **HARD** for the full "steal from someone's tanks with consequences" loop, because the pump,
the ship tank, per-body fluid identity and every piece of the theft response are unbuilt.

### Already designed — the owner's idea is an existing FlowWorks pillar

`design/RimMandrake/liquids_framework_design.md` §4 (lines ~177-182) already specifies the
**Tanker raid**: *"fly to a typed liquid body → deploy `RM_HoseSpool` (fast-build, cheap, fragile
conduit-thing hose with a length cap — NOT terrain, NOT a VE pipe) from shore to ship tank →
`RM_PumpPortable` (found or stolen, heavy) pulses N units per interval … into `RM_ShipTank` →
undeploy, fly away rich. Raid pressure = time on the ground while pumping."* Ownership: FlowWorks
owns tank/pump/hose hardware since ruling 20 (2026-09-16; Liquid Logistics never ships —
`LIQUID_LOGISTICS_MOD_1` closed superseded). Build order there: **tank → pump → hose → tanker loop
→ trade**. So the owner's "flexible piping" is `RM_HoseSpool`, and "maybe that's part of this mod
too?" has an existing answer for the *plumbing*: FlowWorks. What is new is that the hose should
**look like** a Messy Conduit cord, and that theft targets other factions' *tanks*, not just lakes.

### Built vs designed (census 2026-10-02, items + `src/` grep; a subagent's sweep, spot-checked)

| thing | state |
|---|---|
| `RM_LiquidBody` / `RM_LiquidStock` (`src/RimMandrake/FlowWorks/Source/`) — bodies, stock, limitless sentinel, recession, `TryDebit(map, c, units, owner)` / `TryCredit` | **BUILT** |
| `Building_LiquidTank` / `RM_LiquidTank` — 2×2, fixed, one `LiquidDef` + `storedUnits`, refuses a second liquid until empty, bottle/barrel jobs only | **BUILT** (no pump/hose interop) |
| `Building_LiquidDrill` | BUILT |
| `RM_HoseSpool`, `RM_PumpPortable`, `RM_ShipTank`, universal cargo tank | **design only** — no class or def in `src/` |
| per-body / per-cell fluid identity (`LIQUID_BODY_FLUID_IDENTITY_1`; owner Q3 *"they don't mix"*, `flowworks_pits_unified_model_2026-10-02.md` §7) | design only; today one map-wide `activeFluid`, and built `TryDebit` uses `owner.ActiveFluid` |
| `LIQUID_INDUSTRY_SETPIECES_1` — found desal/refinery/pumping stations "stock stealable pumps and tanks feeding the tanker pillar" | open, designed |
| `BAZAAR_BROKER_TAB_1` — bulk liquid pump-to-sell / pay-to-fill over the tank API | open, blocked on a tank+pump API that does not exist |
| `TUSKEN_WATER_RAID_1` (closed) — raiders steal water via `JobGiver_StealWater` | built; the **inverse** of player theft — a reusable precedent for "faction reacts to a liquid theft" |
| Any queue item titled hose / siphon / ship tank / power pole / wire / messy conduit | **none found** |

### How a hose plugs into FlowWorks

| part | verdict | DETECT / TREAT / LOOK / RISK |
|---|---|---|
| Pump as a sink on a body | **EASY** | TREAT: `RM_PumpPortable` (minifiable, heavy, `CompPowerTrader` — this is where 2A's aerial span earns its keep) has an intake cell; every pulse it calls `RM_LiquidStock.TryDebit` on the body at the intake cell for `rate × pulse`; a short/false return stalls it (ruling 4: scarcity is stock, not rate; a limitless body always pays). DETECT: body stock falls, ship tank rises. RISK: `TryDebit` is single-fluid today. |
| Pump drawing from a **tank** (theft from a base) | **EASY** | Second intake mode: adjacent to a `Building_LiquidTank` (any faction) → `TryRemoveLiquid`. Same for future universal tanks. No body involved. |
| Fluid identity | **MODERATE** | The hose carries one `LiquidDef` at a time; it takes its identity from the first unit moved and refuses others until purged (mirrors the built tank rule; consistent with the owner's "don't mix"). Lake intake depends on `LIQUID_BODY_FLUID_IDENTITY_1` landing first; tank intake does not. |
| Ship tank | **MODERATE** | `RM_ShipTank` = `Building_LiquidTank` subclass that is a valid gravship substructure building (must survive launch with contents — Scribe already saves `storedLiquid`/`storedUnits`). RISK: whether gravship launch carries arbitrary `Building` state intact is **UNVERIFIED** here (§4); a 1-hour RimSage read of the Odyssey launch/landing copy path before building. |
| Hose as a Thing | **MODERATE** | Not terrain, not a pipe network: a **two-ended link** exactly like a 2A span, but on the floor. Endpoints = pump outlet and tank inlet (or a hose coupler); the path is planned by the Messy Conduit nodal cord planner between those two nodes (walkable cells, slack loops piling against walls). Length cap from the spool item. Stored as data on the pump (endpoints, planned polyline, HP), not as per-cell things — so laying 40 cells is one job, not 40 blueprints. |
| Install / de-install jobs | **EASY-MODERATE** | "Deploy hose": pawn carries the spool, walks the planned path (one job, work scaled by length), places both ends. "Reel in": one job at either end, spool returns to inventory. Fast both ways is the point (raid pressure = time on the ground). Hauling the heavy pump is vanilla minified hauling. |
| Look | **EASY** given the cord renderer | Same strand mesh as the nodal cords with a **ribbed/corrugated hose material** (the Jawa swatch sheet already carries "dark corrugated steel hose" and hose clamps). Flow shown as slow darker pulses travelling along the polyline in the fluid's colour (one UV-scroll on the strand material, active only while pumping). Coiled spool sprite when packed. |
| Breaking | **MODERATE** | A hose has HP; a pawn walking on it does nothing; explosions/fire/melee cut it. A cut hose spills: credit the *remaining units in transit* as a small puddle (FlowWorks' filth or a one-cell `TryCredit`) and stalls the pump — the liquid twin of the downed sparking wire. |

### Theft consequences (design sketch only — nothing here is ruled)

- **Who notices:** stealing from a *faction-owned* tank or a body inside a settlement's map is a
  hostile act. Model it as a goodwill hit per pulse delivered (capped), and the base's pawns get a lord duty to go break the hose/pump (reuse the
  `TUSKEN_WATER_RAID_1` job pattern, inverted).
- **Alerts:** the victim side's "Their water is draining" is invisible to the player; the player gets
  "Hose discovered" when a hostile pawn is assigned to it, and "Hose cut" when it parts.
- **Escalation:** after the ship leaves, a revenge raid from that faction at a probability scaled by
  units stolen (one `IncidentWorker`, or a quest via `rimworld-quests`). Lakes in the wild are
  victimless — only Raid pressure from the map's normal threats applies.
- **Stealth lever:** a quieter, slower hose (Mod Settings rate) vs a fast loud pump — the owner can rule
  which knob he wants.

## 3. Strategy and architecture

### The three options

| | A. everything inside Messy Conduit | B. one shared cord kit + thin features | C. three independent mods |
|---|---|---|---|
| coupling | one mod does cosmetics, power behaviour and liquids | renderer/planner/node model once; features depend on it | three renderers drift apart |
| settings | one huge screen; "turn off the messy look" also turns off your pumps | each feature its own on/off; the kit has only rendering knobs | three screens, duplicated knobs |
| identity | a *cosmetic* mod that secretly changes power nets and owns liquid hardware, which breaks Messy Conduit's "cosmetic, saves nothing, safe to remove" promise | cosmetic stays removable; behaviour is explicit | clean but triplicated |
| ownership | collides with ruling 20 (FlowWorks owns hose/pump/tank) | hose/pump/tank stay FlowWorks'; the hose only *borrows the look* | same collision as A for the hose |
| Northstar | one script must cover three subjects | one small checkable script per mod | as B, plus three rendering scripts |
| risk | one bug disables all three | a kit bug hits all three, mitigated by the kit being pure drawing + planning | lowest blast radius, highest cost |

### Recommendation: B, with the cord kit living *inside* Messy Conduit's assembly at first

Not a fourth mod on day one. A separately loadable library costs a packageId, an About.xml, a
load-order rule and a settings screen before it has a second consumer. Instead:

1. **Messy Conduit (`mandrake.rm.messyconduit`, `RM_`, franchise-free)** ships the cord kit as a
   public namespace (e.g. `RimMandrake.MessyConduit.Cords`): the nodal planner (walkable-cell path,
   slack, pile-against-walls settle), the strand mesh printer, strand **material sets** (Jawa matte
   black, ribbed hose, ...), the break readout (sparks / limp ends), and a small two-endpoint link
   interface (endpoints, polyline, HP, on-cut). The floor-conduit overlay is its first consumer. It
   stays cosmetic and saves nothing of its own.
2. **Aerial Lines** as a second *feature* in the same mod, behind its own settings toggle, because it
   is power-only and uses the same art: anchor buildings (Jawa scrap mast, wall bracket, lamp mast),
   the `CellsAdjacentCardinal` postfix, span links saved on the anchor, aerial draw at Skyfaller
   altitude, dropped span becomes a floor cord on anchor death. This part changes behaviour and
   saves data, so toggling it off must only hide the anchors from the architect menu, never break a
   save that holds them. If the owner wants Messy Conduit to stay *purely* cosmetic, split it out as
   `mandrake.rm.aeriallines` depending on Messy Conduit: same code, one more About.xml. That is a
   half-hour decision, not a design one.
3. **FlowWorks** builds hose, pump and ship tank as ruled (tank, pump, hose, tanker loop), with
   `RM_HoseSpool`'s *drawing* delegated to the cord kit through a soft dependency: FlowWorks draws
   a plain fallback line when Messy Conduit is absent. The hose's *behaviour* (endpoints, length
   cap, HP, spill) is FlowWorks code; only the look is borrowed. Per the all-DLC / full-list rule a
   hard dependency is also acceptable; the soft one just keeps FlowWorks' northstar script
   independent of a cosmetic mod.
4. **Promote the kit to its own library mod** (e.g. `mandrake.rm.cordkit`) only when a third
   consumer appears or FlowWorks wants a hard dependency on the look. Step 1 keeps it a clean
   namespace with no references back into the overlay, so that is a folder move.

Naming: all `RM_` / `mandrake.rm.*`. Nothing here is Star Wars IP; the Jawa look is a material set
of invented scrap style, consistent with Q11a ("Star Wars style" naming is not the tier line).

### Order of work and estimates (agent-days of offline work; live verification extra)

| # | step | depends on | days |
|---|---|---|---|
| 1 | Messy Conduit phase 1 per its own design (overlay printer, nodal planner in C#, Jawa material), extracting the cord kit as it is written, not afterwards | — | per the Messy Conduit plan |
| 2 | **Aerial Lines v1**: anchor defs + art (3 kinds), link / unlink / auto-link gizmos, range ring, the postfix, span save/load, aerial draw in the cord material, roof check, links refused to non-player transmitters | 1 (material + curve only) | 3-4 |
| 3 | Aerial Lines v2: anchor death drops the span as a live sparking floor cord; explosion/fire cuts; a "cut cable" job | 2 + the Messy break readout | 2-3 |
| 4 | FlowWorks `RM_ShipTank` (tank subclass carried by the gravship), after a ~1 h RimSage read of the launch/landing copy path | built `RM_LiquidTank` | 1-2 |
| 5 | FlowWorks `RM_PumpPortable`: tank intake first, body intake second | 4; body intake also needs `LIQUID_BODY_FLUID_IDENTITY_1` | 2 |
| 6 | FlowWorks `RM_HoseSpool`: link, deploy/reel jobs, cord-kit look, flow pulses, cut/spill | 1, 5 | 3 |
| 7 | One-way power tap (clamp anchor that drains a foreign net instead of merging) | 2 | 1-2 |
| 8 | Theft consequences: goodwill, defend-the-tank lord duty, revenge incident | 5-7 and owner rulings | 3-5 |

**Build first: step 2 (Aerial Lines v1).** It is the cheapest visible new capability, it proves the
cord kit works outside the floor overlay (the real architectural question), and steps 5-6 need power
at a distance anyway. The hose waits for the pump, which waits for the ship tank: FlowWorks' ruled
order.

Under the 2026-10-01 **build pause** (no new content until every mod has a first functional script
with a recorded run, `design/RimMandrake/debug_process.md`), each mod needs its script first.
Aerial Lines' is small and deterministic: link two anchors N cells apart, assert one `PowerNet`;
destroy one, assert two nets and a dropped cord.

### Top risks

1. **Net merging on hostile maps.** A link to a foreign conduit merges nets both ways (vanilla's
   flood-fill ignores faction). Refuse links to non-player transmitters until the one-way tap exists.
2. **Gravship carriage of tank contents** is unverified (§4) and gates the whole tanker loop.
3. **Fluid identity.** Lake pumping is wrong until `LIQUID_BODY_FLUID_IDENTITY_1` lands; tank theft
   is unaffected, so build tank theft first.
4. **Postfix side effects.** `GenAdj.CellsAdjacentCardinal(Thing)` has other callers and the extra
   neighbour leaks to them. Low (Epicguru has shipped it since 1.2), but scope it with a flag set
   only inside `PowerNetMaker` if anything misbehaves.
5. **Consequence scope creep.** Theft response is a rules question for the owner, not an algorithm
   to derive; put it to him on a card before step 8.

## 4. What could not be verified

- **Epicguru's shipped DLL vs its GitHub source.** Read from `github.com/Epicguru/Power-Poles` HEAD;
  not decompiled, not installed, never run.
- **Licence intent.** The GitHub API reports no licence on either Epicguru repo, and Power Poles
  Extended ships none. "Default copyright: read and depend, do not copy" is the conservative
  reading, not a ruling.
- **Other callers of `GenAdj.CellsAdjacentCardinal(Thing)`** were not enumerated; risk 4 is reasoned.
- **Gravship launch carrying a tank's `storedLiquid`/`storedUnits`** was not read in decompiled Odyssey.
- **Gravship power** is assumed to be an ordinary vanilla `PowerNet` on its map; not re-read here.
- **The Messy Conduit doc is being rewritten** (nodal cord model) while this was written. This cites
  the 1,133-line version on disk at 2026-10-02 ~12:35 and `06_sprawl_jawa.png`. If the rewrite
  changes the planner's interface, §3 step 1 follows it.
- **Range (20 cells), costs and day estimates** are guesses, not measurements.
- **Live behaviour** of any of this: no game, no bridge, by brief.
- **Hose flow pulses** are untested (no mock-up); a UV scroll on the strand material is assumed to
  work like the sway shader Messy Conduit already relies on.
- **The queue census** came from a subagent's scored sweep (1,400 item files, sanity probe passed)
  and was spot-checked against `src/`, not item by item.
