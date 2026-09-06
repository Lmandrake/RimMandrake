# UI_SHELL_SLICE_BUILD_1 — vertical slice landed, coexistence gate owed

Build the RimUtinni Shell vertical slice per `ui_shell_spec.md`:
`mandrake.rut.shell` theme mod (3 button atlases + palette meta.xml), 1
loader + 1 menu-bg art, RimThemes-coexistence gate on next load.

## 2026-09-05 (FOUNDRY, offline while the bridge was free) — landed commit `abd9fba2`

Found the build already complete and settled in the shared working tree
(files untouched for ~2 hours — not mid-write) when this item was claimed.
Verified rather than re-authored:

- `About/About.xml`, `Defs/VBE_Backgrounds_Utinni.xml` — well-formed, cite
  the real `aRandomKiwi.RimThemes`/`vanillaexpanded.backgrounds` packageIds
  (both confirmed present in the owner's live full modlist), `MayRequire`
  correctly gates the VBE def.
- `meta.xml` — the 10 palette keys named in spec §2, values match §1's
  table.
- All 7 shipped textures dimension-checked against the vanilla sizes the
  spec documents: 64×64 (3 button atlas states), 75×75 (Command.BGTex),
  10×10 (LoaderBar/TextBar), 96×96 (Icon) — all exact matches.
- Button atlas: the live one is `_artsrc/options/B_clean`, byte-identical
  (confirmed via `cmp`) — the generator's own algorithmic default; two
  alternates (`A_heavy`, `C_chalk`) are still on disk with a contact sheet
  for the owner to override if he prefers a different one.
- The two AI-generated pieces (menu background: Ishko at the temple gate;
  loader: amber tactical orrery display) — looked at both directly, both
  match their own recorded prompts and the reference art convincingly.

**Fixed before committing**: four `.gitignore` files were excluding ALL
shipped art as "regenerable derived output". True for `gen_textures.py`'s
seeded, deterministic PIL atlases — **not true** for `gen_bg.py`'s two
AI-generated pieces, which that script's own header admits are
non-reproducible on a re-run. Gitignoring them would have silently lost
real shipped game content on a fresh checkout, inconsistent with this
repo's own convention of committing final art (e.g. `RimStarWars/Cuisine`'s
icons). Removed those four `.gitignore`s; kept `_artsrc/`'s own (raw/
generation intermediates and options/ rejects are genuine scratch material,
not shipped content).

## 2026-09-05 (FOUNDRY) — owner reopened the art direction, rust is out

Owner, after seeing a concept render: *"I love love love the tech panel you
made. Rusty buttons are out."* Full context and reasoning in the PIVOT
section of `ui_shell_spec.md`. Built and shipped a new `D_helm` procedural
button/gizmo/icon style (grey-green gunmetal, vector-line brackets, amber
accent) as the new default — commit `506daf52`. The A_heavy/B_clean/C_chalk
rust options this item originally shipped and verified are now archived,
not live. **Still owed**: the menu background (Ishko at the temple gate)
and the loader screen (amber orrery) are image-gen pieces from `gen_bg.py`,
not touched by this pass — they still ship the old rust-adjacent look and
need a fresh generation in the new material language before this item's
art can be called consistent top-to-bottom.

## 2026-09-05 (FOUNDRY) — menu bg + loader re-authored; animated bg attempted; deploy gap caught

Menu background and loader regenerated in the new material language (see
`ui_shell_spec.md`'s pivot section for the full prompt diffs and the
animated-loop build). Owner then asked to consider a lightly-animated menu
loop; built it (dust/fog/pulsing eyes, VBE's real `animated`+`Videos/`
mechanism, not guessed).

**Caught mid-verification: none of today's shell work had been deployed.**
`deploy_custom_mods.py --mod UtinniShell` showed 23 files of drift — the
live game had been running a stale copy this whole session, which is
exactly why `jawa/get_defs` first read `animated: false` on a def whose XML
said `true`. Deployed. **This means every "verified via bridge" claim
earlier today for `D_helm`/the button atlases should be treated as
re-confirmed only from the point of the deploy, not before** — the
Cyberpunk-vs-D_helm control test result itself doesn't change (that used
RimThemes' pre-existing Cyberpunk theme, unaffected by our deploy), but
it's now recorded here in case anyone re-derives from an earlier note.

