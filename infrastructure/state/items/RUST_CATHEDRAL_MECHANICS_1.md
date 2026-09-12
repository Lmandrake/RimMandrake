## spec — the C# kit
Per `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md`:
hum-mood system (a slow-moving attitude value voiced as layered tones, displayed
by the bolts' dances, with droid commentary and hysteresis wiring) · the
deep-drill response event (never described) · wall-tier mining defs (common deck
plate free to mine → dead smartsteel → the sacred tiers) · **living bolts as
mechanical wildlife** · **eel-fishing consequences**.

The governing rule from the sheet: the Cathedral is negotiated **by manners, not
by force** — mine the bulk freely, touch nothing sacred, and when the hum drops,
stop moving. *The bolts freeze first — watch them.*

---

## ⭐ ADDED 2026-09-07 (owner) — THE ROACHES: THE LAND CLEANERS

**Enhancing this item rather than filing a new one, per the owner's own
instruction.** It belongs here because the bolt-dance/hum-mood display and the
coolant eels are already this item's, and the roaches are the third leg of the
same ecology.

> Owner, 2026-09-07: *"reskin the cockroaches mod to pertain to the Scarlands
> around the Rust Cathedral and the Rust Cathedral itself. Both organic and
> artificial versions. Make them much smaller and the synthetic ones strangely
> tough and powerful. Cleaners of the area on land like the eels that live in the
> coolant rivers."*

### the donor, MEASURED 2026-09-07
**`LingLuo.Cockroach` — "Rim cockroach"**, already **ACTIVE** in the mod list.
`steamapps/workshop/content/294100/3196253802`. It ships exactly two creatures,
which map one-to-one onto the ask:

| def | label (donor) | bodySize | parent |
|---|---|---:|---|
| `Ling_Cockroach` | 巨型蟑螂 "giant cockroach" | 2 | `AnimalThingBase` → the **ORGANIC** roach |
| `Ling_Cockroach_Mechanoid` | 机械蟑螂 "mechanical cockroach" | 2 | `BaseMechanoidWalker` → the **SYNTHETIC** roach |

⚠️ Donor labels are **Chinese** — the reskin must relabel and redescribe both
regardless of anything else.

### what the reskin must do
1. **Much smaller.** Both are `bodySize 2` — bigger than a human. They should
   read as small scuttling things, not giants.
   🔑 **`bodySize` does NOT scale melee damage** (see the ceiling-fields lesson) —
   so shrinking them does not disarm them. That is *convenient here*: it is
   exactly how the synthetic ones stay **"strangely tough and powerful"** at a
   fraction of the size. Set the size down; tune armour/health/damage
   deliberately and separately, never by "scale all attributes".
2. **Two registers, one animal.** Organic roaches in the **Scarlands** around the
   Cathedral; synthetic ones in and near the **Cathedral itself**. The synthetic
   version is the unsettling one: small, patient, and much harder to kill than it
   looks.
3. **Cleaners, not vermin.** They are the **land counterpart to the coolant
   eels** — they clear the ground the way the eels clear the canals. That gives
   the Cathedral a closed ecology: eels in the coolant, roaches on the land,
   bolts in the air of its attention.
4. ⛔ **NOT part of the hum-mood system — ruled by the owner, 2026-09-07:**
   *"Leave the roaches out of the hum mechanics for now."*
   The bolts remain the **only** display of the Cathedral's attitude, and the
   survival rule stays as the sheet writes it: *when the hum drops, stop moving —
   the bolts freeze first.* **The roaches are fauna, not instrumentation.** Do not
   wire them to the attitude value, and do not give them a freeze/scatter tell.
   *(Read "for now" as reversible, not as an invitation — reopen only on his word.)*
5. **Salable?** The sheet already has *"bolt-shed curiosities and eel-catch —
   both salable, both watched."* Decide whether roach parts join that list, and
   whether harvesting them is one of the things the Cathedral *minds*.

### before assuming a pure-XML reskin
🔴 The donor ships **`Assemblies/`** (and a `1.6/Assemblies/`). **Read what the
DLL actually does before planning an XML-only reskin** — behaviour may be baked
into C# that a def patch cannot reach, and a reskin that only renames the label
will leave donor behaviour intact under a campaign name.
⚠️ Also check the donor's own `Patches/` folder for what it does to vanilla.

### cross-refs
- `SCARLANDS_MECHANICS_1` — the organic roaches live in its biome; the two items
  share the Scarlands surface and should not invent two different roach stories.
- `the_rust_cathedral.md` §the coolant eels, §the living bolts.
- Naming: new defNames take the tier grammar (`design/NAMING_SCHEME_PLAN.md`) —
  `RUT_` for campaign-specific, and "Jawa" is lore text only.

## 2026-09-11 update — §6 (roaches) BUILT, rest of the kit (§1-5) not started

`mandrake.rut.rustcathedralroaches` shipped: `RUT_ScarRoach` (organic,
Scarlands) and `RUT_CathedralRoach` (synthetic mechanoid, "strangely tough"
per the owner's own words — healthScale 1.6, armor 0.75/0.75 at bodySize
0.22), plus `RUT_CathedralRoachShell` byproduct. Donor DLL independently
re-verified via dnfile enumeration (5 TypeDefs, no Harmony/game-wide hooks —
confirmed, not trusted from the spec). New generic mechanism landed in the
shared `mandrake.rm.creaturebehaviors` engine: `RM_EatCleanableExtension` +
`RM_ThinkNode_EatCleanable` + `RM_JobDriver_EatCleanable`, generalizing the
donor's tamed-only wastepack-eating to wild pawns + filth. C# actually
compiled (`dotnet.exe`, 0 errors), `validate_patch.py` clean on all XML.
Rostered into both `the_rust_cathedral.json` and `the_scarlands.json`
(split from a stale pre-2026-09-07 single organic-only entry). No hum
wiring, per the owner's ruling — structurally enforced by omission.

✅ **Live-verified 2026-09-11** (canonical Ash'karr save, 592-mod full list):
both `RUT_ScarRoach` and `RUT_CathedralRoach` spawn successfully via
`jawa/spawn_pawn` (by PawnKindDef — `jawa/spawn_batch`'s ThingDef+GenSpawn
route throws an NRE on any pawn-race ThingDef, a pre-existing tool
limitation unrelated to these defs, worth a future
`COMPANION_SILENT_FAILURE_HARDENING_1` line: it should refuse pawn ThingDefs
by name rather than NRE). Confirmed alive and listed
(`RUT_ScarRoach609259`/`609260`, `RUT_CathedralRoach609261`) via
`jawa/list_pawns`. Texture-missing warnings fired as expected (placeholder
art, deferred per scope) — no other errors.

**Rest of the kit is untouched**: §1 hum-mood system (new C# MapComponent +
Def type), §2 wall-tier mining defs, §3 living bolts, §4 eel-fishing, §5
deep-drill response. Per the kit spec's own build order these come before
step 6 normally, but §6 was picked first here because it's explicitly
"independent of §1 by design; parallelizable any time" and was the only
slice small enough to hand to one subagent in one clean pass tonight. Item
stays `doing` — the big hum-mood C# system deserves its own focused session,
not a rushed tack-on.

## 2026-09-11 update — §2 (wall-tier mining defs) BUILT, §1/3/4/5 still not started

New dedicated mod `mandrake.rut.rustcathedralwalls`
(`src/RimUtinni/RustCathedralWalls/`), per the kit spec's own build-order note
that §2 is the first recommended buildable step. All four tiers:

- **Tier 1** `RUT_CathedralDeckPlate` — mineable wall, `ParentName="RockBase"`
  (MineableSteel's own shape), yields vanilla `Steel` at 35/cell, unowned.
- **Tier 2** `RUT_MineableDeadSmartsteel` → `RUT_DeadSmartsteel` — same shape,
  yields a new resource (MarketValue 8, yield 25/cell). ❓ **DECIDED**: trade
  commodity only, NOT stuff-capable this pass — a stuff-capable alloy needs
  armor/insulation balance numbers the spec named no target for, and
  "distinctly valuable" is already satisfied without it (see the def's own
  header for the full reasoning). Reversible later without touching the def's
  identity.
- **Tier 3** `RUT_SacredWall_Conduit` — one sacred wall variant (v1 scope;
  more explicitly deferred), a plain faction-owned building (`ParentName=
  "BuildingBase"`, not RockBase — not mineable), spawned owned by vanilla
  `Mechanoid` (faction 13, already reskinned "the Forgotten/Forsaken Arsenal"
  in `mandrake.rut.patches`' `ForgottenArsenal.xml` — reused, not
  re-invented). Destroying/claiming rides vanilla's own `AttackedBuilding`
  goodwill hook automatically. **Deferred, pending §1**: the −15 magnitude
  check and the hum-irritation bump — no numeric hook or MapComponent
  reference exists anywhere in this build, by design, since §1 doesn't exist
  yet.
- **Tier 4** `RUT_LivePatternMetal` — deep-drill-only resource
  (`deepCommonality`/`deepCountPerPortion` 35/`deepLumpSizeRange`, Steel's own
  vanilla shape). Arms §5 (not built).

**Placement mechanism** (task's own instruction: reuse an existing pattern,
not invent one) — two, layered: (1) `RUT_RustCathedral`'s BiomeDef gains
`forceRockTypes` (a genuine vanilla BiomeDef field, confirmed via rimsage
source read of `BiomeDef.cs`/`World.cs`/`GenStep_RockChunks.cs` — and the
exact field the donor Alpha Biomes def used for its own now-absent
`GU_AncientMetals`) pointed at Tiers 1-2; (2) a dedicated, self-gating
`GenStep_ScatterGroup` subclass (same convention as FungalSoilTrade's
`GenStep_ScatterFungalGround` / LanternDeeps' `GenStep_ScatterCavePortal` —
"GenStepDef has no biome field and vanilla ships no
ScattererValidator_Biome") guarantees baseline coverage regardless of the
biome's near-total flatness (211/236 tiles), and a second custom `GenStep`
places the one Tier 3 variant with `.SetFaction(Faction.OfMechanoids)`. Both
self-gate on `map.Biome.defName == "RUT_RustCathedral"` and are added to the
shared `MapCommonBase` genSteps list, no-opping on every other biome.

**Where "zero new C#" didn't hold**: the biome-gated GenStep subclasses
(established local convention, ~2 small files) and one Harmony postfix on
`CompDeepScanner.ChooseLumpThingDef` — vanilla's deep-resource pick is a flat
GLOBAL weighted pool with no biome axis at all, and this repo's existing
biome-exclusive deep resources (Kyber, Pyrinth) solve the equivalent leak by
riding a dedicated pocket-map generator that an ordinary overworld biome
doesn't have. The postfix substitutes vanilla Steel for `RUT_LivePatternMetal`
whenever the scanning map isn't the Cathedral. All three are small, self-
gated, and documented in-file; none is a guess.

C# compiled clean (`dotnet.exe`, 0 errors, 0 warnings). All 10 XML files
well-formed and `validate_patch.py` clean (0 errors; warnings are the
expected "vanilla texPath/ParentName not in this mod's own files" kind,
same as every prior RUT_ mod's own validation runs).

❓ **Not live-verified** (this was pure offline authoring — no bridge/game
touch per this session's brief): whether the wall-tier density actually
reads as "the map is made of it" on a real Cathedral quicktest map, whether
`GenStep_ScatterSacredWalls`'s faction-owned wall actually triggers
`AttackedBuilding` goodwill on attack, and whether the Harmony gate actually
fires (all three need a quicktest once the mod is deployed and enabled —
deliberately left to the parent session, not done here). Not enabled in
`ModsConfig.xml` by this pass.

**Rest of the kit is still untouched**: §1 hum-mood system, §3 living bolts,
§4 eel-fishing, §5 deep-drill response event.

## 2026-09-12 update — §1 (hum-mood system) BUILT, §3/§4/§5 still not started

Picked §1 over §3/§4/§5 for this pass because the kit spec's own build order
says so directly ("everything else plugs into it" — §3 reads its band, §4
and §5 call its irritation input) and it was named first in the item's own
ask. New dedicated mod `mandrake.rut.rustcathedralhum`
(`src/RimUtinni/RustCathedralHum/`), same one-mod-per-section pattern as
walls (§2) and roaches (§6):

- **`RM_BiomeAttitudeDef`** (new Def type, RM_ tier per the spec's own
  naming note — a generic banded-biome-attitude description any biome could
  reuse) + **`RM_MapComponent_BiomeAttitude`** (new MapComponent — an
  ordinary, non-Custom subclass, so `Verse.Map.FillComponents` auto-adds it
  to every map for free, confirmed via RimSage read of `Map.cs`; a no-op
  everywhere except a map whose biome has a matching Def instance).
- **Ledger, zero new C#**: reads LIVE faction-13 (Forsaken/Forgotten
  Arsenal, `Faction.OfMechanoids`) player goodwill every check; vanilla's
  own `FactionRelation.CheckKindThresholds` −75/0 hysteresis is untouched.
- **Fast layer**: a decaying "irritation" float; composite =
  `irritation − goodwill×0.5`, clamped 0–100, mapped to a 0–4 band via the
  spec's own thresholds (10/30/55/80) with a **de-escalation-only hysteresis
  margin** (6 points) — the spec's named "hysteresis wiring" mechanic,
  implemented at the band layer on top of the ledger's own.
- **Band semantics — this build's own resolution**, not literally specced
  (the spec states inputs/outputs, not which end is "calm"): band 0 =
  calmest (one warm-drone `Sustainer`), one more layer per band up through
  3 layers (**exactly the v1 line's "3 sustainer layers"**), band 4 (the
  worst) goes **totally silent** — the sheet's own "when the hum drops, stop
  moving" survival tell, implemented as literal audio silence rather than a
  bolt-only cue (the bolts themselves are §3, unbuilt, so nothing reads the
  band for a visual tell yet).
- **Layered tones — placeholder audio**: no audio pipeline exists anywhere
  in this repo (checked before writing — zero `.ogg`/`.wav` in
  `src/RimUtinni` or `src/RimMandrake`, zero prior custom SoundDef), so
  `RUT_HumLayerDrone/Tense/Alarm` reuse three vanilla mechanoid-ambient clip
  paths verbatim (`MechanoidRelay_Ambient`, `MechanoidStabilizer_Ambient`,
  `AncientVent_Ambient`, all read whole via RimSage) — same "placeholder,
  reuse vanilla" convention RustCathedralWalls used for art. A real hum
  audio pass is a straight 3-clipPath swap later.
- **Droid commentary**: cooldown-gated (12h) `Messages.Message` on band
  transitions, only with a player-faction pawn on the map whose
  `RaceProps.FleshType == FleshTypeDefOf.Mechanoid` — **ASSUMED** definition
  of "a player droid," not specced; no droid-tag convention exists elsewhere
  in this repo to reuse. Four bands of first-pass §P-register lines shipped
  (register law checked line-by-line in the def's own header) — reversible
  placeholder prose, not an authored sitting.
- **Sustained-worst-band goodwill drain**: −1/4h capped at −5/day against
  faction 13, all through vanilla's own `TryAffectGoodwillWith` — "the hum
  never flips hostility by itself; the ledger does," per spec.
- **Public API for §3/§4/§5 to plug into, unconsumed by anything yet**:
  `RM_MapComponent_BiomeAttitude.GetBand(Map)` and
  `.AddIrritation(Map, float)`.
- Every mechanic gated in Mod Settings (`RustCathedralHumSettings`):
  hum on/off, commentary on/off, goodwill-drain on/off, irritation-decay
  speed slider — all-off degrades to true no-op, none of it worldgen-
  affecting.

**Deliberately deferred, per §1's own v1 scope line** (not gaps found late):
the −15-per-sacred-building `AttackedBuilding` magnitude check (§2/§1
boundary — still nobody's), hum-literacy as a knowledge item, per-colonist
mood thought, the line-cycle ambient dressing event.

C# compiled clean (`dotnet.exe`, 0 errors, 0 warnings — one live fix needed,
an `IReadOnlyList<Pawn>` vs `List<Pawn>` mismatch on
`map.mapPawns.AllPawnsSpawned`). Both XML files `validate_patch.py` clean
against the **2026-09-12T08-25-24Z** live def dump (0 errors; an early pass
had `--` inside XML comments, illegal and fixed). `RUT_RustCathedral`
confirmed live in that same dump as `mandrake.rut.patches`'
`BiomeDefs/RUT_RustCathedral.xml`, matching this mod's `targetBiome` string
exactly.

**Deployed** (`deploy_custom_mods.py --apply`, plan read first, additions
only — no other window's files touched, no DLL was already loaded since
this mod is brand new): 4 files written, `VERIFIED in sync`. **Left
disabled in `ModsConfig.xml`** on purpose, same as walls/roaches — the
running game (full 593-mod list, currently UP) is completely unaffected;
turning it on and quicktesting rides the parent session's own call.

❓ **Not live-verified**: whether the band/hysteresis math actually reads
right in play, whether the placeholder audio layers audibly stack, whether
`IsPlayerDroidOnMap` finds player mechs the way a real droid colonist would
be represented once one exists. All need a quicktest once enabled — not
done here per this pass's offline-authoring brief.

**Rest of the kit is still untouched**: §3 living bolts, §4 eel-fishing, §5
deep-drill response event. §3 in particular cannot fully land until
something reads `GetBand()` for its dance/freeze display.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — §3 living bolts built (3/6 sections now)

`RUT_LivingBolt` (mechanoid-flesh ThingDef/PawnKindDef, own BodyDef
`RUT_BoltFrame`, its own `ThinkTreeDefs/RUT_ThinkTree_LivingBolt.xml`),
`RUT_BoltShedCuriosity`, `RM_JobGiver_ResonantDance` (`ThinkNode_JobGiver`,
same base as this repo's `RM_JobGiver_SeekShade`; queues the dance figure
via `pawn.jobs.jobQueue`, verified `StartJob` never clears it), and
`RM_ThinkNode_ConditionalAttitudeBand` (freezes at the highest band, wraps
vanilla `JobGiver_Idle`, above `ThinkNode_QueuedJob` — the shape vanilla's
own `ConditionalLowEnergy`/`ConditionalDeactivated` use). Watched pricing
via Harmony (matching §2's precedent, not a new comp): `+3` postfix on both
`Pawn_CarryTracker.TryStartCarry` overloads (pickup), `+15` prefix on
`Pawn.Kill` (has to be a prefix — the Map is gone by postfix), and a prefix
on `CompSpawner.TryDoSpawn` scoped to `RUT_LivingBolt` for a mod-settings
shed toggle without replacing the vanilla comp.

**Band direction resolved against the spec's own numbers, not its prose**:
the kit spec's prose says "freeze at band 0," but §1 *shipped* band 0 =
calmest and band 4 = silent — freezing at 0 would invert the intent, so the
freeze fires at band >=4 and dance energy falls as band rises. Both are
plain XML fields, a two-number edit reverses it if this reading is wrong.

**Spec's own ❓ resolved, not achievable as asked**: "hunt allowed but
priced" cannot be built — `RaceProperties.Animal` requires
`!ToolUser && IsFlesh`, and mechanoid flesh fails `IsFlesh`, so the Hunt
designator is unavailable to a mechanoid-fleshed race entirely (not a bug,
an engine rule). Killing by draft still works and is what the +15 prices.
Switching to organic flesh to regain Hunt would break "not meat," which the
spec mandates — flagged rather than silently dropping either requirement.

🔴 **Real pre-existing bug found, NOT introduced by this pass, affecting
already-live §6 content**: `RUT_LivingBolt` needed its own main think tree
because `BaseMechanoidWalker` (vanilla `Mechanoid`'s think-tree base) has
NO `insertTag` at all — the `Animal_PreMain` insertion route
`mandrake.rm.creaturebehaviors` uses to add custom animal nodes cannot
reach a mechanoid-tree pawn. **§6's `RUT_CathedralRoach` (already deployed
and ENABLED in the live 593-mod `ModsConfig.xml` as
`mandrake.rut.rustcathedralroaches`) almost certainly never runs its own
`RM_ThinkNode_EatCleanable` node for the same reason** — the roaches ship
live but their land-cleaning behavior may never actually fire. Filed as
its own item: `CATHEDRAL_ROACH_THINKTREE_GAP_1`. Not fixed here — out of
this pass's scope and needs its own live-verify.

Built clean (`dotnet.exe`, 0 errors/0 warnings). `validate_patch.py` against
the 2026-09-12T13-25-42Z live capture (confirmed 592 mods == live
`ModsConfig.xml`'s 592 active): 5 files, 0 errors, 3 warnings (known
placeholder-art texPath kind, same as §1/§2). No defName collisions. Left
DISABLED in `ModsConfig.xml`, matching §1/§2/§6 — not live-verified (dance
figures actually reading as dancing, freeze visibly landing, CompSpawner
firing in practice all need a quicktest once enabled).

**Known gap, not persisted**: the pickup-charge debounce is a session-local
`HashSet<int>` of thingIDNumbers — after a save/load, an already-charged
curiosity can charge irritation again on repickup. Fixing it needs an
ExposeData field on §1's MapComponent (no new comp on the item, per ban 1).

**Kit tally: 4/6 sections now** (walls, roaches, hum-mood, living bolts).
§4 eel-fishing and §5 deep-drill response remain untouched.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — §4 eel-fishing + §5 deep-drill response built: 6/6 sections offline-complete

**§4**: `RUT_CoolantEel` fish ThingDef, sole `fishTypes` entry on Cathedral
canal water; line-in tell via the spec's preferred interval-scan route (no
Harmony needed there — §1's existing 250-tick scan check vs a ~7500-tick
fishing job, nothing structurally awkward); per-catch pricing DOES need a
Harmony postfix on `WaterBodyTracker.Notify_Fished` (a catch is invisible
to any scan, it fires inside one toil's initAction); one
`RUT_NegativeFishingOutcome_CoolantEel` (vanilla def type), vanilla gate
re-confirmed live in `FishingUtility.cs` (2%, 300000-tick/5-day cooldown —
the class's own `NegativeCatchCooldownTicks` constant is dead code, not
what actually executes).

🔴 **Real bug found and fixed, not a §4 build choice**: the Cathedral biome
shipped `maxFishPopulation = 0`, which makes `Zone_Fishing` refuse to exist
at all — §4 would have been dead content without this patch, same failure
class as the `RUT_LivingBolt`/roach think-tree gap found in §3.

**§5**: built to the spec's own v1 line, quoted verbatim — "incident +
worker + lord reuse + undescribing letter" (pre-event tells and partial
responses explicitly deferred, per spec). A faction-13 force converges on
a drill sitting over `RUT_LivePatternMetal` via vanilla
`LordJob_AssaultThings`, destroys it, withdraws. The spec's own ❓
(unweighted incident-category roll) resolved via its own stated fallback:
a Harmony postfix disabling vanilla bug-infestation on Cathedral maps only.
**Spec's premise corrected**: `RM_LordJob_DefendPerimeter` (named in the
kit doc) does not exist in this repo (`ScarlandsLadder` ships no Source) —
used vanilla `LordJob_AssaultThings` instead, so "withdraw 1 day after
drill death" becomes immediate-on-death rather than a timed retreat.

🔴 **Repo-wide finding, flagging rather than sweeping solo**: `MayRequire`
on a patch `<Operation>` element is **inert** —
`ModContentPack.LoadPatches` ignores it entirely. This mod's own Odyssey
gate was built by xpath-testing for `FishBase` instead. Every OTHER patch
file in this repo relying on a per-Operation `MayRequire` may be silently
unguarded — worth a dedicated sweep item, not assumed fixed here.

Built clean (0 errors/0 warnings). `validate_patch.py` against the
2026-09-12T13-25-42Z live capture (fingerprint-confirmed 592==592): 0
errors on the whole mod's `Defs/`+`Patches/`. No defName collisions
against the 68,881-name live dump. Left DISABLED in `ModsConfig.xml`, same
as every other section. Not live-verified (offline brief) — Harmony
binding, the interval scan catching a real fishing job, and the response
force spawning all need a quicktest.

**Kit tally: 6/6 sections now offline-complete** (walls, roaches, hum-mood,
living bolts, eel-fishing, deep-drill response). Nothing in the kit is
enabled live. `needs=bridge` for the whole-kit enable + quicktest pass.
