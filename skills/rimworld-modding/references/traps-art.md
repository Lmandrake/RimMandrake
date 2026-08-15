# traps — Art, textures and what the eye sees

Textures, AssetBundles, graphic selection, sprite metrics.

**Read this one before concluding art is missing or broken.** Presence, selection and rendering are three separate claims, and a file census can only speak to the first.

What goes in, and what does not: `references/traps.md`.

---

### A mod's art can be invisible to a file audit — AssetBundles are readable, and loose files still beat them
**Symptom:** `find -name '*.png'` returned nothing for four Star Wars race mods, so a texture-quality audit recorded them as *"UNVERIFIED — art locked in AssetBundles"*, implying replacement art would have to be commissioned blind.
**Cause:** RimWorld 1.6 gave AssetBundles first-class support, and authors ship art compiled rather than loose to halve download size.
**Fix:** `pip install UnityPy` opens them — one bundle yielded 554 `Texture2D` objects with dimensions and internal paths, stored at `assets/data/<packageid>/textures/<the ordinary RimWorld path>`, so stripping the prefix recovers the path. Tooling: `src/RimMandrake/Utils/extract_bundle.py`, which needs Windows `python3.exe`, not WSL `python3` (UnityPy is installed only for the Windows interpreter).
**Recurs when:** overriding bundled art — RimWorld resolves a texture as **loose file in any active mod → base game resources → bundles**, so a loose PNG at the same path wins *regardless of load order*, and a bundle can never override a base-game texture.

---

### "The art is bad" has twice meant "the wrong art is being SELECTED"
**Symptom:** the Gamorrean read as "a grumpy human with horns"; the Wookiee rendered at 128×128 where every other species in the same mod is 512×512.
**Cause:** neither was missing art. `PigEars` already existed in Biotech and simply was not on the xenotype — and 206 of 318 loaded `HeadTypeDef`s declare no `requiredGenes`, so a pawn without a head gene rolls from a pool that is two-thirds modded alien skulls. For the Wookiee, **two complete, correctly-gated head chains exist** — Outer Rim's at 512×512 and Star Wars Xenotypes' at 128×128 — and `BTD_Wookiee` carries the gene pointing at the worse one. That mod was adopted *specifically* to dedupe the overlap, and its own `BTD_Data/XenotypeEquivalencies.xml` lists all three Wookiee xenotypes in one `EquivalentGroup`: it knew both existed and picked the lower-resolution one.
**Fix:** a def patch, not a commission — `WookieeHead_Upgrade.xml` swaps one gene. Dump which def is actually chosen and what it points at before commissioning pixels; the def layer is free to change and art is the least reversible input.
**Recurs when:** installing any "compatibility" or "dedupe" mod — it resolves the conflict by transferring the choice to its author, silently, across every def it touches. Its equivalency data is usually plain XML; audit which side it picked for the things you care about.

---

