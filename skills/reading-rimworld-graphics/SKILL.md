---
name: reading-rimworld-graphics
description: Finding and reading RimWorld texture assets from disk — loose PNGs, Unity AssetBundles, and the base game's resources.assets — so sprites can be rendered, compared or reviewed outside the game. Use whenever a def's art needs to be located, extracted or displayed offline; whenever a texture "does not exist" but the thing renders fine in game; when building contact sheets, art audits or texture diffs; when a texPath will not resolve; or before concluding that any RimWorld asset is missing.
---

# Reading RimWorld graphics from disk

Art lives in three different places, and a scanner that knows about only one
concludes that a third of the game has no textures. That conclusion is always
wrong, and it is expensive: it makes content look unreviewable and invites people
to cut things they simply could not see.

## The diagnostic that saves the most time

> **It renders in game but comes up blank offline ⇒ the art is bundled, not
> missing.** Unity loads it at runtime; your file walk cannot see it.

Reach for that before concluding anything is absent. The opposite mistake —
"we can't display it, so it can't be reviewed" — turns a tooling gap into a
content decision.

## The three homes

| where | what lives there | how to read it |
|---|---|---|
| **Loose PNGs** — `<mod>/<contentDir>/Textures/…` | most mod art | walk the filesystem |
| **AssetBundles** — `<mod>/<version>/AssetBundles/<name>` | some mods, all DLC | UnityPy |
| **`RimWorldWin64_Data/resources.assets`** | 🔴 **all base-game art** | UnityPy |

🔴 **Core ships no `Textures/` folder AND no `AssetBundles/`.** Vanilla art is in
`resources.assets` under the game install. A bundle-only extractor still leaves
every vanilla item blank, which reads as a bug in your resolver when it is
actually a missing source.

## Resolving a def's texPath

`ThingDef.graphicData.texPath` is a **path prefix, not a filename** — no
extension, no side.

```
Things/Equipment/Ranged/Yautja_Needlegun
  ->  Yautja_Needlegun.png · _south · _east · _north · _m
```

Try the bare name and each suffix. `_m` appears on mod art that ships a mask.

**Where the sprite lives differs by def type**, and guessing wrong yields nothing:

- **Weapons, apparel, buildings, items, plants** — `graphicData.texPath` is on
  the ThingDef. Straightforward.
- **Animals and pawns** — `graphicData` is **null**. The sprite hangs off the
  `PawnKindDef`: `lifeStages[LAST].bodyGraphicData.texPath`. Take the last life
  stage; adults are what a reviewer wants to see.

### graphicClass changes what texPath means

| class | meaning |
|---|---|
| `Graphic_Single` | one file |
| `Graphic_Multi` | a set of side variants |
| `Graphic_Random`, `Graphic_StackCount` | 🔴 **texPath names a DIRECTORY** |

For the directory forms the suffix ladder can never hit, because there is no
single file to find. **On the loose filesystem, list the folder** and show one
variant, marked as one of N. Some defs are only reachable this way — 54 weapon
cells in one real audit.

🔴 **Inside a bundle there is no folder to list.** The variants are flattened to
siblings with a LETTER suffix, and the bare name does not exist at all:

```
def texPath : Things/Item/Resource/Shell/Shell_Firefoam
in bundle   : Shell_Firefoam_a · Shell_Firefoam_b · Shell_Firefoam_c
```

So the bundle ladder needs `_a`.. `_h` alongside the side suffixes. Without it
every `Graphic_StackCount` family renders blank — that alone was **373 of 397
missing item cells**, and it looked exactly like "vanilla art is unreachable".

⚠️ A suffix ladder still cannot save you when the STEM differs. Vanilla's
`Shell_AntigrainWarhead` extracts as `Shell_Antigrain_a`; nothing but a fuzzy
stem match finds that, and fuzzy matching is what caused the apparel disaster.
Leave those few blank and say so.

## Which content folders a mod actually loads

A mod's `LoadFolders.xml` maps game version to folders, and **only the listed
ones load**:

```xml
<v1.6>
  <li>/</li>
  <li>Common</li>
  <li>1.6</li>
</v1.6>
```

Index textures from each listed contentDir **and** the mod root. Indexing only
`<mod>/Textures/` finds nothing for any mod that uses this, and it fails
silently — the mod just renders blank.

🪤 **The stranded-folder trap.** A mod can leave art in a folder an older version
loaded and the current one does not. One real case: 1,053 PNGs sitting in
`Common_Old`, which `<v1.5>` loads and `<v1.6>` does not, while `Common` held 52.
Those defs are textureless **in the running game too** — so this one is a genuine
finding about the mod, not a resolver bug. Check which side of that line you are
on before reporting it.

## Extracting bundles

UnityPy reads both AssetBundles and `resources.assets`:

```python
import UnityPy
env = UnityPy.load(bundle_path)
for o in env.objects:
    if o.type.name == "Texture2D":
        d = o.read()
        d.image.save(f"{d.m_Name}.png")   # m_Name is the handle you match on
```

⚠️ **Environment matters.** Pillow and UnityPy commonly live on the Windows
Python while WSL's `python3` is PEP 668-locked against `pip install`. Check both
interpreters before concluding a library is unavailable.

Cache the output and make re-runs incremental — compare bundle mtime and size
against a manifest. Extraction is minutes cold; a re-run should be seconds.
Scale to expect: ~23,000 textures across ~67 sources, a few hundred MB.

### Matching a bundle texture to a def

🔴 **`m_Name` IS NOT UNIQUE INSIDE A BUNDLE, and RimWorld texPaths routinely end
in a generic word.** These two facts together destroy data and then hide it.

Measured in one real stack: **60 textures named `Apparel`**, 27 named `Head`.
One mod alone shipped 42 called `Apparel`, because apparel texPaths carry their
identity in the DIRECTORY:

```
OuterRim/Apparel/Stormtrooper/DeathCuirass/Apparel
OuterRim/Apparel/ImperialArmy/Cuirass/Apparel
OuterRim/Apparel/ImperialUniform/ISBAgent/Apparel
```

Two consequences, and both bit:

- **Never write extracted textures as `<source>/<m_Name>.png`.** Disambiguating
  on disk (`Apparel~2.png` … `Apparel~42.png`) keeps the bytes, and that is worth
  doing, but it does **not** save you: the filename no longer says which garment
  it is, so the index is still name-keyed and 41 of the 42 are unreachable.
  Preserve the object's **container path** — `obj.container` on the ObjectReader,
  NOT on the parsed Texture2D, where it is absent — and carry it in the index as
  its own column. Where none exists, fall back to `m_Name` and disambiguate.
- **Never match on the last path segment alone.** Compare texPath against the
  container path **from the right-hand end**, requiring as many segments to agree
  as are available, so `DeathCuirass/Apparel` beats `ISBAgent/Apparel`.

⇒ **Match by trailing path segments, and prefer the def's own mod before any
other source.** The own-mod rule alone would have caught this: every wrong render
came from a different mod's file.

🔴 **Names collide across sources.** `TorchLamp` exists in several mods, and so
do generic relative paths like `Things/Item/Equipment/Tool/Axe`. A global
name-keyed index silently hands one mod's art to another mod's def, which looks
like a correct render and is wrong.

**Prefer a texture from the def's own mod; fall back cross-source only when there
is no local match.** Record which source won, so a suspicious cell can be traced.

⚠️ **`resources.assets` has no container paths — every AssetBundle does.**
Measured: 522/522 on Royalty, 697/697 on one mod bundle, **0/3,469** on the game
player's own file. So the base game is the one source you can only match by name,
and a cross-source fallback that demands an agreeing path segment will blank
every modded def that points at Core art (a modded `PoisonDeer` reusing
`Things/Pawn/Animal/Deer/DeerMale`). Let a **pathless** candidate through as the
last resort, ranked below every path match — it costs nothing, because Core ships
no texture called `Apparel` or `Head`.

