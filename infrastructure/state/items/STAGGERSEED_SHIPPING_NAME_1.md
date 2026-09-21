# STAGGERSEED_SHIPPING_NAME_1 — owner card: the cycle plant's shipping name

## the ask

`design/Jawa/worldbuilding/biomes/desert.md` §4b marks this one plant's name as
**"owner's pick. Working: staggerseed."** — the only desert plant whose name is
still yours (the ultracactus's already stands). §4b and §7 use the working name
throughout, so nothing has been shipped under a real one yet.

**What it is, in one breath:** an edible-looking plant of the protected water
pockets. Eat the fruit raw and it hatches its seeds in your belly; you die, and
on the way down you stagger toward the nearest shade and die *in* it, which is
where the seeds wanted to be. Prepared properly, the seeds start to grow and
then perish before they can hurt you — and that near-miss is euphoric. It
disperses by killing, and it aims at shade.

## the decision this needs

Pick a name — or write your own, which beats every option here.

- **(a) staggerseed** — keep the working name. Plain, English, says exactly what
  it does. Reads more RimWorld than Star Wars.
- **(b) jarrik** — jarrik fruit / jarrik seed. Hard, dry, alien; sits beside
  chak-root, hubba gourd and surra grass without effort. Says nothing about the
  mechanic, which may be the point: the danger is something you learn.
- **(c) shade-walker** — names the corpse, not the plant. The Jawa word for the
  thing that gets up and walks to the shadow.
- **(d) kessek** — kessek pod. Same register as (b), softer ending, easier on
  the tongue for a delicacy ("kessek, prepared").
- **(e) vorrel** — vorrel fruit. The prettiest of the invented names; reads like
  something you would be offered at a table and should refuse.
- **(f) something else entirely** — your words, verbatim, land straight on the
  def.

Whatever comes back, the raw fruit and the prepared dish take the same stem
(fruit and seed, not two unrelated words) — the joke only works if the player
recognises the delicacy as the thing that killed their pack animal.

## why it matters

`DESERT_STAGGERSEED_BUILD_1` built both mechanisms and both ThingDefs under the
internal working name `RUT_Staggerseed` / `RUT_StaggerseedSeedDish`. That item
stays **open** until this card returns — its own `## verify` refuses to ship
under the working name. The rename is cheap (defNames, labels, texPaths, the
`RUT_Desert` wildPlants entry, three C# comments) and blocks nothing else.

## Watch out

The name lands in five places, not one: the two ThingDefs, the two HediffDefs
(`RUT_StaggerseedBrood`, `RUT_StaggerseedEuphoria`), the ThoughtDef, the
`RUT_Desert` `wildPlants` entry, and the texPaths under
`src/RimUtinni/AshkarrFlora/Textures/`. Art queued under the working name will
need its texPath moved with it — check `infrastructure/artpipe/` before
regenerating anything.

## verify

Every `RUT_Staggerseed*` defName, label and texPath carries the owner's chosen
name, and `desert.md` §4b's "(Name owner's pick. Working: **staggerseed**.)"
line is replaced with the ruled name.

## criteria

The cycle plant ships under a name the owner chose, not a working name.

## 🔴 Owner ruling 2026-09-21, and closed on it

**(e) vorrel.** Owner picked it directly from the card's options.

Renamed across every touching file: `RUT_Staggerseed`→`RUT_Vorrel`,
`RUT_StaggerseedFruit`→`RUT_VorrelFruit`, `RUT_StaggerseedSeedDish`→`RUT_VorrelSeedDish`,
`RUT_StaggerseedBrood`→`RUT_VorrelBrood`, `RUT_StaggerseedEuphoria`→`RUT_VorrelEuphoria`,
`RUT_StaggerseedEuphoriaThought`→`RUT_VorrelEuphoriaThought`, all three texPaths, the
`RUT_Desert` wildPlants entry, and every label/description/comment using the lowercase
working name — 14 files under `src/RimUtinni/AshkarrFlora/`,
`src/RimUtinni/UtinniPatches/`, `design/Jawa/`, plus `desert.md` §4b/Owed and the two
pending artpipe job notes (`rutstaggerseed_v1`, `rutstaggerseeddish_v1` — art itself is
name-free per those jobs' own notes, no rework owed). No live-save risk — MEASURED via
literal-string check against `CANONICAL_ASHKARR_START_2026-09-12.rws`: no placed
`RUT_Staggerseed` instance exists on the canonical save. `DESERT_STAGGERSEED_BUILD_1` can
now close on its own `## verify`.
