# Messy Conduit: choosing the art style when you build

status: **DESIGN, nothing built.** Design pass 2026-10-04 (FOUNDRY), item `MESSYCONDUIT_STYLE_PER_BUILD_DESIGN_1`.

Owner brief, 2026-10-04 (typed): *"I'm starting to feel that the configuration setting approach for artstyle is getting
in the way. I think we should just build different art renderings of these buildings as options when you build them. A
single build menu should allow the player to select between these four art styles for the poles, hose reels, hoses, and
cables somehow. We need to think carefully how the user would select the art style for a particular conduit run.
Obviously a single connected run of conduit no matter how large would be a single art style. Please do a design pass
now on how we can get this done."* He also asked for a hose reel that looks different when its hose is laid out, with
the hose running into the reel.

The four styles are **Scrapper** (rough, hacked-together, crude), **Industrial** (thick black cable, tough steel),
**Modern** (multi-coloured extension cords on the ground with a colour choice, modern poles, black overhead lines) and
**Futuristic** (sleek angular steel).

## The answer in one table

| | **A. A separate building per style** | **B. One building, the style rides the game's own style system** (recommended) | **C. One building, our own style tag** |
|---|---|---|---|
| What the player sees | One Architect button per building opens a grid of 4 icons (the way carpets pick a colour) | Clicking the build button opens a 4-item menu with icons, the way walls ask for a material. The button remembers the last choice | Same as B |
| Where the style lives | In the building's type (`…_Industrial`) | On each building, in the game's own style field, which blueprints and frames already carry | On each building, in a small field of ours. We carry it through blueprint and frame ourselves |
| Survives save, load, packing up, copying | Yes, for free | Yes, for free (the engine already copies it from blueprint to frame to building) | Yes, but every hand-off is our code |
| Mod removed from a save | **Every conduit cell not in the default style disappears** and the grid breaks | Vanilla conduit stays and works. Only our own poles and reels go, as they do today | Same as B |
| Other mods that build conduit | They build plain vanilla conduit, which shows in the default style | They build plain conduit, which then joins the run it touches | Same as B |
| New code | Little: mostly XML | Moderate: 1 picker, 2 small engine patches, run logic | More: about 4 engine patches plus our own graphic swap |
| New definitions | About 32 building defs | About 20 small style defs, still 1 def per building | 0 |
| Risk | Uninstall loss. The build menu bloats. Costs and research are duplicated ×4 | Ideology's own style rules must not override ours (one patch handles it) | We re-create machinery the engine already has |

**Recommendation: B**, because the engine already carries a per-building style from blueprint to frame to finished
building and draws each building in its own style. We add only the picker and the "one run, one style" rule.

## 1. How the style can be chosen when building: the RimWorld mechanisms, checked

The engine facts below were all read from decompiled RimWorld 1.6 (RimSage, this pass) and from our own source.

### 1.1 Picking a material (stuff)

When a building can be made of different materials, `Designator_Build.ProcessInput` opens a float menu of the materials
you own. The choice stays on the build button (`stuffDef`) and goes to the blueprint (`stuffToUse`). This is the exact
**menu shape** we want, but stuff is a material with stats, cost and colour. Using it to mean "art style" would mean
inventing four fake materials ("scrapper steel") that would show up in stockpiles, trade and costs. **Rejected as the
carrier.** We copy its menu, not its data.

### 1.2 The game's own style system (Ideology's ThingStyleDef and style categories)

- Every generated **blueprint and frame** has a style field. `ThingDefGenerator_Buildings.BaseBlueprintDef` and
  `BaseFrameDef` always add `CompProperties_Styleable`. `Designator_Build.DesignateSingleCell` writes the designator's
  style onto the blueprint. In god mode it writes it straight onto the building. `Blueprint_Build.MakeSolidThing`
  copies it to the frame, and `Frame` copies it to the finished building (`thing.StyleDef = StyleDef`, Frame.cs line
  317). A reinstall blueprint keeps the packed building, comps included.
- **The building draws its style's graphic by itself.** `Thing.Graphic` uses `StyleDef.graphicData` when the style has
  one (Thing.cs lines 482-493), and `Blueprint` uses `StyleDef.blueprintGraphicData`. Menu icons use
  `Widgets.GetIconFor(def, stuff, styleDef)`.