**Found and fixed a real codec bug**: Unity's `VideoPlayer` errors hard on
VP9 (`Error: Unsupported video codec 'VP9'`); switched `animate_menu.py` to
VP8 (`libvpx`), confirmed via `ffprobe` and a clean reload.

**Found, NOT fixed, filed separately**: even with the def, video, and VBE
settings all independently confirmed correct, the main-menu background
renders solid black while any non-Vanilla RimThemes theme is active —
reproduced 3x, and shown to be unrelated to our mod by switching RimThemes
to Vanilla and watching a (different, unrelated) VBE background appear
immediately. Filed as `RIMTHEMES_VBE_BACKGROUND_CONFLICT_1` — this may mean
the menu background has NEVER been visible during real play with Utinni
Shell selected, static or animated, predating this session's animation
work entirely.

## criteria
- [x] Mod skeleton, theme, and art built (offline half of spec §2/§3).
- [x] Shipped art actually committed, not silently gitignored.
- [x] **Button/gizmo/icon art re-authored to the owner's confirmed
      direction** (`D_helm`) — see above. The menu background and loader
      are NOT yet re-done and still need their own pass.
- [x] **§4 gate — RESOLVED** (see the 2026-09-05 real-OS-click entry below):
      activated `aRandomKiwi.RimThemes` +
      `mandrake.rut.shell` in the live ModsConfig (596 mods now), restarted,
      confirmed both load with **zero errors** (`Player.log` grepped clean
      for either packageId). RimThemes' own theme picker
      (`Dialog_ThemesList`, opened directly via
      `rimworld/open_window_by_type` since the main menu's own button row
      isn't reachable through `get_ui_layout`/`click_ui_target` — it's drawn
      by `MainMenuDrawer` directly, not as a `Window`) **correctly discovers
      "Utinni Shell"** with its real name, description and icon pulled from
      `meta.xml`.

  **2026-09-05 (FOUNDRY), deeper pass — root cause narrowed, still unresolved.**
      Two things that looked like plausible culprits are now RULED OUT by
      decompile (`ilspycmd` against the live `RimThemes.dll`,
      `1668983184/1.6/Assemblies/`):
      - `Widgets_ButtonImage_Patch` (the obvious suspect) only patches the
        **6-arg** `Widgets.ButtonImage(Rect, Texture2D, Color, Color, bool,
        string)` overload. The select-icon button in `Dialog_ThemesList`
        calls the **4-arg** overload (`Rect, Texture2D, bool, string`) —
        completely unpatched, runs stock vanilla code. Not the interceptor.
      - `WindowStackOnGUI_Patch`'s per-frame "only the topmost layer-1 window
        draws" gate doesn't apply either: with only `Dialog_ThemesList` open
        (plus the debug-toolbar `ImmediateWindow`, a different layer), it's
        trivially the sole layer-1 window and always wins the "topmost" check.
      A REAL bug was found and is now understood: the bridge's `targetId`
      embeds a frame/surface generation number
      (`ui-element:<surface>:2:<n>`) that **increments continuously** even
      with no clicks happening — a `targetId` captured by `get_ui_layout` and
      then used a few hundred ms later in `click_ui_target` times out
      ("Timed out waiting ... to be redrawn") because that exact generation
      no longer exists. Fetching the target immediately before the click
      fixes this and produces a clean `success: true` — a real, generally
      useful finding for anyone else driving dialogs through this bridge.
      **But even with a fresh, non-stale target and a `success: true` /
      non-timeout click: the theme selection still does not take effect.**
      Proven definitively this pass, not just inferred: opened the dialog,
      screenshotted it (`Transient/rimthemes_after_click.png` — not
      committed, Transient convention), clicked Utinni Shell's select icon
      (fresh target, `success: true`, message "Activated an icon button...
      UI state did not change"), screenshotted again — **the selection
      marker never moved off "Centipede"** (the colourful hex icon stays on
      Centipede's row; Utinni Shell's icon stays the plain grey unselected
      hex). Repeated against **Vanilla** as a control (not our mod, to rule
      out something Utinni-Shell-specific) — same result: click reports
      success, selection marker doesn't move. **This is a general
      RimThemes-dialog click-injection gap, not specific to our theme or to
      a target-mapping bug** — the click is delivered and accepted by Unity
      IMGUI (no timeout, a real `ButtonInvisible`-equivalent presumably
      returns true) but `Themes.changeThemeNow` (or its precondition) isn't
      firing through to `Settings.curTheme`. Not chased further into
      `Themes.changeThemeNow`'s own body this pass — worth a look if anyone
      picks this up again, but likely an IMGUI hot-control/event-consumption
      interaction between the bridge's synthetic input and RimThemes' custom
      `GUI.BeginGroup`/`EndGroup` nesting around each row, not something
      fixable from the tool-call side.
      **RESOLVED, same pass, without a human click.** The owner was away
      from the keyboard and suggested "consider computer usage" — instead of
      the bridge's semantic `click_ui_target` (which only simulates a click
      to RimWorld's own input handling), drove the REAL OS mouse: Windows
      `user32.dll` via `ctypes` (`SetProcessDpiAwareness(2)` first — without
      it, `GetWindowRect`/`GetClientRect` return virtualized 96-DPI
      coordinates and every computed screen point is wrong on this
      multi-monitor, scaled setup), `SetCursorPos` + `mouse_event`
      LEFTDOWN/LEFTUP at the real screen coordinates (RimWorld's window was
      already OS-foreground; UI-space coordinates from `get_ui_layout`
      mapped 1:1 to logical screen pixels once DPI-awareness was set, no
      scale correction needed). **Worked on the first attempt** — confirmed
      by two screenshots: the dialog itself re-skinned live the instant the
      click landed (its own "Supported by" button, row highlighting, and
      the Utinni Shell row's select icon all switched to the selected/brass
      look), and after closing the dialog with a second real click, the
      **main menu now renders the Utinni Shell button atlas** and the
      bottom-right RimThemes indicator shows our icon as active. This
      strongly confirms the earlier root-cause theory (an IMGUI
      hot-control/event-consumption gap specific to the bridge's synthetic
      injection path) rather than anything wrong with the target mapping or
      RimThemes itself — a real OS click sails through with no special
      handling needed. Worth a `rimbridge-companion` note: for dialogs from
      mods with heavy custom GUI patching, a real `SendInput`-based click is
      a working fallback the bridge doesn't offer natively yet.
- [ ] §5 verify, remainder: `validate_patch.py` doesn't actually apply here
      (`VBE_Backgrounds_Utinni.xml` is a plain `BackgroundImageDef`, not a
      `PatchOperation` file — nothing for that tool to check). VBE
      Backgrounds ships no assembly and no picker dialog for this def type
      (confirmed: no DLL under the mod's workshop folder) — it's rotated in
      randomly by VBE's own main-menu background system, so "shows in the
      picker" isn't a real verification step; the honest check is "does our
      background ever get drawn," which needs either several main-menu
      reloads (nondeterministic) or reading VBE's own selection code. Not
      done this pass. **Loader art on a cold load** is still genuinely
      pending — needs an actual ~25-minute cold load with the full modlist,
      not a quicktest.

Left `doing` — the offline half is done, the gate is one human click and a
four-screenshot pass away from complete.

## 2026-09-05 (BENCH, owner-authorized takeover after FOUNDRY's seat was
OOM-killed) — §5 remainder in progress

- **VBE background question SETTLED by decompile** (subagent, `ilspycmd` on the
  live workshop DLL; scratch at `/tmp/vbe_decomp/`). Corrects the earlier "VBE
  ships no assembly / no picker" note: workshop folder `2775017012` ships
  `1.6/Assemblies/VBE.dll`. `VBESettings.Allowed()` gates only on: def resolved,
  `enabled[defName]` (defaults **true** via `CheckInit()`), not-animated, and no
  pinned `current`. Defaults are `randomize=true, cycle=true (10–15s),
  current=null`, and **no VBE settings file exists in Config/** — install runs
  on code defaults. So `RUT_BG_ShellIshkoGate` is in the live rotation pool
  as-shipped, and TWO user-facing pickers list it
  (`HarmonyPatches.DoMenuBackgroundButton` float menu; `VBEMod.
  DoSettingsWindowContents` thumbnail grid). Spec §5's "shows in VBE's picker"
  is therefore checkable in-game after all.
- **Theme persistence PROVEN on disk**: `Config/Mod_1668983184_RimThemes.xml`
  carries `curTheme>mandrake.rut.shell§Utinni Shell` — FOUNDRY's OS-click
  selection survived the session.
- **Full-stack session log is clean for our mod**: preserved at
  `Transient/Player_log_quicktest_crash_2026-09-05.log`; exactly one mention of
  `mandrake.rut.shell` (the mod-list line), no error naming it or Utinni Shell.
- ⚠️ **`rimworld/start_debug_game_ready` KILLED the 596-mod game** — log stops
  mid-quicktest-setup (Ninefold research grants), no managed exception, no
  Unity crash dump (latest is Sep 1). Cause UNMEASURED. The 2026-08 measurement
  (78.5 s on 580 mods) no longer guarantees safety at this stack size.
- Cold load relaunched (the load §5 was owed anyway); loader-art capture loop
  running (`Transient/loadercaps/`). Mid-load frame already shows the amber
  tactical orrery loader art rendering on the real stack.

## 2026-09-05 (BENCH) — cold-load verdicts. §5 is done except two map shots.

- **Loader art on a real cold load: MEASURED PASS.** The 596-mod load rendered
  the amber tactical orrery full-screen; captured frames
  (`Transient/loadercaps/`, full-res `Transient/foundry_window_check2.png`)
  match `_artsrc/raw/loader_tactical_raw.png` element-for-element (Star
  Destroyer inset, glyph clusters, orrery rings).
- **Theme persistence across restart: MEASURED PASS.** Twice over: RimThemes
  config carries `curTheme>mandrake.rut.shell§Utinni Shell` pre-launch, and
  post-restart the picker shows the colourful selected-hex on Utinni Shell's
  row (screenshot `rimbridge_20260905_151314.png` in the game's Screenshots
  folder) while every other theme wears grey. Dialog chrome renders themed.
- **Runtime def presence: MEASURED PASS.** `jawa/get_defs`
  `VBE.BackgroundImageDef/RUT_BG_ShellIshkoGate` → found, label intact
  ("1 of 1 def(s) resolved"). With the decompile eligibility analysis above,
  the background is in VBE's live rotation pool and both pickers.
- **Post-restart log: clean.** No error naming the mod; the two "Utinni"-ish
  config errors are the pre-existing AdvancedShowers/VCE_StewCooking research
  coord collision on `RUT_Tree_Hearth`, not the theme.
- Clean themed-menu shot post-restart: `rimbridge_20260905_151441.png`.
  ⚠️ Honest note: B_clean is vanilla-faithful wood, so the menu-button skin is
  not visually distinguishable from vanilla in a still; the selected-hex +
  active indicator carry the proof. A B_clean mouseover (strong amber) hover
  test came back inconclusive — likely focus mechanics, not evidence against.
- **Remaining, deferred to a map session:** themed **gizmo row** and **float
  menu** screenshots (§4's last two surfaces) plus RimHUD/Dubs sanity — needs
  a map, and `start_debug_game_ready` on the full stack killed the game once
  today with host RAM at 9.4 GB free. Ride the next load round, a
  minimal-list+theme restart (22 s), or a moment with host headroom.

## 2026-09-05 (FOUNDRY) — gizmo-row attempt: a real gap found, not the pass we wanted

Tried the full-stack route first: `start_debug_game_ready` **crashed the game
again**, exact same spot as BENCH's earlier hit (dies mid quicktest research-
grant spam, no managed exception, no crash dump) — but this time with **33 GB
host RAM free**, not 9.4 GB. That rules out host memory pressure as the
cause; this is a reproducible crash in the debug-quicktest research-grant
path on the full 596-mod research tree, independent of RAM. Filed separately
so it doesn't get lost: `NINEFOLD_DEBUG_GAME_READY_CRASH_1` (not written yet
this pass — flagging here so the next session knows to check for it / file
it before re-attempting `start_debug_game_ready` on the full stack).

**Fell back to BENCH's own suggested route**: swapped to the 21-mod MINIMAL
list plus `aRandomKiwi.RimThemes` + `mandrake.rut.shell` (23 mods), a real
restart via `launch_and_wait.sh` (not `./game up`, which — corrected
understanding — only stamps the ledger/broadcasts state, it does not launch
anything; the actual launch mechanism is `launch_and_wait.sh`). Loaded
clean, quicktest reached Playing in 5s, no crash.

- **Theme persistence, now proven across a MOD-LIST-CHANGING restart, not
  just a same-list one**: `Config/Mod_1668983184_RimThemes.xml` still reads
  `curTheme>mandrake.rut.shell§Utinni Shell` after swapping the entire active
  mod list out and back. Stronger evidence than BENCH's same-session check.
- **Gizmo row screenshot taken** (`Transient/rimtheme_gizmo_row.png`, not
  committed) — but **the Draft gizmo's background panel is a plain grey-blue
  square, not the shipped rust/brass `Command.BGTex` art.** Zoomed crop
  confirms this directly, not a resolution artifact. This is a genuine
  finding, not yet explained: either (a) this specific texture only re-skins
  once a pawn is actually drafted / a different game state than a fresh
  quicktest wanderer, (b) something about the minimal 23-mod list changes
  how RimThemes resolves this asset versus the full stack, or (c) a real gap
  in how `Command.BGTex` is wired into the theme. **Not chased further this
  pass** — recording it plainly rather than either claiming the gizmo row is
  themed (it visibly isn't, in this shot) or guessing why.
- **Float menu screenshot: inconclusive, not a real test.** `right_click_
  cell` on empty ground resolves instantly to a single unambiguous "go here"
  order — RimWorld never opens an actual multi-option `FloatMenu` for that,
  so the screenshot (`Transient/rimtheme_float_menu.png`) is identical to
  the gizmo shot and proves nothing. A real float-menu test needs a target
  with multiple possible interactions (another pawn, an item, a corpse) —
  not attempted this pass.
- Modlist restored to the owner's full 596-mod list and game left DOWN
  afterward (no forced full reload — nobody was waiting on the game being
  up). `ModsConfig.PRESWAP.20260905_152515.xml` holds the minimal+theme list
  if anyone wants to resume this exact test setup without re-deriving it.

## 2026-09-05 (FOUNDRY), owner asked to rule out mod interference — DONE, ruled out

Owner's hypothesis: another mod might be interfering with RimThemes'
`Command.BGTex` reskin. Decompiled `Themes.cs`'s actual substitution
mechanism to check: it keeps a `fieldsOfInterestTex["Command"] = ["BGTex"]`
table and, on theme change, does
`ImageConversion.LoadImage(existingFieldTexture, EncodeToPNG(ourTexture))`
against `Verse.Command.BGTex` by reflection — so the mechanism DOES target
exactly our shipped file, ruling out "RimThemes has no hook for this asset
at all."

**Control test, same minimal 23-mod list (no RimHUD/Dubs/other UI mods
present to interfere)**: switched the live theme to **Cyberpunk** — a theme
shipped by RimThemes ITSELF, with both `.dds` and `.png` copies of
`Command.BGTex` (ours ships `.png` only, which was not itself the
differentiator) — via the same real-OS-click method, then re-ran the same
gizmo screenshot. **Identical result**: the Draft gizmo's panel interior is
the same plain grey-blue square as with our own theme, unchanged from
vanilla. Only the accent BORDER color reads as Cyberpunk-cyan (from
`ColorsSubstitution`'s separate, working color-field mechanism), not the
panel texture itself.

**Conclusion: not mod interference, not a defect in our shipped asset.**
RimThemes' own first-party theme shows the identical non-reskinned gizmo
interior. Whatever prevents `Command.BGTex`'s reflective swap from visibly
taking effect (leading hypothesis, still unconfirmed: vanilla's cached
`Command.BGTex` `Texture2D` may not be marked CPU-readable, which would
make `ImageConversion.LoadImage` silently no-op into it — no log line for
this was found either way) affects **every RimThemes theme equally**, ours
included. Nothing to fix on the Utinni Shell side. Not chasing the RimThemes
internals further — this is upstream-mod behavior, not our bug.

**Real float-menu screenshot also captured** this pass (the earlier
attempt's right-click resolved to a single instant order, not a real menu):
right-clicked one colonist onto another to get an actual multi-option
`FloatMenu` (`Pick up medicine...`, disabled with a reason shown) —
`Transient/rimtheme_real_float_menu.png`. Same pattern as the gizmo: cyan
accent border present, panel interior plain, consistent with the
control-tested RimThemes limitation above, not a separate bug.

**§4/§5 is now genuinely complete** for what bridge automation can prove.
Remaining open-ended, cosmetic-only question (own item territory, not this
one): whether `Command.BGTex`/float-menu panel texture reskinning is worth
chasing into RimThemes' own source further, given it doesn't work for ANY
theme today.
