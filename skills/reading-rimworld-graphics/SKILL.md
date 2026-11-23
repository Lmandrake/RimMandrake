---
name: reading-rimworld-graphics
description: Finding and reading RimWorld texture assets from disk — loose PNGs, Unity AssetBundles, and the base game's resources.assets — so sprites can be rendered, compared or reviewed outside the game. Use whenever a def's art needs to be located, extracted or displayed offline; whenever a texture "does not exist" but the thing renders fine in game; when building contact sheets, art audits or texture diffs; when a texPath will not resolve; or before concluding that any RimWorld asset is missing.
---

# Reading RimWorld graphics from disk

Art lives in three different places. A scanner that knows about only one place concludes that a third of the game has
no textures. That conclusion is always wrong, and the conclusion is expensive. Content then looks unreviewable. People
then cut things that they could not see.

The evidence behind these lines, and the old lines that are no longer true, are in `references/history.md`.

## The diagnostic that saves the most time

> **It renders in game but comes up blank offline ⇒ the art is bundled, not
> missing.** Unity loads it at runtime; your file walk cannot see it.

- Apply this test before you conclude that any art is absent.
- The opposite mistake is "we can't display it, so it can't be reviewed". That mistake turns a gap in our tools into a
  decision about content.

## The three homes

| where | what lives there | how to read it |
|---|---|---|
| **Loose PNGs**: `<mod>/<contentDir>/Textures/…` | most mod art | walk the filesystem |
| **AssetBundles**: `<mod>/<version>/AssetBundles/<name>` (a DLC has no version folder) | some mods, all DLC | UnityPy |
| **`RimWorldWin64_Data/resources.assets`** | 🔴 **all base-game art** | UnityPy |

- 🔴 **Core ships no `Textures/` folder AND no `AssetBundles/`.** Vanilla art is in `resources.assets` under the game
  install.
- An extractor that reads only bundles still leaves every vanilla item blank. The blank looks like a bug in your
  resolver (the code that turns a texPath into a file). The actual cause is a missing source.
- ⛔ **`resources.assets` exists only where the game is installed: the Windows machines, Archmagi and SteveDesktop.**
  The Laptop has no RimWorld install. So **any question of the form "what does vanilla do?" cannot be answered from
  there**. Do not answer such a question from a mod instead.
- **Say which you measured.** Donor art (the art of the mods that our content came from) is a legitimate corpus. Donor
  art is evidence about donor practice, not about vanilla.
- Donor art cannot tell you if vanilla shipped with variation. Do not report donor art as if it could. Such a report
  presents a house convention as conformance to the engine.
- When the install is out of reach, name the gap. Give the vanilla half of the question to a machine that has the file.

## Resolving a def's texPath

`ThingDef.graphicData.texPath` is a **path prefix, not a filename**. A texPath has no extension and no side.

```
Things/Equipment/Ranged/Yautja_Needlegun
  ->  Yautja_Needlegun.png · _south · _east · _north · _m
```

Try the bare name and each suffix. `_m` is on mod art that ships a mask. A mask is not the art, so try `_m` after the other side suffixes.

**Where the sprite lives differs by def type.** A wrong guess gives nothing:

- **Weapons, apparel, buildings, items, plants:** `graphicData.texPath` is on the ThingDef.
- **Animals and pawns:** `graphicData` is **null**. The sprite is on the `PawnKindDef`:
  `lifeStages[LAST].bodyGraphicData.texPath`. Take the last life stage, because a reviewer wants to see the adult.

### graphicClass changes what texPath means

| class | meaning |
|---|---|
| `Graphic_Single` | one file |
| `Graphic_Multi` | a set of side variants |
| `Graphic_Random`, `Graphic_StackCount` | 🔴 **texPath names a DIRECTORY** |

The suffix ladder is the ordered list of suffixes that a resolver tries. A rung is one step of that ladder. For the
directory classes there is no single file, so the suffix ladder can never hit.

