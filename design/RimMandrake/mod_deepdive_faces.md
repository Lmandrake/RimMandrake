# Deep dive: the facial-animation mods, and what a takeover would take

Owner ruling C16, 2026-10-10 (typed; `design/RimMandrake/mod_audit/OWNER_RULINGS.md`): *"Keep all the facial
stuff for now. The only reason we would get rid of it is if we take it over. And we might. In fact I would like
you to deeply assess these facial mods and explore what would be required to reproduce them. Seriously. Do a deep
background analysis on this. Look also if the GitHub codes are available to assist this."*

**Nothing in this document removes, disables or reorders any mod.** C16 stands: every facial mod stays loaded
until a takeover replaces it. Standing rule (CLAUDE.md, "What is where"): **cosmetic changes need the owner's
permission first — they can break animated faces.** Every phase below that changes what a pawn looks like is
an owner decision point (§8).

Method (FOUNDRY, 2026-10-10, offline; no bridge, no game). Census = parse `About.xml` `<name>`+`<description>`
of all 589 mods in `facts/universe.json` (sanity probe: the sweep found `nals.facialanimation` with a 687-char
description). Code = `ilspycmd` decompiles of every shipped 1.6 DLL (scratch, outside git:
`D:\ClaudeWork\rimmandrake\scratch\faces_decomp\`), plus the source FaceAddonFramework ships in its own folder. Engine
facts = RimSage (decompiled 1.6). GitHub = public metadata via `gh api`. Labels: **MEASURED** (read in a file
or source this session), **INFERRED** (reasoned, not observed), **UNMEASURED** (needs the live game).

## 1. Census: which mods are facial

The About.xml sweep (keywords facial/blink/eyelid/eyebrow/mouth/face addon/expression; then a wider name-only
pass for eye/head) returned 17 hits; 4 are false positives (sound mods, the slave-collar mod, three of our own
creature mods whose descriptions mention a mouth). The facial family is **13 mods**, in four roles:

| role | packageId | name | list pos |
|---|---|---|---|
| **engine** | `nals.facialanimation` | [NL] Facial Animation - WIP (FA) | 32 |
| engine add-on (C#) | `sd.fa.geneticheadsframework` | Genetic Heads Framework for [NL] FA | 394 |
| engine add-on (C#) | `danzinagri.facialanimationcompatabilityproject` | Facial Animation Compatability Project (FACP) | 500 |
| art + defs | `nals.facialanimationexperimentals` | [NL] FA - Experimentals | 380 |
| art + defs | `vanillaexpanded.vtexe.facialanims` | Vanilla Textures Expanded - [NL] FA (VTE-FA) | 468 |
| art + defs | `reel.facialanims` | Reel's Facial Animation Textures | 448 |
| art + defs | `sd.fa.geneticheadsbiotech` | Genetic Biotech for FA | 440 |
| art (+1 small DLL) | `sd.fa.geneticheadsmods` | Genetic Mods for FA (ships `AuraeylFa.dll`, gated, inactive) | 441 |
| art only | `sd.fa.reelsadjustments` | Adjustments for Reel's FA Textures | 452 |
| art only | `sd.fa.vteadjustments` | Adjustments for VTE - [NL] FA | 476 |
| **separate engine** | `eoralmilk.faceaddonframework` | Face Addon Framework (FAF) | 133 |
| eye genes, FA-aware | `lazyfridaystudio.genesexpandedeyes` | [LFS] Genes Expanded - Eyes | 379 |
| eye genes | `lts.geg` | Glowing eyes genes | 144 |

Twelve other mods reference FA without being face mods (MEASURED, `facts/mod_facts.jsonl` `dependants_detail`),
and the kind of reference decides whether FA's removal hurts them:
- **load_after only** (nothing breaks): ChezhouLib, Melee Animation, Kem's Beard Adjustment, Big & Small core.
- **guarded** (silently inert without FA): Romance on the Rim (its FA defs sit in `1.6/ModCompat/FacialAnimation`,
  loaded through `LoadFolders.xml` `IfModActive`), Big & Small races (`MayRequire`), one adult-content mod (`findmod`).
- **xpath patches touching FA-owned defNames** (Complex Jobs, Survival Tools, Giddy-Up, Show Me Your Tools,
  Better Prerequisites): whether these are guarded was not checked file by file — UNVERIFIED; the removal
  dry-run (§7.4) decides.
— and **our own** `mandrake.rm.patches`, `mandrake.rsw.patches`, `mandrake.rut.patches` (loadAfter + one FA
def patch).

## 2. Per-mod analysis

### 2.1 `nals.facialanimation` — the engine (everything else hangs off it)

**On disk.** `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1635901197`.
Seven version folders 1.0–1.6, no `LoadFolders.xml` and no `Common/`, so 1.6 loads `1.6/` + `/` only
(RimSage `ModContentPack`: default rule is the current-version folder, else the newest older one, then `Common/`
if present, then root). `1.6/Assemblies/FacialAnimation.dll`
(108,544 B; 82 decompiled files, 6,730 lines). No source shipped. About.xml: *"Redistribution of this MOD data is
prohibited."* (MEASURED)

**Data model (MEASURED, decompiled + `1.6/Defs`).**
- `FaceTypeDef` (abstract-ish base) with subclasses per layer: `HeadTypeDef`, `EyeballTypeDef`, `LidTypeDef`,
  `LidOptionTypeDef`, `BrowTypeDef`, `MouthTypeDef`, `SkinTypeDef`, `EmotionTypeDef`. Fields: `texPath`,
  `shader`, `shaderColorOverride`, `minColor`/`maxColor` (random tint range), `gender`, `raceName`,
  `probability`, `altMaskPath`, `optTexPath`, `colorMode`, **`targetGeneDefs`** (the Biotech hook).
  ⚠️ FA's `FacialAnimation.HeadTypeDef` is a different type from vanilla `Verse.HeadTypeDef`.
- `*ShapeDef` per layer (`normal`, `close`, `happy`, …): the named poses a frame can select.
- `FaceAnimationDef`: a list of `AnimationFrame { duration; head/brow/lid/lidOption/eyeball/mouth/emotion
  ShapeDef; head/brow/lid/eyeball(L/R)/mouth offsets }`, plus selectors `targetJobs`, `targetThoughtDefs`,
  `targetMood{Min,Max}`, `targetPain{Min,Max}`, `raceName`, `priority`, `roopIntervalMin/Max` (loop interval,
  sic), `applyWhenStandingOnly`. 16 job animations ship (Goto, LayDown, Lovin, Ingest, Mine, Wait_Downed,
  AttackMelee, DoBill, Research, …) plus constants (`blink`, `eyeMoving`, `eyeFlicker`, thought-driven).
- `FaceAdjustmentDef` (per-race/head offsets), `EyeballColorDef` (Biotech eye colours), a `MainButtonDef`
  face-editor tab (`NL_SelectPartWindow`, 1,134 lines — the biggest file).

**Texture layout (MEASURED).** `Textures/Things/Pawn/Humanlike/{Heads_Blank,Eyes,Lids,Brows,Mouth,Skins}/<Style>/<Gender>/<shape>_<facing>.png`
with `…m.png` masks (CutoutComplex two-colour tint) and `_highlight_` variants for eye shine. Facings are
`south`/`east` only (north is never drawn for face parts: `NLFacialAnimationPartNodeWorker` returns no graphic
when facing north; west mirrors east). Canvas **512×512** for 1,188 of 1,237 PNGs. 1.6 folder: **183 PNGs**.

**Render mechanism (MEASURED, `HarmonyPatches.cs`, `DrawFaceGraphicsComp.cs`).** 1.6-native PawnRenderTree,
plus 13 Harmony patches. A `Race_Patches.xml` adds **eight ThingComps to `ThingDef[defName="Human"]`** (draw,
head, eyeball, lid, brow, mouth, skin, animation controller). (`EmotionControllerComp` is commented out in that patch.) `DrawFaceGraphicsComp.CompRenderNodes()` returns
**one master node + 18 part nodes** (15 on a dead pawn) parented to `PawnRenderNodeTagDefOf.Head` at baseLayer
50–59 (brows at 100 when "brows above hat"), and **no nodes at all** for a pawn whose `EnableDrawing` is false
(excluded race-xenotype or gender). FACP can add the same eight comps to one more race,
`BS_InsectoidHumanoid_FourArmed`, behind a toggle (`StartupPatcher.AddFacialAnimationComps`). Then:
- `PawnRenderTree.ParallelPreDraw` postfix **removes the vanilla `PawnRenderNode_Head` draw request** — FA
  draws the whole head itself from a blank head + layers. This is why any vanilla/gene/HAR head art on an
  FA-drawn pawn is invisible (our docs record this: `design/Jawa/art/graphics_overhaul_protocol.md:104`).
- `PawnRenderNode.AddChildren` postfix reorders head children so FA nodes come first.
- `PawnRenderTree.AddChild` prefix **vetoes Biotech gene render nodes** (headbone, ears, eyes, nose) per
  settings — eyes are vetoed by default (`DrawEyesParts=false`; the owner's config sets it `True`).
- `PawnRenderer.ParallelGetPreRenderResults` prefix sets `disableCache=true` for **every pawn carrying
  `FacialAnimationControllerComp`** — i.e. every `Human`, including xenotypes FA is told not to draw (the check
  is `GetComp != null`, not `ShouldDrawPawn`). Engine side (RimSage, `PawnRenderer.ParallelGetPreRenderResults`):
  `useCached` is the zoomed-out (`ZoomRootSize > 18`) cached-atlas path; FA forces every human off it, so the
  full render tree runs `ParallelPreDraw` every frame at every zoom. For an excluded pawn that tree carries no
  FA nodes, but it still loses the cache.
- Others: `BaseHeadOffsetAt` (head bob), beard/hair mesh-set overrides, `ShaderUtility.GetSkinShader`
  (optional dark-skin shader), `Pawn_GeneTracker.Notify_GenesChanged` (re-roll face on gene change),
  `CompStatue` snapshot hooks (statues keep faces), `PlaySettings` (tab button).
- `Graphic_RenderTexture` + `MyRenderTexturePool`: composited tinted layers are baked into **RenderTextures**
  (pooled in a static dictionary keyed by path and facing; `MyRenderTexturePool` has no remove/release, so they
  are never freed — MEASURED).
- `NLPngWatcher`: a `FileSystemWatcher` for hot-reloading PNGs, shipped in release but only switched on from
  the editor window (`NL_SelectPartWindow`); off otherwise.

**Animation driver / state machine (MEASURED).** Not a tick: it runs at **draw time**, in the master node
worker's `PreDraw` → `UpdateStatus(TicksGame)` + `UpdateAnimation()` (so off-screen pawns cost nothing).
`UpdateStatus` re-reads the job every tick it is drawn and mood/pain/thoughts every 60 ticks.
`CreateAnimationDict` builds, **per pawn** (on its first draw), a dictionary keyed by **every JobDef in the game**
(a 589-mod list has hundreds), and because its source is a deferred `Select(new FaceAnimation…)`, every key gets
its **own fresh copies** of every constant (`ConstantJob`) animation — JobDefs × constants objects per pawn. The
active list is filtered by mood/pain/thought ranges and sorted by priority; that filter is a **deferred LINQ
query** stored as `IEnumerable`, so it is re-evaluated each time the accumulator enumerates it (twice per draw); `AnimationFrameAccumulator` overlays looping constants (blink 30–500 ticks, gaze flicks)
on the job animation; `AnimationFrameMapper` pushes shapes/offsets into the controller comps; offsets lerp
(0.4). `CompTick` only dirties the portrait cache every N ticks if portrait animation is on (default off).

**Settings (MEASURED).** Per gender on/off, per **race-xenotype exclusion list**
(`IgnoreEnableAnimationForRaceXenoTypeList`, key `"<raceDefName>-<xenotypeDefName>"`), gene-part toggles,
beard/hair mesh overrides, odd-eye chance, dark-skin shader, portrait animation. The list lives in the
player's `Config\Mod_1635901197_FacialAnimationMod.xml`, **not in any def** — it ships to nobody. In code it is
a public `List<string>` on the public static `FacialAnimationMod.Settings`, read live by
`ShouldDrawRaceXenoType` (MEASURED) — so another mod can add keys in memory at startup.

**Save data (MEASURED).** Each controller comp scribes `<CompName>_faceType` (a def name) and `<CompName>_color`
on the pawn — e.g. our founder files carry `HeadControllerComp_faceType`. Removing FA leaves those as unread
nodes, which Scribe ignores: loading is pull-by-label (`Scribe_Defs.Look` → `curXmlParent[label]`, RimSage), so a
node no comp asks for is never parsed. Still to be confirmed end to end in a removal dry-run (§7).

### 2.2 `nals.facialanimationexperimentals`
Art + defs only, depends on FA. 93 defs (49 `FaceAnimationDef` — the expression library — plus lid, eye,
mouth, skin, brow, emotion types). 358 PNGs, all 512×512, under `Textures/Things/Pawn/FA-Experimentals`. Same
author, same redistribution ban. 12 dependants including `mandrake.rm.flowworks` and `mandrake.rut.pawnflavor`
(MEASURED, facts row) — check why before any removal.

### 2.3 `vanillaexpanded.vtexe.facialanims` (VTE-FA)
Art + defs: 65 defs (24 mouth, 18 skin, 12 lid, 11 brow types), 7 patch ops into FA/Experimentals. 972 loaded
PNGs at root (plus gated `Mods/{Asari,Drell,Aura,…}` folders, none active). Author "Oracle of Thessia". The
base VTE repo is CC BY-NC-ND 4.0 (§3); the FA add-on has no repo.

### 2.4 `reel.facialanims` + `sd.fa.reelsadjustments`, `sd.fa.vteadjustments`
Reel: 23 defs (mouth/eye/lid types), 420 PNGs. The two `sd.fa.*adjustments` packs are **texture overrides
only** (0 defs; 89 and 46 PNGs) that replace same-path PNGs from Reel/VTE — pure art, zero code.

### 2.5 `sd.fa.geneticheadsframework` (+ `…biotech`, `…mods`)
Framework DLL (`FacialAnimationGeneticHeads.dll`, 12 files, 685 lines; MIT, public repo §3): Harmony patches
on each FA controller comp's face-type pick so a `FaceTypeDef` whose `targetGeneDefs` are all present on the
pawn wins (most-genes-matched first, deterministic per `thingIDNumber`), and re-picks on `Notify_GenesChanged`.
`…biotech`: 7 defs + 116 PNGs (fur-covered heads, etc.). `…mods`: 808 PNGs, 0 defs at root; its defs sit in
`IfModActive` folders. **It carries FA heads for `guy762.StarWarsXenotypes` (Wookiee, Trandoshan, "Fivehead"…)
which is not in our list, so those defs never load — but the PNGs sit in the root `Textures/` and load anyway**
(MEASURED: `LoadFolders.xml` root `/` + the texture path `Textures/StarWarsXenotypes/Heads/…`). The SW block is
**300 of the mod's 808 PNGs, ~320 MB RGBA upper bound (~80 MB DXT)**. The same pattern holds for its heads for
other absent mods (VRE Android, VRE Insector, Roo's Faun, Erin's races — not in our universe), while the VRE
Saurid/Phytokin/Genie blocks serve active mods. Whole mod: ~1.1 GB RGBA upper bound (§2.9).

### 2.6 `danzinagri.facialanimationcompatabilityproject` (FACP)
DLL `FACP.dll` (10 files, 2,009 lines) + 211 loaded PNGs from per-race `IfModActive` folders (Big & Small,
Alpha Genes, Det's xenotypes, VRE Phytokin/Saurid). `StartupPatcher` **mutates other mods' GeneDefs and
XenotypeDefs at startup**: `ClearForcedHeads`, `ClearRenderNodes`, `RemoveRenderNodeByTexPath`,
`ClearModExtensions`, `RemoveGeneFromXenotype`, texture-path redirects, `NeutralizeFaceTypes`, face-adjustment
detaches — each a mod-settings toggle (`ToggleRegistry`). It is the second mod (with LFS) that strips gene
render nodes; our `HuttEyes_RestoreRenderNodes.xml` exists because of that family of behaviour. It also
created `BS_InsectoidHumanoid_FourArmed_FaceAdjustment`, which crashed Head Set For FA's cctor and is patched
by our `src/RimMandrake/MandrakePatches/Patches/HeadSetForFA_Revive.xml`. Repo public, active (pushed
2026-10-10), **no licence** (§3).

### 2.7 `eoralmilk.faceaddonframework` (FAF) — a separate, lightweight engine
Independent of FA. DLL `FaceAddon.dll` (25 files, 1,669 lines) and **ships its own source** in the workshop
folder (`1.6/Source/FaceAddonFramework`). Model: a `FaceAddonDef` is a render node whose texture path is chosen
by pawn state — `aboutToBreak/onEdge/stressed/neutral/content/happy` (mood tiers), `sleeping`, `painShock`,
`dead`, `blink`, `wink`, `drafted`, `damaged` (timed, `damageAnimDuration`), `attacking`, `ingest`,
`mentalStatePaths`, `customs`. `WinkAndBlinkHandler` drives blink/wink; Harmony postfixes on `AddHediff`,
`RemoveHediff`, `TakeDamage` flip states event-driven. **Zero consumers in our list** (MEASURED: no mod defines
`FaceAddon.FaceAddonDef`; `dependants` empty). Apache-2.0 (§3). This is the closest legal template for our own
system.

### 2.8 Eye-gene mods
- `lazyfridaystudio.genesexpandedeyes`: 228 eye GeneDefs + 225 `FacialAnimation.EyeballColorDef`; when FA is
  present its Harmony patch **strips `renderNodeProperties` from eye genes** (our Hutt restore patch counters
  it — `src/RimStarWars/StarWarsPatches/Patches/HuttEyes_RestoreRenderNodes.xml`). 12 dependants including
  `mandrake.rsw.starwarsraces` and `mandrake.rut.pawnflavor`. Not a face mod to replace; it is a consumer.
- `lts.geg` (Glowing eyes genes): 7 genes, a glow mote, ships source in its folder (`1.4/Assemblies/GEG_GlowingEyes`);
  supportedVersions lists 1.6, and its `loadFolders.xml` maps v1.6 to `/` + `1.5` (there is no 1.6 folder).
  Unrelated to FA mechanically; the Jawa glow is our own (§5).

### 2.9 Cost (memory, TPS, Harmony hot paths)

**Textures loaded by the 589 list** (MEASURED count; size is an estimate: w×h×4×1.33 i.e. RGBA32+mips, the
same formula as `facts/` — an **upper bound**. RimSage `ModContentLoader<Texture2D>`: every acceptable file under
each loaded folder's `Textures/` is loaded eagerly at startup, whether or not any def names it, into a per-mod
holder — so an override pack's PNG **adds** memory, it does not replace the original's. A texture whose width and
height are multiples of 4 is compressed to DXT5 (`RGBA_DXT5_UNorm`, 1 byte/px vs 4) when `Prefs.TextureCompression`
(default **true**), with mips stopping near 16 px, so real memory is roughly **¼** of these figures; textures not
divisible by 4, and ≤16 px ones, stay uncompressed):

| mod | loaded PNGs | RGBA est MB | facts/ figure | note |
|---|---|---|---|---|
| nals.facialanimation | 183 | 239 | 1,597 | facts/ counted all 7 version folders (~6.7× over) |
| nals.facialanimationexperimentals | 358 | 499 | 476 | |
| vanillaexpanded.vtexe.facialanims | 972 | 1,395 | 1,770 | facts/ counted inactive gated folders |
| reel.facialanims | 420 | 586 | 559 | |
| sd.fa.reelsadjustments | 89 | 124 | 237 | overrides — wins the path lookup, but both copies stay loaded |
| sd.fa.vteadjustments | 46 | 64 | 61 | overrides (same) |
| sd.fa.geneticheadsbiotech | 116 | 128 | 122 | |
| sd.fa.geneticheadsmods | 808 | 1,098 | 1,047 | SW block 300 PNGs dead; other absent-mod blocks too (§2.5) |
| danzinagri FACP | 211 | 240 | 632 | facts/ counted inactive gated folders |
| lazyfridaystudio eyes | 456 | 114 | 325 | |
| **family total** | **~3,660** | **~4,500 (≈1.1 GB DXT)** | | |

Script: `/home/mandrake/.seat-tmp/faces/loaded_tex.py` (scratch; honours `LoadFolders.xml` `IfModActive`
against the universe, and the root+`1.6` default). The `facts/` over-count is an instrument defect, ticketed.

**CPU (INFERRED from code, UNMEASURED live):** per drawn human per frame — master + 18 part nodes, render-cache
disabled for **all** humans (incl. excluded xenotypes), job read each frame, a deferred LINQ filter
(mood/pain/thought-intersect) re-evaluated on every draw, offset lerps. Per pawn memory: one
`Dictionary<JobDef name, List<FaceAnimation>>` over every JobDef, each list holding its own copies of the
constant animations. Startup: three `[StaticConstructorOnStartup]`-class passes (FA, FACP, GH). The measured session's TPS
profile is stage-level, not per mod (`facts/session_context.json`), so no per-mod TPS number exists yet (§7).

## 3. Source availability and licences

Public GitHub metadata, 2026-10-10 (probe: `pardeike/Harmony` → 200, MIT):

| mod | public repo | licence | last commit | 1.6 code in repo | can we reuse? |
|---|---|---|---|---|---|
| nals.facialanimation (+experimentals) | **none** (user `Nals` has 0 public repos) | none; About.xml bans redistribution | — | — | **No.** Decompiled code is reference only; no copying of code or art |
| reel.facialanims | none found (UNVERIFIED beyond one search) | none | — | — | No |
| vanillaexpanded.vtexe.facialanims | none for the add-on; base VTE `Vanilla-Expanded/VanillaTexturesExpanded` | CC BY-NC-ND 4.0 (no derivatives) | 2025-07-20 | base only | No |
| danzinagri FACP | `DanZinagri/FacialAnimationCompatabilityProject` | **none** (all rights reserved) | 2026-10-10 | yes (`1.6/`, `Source/`) | Read only; ask author for a licence if wanted |
| sd.fa.geneticheadsframework | `sunshineydays/sd.fa.geneticheadsframework` | **MIT** | 2026-07-09 | yes (`1.6/Source/*.csproj`) | **Yes** (code), with notice |
| sd.fa.{biotech,mods,reels/vte adjustments} | none | none | — | — | No (art) |
| eoralmilk.faceaddonframework | `EoralMilk/FaceAddonFramework` (stops at 1.5, 2024-05-31); 1.6 port `AmCh-Q/FaceAddonFramework` (separate repo, 2025-09-02); 1.6 source also **in the workshop folder** | **Apache-2.0** | 2024-05-31 / 2025-09-02 | upstream no; AmCh-Q yes | **Yes** (code), with NOTICE + licence |
| lts.geg | none (source ships in mod folder) | none stated | — | — | Read only |
| lazyfridaystudio eyes | none under the author (UNVERIFIED) | none | — | — | No |

Repo-vs-shipped check: FAF upstream predates the shipped 1.6 DLL (the workshop folder's own `Source/` is the
best match); GH repo has 1.6 csproj consistent with the shipped `1.6/Assemblies` DLL (not byte-compared —
UNVERIFIED); FACP repo was pushed the day of this audit, so it may be ahead of the installed copy.

**Bottom line:** the engine that matters (FA) is closed and redistribution-banned, and all art in the family is
unlicensed or NC-ND. Legitimately reusable: **FAF (Apache-2.0)** and **GH (MIT)** code only. Every pixel of a
replacement must be ours.

## 4. Comparison table

| mod | does | code | loaded art | source / licence | overlaps | C16 status → takeover fate |
|---|---|---|---|---|---|---|
| FA | layered head, blink/gaze, job+mood expressions, editor tab, gene-part vetoes | 6.7k lines, 13 Harmony patches, 8 comps on Human | 183 PNG | closed, no-redistribute | everything below | keep → **replaced by our engine** |
| FA Experimentals | expression library (49 anims) | none | 358 | closed | FA | keep → replaced by our expression defs |
| VTE-FA | more mouths/skins/lids/brows | none | 972 | NC-ND / none | Reel | keep → dropped with FA |
| Reel + sd adjustments | alt mouths/eyes/lids; pure overrides | none | 420+89+46 | none | VTE-FA | keep → dropped with FA |
| GH framework | gene → face-type matching | 685 lines | 0 | **MIT** | FACP | keep → **logic reused** |
| GH biotech / mods | gene-specific FA heads; SW heads dead | 143-line gated DLL | 116 + 808 | none | FACP | keep → dropped; dead SW textures are pure cost today |
| FACP | per-race fixes, startup def surgery on others' genes | 2k lines | 211 | none (public) | GH, LFS | keep → dropped; its gene surgery stops |
| FAF | lightweight state-swap face addons | 1.7k lines, source shipped | 0 | **Apache-2.0** | none (0 consumers) | keep → **template for our engine** |
| LFS eyes | eye genes; strips eye nodes under FA | 186 lines | 456 | none | FA | keep (consumer; its FA branch goes inert) |
| lts.geg | glowing-eye genes | small, source shipped | 13 | none | none | keep (not a face engine) |

## 5. What we actually use

From a census of `src/`, `design/`, live items and the owner's FA config (MEASURED unless marked):

1. **Jawa (`RSW_MandrakeJawa`, gene-based, not HAR):** *no visible face* — hood, `RSW_Jawa_Head_Plain`, and
   **two steady, unblinking glowing eyes** (`Textures/RimMandrakeSW/Jawa/jawaeyes_glow.png`, drawSize 0.16,
   `MoteGlow`, frozen 2026-08-11). `src/RimStarWars/StarWarsRaces/README.md:35`: the glow works *"only because
   Jawa are excluded from Facial Animation"*. **Jawa need nothing from FA except to be left alone.**
2. **All six founders are Jawa-xenotype `Human` pawns** (`design/Jawa/worldbuilding/founders/founder_*.xml`),
   so FA should animate none of them. Their files still carry FA save fields (`HeadControllerComp_faceType`).
3. **68 other Star Wars xenotypes** (70 `XenotypeDef`s in `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/`, all
   `RSW_`-prefixed, two of them Jawa) (138+ `HeadTypeDef`s with `requiredGenes`): their own head art must show,
   so they too must be FA-excluded (`skills/rimworld-xenotypes/SKILL.md` §3b).
4. **Droids** (Droidworks, HAR `DW_Race_Base`): no face. FA's comps are patched onto `ThingDef Human` only (plus
   FACP's toggle-gated add to Big & Small's `BS_InsectoidHumanoid_FourArmed`), so FA never touches a HAR droid
   (MEASURED, `Race_Patches.xml`, FACP `StartupPatcher.cs`); the open human-face-on-droid defect
   (`DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1`) is a HAR `headTypes` issue, not FA.
5. **Mortis:** no pawn race exists (only a faction rename) — nothing needed.
6. **Who FA actually serves:** baseline-human and non-SW-xenotype NPCs from other mods (raiders, traders,
   VRE/Big & Small xenotypes). That is the population that would lose blink/expressions in a takeover.
7. **Gene eye nodes must survive** (Hutt slit eyes) — today we fight FA/LFS/FACP to keep them.

### 5.1 Probable live defect found by this pass

FA's exclusion list in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_1635901197_FacialAnimationMod.xml`
(last written **2026-08-15**, 156 keys) holds `Human-MandrakeJawa`, `Human-RimMandrakeJawa`,
`Human-RimMandrakeTusken`, `Human-RimMandrakeWookiee`, … but the live xenotype defNames have been
`RSW_MandrakeJawa`, `RSW_RimMandrake*` since the tier rename (2026-08-30/31); all 70 of our XenotypeDefs are
`RSW_` and the config holds **zero** `RSW_` keys (MEASURED). Key = `"<pawn.kindDef.race>-<xenotypeDefName>"`
(MEASURED, `FacialAnimationModSettings.CreateRaceXenoTypeKey` / `ShouldDrawRaceXenoType`). The one fallback in
that check — it swaps in the defName of any XenotypeDef whose translated label equals `pawn.genes.xenotypeName`
— cannot rescue this: `Pawn_GeneTracker.SetXenotype` sets `xenotypeName = null` for a def xenotype (RimSage), so
it only fires for custom/hybrid xenotypes, and even then it yields a current (`RSW_`) defName. A race-wide
`Human-null` key would exclude every human and is not present. So **no RSW_ xenotype is excluded any more**:
FA should be drawing a human face (and hiding the vanilla head, and the gene eye nodes under default settings)
on every Jawa and SW species. Live render UNMEASURED. Two deeper problems regardless of the fix:
(a) the exclusion is **per-machine config**, so a player receiving our savegame gets FA faces on every Jawa;
(b) it is keyed on defNames, so every rename silently unprotects (already in the skill).
⇒ Even before any takeover, we need a **shipped, def-level** opt-out (§6, phase 0).

## 6. Takeover analysis

### 6.1 What "reproduce" means here
We do not need FA's feature list; we need (i) **never draw a face on our species** (shipped, def-driven, rename
proof), (ii) **a believable living face for the humans and non-SW xenotypes that do have faces** — blink,
gaze, a handful of mood/pain/sleep/dead expressions, (iii) **gene head/eye render nodes left intact**, and
(iv) a face-art pipeline in our lawset. FA's editor tab, per-job animation library (16 jobs), statues, dark-skin
shader and portrait animation are optional.

### 6.2 What we can reuse legitimately
- **FAF (Apache-2.0)**: the state→texture-path model, blink/wink handler, damage/hediff event hooks, its 1.6
  render node. Reuse with the licence + NOTICE kept and our changes marked.
- **GH (MIT)**: the gene-match picker (most genes matched, deterministic per pawn).
- **The engine itself**: vanilla 1.6 `PawnRenderNode`/`PawnRenderNodeWorker`/`PawnRenderNodeProperties` +
  gene `renderNodeProperties` — no Harmony needed to *add* face layers (Biotech eyes already are nodes).
- **Nothing from FA, Experimentals, VTE-FA, Reel, sd art packs, FACP**: closed, banned or unlicensed.
  Decompiled FA is design reference only (allowed to learn from; not to copy).

### 6.3 What must be written from scratch
1. **`RM_FaceSystem` mod** (name per tier grammar: `mandrake.rm.faces`): a `ThingComp`/`HediffComp`-free design —
   a `PawnRenderNode_Face` subtree under the Head tag, layers eye-white/iris/lid/brow/mouth, each a
   `PawnRenderNodeWorker` choosing a texture by state; **does not remove the vanilla head** (draws on top of a
   head-type that is designed for it), so gene/HAR heads keep working.
2. **State machine**: blink (random 2–8 s, 3-tick close), gaze offset, expression from mood tier, pain shock,
   sleeping, downed, dead, drafted, eating; event-driven via job/mental-state changes, not a per-frame LINQ.
   Must leave `useCached` alone at zoom-out (no `disableCache`), animating only when zoomed in.
3. **Def-level opt-in/out**: a `DefModExtension` on `XenotypeDef`/`HeadTypeDef`/`ThingDef` (`RM_FaceProfile`:
   `none` | profile def). Our species ship `none`; rename-proof by construction.
4. **Save migration**: read and drop FA's `*_faceType`/`*_color` nodes; optionally map FA face types to ours.
5. **Art pipeline**: face-part sheets at our head resolution (FA uses 512² for a 128-ish head; we would use
   per-part atlases or 256²), south+east facings, masks for tint, generated through the art ledger and judged
   against canon entries. The owner reviews in game (saves, not browser sheets).
6. **Compatibility check** for the third-party mods that reference FA (§1). An unguarded def whose element names
   a missing type logs `Type … is not a Def type or could not be found` (RimSage, `DirectXmlLoader`), and an
   unguarded xpath patch on a vanished def fails with an error. But of the twelve, four are load-order only and
   three are guarded (`IfModActive` load folder, `MayRequire`, `findmod`); only the five xpath-patch mods are
   open (UNVERIFIED). A **stub assembly declaring FA's def types with no behaviour** is a fallback only if the
   dry-run shows errors (licence: re-declaring type names is not copying code — INFERRED, owner/legal judgement).

### 6.4 Effort and phases

| phase | what | size | cosmetic? |
|---|---|---|---|
| **0 — protect** | Ship a def-level FA exclusion for our xenotypes via a tiny C# shim (soft dependency, reflection/Harmony, no-op when FA is absent). Two feasible routes, both MEASURED-possible against the decompile: (a) at startup add `"Human-<defName>"` for every XenotypeDef carrying our `DefModExtension` to the public `FacialAnimationMod.Settings.IgnoreEnableAnimationForRaceXenoTypeList` (in memory; it reaches the player's config file only if they save FA's settings); (b) a Harmony postfix on `FacialAnimationModSettings.ShouldDrawRaceXenoType` returning false for those xenotypes — no config writes at all. Either is rename-proof because keys are computed from live defs. Neither removes FA's `disableCache` on excluded pawns (that prefix keys on comp presence) — a third small patch would. No FA removal. | S | yes — Jawa/SW faces change back; owner sign-off |
| **0b — measure** | §7 measurements: FA on/off TPS + memory on the cheap list; render-cache effect | S | no |
| **1 — vendor? no** | Vendoring a pinned FA fork is **not legal** (redistribution ban). Instead: freeze the installed version in the modlist snapshot and record its hash | S | no |
| **2 — build our engine** | `mandrake.rm.faces` from FAF (Apache) + GH (MIT) ideas: nodes, state machine, def extension, settings screen (C16 + "superb Mod Settings" rule) | M–L | no (inert until art) |
| **3 — art** | human face-part set in our lawset; any xenotype faces we want | L (art volume, owner review) | **yes** |
| **4 — cut over** | disable FA family in a test tier, run migration, compare screenshots; then owner decides removal | M | **yes** |
| **5 — remove** | drop the 10 FA-family mods; keep LFS/lts.geg; stub FA def types if third-party mods still need them | S–M | yes |

**Overall: L** — roughly 2–3 weeks of C# + testing for phases 0–2 and 4 (INFERRED; a guess, not costed from a
task breakdown), plus an art campaign (phase 3) whose
size is the owner's call (one human face set vs. per-xenotype sets). Phase 0 alone is **S** and is worth doing
whether or not the takeover happens.

### 6.5 Risks
- **1.6 render API**: we would be on vanilla node APIs (lower risk than FA's 13 patches); a Harmony-free
  design is the goal. RimSage-check every node hook before writing.
- **Save compatibility**: existing pawns carry FA comp nodes; dropping them should be silent but must be
  proven in a removal dry-run on a copy of the keeper save.
- **Third-party FA references** (12 mods, 5 not yet shown to be guarded): see §6.3(6).
- **Harmony conflicts while both run**: two face systems on one pawn → double faces. Our engine must refuse
  to draw on any pawn FA is drawing (check `DrawFaceGraphicsComp.EnableDrawing` via reflection) until cutover.
- **Visual regression for NPC humans**: players lose FA's expression variety; quality bar is the owner's.
- **Cosmetic breakage**: any head/eye change can break animated faces (standing rule) — every phase marked
  "yes" above needs his permission first.

## 7. Measurement plan (per face mod, memory and TPS)

All offline-prepared, run on the cheap mechanism list (`rimworld-load-round`), never a full cold load per mod:
1. **Memory**: tiers A = cheap list, B = A + FA, C = B + Experimentals + VTE-FA + Reel + sd adjustments,
   D = C + GH + FACP + geneticheadsmods. Read process private bytes and Unity texture memory at main menu and
   after a quicktest map; deltas attribute memory to each layer. Check `Prefs.TextureCompression` is on.
2. **TPS / frame time**: one map, 30 spawned humans (spawn many — one pawn's result is RNG), camera zoomed
   in and zoomed out, FA on vs. off; record frame time at each zoom (the `disableCache` effect shows zoomed
   out), and TPS at 3× speed.
3. **Exclusion check**: spawn one of each SW xenotype; screenshot with FA settings as shipped vs. fixed; read
   `DrawFaceGraphicsComp.EnableDrawing` per pawn via a bridge state read (deterministic, no visual hunt).
4. **Removal dry-run**: copy the keeper save, load with FA family off, read the log for unresolved FA
   cross-references, def-type errors and failed patch operations from the twelve third-party mods.

## 8. Owner decisions

1. **Phase 0 now?** Re-key / ship the FA exclusion so Jawa and SW species stop getting FA faces. Cosmetic: it
   changes how those pawns look today (back to intended).
2. **Takeover scope**: (a) protect-only (phase 0, keep FA forever); (b) own engine for humans, FA removed;
   (c) own engine with per-xenotype faces for SW species too (biggest art bill).
3. **Expression bar**: blink + gaze + 5–6 states (FAF-level), or FA-level job-specific animation?
4. **Dead SW heads in `sd.fa.geneticheadsmods`**: ~808 PNGs load with no defs; C16 says keep — confirm.
5. **Art resolution and style** for face parts in the lawset (cosmetic permission point).

## 9. Tickets (names only, not filed)

| name | what | size |
|---|---|---|
| `FA_EXCLUSION_REKEY_RSW_1` | Ship FA exclusions for every xenotype of ours (today all 70 are `RSW_`); startup shim keyed on a DefModExtension, not per-machine config | S |
| `FA_EXCLUSION_LIVE_CHECK_1` | Bridge state read: which SW pawns FA is drawing today | S |
| `FACE_MOD_COST_MEASURE_1` | §7 memory/TPS tiers A–D, zoomed in/out | S–M |
| `MODAUDIT_LOADFOLDERS_TEXTURE_COUNT_1` | `diskfacts.py` counts textures in every version folder and inactive `IfModActive` folders (FA 1,597 MB vs ~239 MB) | S |
| `FACE_ENGINE_OWN_1` | Build `mandrake.rm.faces` from FAF (Apache-2.0) + GH (MIT) designs | M–L |
| `FACE_ART_HUMAN_SET_1` | Human face-part art set in our lawset (owner permission first) | L |
| `FA_SAVE_MIGRATION_DRYRUN_1` | Keeper-save load with FA family off; log triage | S |
| `FA_THIRDPARTY_DEFTYPE_STUB_1` | Check the 5 unguarded-looking xpath-patch mods; stub FA def types only if the dry-run errors | S |

## 10. Review disposition

Fresh-context adversarial review, 2026-10-10 (offline; decompiles, workshop folders, RimSage, `gh api`).

| finding | verdict | evidence |
|---|---|---|
| §5.1 exclusion key is `<race>-<xenotypeDefName>`; no RSW_ key in config | INVALID-kept (claim holds; race is `pawn.kindDef.race`) | FA `FacialAnimationModSettings.cs` 98–127; config: 156 keys, 0 `RSW_`, 0 `Human-null` |
| §5.1 label-lookup fallback might still match | INVALID-kept (cannot rescue def xenotypes) — explanation added | RimSage `Pawn_GeneTracker.SetXenotype` (`xenotypeName = null`) |
| xenotype defNames are RSW_ now | INVALID-kept; count made exact (70, "~69 others" → 68) | `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/` |
| `disableCache` applies to excluded pawns too | INVALID-kept; added that excluded pawns get no FA nodes but still lose the cache | FA `HarmonyPatches.PrefixParallelGetPreRenderResults`, `DrawFaceGraphicsComp.CompRenderNodes`; RimSage `PawnRenderer.ParallelGetPreRenderResults` |
| "master + 19 part nodes" | VALID-fixed → 18 (15 dead), layers 50–59 | `DrawFaceGraphicsComp.cs` 110–175 |
| eight comps on Human only | INVALID-kept (Emotion commented out); FACP's gated add to `BS_InsectoidHumanoid_FourArmed` added | `Patches/Race_Patches.xml`; FACP `StartupPatcher.cs` 212, 577 |
| per-pawn JobDef dictionary | INVALID-kept, strengthened (fresh constant-animation copies per key) | FA `FAHelper.CreateAnimationDict` |
| "LINQ filter on job change and every 60 ticks" | VALID-fixed: deferred `IEnumerable`, re-evaluated every draw | `FacialAnimationControllerComp.cs` 19, 173; `AnimationFrameAccumulator.cs` 21–31 |
| RenderTexture pool never freed (INFERRED) | VALID-fixed → MEASURED | `MyRenderTexturePool.cs` (no remove/release) |
| PNG watcher "live in release" | VALID-fixed: only enabled from the editor window | `NL_SelectPartWindow.cs` 999–1011 |
| textures load eagerly incl. gated-off defs | INVALID-kept | RimSage `ModContentPack.ReloadContent`, `ModContentHolder.ReloadAll`, `ModContentLoader.LoadAllForMod` |
| DXT applies to "power-of-two" textures | VALID-fixed: condition is width/height divisible by 4; DXT5 ⇒ ≈¼ holds | RimSage `ModContentLoader.LoadTextureViaImageConversion`, `StaticTextureAtlas.FastCompressDXT`, `PrefsData.textureCompression = true` |
| override packs "replace, do not add" memory | VALID-fixed: both copies load (per-mod holders) | RimSage `ModContentHolder.ReloadAll` |
| family totals (~3,660 PNG / ~4,500 MB) | INVALID-kept (rows sum to 3,659 / 4,487) | §2.9 table arithmetic |
| GH-mods SW block "~1.1 GB, largest dead block" | VALID-fixed: SW block is 300 PNGs ≈ 320 MB; 1.1 GB is the whole mod | `3501317734/Textures/*` dimension scan; `LoadFolders.xml` |
| default load folders `/` + `1.6` | INVALID-kept; `Common/` rule added (FA has none) | RimSage `ModContentPack` default-folder block |
| lts.geg "1.5-only" | VALID-fixed: supports 1.6; `loadFolders.xml` maps v1.6 → `/` + `1.5` | `3023336989/loadFolders.xml`, About.xml |
| save compat: Scribe ignores unknown nodes | INVALID-kept, upgraded INFERRED → engine-confirmed (dry-run still owed) | RimSage `Scribe_Defs.Look` (`curXmlParent[label]`) |
| "nine" third-party FA mods; stub "likely needed" | VALID-fixed: twelve, seven harmless/guarded, five xpath mods UNVERIFIED; stub is a fallback | `facts/mod_facts.jsonl` `dependants_detail`; RotR `LoadFolders.xml`; RimSage `DirectXmlLoader` error text |
| ThingComp `CompRenderNodes` / node APIs exist in 1.6 | INVALID-kept | RimSage `ThingComp.CompRenderNodes` |
| phase 0 feasible (add keys to FA list at startup) | INVALID-kept, made concrete (public static list, or postfix on `ShouldDrawRaceXenoType`); noted neither removes `disableCache` | FA `FacialAnimationMod.cs` 8–13, `FacialAnimationModSettings.cs` 59 |
| licence table | INVALID-kept (FACP none, GH MIT last commit 2026-07-09, FAF/AmCh-Q Apache-2.0, VTE CC BY-NC-ND 4.0 in LICENSE, `Nals` 0 repos) | `gh api repos/…`, `…/license`, `…/commits`; FAF `LICENSE` in workshop folder |
| reel / LFS "no repo" | UNVERIFIED (not re-searched) | — |
| effort "2–3 weeks" | UNVERIFIED — now labelled INFERRED | — |
| §5.1 live render (FA drawing on Jawa today) | UNVERIFIED — needs `FA_EXCLUSION_LIVE_CHECK_1` | — |
