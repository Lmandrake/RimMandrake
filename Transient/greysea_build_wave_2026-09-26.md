# Grey Sea offline build wave — 2026-09-26 (FOUNDRY background agent)

Owner ruling that started it: *"Grey Sea is indeed the priority, push it to as close to
done as possible."*

Offline only. The game was never launched, the bridge was never taken, nothing here has
been seen running. Every def below validates `0 errors, 0 warnings` under
`validate_patch.py` against the full installed mod set, and the one new assembly builds
clean — that is the whole of the evidence.

---

## Where the Grey Sea stood before this wave (MEASURED by BENCH, content doc §0)

> "NOT built: zero plants, zero own weather, zero own terrain, zero buildings, zero
> incidents, zero minerals — **and the pillars exist in no def of any kind**, though four
> creature descriptions reference them."

## Where it stands now

| | before | after |
|---|---|---|
| plants | 0 | **7** (his seven crystalline forms) |
| own weather | 0 | **1** (salt snow) — and vanilla `Rain` removed |
| own terrain | 0 | **5** (shore crust, brine channel, seep apron, pool shallow/deep) |
| buildings / formations | 0 | **9** (pillar, 2 domes, chimney, jacket, 4 crystals) + the Elder + the encasement |
| minerals / items | 0 | **5 salts, 2 Elder treasures, 3 sessile catches, 4 cured rations** |
| floor animals | 5 | **15** |
| the pillars | *in no def of any kind* | **`RM_SaltPillar`, scattered on every Grey floor map** |

---

## Item by item

### BUILT and closed