- **It is saved per building** in `CompStyleable.PostExposeData` (`Scribe_Defs … "styleDef"`).
- **The catch: the vanilla picker is tied to ideoligions.** The designator's style is
  `ThingStyleDefNonPreceptSource`. That returns the player's chosen style **only in classic mode** with
  `styleOverridden` set. Otherwise it returns the primary ideoligion's style for that building, which for our buildings
  is nothing. The "Change style" gizmo on blueprints only appears in classic mode and only lists ideoligion style
  categories. So vanilla gives us the **storage and the drawing**, but not a picker we can use. We need one small patch
  on that getter: for our own buildings it returns the style picked on our menu.
- A building only has the style field if its def lists `CompProperties_Styleable`. The engine does not add it by itself
  (`ThingStyleHelper.CanBeStyled`). Vanilla `PowerConduit` does not list it, so we would add it by patch.

### 1.3 Grouped build buttons (`designatorDropdown`)

Any buildable def (things too, not only floors) with the same `DesignatorDropdownGroupDef` is folded into one
Architect button (`DesignationCategoryDef`, lines 297-308). Setting `useGridMenu` makes it a grid of icons, which is
how vanilla carpets offer their colours. This is the natural menu for Architecture A. It needs a separate def per
style, because each entry is its own `Designator_Build`.

### 1.4 Our own build button (a Designator_Build subclass or a patch on it)

We could replace the button's click with a float menu of 4 styles (copying 1.1), each showing its icon. Subclassing is
awkward because the Architect makes its designators by itself. A Harmony patch on `ProcessInput` for our defs does the
same job with much less code. Architectures B and C both use this.

### 1.5 Restyling by building over (`replaceTags`)

`PowerConduit` carries `replaceTags` = `Conduit`, and `DesignateSingleCell` wipes and replaces things that share a
tag. Under Architecture A, this is how a player would restyle conduit: build the other style's conduit on top. It works
like waterproof conduit replacing ordinary conduit, and it costs a rebuild.

### 1.6 Each mechanism against the questions

| | Stuff | Style system (B) | Grouped defs (A) | Our own tag (C) |
|---|---|---|---|---|
| What the player sees | Float menu | Float menu with icons (our patch) | Grid of icons | Float menu with icons |
| Choice stored on | Thing's material | Thing's style field, blueprint and frame too | Thing's def | Our comp on the thing; a patch copies it across blueprint and frame |
| Save/load | Free | Free | Free | Our field, no class name in the save |
| Deconstruct then rebuild | New choice | New choice (the button remembers the last one) | New choice | New choice |
| Pack up and reinstall | Kept | Kept | Kept | Kept if our comp is on the packed thing |
| Mod removed | — | Conduit stays vanilla; the extra saved field is skipped | Styled conduit **vanishes** | Same as B |
| Build cost | Changes cost | Same cost for every style (unless we choose otherwise) | One cost list per def, ×4 | Same |
| How a check reads it | — | Read `thing.StyleDef` on each building | Read the def name | Read our field |

## 2. What a style belongs to: a run

### 2.1 What conduit really is here

Conduit is vanilla `PowerConduit` and `WaterproofConduit`, made invisible by this mod (`ConduitVisuals`: every
`isPowerConduit` def except `HiddenConduit`, which stays the tidy option and is drawn as buried). The cords are not
things. They are drawn every rebuild by `RM_MapComponent_CordGraph` from the conduit grid, and nothing about them is
saved. The cord graph already groups its pieces into connected nets: `ComputeNetSeeds` unions pieces by the cells they
touch. It already gives each net one colour or cable kind (`CordMaterials.VariantFor(netSeed)`). Today the **style** is
one global value for every net (`GimmeSomeSlackSettings.style`, read in `CordMaterials.Build` and
`AerialMaterials.Build`). Pole art is changed by **editing the shared ThingDef's graphic** (`AerialMaterials.ApplyPoles`),
so every pole on every map always looks the same.

### 2.2 The definition

> **A run is a connected group of conduit cells, power switches, and the poles and wall brackets wired into them,
> together with the overhead spans between those anchors.** Machines, batteries and generators end a run; they are not
> part of it.

This is "a single connected run of conduit no matter how large", with the overhead line counted in because the
owner's styles describe the poles and the hanging cable together with the ground cable. It is *not* the vanilla power
net. A power net runs through batteries and machines, and two runs joined only through a battery are two runs.

### 2.3 How a style is recorded, and the rules (recommended set)

The style is stored **on every conduit cell and every anchor** (in its style field). The run is never stored, because
the conduit grid is the truth and the run is worked out from it.