- **On the loose filesystem, list the folder.** Show one variant, marked as one of N. Some defs are only reachable this
  way: 54 weapon cells (pictures on a contact sheet) in one real audit.
- ⚠️ **Writing a `Graphic_Random` texPath as a file STEM is a hard error, and `validate_patch.py` catches it.** A stem
  is the last segment of a path, without the extension. Example: the def names `Things/.../ScrapNest/ScrapNest`.
  The correct path is the folder `Things/.../ScrapNest`, which holds `ScrapNest_a/b/c.png`.
- The same checker can call a CORRECT vanilla texPath an ERROR. On a normal Steam install, two conditions must both be true:
  - Your mod ships the parent folder of that path (for example, under its own `Textures/Things/` root). The checker then
    treats the path as *that mod's* namespace. The old checker compared only the top folder, `things/`.
  - The checker finds no Core or DLC def that uses the exact path. Without a mod list, the checker cannot look for one.
- Before you trust an ERROR on a texPath that points at vanilla art, read the checker's namespace assumption. That
  assumption is `own_parent_exists` and `vanilla_uses` in `skills/rimworld-modding/scripts/validate_patch.py`.

🔴 **Inside a bundle there is no folder to list.** The variants become siblings with a LETTER suffix. The bare name
does not exist at all:

```
def texPath : Things/Item/Resource/Shell/Shell_Firefoam
in bundle   : Shell_Firefoam_a · Shell_Firefoam_b · Shell_Firefoam_c
```

- So the bundle ladder needs `_a`.. `_h` alongside the side suffixes. Without the letters, every `Graphic_StackCount`
  family renders blank. That gap alone was **373 of 397 missing item cells**. The gap looked exactly like "vanilla art
  is unreachable".
- When the def has a directory class, pass `dir_hint=True` to `resolve_texture()`. The bundle suffix ladder then tries only
  the letter forms. A bare name there can match an unrelated file of the same mod. For `Plant_HubbaGourd_Wild`, the bare name
  matched an icon of a crate. The code also counts `Graphic_Appearances` and `Graphic_Indexed` as directory classes.

**There is a SECOND variant form, and it has no underscore.** Most plants are `Graphic_Random` families. Such a family
puts a BARE capital letter straight after the stem:

```
def texPath : Plant/Dandelion
on disk     : DandelionA · DandelionB · DandelionC
also        : GrassA · GrassB · AgaveA · AgaveB · SnowyTreeCecropiaA
```

- A ladder that only knows `_a` will miss every one of them. Measured: **172 of 175 missing plant cells** were
  `Graphic_Random`. Every other category had a ~1% blank rate.
- Before you report a blank, try both forms: bare `A`..`H` and `_a`.. `_h`.
- **An outlier blank rate for ONE category is a resolver gap, not missing art.** Plants were at 30.8%. Weapons, apparel
  and items were near 1%. Missing content does not collect in one category. The effect of an unhandled graphic class
  does.
- Compare categories against each other before you compare any of them against zero.

**A THIRD form: the letter lands in the MIDDLE.** A texPath can carry a trailing qualifier, here `_Leafless`. The
variant letter then goes before the qualifier, not at the end:

```
def texPath : Things/Plant/Grass_Leafless
on disk     : GrassA_Leafless · GrassB_Leafless
```

A ladder that only appends will never see these. Also try the letter as an **infix** before the last `_` segment.

🔴 **A FOURTH form, and it is the one that hides most: the bundle DIRECTORY whose files carry a DIFFERENT STEM.** The
texPath names a container (a folder path inside the bundle). The files in that container have an unrelated name:

```
def texPath : Things/Plant/RG_Bush
in bundle   : things/plant/rg_bush/busha.png   <- stem is `busha`, not `rg_bush`
```

- **No suffix on the texPath's own stem can ever reach it.** So a bundle index with only the stem as key reports the art
  missing.
