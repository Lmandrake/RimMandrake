"""validation.py -- modcheck suite for RimMandrake RustChrome (mandrake.rm.rustchrome).

Grounded in this mod's actual Source (`RustChromeColors.cs`, `RustChromeMod.cs`),
read whole before writing this -- never the walk doc's own quoted strings, which
turned out to be STALE against the code actually on disk (see the note below).

WHAT THIS MOD ACTUALLY IS AT RUNTIME: Tier 1 is 14 loose PNG overrides at vanilla
UI texture paths (zero code; checked statically by `override_textures_static`
below -- present, non-blank, vanilla-sized). Tier 2
(`RustChromeColors`, `[StaticConstructorOnStartup]`) reflection-sets six
`Verse.Widgets` colour fields plus `RimWorld.InspectPaneUtility.
InspectTabButtonFillTex`, once at its own static-ctor time, driven by
`RustChromeMod.settings.themeEnabled` (default `true`).

🔴 THE WALK DOC IS STALE, same family as CLAUDE.md's "a doc can describe defects
fixed before the doc was written": `design/validation_walks/RimMandrake/
RustChrome.md` quotes the boot log line as `"[RimMandrake.RustChrome] colour
fields set."` and says nothing about a Mod Settings toggle. The code on disk
(post MOD_OPTIONS_RETROFIT_1) logs `"... colour fields set to theme."` /
`"... restored to vanilla."` depending on `themeEnabled`, and ships a real
`RustChromeSettings.themeEnabled` checkbox. This suite asserts the CURRENT
strings, read from `RustChromeColors.cs`/`RustChromeMod.cs` directly -- the walk
doc itself needs its own correction pass, out of scope for this file.

MOD SETTINGS -- suite.toggles below:
  `themeEnabled` is an INSTANCE field on `RustChromeSettings` (not `public
  static`, unlike Pits/RimProperty/Aftermath's settings classes), so
  `jawa/mod_settings_field` (`t.set_setting`) can actually reach it -- no
  static-field refusal expected here.

  It is still left UNCOVERED, and that is a genuine floor gap, not an
  oversight: `RustChromeColors.Apply()` is called from exactly two places --
  the static constructor at boot (reads the setting once) and
  `RustChromeSettings.DoWindowContents`'s own `if (themeEnabled != before)`
  branch, which only runs from inside the actual Mod Settings window's UI
  code. Setting the field directly via `jawa/mod_settings_field` changes the
  in-memory value but calls `Apply()` from neither path, so the live colours
  and the boot log line would not move -- a component built on `set_setting`
  here would either assert nothing real or assert against a value that
  never took effect. Proving the `false` path needs a persisted-setting
  restart (write `ModSettings.xml`, reload), which is a heavier op than this
  smoke suite's single-session, no-restart shape affords; flag for a future
  pass rather than fake it.

Still not proven / likely first-live-run corrections:
  1. Whether `jawa/drain_log` still holds this mod's boot-time line by the
     time a quicktest chain gets to read it -- RustChrome's static ctor runs
     during `LoadedModManager.LoadAllActiveMods`, long before a quicktest
     map exists, same timing concern LoadTracer's own docstring flags for
     its own boot lines. Untested live.
  2. `Log.Error`'s message cap/dedup behaviour was not exercised -- if
     `field not found:` never fires on a healthy load (expected), the
     negative assertion below has never actually been proven to catch a
     real regression, only reasoned about from the source.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("RustChrome")
suite.toggles = ["themeEnabled"]

BOOT_LOG_TAG = "[RimMandrake.RustChrome]"


@suite.chain("boot_theme_applied")
def boot_theme_applied(t):
    """Beyond-toggle: proves `RustChromeColors`'s static ctor actually ran
    and every field/tex it reflects into resolved under the currently-
    installed RimWorld build -- a field-name drift after a version bump
    would otherwise load clean (no XML config error) while doing nothing.
    Default `themeEnabled=true`, so this is the "set to theme" branch."""
    with t.component("colour_fields_resolved", beyond_toggle=True):
        t.expect_log_contains(BOOT_LOG_TAG, field=None, value=None)
        line = t.bridge_call("jawa/drain_log", limit=200, contains=BOOT_LOG_TAG)
        msgs = [m.get("text", "") for m in ((line or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            if "colour fields set to theme." not in joined:
                raise ExpectationFailed(
                    "no '%s colour fields set to theme.' line found -- "
                    "either the static ctor never ran, or themeEnabled was "
                    "false at boot. Recent matching lines: %r" % (BOOT_LOG_TAG, msgs))
            if "field not found:" in joined:
                raise ExpectationFailed(
                    "'%s field not found:' appeared -- a Widgets/"
                    "InspectPaneUtility field name has drifted under this "
                    "RimWorld build. Recent matching lines: %r" % (BOOT_LOG_TAG, msgs))
        t.screenshot()


# RUSTCHROME_COVERAGE_GAPS_1 static bar: Tier 1 (the 14 loose PNG overrides) had no check at all.
# Vanilla sizes MEASURED 2026-10-03 by Texture2D name from RimWorldWin64_Data/resources.assets (UnityPy
# 1.25.3, ~/.venvs/rimart); CheckOn/CheckOff each appear twice there, both 64x64. Atlases are 9-sliced by
# Widgets.DrawAtlas from the texture's own size, so they must match exactly; a plain background is
# stretched into its rect, so only its aspect must match (AbilityButBG/DesButBG ship 76x76 vs 75x75).
VANILLA_UI_SIZES = {
    "UI/Buttons/SliderHandle": (24, 24), "UI/Buttons/SliderRail": (24, 24),
    "UI/Widgets/AbilityButBG": (75, 75), "UI/Widgets/DesButBG": (75, 75),
    "UI/Widgets/ButtonBG": (64, 64), "UI/Widgets/ButtonBGClick": (64, 64),
    "UI/Widgets/ButtonBGMouseover": (64, 64), "UI/Widgets/ButtonSubtleAtlas": (64, 64),
    "UI/Widgets/CheckOff": (64, 64), "UI/Widgets/CheckOn": (64, 64), "UI/Widgets/CheckPartial": (64, 64),
    "UI/Widgets/RadioButOff": (64, 64), "UI/Widgets/RadioButOn": (64, 64), "UI/Widgets/TabAtlas": (64, 32),
}
ATLASES = ("UI/Widgets/ButtonSubtleAtlas", "UI/Widgets/TabAtlas")


def override_texture_problems(tex_root=None):
    """[(path, why)] for the Tier-1 overrides: every vanilla path present, decodable, non-blank, sized
    like the vanilla texture it replaces (exact for atlases, same aspect otherwise), and no stray PNG
    under Textures/UI that overrides nothing in the table."""
    import os as _os
    from PIL import Image
    tex_root = tex_root or _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Textures")
    out = []
    for rel, (vw, vh) in sorted(VANILLA_UI_SIZES.items()):
        p = _os.path.join(tex_root, rel + ".png")
        if not _os.path.isfile(p):
            out.append((rel, "missing"))
            continue
        try:
            im = Image.open(p).convert("RGBA")
        except Exception as e:  # noqa: BLE001
            out.append((rel, "undecodable: %s" % e))
            continue
        w, h = im.size
        if not any(a > 0 for a in im.getchannel("A").tobytes()):
            out.append((rel, "fully transparent"))
        if rel in ATLASES and (w, h) != (vw, vh):
            out.append((rel, "atlas %dx%d != vanilla %dx%d" % (w, h, vw, vh)))
        elif w * vh != h * vw:
            out.append((rel, "aspect %dx%d != vanilla %dx%d" % (w, h, vw, vh)))
    known = {r + ".png" for r in VANILLA_UI_SIZES}
    for d, _dirs, files in _os.walk(_os.path.join(tex_root, "UI")):
        for f in files:
            rel = _os.path.relpath(_os.path.join(d, f), tex_root).replace(_os.sep, "/")
            if f.endswith(".png") and rel not in known:
                out.append((rel, "stray override not in the vanilla table"))
    return out


@suite.chain("override_textures_static")
def override_textures_static(t):
    """Static (no bridge): Tier 1's 14 loose PNGs present, non-blank, vanilla-sized (see VANILLA_UI_SIZES)."""
    with t.component("fourteen_overrides_present_nonblank_vanilla_sized", beyond_toggle=True):
        bad = override_texture_problems()
        if bad:
            raise ExpectationFailed("%d override problem(s): %s" % (len(bad), bad))
