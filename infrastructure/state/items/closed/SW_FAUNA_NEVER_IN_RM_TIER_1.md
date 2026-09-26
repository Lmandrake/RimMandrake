# SW_FAUNA_NEVER_IN_RM_TIER_1 — Star Wars fauna never sits in a RimMandrake-tier def

## the ruling

Owner, 2026-09-22, typed into a question-card note — which **is** valid owner-said provenance
as of the same day (he ruled it so, and `block_forged_owner_said.py` now accepts card notes;
an option label he merely *clicked* still does not count):

> *"RimMandrake should not name star wars ever. RimMandrake.StarWars purely centers around
> this. Utinni is all about this particular scenario."*

And on the donor dependency underneath it:

> *"if it's a canon reference, we make our own version and it's NOT a conflict with the IP in
> MLIE"*

⇒ A `RM_` def may not reference a Star Wars creature **by any route** — not ours (`RSW_`), not
a donor's (`mlie.starwarsanimalcollection`), inline or otherwise. **A `MayRequire` does not
launder it.** Star Wars fauna reaches a `RM_` biome only through the Utinni patch layer.

Recorded as §7 **Q11** in `design/RimMandrake/biome_mod_architecture.md`, which it also
**narrows §7 Q9** — Q9 said "donor fauna inline in RimMandrake defs: ACCEPTABLE", which as
written would have admitted Mlie's Star Wars rows. It never meant that.

## why this exists at all

`biome_mod_architecture.md` §4a instructed the Greentide split to keep 22 of its 27
`wildAnimals` inline in `RM_Greentide`, describing them as "22 vanilla". **MEASURED 2026-09-22
by `MayRequire`: zero of the 27 are vanilla** and those 22 are `mlie.starwarsanimalcollection`.
Following that instruction would have introduced the first violation of this ruling.

## what is actually true today — MEASURED 2026-09-22

✅ **Nothing shipped is in violation.** All four existing `RM_`-tier BiomeDefs name **zero**
Star Wars rows in `wildAnimals` or `wildPlants`:

| `RM_` def | Star Wars rows |
|---|---|
| `RM_Greentide` | 0 |
| `RM_Pyrelands` | 0 |
| `RM_GelatinousSlime` | 0 |
| `RM_FloodedCanyon` | 0 |

🔑 **`RM_Pyrelands` is the worked precedent for the correct shape**: its Star Wars fauna
arrives via `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`, a
`PatchOperationAdd` onto the `RM_` def. Copy that, per biome.

✅ **Greentide's animal half is DONE, 2026-09-22** — `WildAnimals_Greentide.xml`, 27 rows,
sum 9.318, verified row-for-row against the frozen `RUT_` def, casting our own `RSW_` ports
rather than Mlie's bare names per the owner's 2026-09-19 donor ruling. It is the second
worked example and the one to copy for the rest, because unlike the Pyrelands it also shows
what to do when a port does NOT exist (leave the row out and name the owed port — never
reach for the donor defName). 🔴 UNVERIFIED against a load; see step 5.

🔴 **A `wildAnimals` key resolves to a `PawnKindDef`, not a `ThingDef`, and a `ThingDef` name
there fails SILENTLY.** Check both def types exist for every port before casting it — all 24
of Greentide's did, but that was measured, not assumed.

The work is in the **12 `RUT_` defs still to split**, carrying **97** `mlie.*` rows between
them (plus their own `RSW_` rows, which this ruling also routes out):

| `RUT_` def | `mlie.*` rows / total |
|---|---|
| `RUT_AridShrubland` | 35 / 45 |
| `RUT_Greentide` | 22 / 27 |
| `RUT_Miasma` | 9 / 31 |
| `RUT_WeepingStones` | 8 / 10 |
| `RUT_FeverWood` | 7 / 11 |
| `RUT_CrackedLands` | 5 / 10 |
| `RUT_PoisonForest` | 3 / 17 |
| `RUT_Webwork` | 3 / 4 |
| `RUT_TheForge` | 2 / 7 |
| `RUT_Scarlands` | 1 / 9 |
| `RUT_Wasteland` | 1 / 17 |
| `RM_TheRot` | 1 / 20 |

## spec

