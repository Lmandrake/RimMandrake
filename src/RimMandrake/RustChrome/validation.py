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

  `set_setting` alone cannot drive it: `RustChromeColors.Apply()` runs only from the static ctor and
  from the settings window's own checkbox branch, so writing the field changes the in-memory value but
  moves no colour. RUSTCHROME_COVERAGE_GAPS_1 covers the toggle by calling the SHIPPED `Apply(true)` /
  `Apply(false)` through `RustChromeColors.ProofTheme` (jawa/static_call) and reading the six Widgets
  fields + the inspect-tab texture back: chain `theme_toggle_applies_and_restores` (bottom of this file).

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
import os
import re

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


# RUSTCHROME_COVERAGE_GAPS_1: the toggle and the colour values. RustChromeColors.ProofTheme (jawa/static_call) runs the
# SHIPPED Apply(true) then Apply(false) -- the very call the Mod Settings checkbox makes -- reading the six Widgets colour
# fields and the inspect-tab fill texture back after each, then re-applies the real setting. set_setting cannot drive
# this (it never calls Apply), a direct call can. Expected palette is parsed from the C# constants here, never read back
# from the live fields; the "off" arm must equal the vanilla values the mod captured BEFORE it overwrote them.
_THEME_PROOF = "RimMandrake.RustChrome.RustChromeColors"
FIELDS = (   # (short key, Widgets field, palette constant)
    ("wfill", "WindowBGFillColor", "WindowFill"), ("wborder", "WindowBGBorderColor", "WindowBorder"),
    ("sfill", "MenuSectionBGFillColor", "SectionFill"), ("sborder", "MenuSectionBGBorderColor", "SectionBorder"),
    ("ounsel", "OptionUnselectedBGFillColor", "OptionUnselectedFill"), ("osel", "OptionSelectedBGFillColor", "OptionSelectedFill"),
)


def _src(name):
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", name), encoding="utf-8").read()


def palette(src=None):
    """{constant: 'r,g,b'} from `private static readonly Color X = new Color(a, b, c);` (each part `N f / 255f` or `0.42f`)."""
    src = src if src is not None else _src("RustChromeColors.cs")
    out = {}
    for m in re.finditer(r"private static readonly Color (\w+)\s*=\s*new Color\(([^;]+)\);", re.sub(r"//[^\n]*", "", src)):
        vals = []
        for part in m.group(2).split(","):
            nums = [float(x) for x in re.findall(r"[0-9.]+(?=f)", part)]
            vals.append(nums[0] / nums[1] if len(nums) == 2 else nums[0])
        out[m.group(1)] = ",".join(str(int(round(v * 255))) for v in vals[:3])
    return out


def theme_static_findings(src=None, mod_src=None):
    """Pure: the six fields are all read, applied AND restored; the tab texture is applied and restored; the checkbox
    re-applies on change; the palette parses (sanity probe: six constants)."""
    src = src if src is not None else _src("RustChromeColors.cs")
    mod_src = mod_src if mod_src is not None else _src("RustChromeMod.cs")
    bad = []
    if len(palette(src)) < 6:
        bad.append("palette probe found %d constants, want >= 6 (sanity probe failed)" % len(palette(src)))
    body = re.sub(r"//[^\n]*", "", src)
    m = re.search(r"public static void Apply\(bool enabled\)\s*\{", body)
    ap = body[m.end():] if m else ""
    on, _, off = ap.partition("else")
    for _k, field, const in FIELDS:
        if 'SetColorField(typeof(Widgets), "%s", %s)' % (field, const) not in on:
            bad.append("Apply(true) no longer sets %s to %s" % (field, const))
        if 'GetColorField(typeof(Widgets), "%s")' % field not in body.split("static RustChromeColors")[1].split("Apply(enabled)")[0] + body.split("private static void CaptureVanilla")[1].split("captured = true")[0]:
            bad.append("%s is never captured before being overwritten" % field)
        if not re.search(r'RestoreColorField\("%s", vanilla\w+\)' % field, off):
            bad.append("Apply(false) no longer restores %s to the captured vanilla value" % field)
    if 'SetTexField(typeof(InspectPaneUtility), "InspectTabButtonFillTex", vanillaInspectTabTex)' not in off:
        bad.append("Apply(false) no longer restores InspectTabButtonFillTex")
    if "SolidColorMaterials.NewSolidColorTexture(WindowFill)" not in on:
        bad.append("Apply(true) no longer sets the inspect-tab fill to the window fill")
    if "RustChromeColors.Apply(themeEnabled)" not in mod_src or "themeEnabled != before" not in mod_src:
        bad.append("the Mod Settings checkbox no longer re-applies on change")
    return bad


def _theme_kv(t):
    r = t.bridge_call("jawa/static_call", type=_THEME_PROOF, method="ProofTheme", args="go")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RustChromeColors.ProofTheme answered nothing (DLL not rebuilt/deployed yet?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofTheme: %s" % text)
    return dict(re.findall(r"(\w+)=(\S+)", text)), text


@suite.chain("theme_toggle_applies_and_restores")
def theme_toggle_applies_and_restores(t):
    with t.component("static_apply_restore_symmetry", beyond_toggle=True):
        bad = theme_static_findings()
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("the_theme_actually_differs_from_vanilla", beyond_toggle=True):
        kv, text = _theme_kv(t)
        if kv:
            same = [k for k, _f, _c in FIELDS if kv.get("on_" + k) == kv.get("van_" + k)]
            if len(same) > 1:
                raise ExpectationFailed("the theme leaves %d of 6 fields identical to vanilla (%s): it recolours nothing there: %s" % (len(same), same, text[:300]))
    with t.component("theme_on_sets_the_six_fields_and_the_tab_fill_to_the_palette", beyond_toggle=True):
        kv, text = _theme_kv(t)
        if kv:
            pal = palette()
            for key, field, const in FIELDS:
                if kv.get("on_" + key) != pal[const]:
                    raise ExpectationFailed("Widgets.%s after Apply(true) = %s, palette says %s=%s: %s" % (field, kv.get("on_" + key), const, pal[const], text[:300]))
            if kv.get("tex_on") != pal["WindowFill"]:
                raise ExpectationFailed("InspectTabButtonFillTex pixel after Apply(true) = %s, want WindowFill %s" % (kv.get("tex_on"), pal["WindowFill"]))
    with t.component("themeEnabled_off_restores_the_captured_vanilla_colours_and_texture", toggle="themeEnabled"):
        kv, text = _theme_kv(t)
        if kv:
            for key, field, _c in FIELDS:
                if kv.get("off_" + key) != kv.get("van_" + key):
                    raise ExpectationFailed("Widgets.%s after Apply(false) = %s, captured vanilla was %s: %s" % (field, kv.get("off_" + key), kv.get("van_" + key), text[:300]))
            if kv.get("tex_off_is_vanilla") not in ("True", "-"):
                raise ExpectationFailed("InspectTabButtonFillTex after Apply(false) is not the vanilla texture object: %s" % text[:300])