**`GREYSEA_FLOOR_FORMATIONS_1`** — `RM_SaltPillar`, `RM_SaltDome`, `RM_SaltChimney`
(vanilla `Building_SteamGeyser`, so the plume costs no C# at all), `RM_BrineJacket` and
four coloured great-crystal nodes. Placed by eight `GenStep_ScatterThings` steps.
🔑 Scoped by the **generator list**, never by the `RM_SeaFloorGround` terrain tag — all
four sea floors share that tag, so the Scald-wreck pattern of a global tag-scoped
registration would have grown salt pillars on the Scald and the Propane Lake.

**`GREYSEA_SALT_SNOW_WEATHER_1`** — `RM_GreySaltSnow` on the Pyrelands `AshFall` pattern
(borrowed snow particle sheet, own off-white `<overlay>`, `snowRate` and `rainRate` both
0 so nothing accumulates as water-snow or melts at +12 °C). The pre-existing defect is
fixed in the same change: `RM_GreySea` carried vanilla `Rain 4` against
`terminator_sea.md`'s ban, and it is **removed, not annotated**.

**`GREYSEA_CRYSTAL_FLORA_1`** — all seven forms, each def carrying the owner's own
verbatim spec in its comment. **Three engine facts had to be fixed or the whole set
would have silently never spawned**, with no error and no log line:
1. the floor terrain is `fertility 0` → every def sets `completelyIgnoreFertility`;
2. `BiomeDef.plantDensity` defaults to `0f` and `RM_GreySea` never set it;
3. the vanilla `Plants` GenStepDef was not in the sea-dive generator at all.

**`GREYSEA_SESSILE_LAYER_1`** — `RM_Nissik` / `RM_Thollim` / `RM_Grusk`, all three new
per the ruling that overrode BENCH's "`RM_Fessk` already covers shrimp". The new shrimp
is `baseBodySize` 0.08 against the ossuary shrimp's 0.9. **"Abundant" is carried by
commonality and never by `wildGroupSize`** — that is how the layer satisfies ban 2
rather than arguing with it.

**`GREYSEA_SALT_CUISINE_1`** — four crystal salts, four cure recipes, four rations in
`mandrake.rsw.cuisine` behind `MayRequire`. One recipe per colour so the node you cut is
a real decision; `RM_RawSalt` is refused everywhere.

**`GREYSEA_SHORE_MUTATOR_SPECIFICS_1`** — the item's (a)/(b)/(c) question answers **(a)**,
and (a) turned out to be **already built**. `RM_TileMutatorWorker_SeaCoast` already
resolves the bordering sea and reads its `RM_SeaShoreExtension` for deep/shallow/beach
terrain; the Grey had all three unset, so **its shore was generating as vanilla ocean**.
Fixed with data, not a fourth mutator.

**`GREYSEA_BRINE_POOL_DEFENCE_1`** — the mechanism, not just the place.
`GenStep_GreySeaFloorDressing` reads the map's own elevation grid, makes its lowest point
the deepest pool, rings it with jacket mineral and stands an Elder in it.
`RM_BrineEncasement` + `MapComponent_BrineCrystallisation` implement Q1(b): a
crystallised pawn is **encased as an object that must be mined out**. It subclasses
`Mineable`, not `Building_Casket`, precisely because `Designator_Mine` gates on
`def.mineable` and *mined* is the word in the ruling. Q2's chimney plume is in, shorter
range and on a per-sweep roll so the chimney really is the visible teacher. Ships its own
Mod Settings toggle.

### PARTIAL, noted not closed

**`GREYSEA_BRINE_ELDERS_1`** — the organism ships (7×7 sessile, one per Grey tile's
deepest pool) with two of its three `RM_` treasures. Not built, and **deliberately not
faked in XML**: the discharge, the persisted per-tile novelty seen-set and its trade, the
pool-dissolving, and the resonant storage crystal (which is not shipped as a def at all,
because a building with no comp is a decoration that lies about what it does). The
*"beautifully useless artifact"* is **withheld on the sheet's own instruction** — it needs
a plot home first or it gets built as a trinket.

**`GREYSEA_ANCHOR_CREATURES_1`** — the pillar-mason is **done**, as the item's own scoping
said it should be: a navigation system, not a creature. No `RM_PillarMason` pawn exists
and none should. Still open: the `AA_Aerofleet` replacement, **not invented on purpose** —
the cut drifter was a *shore* creature, `BiomeDef.coastalWildAnimals` is read off the
**land** biome of a coastal tile and never off the sea, so casting one means editing the
adjacent land biomes' rosters, which `BIOME_SPECIFIC_FAUNA_LAW_1` puts at those biomes'
own sittings. `RM_Maalu` (built this wave) also already occupies the "drifting bell" read.

**`SEA_FISHABLES_ALIVE_IN_DEPTHS_1`** — Grey portion done, all seven catch-only species
given bodies **from their own item descriptions**, which already contained the design.
Other three seas untouched.

---

## Things the owner may want to look at

1. **A tier mismatch this wave exposed but did not fix.** The Grey's seven catch items are
   `RUT_` and `MayRequire`-gated; every one of those names is an *invented* word, and
   Q11a says invented names are free-tier. Their new bodies are `RM_` and inline so the
   free mod's floor stands alone, which leaves `RM_Sallik` (floor) ↔ `RUT_Sallik` (catch)
   instead of the `RM_Essarn` ↔ `RM_EssarnCatch` shape. The real fix is migrating those
   items down to `RM_` — a cross-mod rename touching RimUtinni, not made unilaterally.
2. **No live test of anything here**, including the encasement mechanism, which can take a
   colonist out of the player's hands. It has a Mod Settings toggle and a wide rescue
   window (~1 in-game day) for exactly that reason, but it wants a look.
3. **Every scatter count and every timing number is INVENTED** and says so in its file.
   Density is a thing to judge by looking.
4. **Grey-specific Mod Settings toggles in `mandrake.rm.terminalbiomes` were NOT added**,
   because that assembly was under concurrent edit by the Scald wave all session and two
   agents rebuilding one DLL is how a merge silently drops half a build. The Grey's own
   `greySeaEnabled` biome toggle already existed; per-mechanic sub-toggles for the new
   formations / flora / weather are owed, and the pool defence got its toggle in
   `mandrake.rm.divinginteraction` instead.

## One incident worth recording

A peer agent's `shared_sync.py` ran between my commit and my push, `reset --keep` to
`origin/main`, and **silently discarded a finished commit of mine** (`4a5622ad5`, 16 files).
Nothing warned; `git log origin/main..HEAD` came back empty as though everything were
pushed. Recovered byte-exact from the dropped commit's own blobs via `git show <sha>:<path>`.
⇒ In a shared tree, after every sync, verify with
`git merge-base --is-ancestor <your sha> origin/main` — "0 local-only commits" is not proof
your work landed.

---

## Commits (all pushed)

| | |
|---|---|
| `07618c8e9` | floor formations, salts, scatter steps, generator wiring |
| `31dbd962d` | salt snow weather; vanilla Rain removed |
| `88552b118` | seven crystal flora, five terrains, plantDensity/wildPlants/Plants genstep |
| `1653976ef` | sessile layer + a body for every catch that had none |
| `ab7a48162` | crusted white shore |
| `84a705e3a` | 13 placeholder textures (re-commit after the drop above) |
| `2df65888c` | coloured-salt cuisine |
| `78097f340` | floor-dressing genstep: pool basin, Elder, channels, aprons |
| `6ab38fd77` | kelp + chimney vine joined the roster |
| `4b6e4c703` | the crystallisation defence |
| `6a8e7ce1a` | ledger |