1. **This is not a standalone sweep — it is a rule each `<BIOME>_RM_MOD_BUILD_1` obeys at its
   own split.** ⛔ Do not pre-emptively rewrite the 12 `RUT_` defs: they carry the player's
   world until the terminal paint (`BIOME_PAINT_ONCE_AT_THE_END_1`) and are frozen, not edited,
   at step 3. The routing happens when the content is copied into the `RM_` mod at step 2.
2. At each split, the `wildAnimals`/`wildPlants` rows partition three ways:
   - **Star Wars → Utinni.** Any row whose `MayRequire` is `mlie.starwarsanimalcollection` or
     `mandrake.rsw.swbestiary`, or whose defName starts `RSW_`/`SW_`, goes to
     `UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a `PatchOperationAdd` onto the `RM_`
     def, keeping its `MayRequire` and commonality unchanged.
   - **Non-Star-Wars donor → inline**, per Q9's real scope: `sarg.alphaanimals`,
     `oskarpotocki.vfe.insectoid2`, `GR_`, `vanillaexpanded.*` and similar stay in the `RM_`
     def with their `MayRequire`.
   - **Ours and not Star Wars → inline**, renamed `RM_`. §7 Q10's seven creatures
     (`RUT_FurnaceBeast`, `RUT_FireHawk`, `RUT_Emberscythe`, `RUT_FireWasp`, `RUT_Flamefang`,
     `RUT_Barbslinger`, `RUT_Sytheclaw`) are campaign originals, so they belong here.
3. **Price the thin-roster consequence per biome and report it, do not silently ship it.** With
   Star Wars routed out, `RM_Greentide` carries 4 animals standalone, `RUT_WeepingStones`' mod
   would carry 2 and `RUT_Webwork`'s 1. Authoring each `RM_` biome its own non-Star-Wars fauna
   is owed work; ⛔ it is **not** a reason to keep Star Wars rows inline.
4. **The long-term answer for the 97 donor rows is `DONOR_DEFS_PORT_TO_OURS_1`** — port them to
   our own `RSW_` defs, which the owner's second sentence above explicitly blesses. That
   removes the Mlie dependency; it does **not** make them eligible for a `RM_` def, since
   `RSW_` is still Star Wars.

## verify

- For each biome split: its `RM_` def names zero rows matching `MayRequire` in
  {`mlie.starwarsanimalcollection`, `mandrake.rsw.swbestiary`} and zero defNames starting
  `RSW_`/`SW_`, and every such row appears exactly once in that biome's Utinni patch.
- 🔴 **An unmatched `PatchOperationAdd` is SILENT.** A clean `validate_patch.py` run is not
  proof a row landed — confirm from a post-load def dump, per each build item's own verify.
- Row counts before and after match per biome (no row lost in the move).

## criteria

A player installing a RimMandrake biome mod alone gets a biome with no Star Wars in it; the
same biome inside the Utinni scenario is unchanged from today.

## Watch out

- ⚠️ **`wildPlants` is in scope too, and it is easy to miss** — `RUT_Greentide`'s plant list
  carries 8 `mlie.starwarsanimalcollection` rows (hydenock, jogan, muja, hubba gourd, felucian
  glowspore, bubblespore, chakroot, tooke-trap) alongside 2 `sarg.alphabiomes` and our own
  `RUT_GiantLeaf`. Star Wars *plants* route out exactly like the animals. §7 Q8 dissolves
  `mandrake.rut.ashkarrflora` into the biome mods, so these two rules meet — read both.
- ⚠️ **A `fishTypes` block can name Star Wars too.** `RUT_Greentide`'s names `RSW_MeeCatch`,
  `RSW_FaaCatch`, `RSW_LaaCatch`. Those are ours and Star Wars, so under this ruling they
  cannot sit on a `RM_` def either — the Odyssey `fishTypes` block needs the same Utinni-patch
  treatment, and no existing `WildAnimals_*.xml` does that yet. **This is the one part of the
  routing with no precedent to copy.**
- ✅ **The quote at the top IS usable as owner-said provenance** — card notes were made valid
  2026-09-22 on his ruling. ⛔ But an option **label** still is not: the guard subtracts every
  string the assistant authored, so quoting a label he clicked is refused by design.
- 🔑 The `MayRequire` attribute is the only reliable tier signal, and **the defName is not** —
  Mlie's Star Wars rows carry bare names (`Gizka`, `Bantha`, `Convor`, `Nuna`) with no prefix
  at all, which is exactly how 22 of them got read as "vanilla" in the first place. Bucket by
  `MayRequire`, never by name.

## AUDIT — 2026-09-25, FOUNDRY

Audited every `RM_`-tier BiomeDef XML on disk (24 files across the 23 biome-mod-build items
closed this session: BlueDesert, Contagion, FeverWood, FloodedCanyon, ForsakenCrags,
GelatinousSlime, Greentide, LeaningScrub, LongShade, Miasma, NightsideIce, PoisonForest,
Pyrelands, RustCathedral, Scarlands/Warscar, Stillsand, TerminalBiomes×4 (GreySea/PropaneLake/
TheScald/TwilightSea), TheForge, TheRot, TheSump, Wasteland, Webwork, WeepingStones) — parsed
`wildAnimals`/`wildPlants`/`fishTypes` in both the verbose `<li>` form and the shorthand
dictionary form (including `fishTypes`' nested category wrapper, e.g.
`<freshwater_Common><DefName>N</DefName></freshwater_Common>`), bucketed every row by
`MayRequire` first, defName prefix second, and cross-checked bare names against the 205
Star-Wars-tagged names measured off the frozen `RUT_` defs.

**One real violation found and fixed:** `RM_LongShade.xml`'s `wildPlants` carried 6 RSW_-tier
rows inline (`RSW_Ultracactus`, `RSW_SurraGrass`, `RSW_Plant_Chakroot_Wild`,
`RSW_Plant_HubbaGourd_Wild`, `RSW_VellaraBloom`, `RSW_DommoTree`) — moved to
`UtinniPatches/Patches/WildAnimals_LongShade.xml` as a `PatchOperationAdd`, same shape as its
existing wildAnimals op. That file's own header claimed this was "the same still-open
WildPlants gap every other RimMandrake biome mod carries" — **false**, every other biome's
wildPlants list was already clean; corrected in the same commit (correctness-outranks-seat
rule).

**Everything else audited clean** — all 23 other files had zero Star Wars rows inline in any
of the three blocks. `wildAnimals` and `wildPlants` are fully routed everywhere they carry
content today.

**The one named "no precedent" gap (`fishTypes`) is now closed for Greentide**, the case the
item's own text used as the example. `RM_Greentide` ships no `fishTypes` at all (a Core-only
deferred block, per `WildAnimals_Greentide.xml`'s own header); added the whole nested block
via `PatchOperationAdd` onto the `BiomeDef` itself (no existing node to Replace) — the exact
shape `SandFishing_CrackedLands.xml`'s already-shipped `RM_FloodedCanyon` op used, which means
the item's "no existing `WildAnimals_*.xml` routes one" claim was already stale before this
fix, just not yet applied to Greentide. `RSW_MeeCatch`/`FaaCatch`/`LaaCatch` already have real
`RSW_` ports, so unlike Greentide's wildPlants gap (blocked on `DONOR_DEFS_PORT_TO_OURS_1`
porting 6 of 8 plants) there was no blocking dependency.

**Still open, correctly deferred, not touched:** `RM_Greentide`'s `wildPlants` — 6 of 8 Star
Wars plant rows have no `RSW_` port yet (`DONOR_DEFS_PORT_TO_OURS_1`), so the whole block stays
off `RM_Greentide` rather than shipping half a flora roster or reaching for donor defNames.
This is a real dependency, not an oversight — do not "fix" it by casting donor bare names.

**Out of this item's scope, not touched:** `RM_LongShade`'s `foragedFood`
(`MayRequire="mandrake.rsw.swbestiary"` on `RSW_RawHubbaGourd`) and `allowedPackAnimals` (5
RSW_ rows) are Star-Wars-tagged fields on a `RM_` def too, but the item's own spec section
scopes the routing rule to `wildAnimals`/`wildPlants`/`fishTypes` specifically. Flagging for a
future item rather than expanding scope here.

Both changed/created XML files validated 0 errors/0 warnings via
`skills/rimworld-modding/scripts/validate_patch.py` against the real game install
(`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld`), workshop content, and the live
`ModsConfig.xml` (628/628 mods resolved) — every xpath hit exactly once, confirming the target
nodes exist in the deployed defs.

Fix commit: `9252f5e2d`.
