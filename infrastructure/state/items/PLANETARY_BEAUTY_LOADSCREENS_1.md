# PLANETARY_BEAUTY_LOADSCREENS_1 — mechanism identified, two candidates offered

No prior item file existed (per the queue's own note). Fresh start, FOUNDRY/BELT,
2026-09-09. Game was down all session (crashed twice during quicktest map gen) —
this item is pure offline graphics-pipeline work, no bridge call made or attempted.

## The mechanism (read from the vanilla decompiled source via RimSage, not guessed)

RimWorld has **no dedicated "loading screen" image system** — no `LoadingScreenImages`
folder, no per-load-event def field. What actually paints the screen behind both the
main menu AND every loading spinner (map gen, savegame load — any `LongEventHandler`
long event) is one shared full-screen background manager:

- `Verse.UIMenuBackgroundManager.background` — a single static `UIMenuBackground`
  instance, set to a `RimWorld.UI_BackgroundMain` in `UIRoot_Entry.Init()`.
- `UI_BackgroundMain.BackgroundOnGUI()` (`Source/RimWorld/UI_BackgroundMain.cs`) draws
  either `overrideBGImage` or the core fallback texture `UI/HeroArt/BGPlanet`
  (2048×1280, ~1.6:1), `ScaleMode.ScaleToFit`, full-screen.
- `Verse.LongEventHandler.cs` (~line 229-233) calls that SAME
  `BackgroundOnGUI()` during any long event — i.e. **the loading screen and the main
  menu are the same background draw call**, not two separate mechanisms.
- The image behind it is driven by `RimWorld.ExpansionDef`'s XML field
  **`backgroundPath`** (`Defs/Core/Misc/ExpansionDefs/ExpansionDefs.xml`), one per
  installed expansion: `UI/HeroArt/BGPlanet` (Core), `UI/HeroArt/MenuBG_Royalty`,
  `MenuBG_Ideology`, `MenuBG_Biotech`, `MenuBG_Anomaly`, `MenuBG_Odyssey`. The game
  either shows a fixed player-chosen one (`Prefs.BackgroundImageExpansion`) or
  randomizes across active expansions each menu visit (`Prefs.RandomBackgroundImage`,
  the default) — see `MainMenuDrawer.Init()` and `Dialog_Options.cs` ~line 611-631.
- Hovering an expansion icon on the main menu cross-fades in that expansion's own
  `backgroundPath` image over the current one (`UI_BackgroundMain.DoOverlay` +
  `Notify_Hovered`).

**So the real, buildable hook for a mod**: an `ExpansionDef` (or a patch adding a
`backgroundPath` to one, though vanilla does not expose a generic "add another
rotation slot" — every existing `ExpansionDef` is one of the six above) pointing
`backgroundPath` at a new texture matches the exact same code path vanilla uses for
its own load/menu beauty art. This is the mechanism to wire against later — **not
wired in this item**, per its scope (candidates only).

Vanilla loose PNGs for `UI/HeroArt/*` were not found on disk (`Data/Core/Textures`
has no matching files) — they live packed in `resources.assets`/AssetBundles per
`reading-rimworld-graphics`; not extracted for this item since the aspect ratio
(2048×1280, ~1.6:1) was enough to scope the candidates without a live pull.

## Candidates produced (Codex image pipeline, shared `--codex-home`, no isolated-home
orphan risk since neither call used `--codex-home`)

Both generated with `skills/generating-images/scripts/codex_image.py generate`,
benefiting from tonight's `CODEX_EDIT_TIMEOUT_1` orphan-cleanup fix being in the
script even though this item's calls didn't need it (shared home, no timeouts hit).

1. `Transient/planetary_beauty_loadscreens/candidate_1_crescent.png` — 1916×821,
   2.03 MB. Low-orbit crescent view of a sand-colored desert world, dust-storm
   spiral visible, thin blue atmosphere limb, starfield. Prompt: *"A single
   sand-colored desert planet seen from space, wide crescent view, thin blue
   atmospheric glow along the horizon, swirling dust-storm bands across
   dune-colored terrain, deep black starfield background, cinematic realistic
   space photography, wide landscape composition, no text, no UI, no logos."*
   44 s.
2. `Transient/planetary_beauty_loadscreens/candidate_2_twin_suns.png` — 1672×941,
   1.88 MB. Full-disc view of an ochre/rust desert world lit by a visible binary
   star pair near the limb — reads as a Tatooine/Ash'karr-style twin-sun desert
   world. Prompt: *"Full disc view of an arid desert planet floating in deep
   space, twin suns glowing near its limb, warm ochre and rust-colored terrain
   with faint canyon shadows and thin high clouds, distant sparse starfield,
   moody realistic space photography, wide landscape composition, no text, no
   UI, no logos."* 56 s.

Both inspected directly (read back as images, not just file-exists checked) — no
text/UI artifacts, no watermarks, no chroma-key fringing (neither needed alpha;
both are opaque full-bleed backgrounds by design, matching how vanilla uses them).
Neither cropped/resized to the vanilla 1.6:1 yet — that's a decision for whichever
candidate the owner picks, since crop framing is a creative choice, not a technical
one.

## Scope — candidates only, same pattern as `DESERT_WRAPS_ART_COMMISSION_1`

Per this repo's design-loop doctrine (mockups first, owner picks, then iterate):
**not** wired into any `ExpansionDef`/mod, **not** a whole loadscreen rotation. This
item stops at two reviewable stills under `Transient/` for the owner's pick.

## Next step (owner's call, not taken here)
- Pick one (or neither, or "try again with X changed").
- If picked: crop/pad to 2048×1280 (or whatever aspect the target `backgroundPath`
  slot needs), then wire via a new/patched `ExpansionDef.backgroundPath` in a
  RimMandrake-tier mod (`design/NAMING_SCHEME_PLAN.md` applies to the new def).
- Consider a second pass once picked: 2-3 more beauty shots in the same style for
  an actual rotation, once the single-candidate direction is confirmed.

## criteria
- [x] Mechanism identified from the decompiled vanilla source (RimSage), not guessed
      — `UI_BackgroundMain` / `ExpansionDef.backgroundPath` / `LongEventHandler`'s
      shared draw call.
- [x] 2 candidate beauty shots generated via the `generating-images` skill's Codex
      pipeline, inspected directly, paths under `Transient/`.
- [ ] Not done (out of scope): wiring into a live mod/def, cropping to exact vanilla
      aspect, building a rotation. Awaits the owner's pick.
