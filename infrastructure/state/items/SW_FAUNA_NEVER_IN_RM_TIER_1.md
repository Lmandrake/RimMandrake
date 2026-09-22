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
| `RUT_TheRot` | 1 / 20 |

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