- Index the cache **by containing directory** as well as by stem.
- Match the directory the same way as a stem: from the right-hand end. A container path runs deeper than the texPath.
- Every ReGrowth retexture of a vanilla plant lives here.

Measured over 190 plants: **69 needed a rung the ladder did not have.** A third of the set would have come back
"missing". The whole promise of this resolver is that it can tell MISSING from NOT FOUND.

- The working ladder is `resolve_texture()` in `src/RimMandrake/Utils/animal_contact_sheet.py`.
- The calibration fixture is `design/Jawa/mods/plant_sprites/manifest.json`. Each resolved entry has a `variant` field
  that names the rung that found the file. The one unresolved entry, `Plant_Berry_Leafless`, has `missing` and `why`.

⚠️ A suffix ladder still cannot save you when the STEM differs and no directory holds them together:

- Vanilla's `Shell_AntigrainWarhead` extracts as `Shell_Antigrain_a`.
- `Plant_Berry_Leafless` declares `Things/Plant/BerryPlant_Leafless`. ReGrowth's art is `BerryBush_Leafless*`.
- Nothing but a fuzzy stem match finds those. Fuzzy matching caused the apparel disaster. There, a name alone
  matched, and the paths did not agree (see "Matching a bundle texture to a def").
- **Leave them blank and say WHY.** A blank with its reason is the correct answer. `Plant_Berry_Leafless` is the regression case that must
  stay unresolved.

Three more rules about what renders in game:

- **Deployed, byte-identical and in sync proves nothing about what renders: the def may not point at the art.**
  - Read the PawnKindDef's `lifeStages[].bodyGraphicData.texPath` and its `alternateGraphics`. Read them from the mod's
    own XML on disk. Then look at one in game.
  - Never score art by whether the file deployed.
  - The path misses in three ways:
    1. Life stage. `_j` is the JUVENILE texture: the calf reads `BanthaW_j`, the adult reads `BanthaW`. If you supply
       only `_j`, every adult stays unchanged.
    2. Foreign defName. A def's texPath can name another creature's file (`AA_Behemoth` uses `FO_ForsakenDragon`).
    3. `alternateGraphics`. Example: `alternateGraphicChance` is 0.8, over five separate texPaths `EopieA..EopieE`. An
       override of the base art then reaches one animal in five.
  - Alternates that are colour tints have no texPath and need nothing. Both kinds look identical in the XML until you
    read the `<li>` bodies.
  - `jawa/get_defs` returns null for `graphicData`, because the tool does not serialise nested objects.
  - Take `graphicData` from the mod source XML, or from a def dump. An old def dump carries no `drawSize`, so check that
    the record has the key.
- **`jawa/thing_graphic` cannot judge creature textures.**
  - The tool reads `UI/Misc/BadTexture` / `Pawn.Graphic=BadTexture` for EVERY undrawn pawn, vanilla Muffalo included
    (144/144 false badTex FAILs). `jawa/texture_audit` also missed the known RM_Glasmaw miss.
  - The cause: the tool reads `Thing.Graphic`. For any Pawn, that is the ThingDef's null `graphicData`. So
    `badTex=true`, regardless of art.
  - Read a vanilla control pawn first. A harness that is proven only against a fake bridge lies on the real bridge.
  - Player.log texture lines (`Failed to find any textures at`) are the instrument.
  - Judge pawn art with the appearance block of `jawa/thing_explain` instead. The block gives the life-stage paths,
    `packsHoldingPath` and the OBSERVED provider.
- **A pawn's alternate graphic cannot be forced through `Thing.overrideGraphicIndex`.**
  - `PawnGraphicUtils.TryGetAlternate` rolls `kindDef.alternateGraphicChance`, seeded by `thingIDNumber`. The method
    reads nothing else.
  - To switch an animal's look on a state, do three things. Set `alternateGraphicChance` to 0. Put the look in
    `alternateGraphics`. Postfix `TryGetAlternate` (example: `RSW_TaozinPalePatch`).
  - Vanilla then draws body, rotting and dessicated from that look.

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

