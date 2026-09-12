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