### Absence of a texture folder is not absence of art
**Symptom:** a texture audit reported the Wookiee as having "no body art at all" because no `Textures/Pawn/BodyType/wookiee` folder exists.
**Cause:** the fur *is* the body treatment. `Furskin` is a Biotech `GeneDef` whose `renderNodeProperties` attach a `PawnRenderNode_Fur` (worker `PawnRenderNodeWorker_Fur`) to the `Body` tag. The art arrives through the render tree rather than a per-race folder.
**Fix:** withdraw the finding.
**Recurs when:** any folder-shaped art search — since 1.6 graphics reach a pawn by at least three routes (a race's `graphicPaths`, a `HeadTypeDef`'s `graphicPath`, a gene's `renderNodeProperties`) and a folder search sees only the first two. State the search method in the finding so the blind spot is visible.

---

### A missing directional texture is not a defect — read `visibleFacing` first
**Symptom:** the Falleen ridged-spine ships `_east` and `_north` for all five body variants and **no `_south`**. It sat in the queue for days as "missing art", with an artist hand-off waiting on missing-vs-mis-pathed.
**Cause:** neither. `guy762_BodyAttachment_falleen` declares `<visibleFacing><li>East</li><li>North</li><li>West</li></visibleFacing>` — a spine ridge is on the back, so south is deliberately omitted, and `Graphic_Multi` mirrors West from East. The failure mode is silent by construction: `Graphic_Multi.Init` substitutes north for a null south rather than erroring, so there is no red error, no `Failed to find any textures at`, and no visual artifact.
**Fix:** read the def's own declaration of what it renders before calling art missing — `visibleFacing`, `renderNodeProperties`, `drawSize` and `bodyTypeGraphicPaths` each let a def legitimately ship fewer files than the naive N/E/S/W expectation. The author's convention is the tell: `hutt/bp_fat` (also a back attachment) ships east+north only, while the front-visible `zabrak/Body_Maul` **does** ship `_south`.
**Recurs when:** any art audit whose only outcomes are "missing" or "mis-pathed" — it lacks the option *"correct as shipped"* and will manufacture commissions, here five hand-drawn sprites the engine would never have drawn.

---

### Two art bugs that no log line and no file census can ever reveal
**Symptom:** `CereanMane_south.png` is present at 1,097 bytes, loads successfully, and is **empty** — `alpha max = 0`, 0 of 262,144 pixels non-transparent — so a Cerean wearing that hair renders bald from the front. Separately `OuterRim/Droid/MSE` is declared `Graphic_Multi` and ships `_south` + `_east` with **no `_north`**. Zero log lines, zero missing files, zero failed patches.
**Cause:** `Failed to find any textures at` fires **only when every direction is missing**. A present-but-empty texture is a successful load by every definition the engine has, and a partial directional set silently falls back to another facing.
**Fix:** a texture audit must open the pixels — check `alpha max > 0` and coverage, because existence, byte size and resolution all pass on an empty image. "The log is clean" and "the art is correct" are unrelated claims.
**Recurs when:** LoadFolders-selected bundle art — 1.6's `LoadFolders.xml` selects `Common` (bundle only) and *excludes* `Common_Old/Textures/`, so the bundle is the sole source and no loose copy shadows it. "Loose files beat bundles" is a rule about the load path, not about what is on disk.

---

### "Non-transparent pixel count" is the wrong emptiness metric, twice over
**Symptom:** two near-misses from one naive measure. A "flag anything under 0.5% non-transparent coverage" threshold would have reported **~1,855 Facial Animation files** as broken; and `ToolBelt_east` read as "100% of pixels non-transparent", looking like a baked-in opaque background.
**Cause:** FA draws brows and wrinkles on a 512×512 canvas, so a *healthy* brow is about **0.15% coverage** — an absolute threshold is meaningless across art whose subject occupies wildly different fractions of its frame. And `ToolBelt_east` is 10,943 px at alpha 255 (16.7%, in line with siblings) plus **54,161 px at alpha 1–40** — an invisible halo — with 0 px at alpha 0.
**Fix:** compare a texture to its own directional siblings, never to a constant, and count pixels above a *visibility* threshold, not above zero.
**Recurs when:** whole-stack texture sweeps — an empty PNG compresses to almost nothing, so **bytes-per-pixel** (never absolute bytes, which cannot distinguish a legitimate 64×64 icon from an empty 1024×1024) shortlisted 108,620 files to 4,970 opened. Of 355 genuinely empty textures only 13 were bugs; record which idioms were filtered so the next sweep does not re-litigate them.

---

### A tint mask marks the animal's FILL, not the animal — the keyline is tagged as vehicle
**Symptom:** reskinning Alpha Vehicles – Neolithic means erasing the draught animal painted into the vehicle texture. The mod ships a paired `<facing>m.png` tint mask where `(255,0,0)` takes the player's vehicle colour and `(0,0,0)` stays untinted, so dropping every pixel opaque in the art and black in the mask looks free. It is not: two dark dashes stayed floating under the sled through three drawing attempts.
**Cause:** the black region is the animal's **interior fill only**. The animal is drawn with a pure-black keyline roughly 4–6 px thick, and that keyline is tagged **RED**, i.e. vehicle. The mask is an inward-eroded copy of the animal, inset by the keyline width **on every edge**, not just the leading one — WarChariot south rows 288–292 are 100% red and are horse *shoulders*.
**Fix:** **dilate the black region outward by 8 px before using it as a stencil.** Raw inset measures 4–6 px, but requiring a row to be *majority* black pushes the mislabelled depth to 8 (WarChariot north and south); 8 px covers every facing measured. The leftover is worst at horns, ears, muzzles and hooves, where the keyline is all there is.
**Recurs when:** reusing any mask authored for RENDERING as a segmentation map — it inherits whatever the renderer did not care about. Two extras here: not everything black is animal (CoveredCarriage tags its **wheel rims** black in 62–364 px blobs, so filter connected components to **≥600 px**), and the "erase everything on the animal's side of the hitch" shortcut needs an isolated hitch band, which CoveredCarriage north and WarChariot north do not have.

---

### Judge the sprite the game draws, not the file or the review sheet
**Symptom:** the owner reviewed a reskinned sled team and said the creature "appears to have its nose cut off". Every offline check passed — canvas right, alpha real, bbox inside the footprint, subject ending at x=489 of 512 with 22 px of margin.
**Cause:** the sprite renders at ~104 px wide and the downsample turned a soft muzzle curve into a hard vertical wall. (Authoring rule and the fix: `skills/generating-rimworld-sprites/SKILL.md`, "Art direction that survives downscaling".)
**Fix:** put a true-in-game-size strip on every review sheet, and make the review image the **rendered** one — the same sled looked white in review and grey in play, because the def tints it and the sheet showed the raw PNG.
**Recurs when:** grading art by an ink-coverage-style metric — those measure presence, never correctness. The facing that measured *weakest* on fill was the anatomically correct one, and acting on the metric would have destroyed the reference the real fix depended on.

### Our own mods shadow each other, and identical bytes make it invisible
**Symptom:** two newly-authored art-fix mods, `GravshipAstronautFix` and `SauridFrillFix`, were deployed, enabled, correctly ordered after their donors, threw nothing — and did nothing. Their textures never rendered. Nothing on screen differed, because the art that DID render was byte-identical.
**Cause:** `Jawa_Patches` shipped the **same three texture paths**, and it loads **last** (index 581 against their 561–562) because it is the campaign patch mod. Loose file versus loose file is decided by load order alone — **last wins** — so the patch mod's older copies shadowed both new mods completely. `md5sum` on all three pairs matched exactly, so no visual, no log line, and no file audit could reveal it.
🔴 **The danger is deferred, not present.** While the bytes agree the shadowing costs nothing. **The moment anyone improves the fix mod's art, the improvement silently does not appear** — and the investigation starts at the fix mod, which is correct, deployed and enabled. The cause is a file in a different mod that nobody is looking at.
**Fix:** delete the duplicate from whichever mod is not the owner — here `Jawa_Patches`, via `deploy_custom_mods.py --apply --prune`, which lists them as `-` lines and removes them. **Verify the pair with `md5sum` before deleting**: identical bytes prove it is a duplicate rather than a deliberate override.
**Detect it:** sweep every *authored* mod's `Textures/` for repeated relative paths across mods. A path appearing in two of our own mods is either an intended override — which must then be the LATER one — or this bug.
**Recurs when:** the collision is **between two of your own artefacts** rather than with a third party's — a mod that is correct, deployed, enabled and ordered can still be inert.

### `Graphic_Multi` falls back to the BARE path — and render nodes are lazy, so a clean log proves almost nothing
**Symptom:** two separate audits concluded a texture set was broken because a facing was missing and the log was clean. Both were wrong, in opposite directions. Biotech's `Eyes_Red` ships only `RedEyes_Female_east` plus a suffix-less `RedEyes_Male`, and never errors. Biomes! Caverns has a genuine `texPath` **typo** affecting 7 defs, and a suffix-less `FacetMothPupa.png` — neither errors, and neither is actually broken.
**Cause:** two independent mechanisms, and you need both to reason about art from a log.
1. **`Graphic_Multi.Init` has a bare-path fallback.** At `IL_011f` it calls `ContentFinder.Get(req.path, reportFailure: false)` — the path *without* any `_north`/`_east` suffix — before taking the error branch at `IL_0139`. **A suffix-less file at the base path silently satisfies a directional request**, so a typo'd or suffix-less texPath resolves and the failure branch is never reached.
2. **Render nodes are built lazily, per pawn, when one is first drawn.** Vanilla's `Eyes_Gray` has **no art anywhere in the game** — only a UI icon — and is silent in a full log purely because no grey-eyed pawn was ever rendered.
**Fix:** ⛔ **Stop treating a clean log as evidence about art at all.** `Failed to find any textures at` requires *every* direction missing **AND** no bare-path file **AND** something actually having been drawn. Audit by opening the pixels and comparing a texture to its own directional siblings. And check `visibleFacing` before calling a facing missing — `PawnRenderNodeProperties_Eye::.ctor` sets `visibleFacing = {East, South, West}` **in C#**, so north eyes are never drawn and counting files against four facings is a category error. `<side>` + `<flip>` likewise means one file legitimately serves both eyes.
**Generalises to:** every "the art is broken" claim sourced from a log or a file census, and to the inverse — a genuine typo that renders correctly. It killed two candidate defects here (the Caverns typo and its suffix-less pupa), where "fixing" the typo would only have changed a rotation offset. **Absence of an error is absence of a render, not absence of a defect.**

### Spawning the pawn does not test the art — a style override is only drawn when the style is SELECTED
**Symptom:** three texture-override mods sat parked as untestable because "neither names a pawnkind defName". The premise was that a fix has a pawn you can spawn to look at. Two of the three override a `HairDef` texPath and the third an apparel `wornGraphicPath`, so a pawnkind spawn draws whatever style that pawn happened to roll — usually not the one under test — and the look reads as a pass or a fail at random.
**Cause:** the overridden path belongs to the STYLE def, not the pawn. `OuterRim_CereanMane` is gated behind a gene whose `hairTagFilter` whitelists one tag, so a fresh Cerean rolls it about 1 in 5; `VAEA_Apparel_ToolBelt` is reached by **no** pawnkind at all — grepped `apparelRequired`, `specificApparelRequirements` and every fixed list across the workshop tree, plus its lone tag, and every reference is loot (a `ThingSetMakerDef`, a TraderGen stock list, a quest reward).
**Fix:** resolve the chain to the def that CARRIES the texPath, then plan the spawn **plus the selection** — set the hair, force-equip the apparel. And name the facing: only one rotation is usually broken, so a shot from the wrong side is a false pass. The tell is on disk — `ToolBelt_west.png` 753 bytes against `ToolBelt_east.png` 16,945; `CenterFrill8_north-.png` carrying a trailing hyphen beside a correctly named `CenterFrill7_north.png`.
**Recurs when:** any `HairDef`, `BeardDef`, `TattooDef`, apparel `wornGraphicPath`, `StyleItemDef` or gene-gated cosmetic — anything whose art is chosen by pawn generation rather than fixed by the pawnkind. ⚠️ **An apparel item that no pawnkind wears is uncollectable without an equip route** — file it for the tool, never queue it for a map.