- Index textures from each listed contentDir **and** the mod root. If you index only `<mod>/Textures/`, you find nothing
  for any mod that uses this. The failure is silent: the mod renders blank.
- The game loads the mod root only when the list names the root (`/`), or when no `LoadFolders.xml` entry applies. So
  check a hit that only the mod root holds against the list.
- 🪤 **The stranded-folder trap.** A mod can leave art in a folder that an older version loaded and the current version
  does not. One real case: 1,053 PNGs were in `Common_Old`, which `<v1.5>` loads and `<v1.6>` does not. `Common` held 52.
- Such defs are textureless **in the running game too**. So a stranded folder is a genuine finding about the mod, not a
  resolver bug. Before you report, check if the cause is a stranded folder or the resolver.

## Extracting bundles

UnityPy reads both AssetBundles and `resources.assets`:

```python
import UnityPy
env = UnityPy.load(bundle_path)
for o in env.objects:
    if o.type.name == "Texture2D":
        d = o.read()
        key = o.container or d.m_Name   # the container path is the handle; m_Name is the fallback
        # safe_path is yours: drop Unity's own .png/.psd; give two objects with one key two files
        d.image.save(safe_path(key) + ".png")
```

- ⚠️ **Environment matters.** Pillow and UnityPy commonly live on the Windows Python. WSL's `python3` is PEP 668-locked
  against `pip install`. Before you conclude that a library is unavailable, check both interpreters.
- Cache the output and make re-runs incremental. Compare bundle mtime and size against a manifest. A cold extraction
  takes minutes. A re-run takes seconds.
- Expect this scale: ~23,000 textures across ~67 sources, a few hundred MB.

### Matching a bundle texture to a def

🔴 **`m_Name` IS NOT UNIQUE INSIDE A BUNDLE, and RimWorld texPaths routinely end in a generic word.** `m_Name` is the
texture's own name in the bundle. These two facts together destroy data and then hide the loss.

Measured in one real stack: **60 textures named `Apparel`**, 27 named `Head`. One mod alone shipped 42 called `Apparel`.
The cause is that apparel texPaths carry their identity in the DIRECTORY:

```
OuterRim/Apparel/Stormtrooper/DeathCuirass/Apparel
OuterRim/Apparel/ImperialArmy/Cuirass/Apparel
OuterRim/Apparel/ImperialUniform/ISBAgent/Apparel
```

Two rules follow. We paid for each one:

- **Never write extracted textures as `<source>/<m_Name>.png`.**
  - Numbered names on disk (`Apparel~2.png` … `Apparel~42.png`) keep the bytes. Numbered names are worth doing, but they do
    **not** save you. The filename no longer says which garment it is. The index is still name-keyed, so 41 of the 42
    are unreachable.
  - Preserve the object's **container path**. Read `obj.container` on the ObjectReader, NOT on the parsed Texture2D,
    where it is absent. Put the container path in the index as its own column.
  - Where no container path exists, fall back to `m_Name` and make the file name unique.
- **Never match on the last path segment alone.** Compare texPath against the container path **from the right-hand
  end**. Require as many segments to agree as are available. Then `DeathCuirass/Apparel` beats `ISBAgent/Apparel`.

**Match by trailing path segments, and prefer the def's own mod before any other source.** The own-mod rule alone would
have caught this. Every wrong render came from a different mod's file.

🔴 **Names collide across sources.** `TorchLamp` exists in several mods. So do generic relative paths like
`Things/Item/Equipment/Tool/Axe`. A global name-keyed index silently gives one mod's art to another mod's def. The
result looks like a correct render and is wrong.

- **Prefer a texture from the def's own mod; fall back cross-source only when there is no local match.**
- Record which source won, so that you can trace a suspicious cell.
- `resolve_texture()` applies this rule inside the bundle suffix ladder and inside the bundle variant rung, not across
  rungs. The first rung that hits wins.