| Situation | Rule |
|---|---|
| A new conduit cell, pole or bracket with no neighbouring run | It takes the style picked on the build button |
| A new piece touching **one** run | It adopts that run's style, whatever the button says. The placement cursor shows "joins Industrial run", so nothing is a surprise |
| A new piece bridging **two runs of different styles** | Owner question 2. Recommended: the older run's style wins, and the other run is repainted to match, with a message naming both styles |
| A run split by deconstruction, a fire or an explosion | Each half keeps the style it already has. Every cell carries the style, so nothing needs to be decided |
| Restyling a run that already exists | Owner question 3. Recommended: a free "Restyle this run" gizmo on any selected conduit or pole that repaints the whole run. It changes art only, never cost or function |
| An overhead span | It draws in its run's style. A span always lies inside one run, so a span with mixed styles cannot exist |
| A pole placed within reach of poles of another style | Auto-link only links to a run of the **same** style. Linking two styles by hand is the same as bridging two runs (question 2) |
| Hose reel, hose, nozzle and end piece | The reel is its own building with its own style. The hose takes the reel's style. A hose is not part of a power run |
| Power-tap clamp | It takes the style of the run it brings power home to. (It keeps its single crude art until the other three exist.) |
| Hidden conduit | Not styled. It stays the "buried, no cords" option it is today |
| Conduit built by something other than the player's menu (another mod, gravship landing, a quest) | No style is given, so the joining rule applies. If there is no neighbour, it uses the default style |

**Where the run rule runs.** A conduit or anchor checks its neighbours when it spawns and copies their style (a small
flood fill over the touching run, done once per placement, not per frame). The cord graph then reads each piece's
style from the cells it is drawn between. Because the whole run already carries one style, it can never disagree
with itself. Repainting writes the style field on every member of the run, then rebuilds that run's cords.

### 2.4 What the global Mod Setting becomes

It stays, with a narrower job:

- **"Default style"**: it pre-selects the build button for a new game and draws anything that has no style yet
  (older saves, and conduit built outside the menu). It keeps its saved key `style`, so nothing breaks.
- **Modern colour**: under the recommended answer to question 4, the colour moves into the build menu ("Modern: random
  colour", "Modern: orange", and so on). The setting keeps only the *default* colour mode (`extCordColorMode`,
  `extCordColor`, keys unchanged).
- The settings screen says plainly: "Style is chosen when you build. This sets what new games start with and how
  unstyled conduit looks."

## 3. Older saves, the review map and the settings keys

- **Older saves load unchanged, and they look exactly as before.** No existing conduit or pole has a style stored, so
  each draws in the default style. That default is the very setting it was drawn with before. The first time the player
  restyles a run, or builds onto it, the style is written for real.
- **Settings keys** `style`, `extCordColorMode` and `extCordColor` keep their names, types and defaults. The probe
  verb `set:style=X` keeps working, and now means "change the default". Existing checks that use it (ST1-ST5 in
  `validation.py`) still prove what they proved before, on unstyled scenes.
- **The style field on vanilla conduit is added by patch.** If the mod is removed, the patch is gone and the saved
  field is simply never read. That needs proving once by the removal check, which is an extended concern
  (`debug_process.md` §6b), not basic checkout. Guard the patch so it adds the style field only if no other mod already
  did.
- **The review map** (`human_review.py`) currently sets the global style and says *"four styles cannot stand side by
  side without a change to the shipped mod"*. After stage 2 they can. Each row gets its four styles side by side as
  separate stations, and `--style` shrinks to "set the default". The draft rule in `northstar_human_review.md`
  ("one switch for global settings") then names MessyConduit as an example that no longer applies.
- The removal of `AerialMaterials.ApplyPoles` (the shared-def edit) is part of stage 1. Pole geometry (insulator
  height, crossarm fan) becomes a lookup by (style, building) instead of an edit to the shared mod extension. The
  lookup data is the same (`PoleGeometryTable`, `BracketGeometryTable`).

## 4. Art: what each style needs, what exists

Paths are under `Textures/RimMandrake/GimmeSomeSlack/` and were listed on disk 2026-10-04. "Fallback" means the code
already draws a stand-in from another style.

