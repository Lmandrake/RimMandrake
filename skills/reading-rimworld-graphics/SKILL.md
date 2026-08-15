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
single file to find. List the folder and show one variant, marked as one of N.
Some defs are only reachable this way — 54 weapon cells in one real audit.

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

**Bundle objects have a NAME, not a path.** The def says
`Things/Equipment/Ranged/Yautja_Needlegun`; the object is `Yautja_Needlegun`.

⇒ **Match the last path segment against `m_Name`**, applying the same suffix
ladder.

🔴 **Names collide across sources.** `TorchLamp` exists in several mods, and so
do generic relative paths like `Things/Item/Equipment/Tool/Axe`. A global
name-keyed index silently hands one mod's art to another mod's def, which looks
like a correct render and is wrong.

**Prefer a texture from the def's own mod; fall back cross-source only when there
is no local match.** Record which source won, so a suspicious cell can be traced.

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