- The loose rungs come first and ignore the own mod. At one path the last loaded mod wins, as in the game.
- The bundle-directory rung ranks path agreement first, and the own mod second.

⚠️ **`resources.assets` has no container paths; every AssetBundle does.** Measured: 522/522 on Royalty, 697/697 on one
mod bundle, **0/3,469** on the game player's own file.

- So the base game is the one source that you can match only by name.
- A cross-source fallback that demands an agreeing path segment blanks every modded def that points at Core art.
  Example: a modded `PoisonDeer` reuses `Things/Pawn/Animal/Deer/DeerMale`.
- Let a **pathless** candidate through as the last resort, ranked below every path match. This costs nothing, because
  Core ships no texture called `Apparel` or `Head`.

🔴 **Never match a def or species name as a SUBSTRING of a filename.** A short name against an index of 77,000 files
matches everywhere. The results look plausible enough to ship:

| wanted | matched | because |
|---|---|---|
| `Hutt` | `CrashedThemisShuttle.png` | s-**hutt**-le |
| `Gand` | `Big and Small Framework.png` | -**and**- |
| `Herglic` | `heads/herglic/herglic_south.png` | art *of* the species, not its icon |

- Two constraints together fix the problem. Neither is sufficient alone:
  - **the PATH must be the right kind of location** (an icon tree, not a heads or gene tree);
  - **the name must match the identifying SEGMENT**. Strip the known prefix, then compare the whole segment.
- The highest resolution is a good tiebreak *after* the two constraints. Before them it is a disastrous one, because the
  junk match is often the biggest file.
- ⚠️ **Then look at the sheet before you hand it over.** These three matches survived an inspection of the filenames and
  failed instantly on sight. Render a montage and read it. You are checking art, so check it with your eyes.

🔴 **A blank-rate metric cannot detect a wrong picture.** "Blanks fell from 30% to 2.6%" measures whether *a* texture
appeared. That number does not measure whether the texture was *the right* one. A wrong render looks like a success in every count that you have.
Forty-two different garments that all showed one white tunic scored perfectly.

**Verify IDENTITY, not coverage.** Take several defs whose looks must differ. Assert that they resolve to **different
files, each under their own mod**. This check takes seconds. No other check catches a collision.

## 🔴 An icon is not the thing's appearance — check which one you were asked about

**A mix-up of icon and appearance is the costliest error available here, because every intermediate step looks right.** A def's `iconPath` is a UI
symbol. What the thing LOOKS like in game often comes from somewhere else. The two are unrelated:

| def | `iconPath` gives you | the appearance comes from |
|---|---|---|
| `XenotypeDef` | a symbol in the xenotype panel | its **genes**: head, ears, skin, eyes, fur, each with its own textures |
| `FactionDef` | the world-map marker | pawn kinds and their apparel |
| `ThingDef` | usually the real thing | `graphicData`, which may differ per stuff or per rotation |

- A xenotype with **no icon at all renders perfectly**, because none of its appearance was ever in the icon. A report of
  "no art" for such a species is not a small overstatement. The report invites someone to delete content that was never
  broken.
- **Before you audit art, say out loud which question you are answering.** The question is
  *does this have a UI icon* or *does this render*.
  Check that your question is the one that was asked. The two questions have different answers, different files and
  different fixes.
- **The cheapest way to decide is to spawn one and look.** If a bridge is available, one spawn beats any amount of work
  on files.

## 🪤 Some rows are not content and can never render

**Abstract parent defs have no `defName`.** Abstract parents carry a `Name=` attribute instead. Abstract parents exist
only for other defs to inherit from. No abstract parent declares art of its own.

- To a simple walker, an abstract parent looks exactly like a real def. The result is the most misleading blank of all.
  The cell says that a thing exists and that its art is missing. Neither half is true.