| Piece | Scrapper | Industrial | Modern | Futuristic |
|---|---|---|---|---|
| Ground cable strand | yes (`Strand_Jawa`) | yes, 3 kinds | yes, 5 colours | yes |
| Plug, 2 junctions, wall stub, rock stub, dead frayed end | yes | yes | yes, in all 5 colours | yes |
| Live frayed end | yes | **missing** (fallback) | **missing** (fallback) | **missing** (fallback) |
| Power strip, lit | — (junction boxes) | — | yes (shared) | — |
| Power strip, dark | — | — | **missing** (tinted stand-in) | — |
| Cable shadow, spark glow | shared, yes | shared | shared | shared |
| Overhead span cable | fallback to ground strand | fallback (black rubber) | fallback (black rubber) | fallback (Futuristic strand) |
| Power mast + its top | yes | yes | yes | yes |
| Lamp mast + its top | yes | yes | yes | yes |
| Wall bracket (north, east, south) | yes | yes | yes | yes |
| Power switch on/off | yes (`PowerSwitch`, `_Off`) | **missing ×2** | **missing ×2** | **missing ×2** |
| Power-tap clamp | yes | **missing** | **missing** | **missing** |
| Hose reel, hose stored | yes (`Reel_PumpHookup`) | **missing** | **missing** | **missing** |
| Hose reel, hose laid (empty drum, hose entering it) | **missing** | **missing** | **missing** | **missing** |
| Hose strand flat / plump | yes (sack cloth) | **missing ×2** | **missing ×2** | **missing ×2** |
| Hose binding, coupling, nozzle, end cap, open mouth (the 5 drawn pieces) | yes | **missing ×5** | **missing ×5** | **missing ×5** |
| Hose shadow | shared | shared | shared | shared |
| Blueprint look, menu icon | free: the engine makes them from the style's graphic | free | free | free |

**Owed: about 41 PNGs.** That is 3 live ends, 1 dark strip, 6 switch frames, 3 clamps, 7 reels (3 stored and 4
laid), 6 hose strands and 15 hose pieces. Per-style overhead span wires are optional, because the fallbacks are the
cables the owner described. Before queuing any of it, search the artpipe state (`artpipe_state.py find`) for finished
art.

**The laid-out reel.** Draw it as two layers. The base graphic is the reel's empty drum with its hose inlet, which is
the "laid" look. A coil overlay is printed on top only while the hose is reeled in, and the reel's map mesh is
refreshed when the hose is laid out or reeled back. Then each style needs one drum and one coil, with no state
machine inside the graphic. The laid hose's first segment ends at the drum's inlet point, measured from the art like the
pole insulators.

## 5. Staged plan, with economical checks

Tests stay few and load-bearing, and each one covers several things at once. Every stage ends with one load round on
the `messyconduit` tier.

**Stage 1: poles alone, proving the whole mechanism (about 1 agent-day).**
Add the style field to the three anchor defs, plus 12 pole style defs (art exists). Build the picker on the build
button and the getter patch, so the button's choice is the designator's style. Remove the shared-def pole edit, and
look up pole geometry by style. Spans draw in their poles' style. The rule for two different styles comes in stage 2,
so until then a span between two styles uses the older pole's style.
*One behaviour check:* place the four mast styles through the real designator twice, once by blueprint and
construction and once in god mode. Pack one up and reinstall it. Save and load. Then read each mast's `StyleDef`, the
texture it draws, and its span texture. One scene covers the picker, the blueprint-to-frame-to-building chain, packing
up, and save/load.
*Review map:* row 2 (overhead lines) shows four masts side by side, one per style.

**Stage 2: conduit runs (about 2-3 agent-days).**
Add the style field to conduit and switches by guarded patch, plus 4 style "markers" (no graphic, because conduit is
invisible). Add the run rule (adopt, split, the bridge rule, the restyle gizmo). Build the cord materials for all four
styles once at start-up. The cord layer picks a piece's material by (style, colour or kind) instead of by the global
setting. The default setting draws unstyled cells.
*Two behaviour checks:* (1) Two runs in two styles, then a bridging cell, then a split by deconstruction, then save and
load. Read the style field of every cell and the printed materials of every section: the existing ST2 "printed meshes
carry only that style" check, made per run. (2) An unstyled legacy scene matches its current screenshot hash, which
proves older saves look unchanged.
*Review map:* row 1 (ground cords) gets one station per style. One extra station shows the bridge between two styles.

**Stage 3: hose reels and hoses (about 1.5 agent-days, plus art).**
Add 4 reel style defs, hose materials per style, the two-layer reel (drum plus coil) and the inlet point.
*One behaviour check:* four reels, each laid out and then reeled in, and saved and loaded while laid out. Read the
reel's style, the hose texture per state, and whether the coil overlay is there.
*Review map:* row 3 shows four reels laid out, plus one reeled in.

