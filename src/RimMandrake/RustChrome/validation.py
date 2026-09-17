"""validation.py -- modcheck suite for RimMandrake RustChrome (mandrake.rm.rustchrome).

Grounded in this mod's actual Source (`RustChromeColors.cs`, `RustChromeMod.cs`),
read whole before writing this -- never the walk doc's own quoted strings, which
turned out to be STALE against the code actually on disk (see the note below).

WHAT THIS MOD ACTUALLY IS AT RUNTIME: Tier 1 is 14 loose PNG overrides at vanilla
UI texture paths (zero code, nothing this suite can check live -- a disk-existence
check belongs in `validate_patch.py`/deploy tooling, not a bridge session). Tier 2
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