- Measured in one animal inventory: **50 of 1,239 rows had no `defName`**. Those rows were `AnimalThingBase`, `BasePawn`,
  `BaseInsect`, `BS_DefaultHumanlike`, `VAEWaste_BaseInsect` and 45 more. Two of them carried a `label` inherited from a
  donor (`race-that-the-author-forgot-to-give-a-name`, `mech`). So those two read as real creatures with names.
- **Filter rows with no `defName` out of any sheet or census before counting anything.** Such rows inflate totals and
  blank rates.
- Do not offer such a row to a reviewer as a keep/cut call. That wastes the reviewer's time, because no cut tool can
  target the row. Cherry Picker keys on `defName`, so a def without one is unreachable.

## Do not walk the mod tree to build a texture index

On a Windows mount under WSL, walking the workshop tree for `*.png` **timed out at 120 s, twice.** The tree is tens of
thousands of files across hundreds of mods. The per-file stat cost dominates.

- **Build the index once, persist it, and query the cache.** The extractor already writes `bundle_textures/index.csv`
  under `observed/inventory/`. Git ignores that folder, so a fresh clone has no cache. Give the loose PNGs the same
  treatment. Do not walk again for each question.
- A diagnosis that cannot finish is not a diagnosis.
- **Texture memory is not 4 B/px over every PNG.**
  - The game loads only `Textures/` of the load folders, one file per path.
  - Under Prefs `textureCompression`, the game DXT5-compresses any texture with both sides %4. DXT5 costs 1 B/px, with mips
    clamped by FastCompressDXT.
  - So a 4 B/px proxy over every PNG in a mod folder overstates RimWorld 1.6 VRAM ~15x. For Planet Atmosphere, the proxy
    was 1131.6 MB against ~74 MB.
  - `modaudit/diskfacts.py` `decoded_mb_est` (RGBA32 across every version folder) is NOT memory either: 41.7 GB against
    10.4 GB on a 551-mod list.
  - Use `src/RimMandrake/Utils/planet_atmosphere_cost.py` `texture_bytes()` or `modaudit/memory_attribution.py`.

## Reporting

Distinguish these reasons, because they need different responses:

| reason | means | do |
|---|---|---|
| `no_loose_png` | no loose PNG and no texture in the bundle cache matched the texPath | check that the bundle cache exists and is current (try bundles), then check LoadFolders |
| `blank_png` | a file matched and is **fully transparent** | often the wrong side variant: try the next suffix |
| `no_texPath` | the def declares no art | correct; nothing to find |
| `no_graphicData` (thing sheets) | the def has no `graphicData`, or its `graphicData` names neither `texPath` nor `graphicClass` | usually correct; if `graphicData` exists, read it |
| `no_pawnkind` (animal sheets) | no PawnKindDef names this race | find out why no PawnKindDef does |
| `no_defName` | 🪤 an abstract parent, not content | drop the row entirely |

A fully transparent PNG is not a missing texture. If you treat it as one, you hide a resolver bug that a different suffix
would fix.

## If you serve these images to a reviewer

**Do not address images by row index.** A new run of the source data reorders the rows. A page that is still open then
shows the right name beside the wrong picture. Reviewers make decisions on that page and never notice. Key on `defName`,
which survives regeneration.

## In this repo

```
src/RimMandrake/Utils/extract_bundle_textures.py   bundles + resources.assets -> PNG cache + index
src/RimMandrake/Utils/thing_contact_sheet.py       weapons/apparel/items/buildings/plants
src/RimMandrake/Utils/animal_contact_sheet.py      animals, via the PawnKindDef hop
```

- Run the sheet generators under Windows `python.exe`. The sheet generators share one texture resolver. Extend that resolver. Do not
  teach each sheet its own lookup.
- For what to DO with the sheets once built, see the `rimworld-content-moderation` skill. That skill says how to run a
  review, cluster decisions and cut safely. Read it by path: `skills/rimworld-content-moderation/SKILL.md`.