🔴 **Never match a def or species name as a SUBSTRING of a filename.** A short
name thrown at a 77,000-file index matches everywhere and the results look
plausible enough to ship:

| wanted | matched | because |
|---|---|---|
| `Hutt` | `CrashedThemisShuttle.png` | s-**hutt**-le |
| `Gand` | `Big and Small Framework.png` | -**and**- |
| `Herglic` | `heads/herglic/herglic_south.png` | art *of* the species, not its icon |

Two constraints together fix it, and neither is sufficient alone: **the PATH must
be the right kind of location** (an icon tree, not a heads or gene tree), **and
the name must match the identifying SEGMENT** — strip the known prefix, compare
whole. Highest-resolution-wins is a good tiebreak *after* that and a disastrous
one before it, because the junk match is often the biggest file.

⚠️ **Then look at the sheet before you hand it over.** These three survived
filename inspection and died instantly on sight. Render a montage and read it;
you are checking art, so check it with your eyes.

🔴 **A blank-rate metric cannot detect a wrong picture.** "Blanks fell from 30%
to 2.6%" measures whether *a* texture appeared, not whether it was *the right*
one — and a wrong render looks like a success in every count you have. Forty-two
different garments all showing one white tunic scored perfectly.

**Verify IDENTITY, not coverage:** take several defs that should look different,
and assert they resolve to **different files, each under their own mod**. That
check takes seconds and is the only one that catches a collision.

## 🔴 An icon is not the thing's appearance — check which one you were asked about

**The costliest error available here, because every intermediate step looks
right.** A def's `iconPath` is a UI symbol. What the thing LOOKS like in game is
often assembled from somewhere else entirely, and the two are unrelated:

| def | `iconPath` gives you | the appearance comes from |
|---|---|---|
| `XenotypeDef` | a symbol in the xenotype panel | its **genes** — head, ears, skin, eyes, fur, each with its own textures |
| `FactionDef` | the world-map marker | pawn kinds and their apparel |
| `ThingDef` | usually the real thing | `graphicData`, which may differ per stuff or per rotation |

⇒ A xenotype with **no icon at all renders perfectly**, because none of its
appearance was ever in the icon. Reporting "no art" for such a species is not a
small overstatement; it invites someone to delete content that was never broken.

**Before auditing art, say out loud which question you are answering** — *does
this have a UI icon* or *does this render* — and check that it is the one that
was asked. They have different answers, different files and different fixes.

**The cheapest disambiguation is to spawn one and look.** A single spawned pawn
settled this after an entire file-based analysis reached the wrong conclusion
twice. If a bridge is available, that beats any amount of disk archaeology.

## Reporting

Distinguish these, because they need different responses:

| reason | means | do |
|---|---|---|
| `no_loose_png` | no file matched the texPath | try bundles, then check LoadFolders |
| `blank_png` | a file matched and is **fully transparent** | often the wrong side variant — try the next suffix |
| `no_texPath` | the def declares no art | correct; nothing to find |

A fully transparent PNG is not a missing texture, and treating it as one hides a
resolver bug that a different suffix would fix.

## If you serve these images to a reviewer

**Do not address images by row index.** Regenerating the source data reorders
rows, and any page still open then shows the right name beside the wrong
picture — reviewers make decisions on that and never notice. Key on `defName`,
which survives regeneration.

## In this repo

```
src/RimMandrake/Utils/extract_bundle_textures.py   bundles + resources.assets -> PNG cache + index
src/RimMandrake/Utils/thing_contact_sheet.py       weapons/apparel/items/buildings/plants
src/RimMandrake/Utils/animal_contact_sheet.py      animals, via the PawnKindDef hop
```

Run the sheet generators under Windows `python.exe`. They share one texture
resolver — extend that, rather than teaching each sheet its own lookup.

For what to DO with the sheets once built — how to run a review, cluster
decisions and cut safely — see the `rimworld-content-moderation` skill.