**Stage 4: art fill.** Generate the 41 PNGs, wire them, and point the existing offline art-sanity check (`O5`) at the
new slots. The stand-ins disappear one by one, and nothing else changes.

## 6. Risks and open points

- **Ideoligion styles could override ours.** If an ideoligion style category ever lists a conduit or one of our
  buildings, the vanilla getter would hand back its style. Our getter patch decides for our buildings and the conduit
  defs, so this cannot happen. A check confirms that no `StyleCategoryDef` lists any of them.
- **Classic-mode "Change style" gizmo.** In classic mode, a conduit blueprint would show vanilla's greyed-out
  "Change style" button, because conduit can now be styled. This is cosmetic. Hiding it on our defs is a small patch if
  it bothers anyone.
- **Copying a building.** Vanilla's copy button carries the style, but the getter only honours it in classic mode. The
  same getter patch makes "copy this pole" copy its style in every mode.
- **Big runs.** A repaint or bridge writes every cell of a run, which is a one-off cost per click. A run of 2,000 cells
  is a few milliseconds, and nothing per frame grows.
- **A section where two styles meet** prints one more material. This only happens where runs touch, which the rules
  make rare.
- **Style and price.** All four styles cost the same in this design. If Futuristic should cost plasteel or Scrapper
  should be cheaper, that is a gameplay ruling, which A would make natural and B can do with a small cost patch. It was
  not asked, so it is left out of the questions below.
- **Not measured here:** that a vanilla conduit's saved style field is skipped silently when the mod is gone. This is
  expected from how comps load, but it is proven only by the stage-2 removal check.

## Questions for the owner

*(2026-10-04 14:32 PDT. Each question has a recommended choice.)*

**1. How should the style be carried?**
- **B, one building with the style stored on it, using the game's own style machinery** *(recommended)*. Older saves
  look the same. Removing the mod leaves working vanilla conduit. About 20 small style defs, and still one build button
  per building.
- **A, a separate building for each style**, grouped under one button with a grid of icons. The least code, and the
  closest to vanilla. But removing the mod deletes every non-default conduit cell, and there are about 32 building defs
  to keep in step.
- **C, one building with our own style tag**, with no use of the game's style machinery. Fully independent of
  ideoligion rules, but we hand-build what the engine already does, with about twice the engine patches.

**2. When a new piece of conduit joins two runs of different styles, what happens?**
- **The older run's style wins and the other run is repainted, with a message** *(recommended)*. Building never
  stops, and the rule "one run, one style" always holds.
- **The placement is refused** ("would join an Industrial run to a Modern run"). Nothing changes by surprise, but
  players have to restyle first and then build.
- **The two styles may meet at a visible adapter box** (a junction drawn in both styles). It looks good and is the
  most "messy" choice, but it breaks the one-style rule and needs adapter art for every pair (6 pairs).

**3. How does a player restyle a run that already exists?**
- **A free "Restyle this run" button on any selected conduit or pole** *(recommended)*. It is instant, because
  style is art only.
- **Only by tearing it down and building again in the new style.** This is the vanilla habit, but it is slow for long
  runs and there is a lot of pointless rebuilding.
- **A "Restyle" button that orders a short rework job** for a colonist at each pole (conduit cells change at once).
  It feels earned, but it is more code and more to test.

**4. The Modern look's cord colour: where is it chosen?**
- **In the build menu, per run** *(recommended)*: "Modern: random colour" (the default) plus one entry per colour. The
  Mod Setting keeps only the default.
- **It stays one global Mod Setting** (a random colour per run, or one colour everywhere), as it is today.
- **Always a random colour per run**, with no choice. This is simplest, but it gives up the one-colour option that
  exists today.

## Owner decisions (question card, 2026-10-04 14:3x PDT)

1. **Architecture: B** — one building per kind, style stored on it with the engine's own style system; a four-item style menu on the build button.
2. **Merging runs of different styles:** the run with the **largest area (number of conduit cells) wins** and the smaller run is repainted to match. (Tie rule is open: use the older run.)
3. **Restyling:** a free **"Restyle this run"** button on any piece repaints the whole run.
4. **Modern cord colour:** chosen **per run in the build menu**, and the menu must include a **"random"** choice meaning the run is not uniform but a mixture of colours (alongside the single-colour choices such as brown and the existing multi-colour look).
