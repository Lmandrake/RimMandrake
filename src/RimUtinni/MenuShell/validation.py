"""validation.py -- modcheck suite for RimUtinni Menu Shell (mandrake.rut.menushell).

Pure-XML/texture mod: confirmed by directory listing -- no `Source/`, no
`Assemblies/`, no `.cs` or `.dll` anywhere under `src/RimUtinni/MenuShell/`
(`find ... -iname "*.cs" -o -iname "*.dll"` and `-type d -iname "Assemblies"`
both return nothing). Per the briefing's own rule for this shape:
`suite.toggles = []`, every component is `beyond_toggle=True`.

Read whole before writing this: `About/About.xml`, both `Defs/*.xml` files,
`Defs/UtinniShell/VBE_Backgrounds_Utinni.xml`, `RimThemes/Utinni Shell/
meta.xml`, and the walk doc.

WHAT THIS SUITE CAN ACTUALLY TEST, per the mod's own walk doc header
(`list: minimal`) and MEASURED against the real minimal list:
`infrastructure/state/modlists/ModsConfig.MINIMAL.xml` does NOT carry
`vanillaexpanded.backgrounds` (grepped directly, not assumed) -- so on the
environment `modcheck run MenuShell` actually composes (MINIMAL + this mod
only), every one of the ten `VBE.BackgroundImageDef` nodes across
`BackgroundImageDefs.xml` and `UtinniShell/VBE_Backgrounds_Utinni.xml` is
skipped by its own `MayRequire="vanillaexpanded.backgrounds"` before
DirectXmlLoader ever tries to resolve the type -- there is no C# type
`VBE.BackgroundImageDef` loaded in this game process AT ALL (VBE's own
assembly is absent, not merely its defs), so `jawa/get_defs` against that
type name in this environment is untested and its actual failure mode
(clean "not found" vs. a reflection error the bridge does not expect) is
unknown -- not attempted here rather than guessed at. This is the one
`TipSetDef`, `RUT_TipSet_Jawa`, that is pure vanilla-compatible XML with no
dependency at all, so it is the ONLY thing this suite proves live.

A REAL, WALK-DOC-IS-STALE FINDING, same family as RustChrome's: the walk doc
(`design/validation_walks/RimUtinni/MenuShell.md`, step 2 and "must be
true") says `RUT_TipSet_Jawa`'s `<tips>` list has **29** entries. Counted
directly (`grep -c '<li>' Defs/TipSetDefs.xml`, 2026-09-17): it is **30**.
Every `<li>` in that file is one tip (no other `<li>`-bearing element
exists in it), so 30 is the correct current count; this suite asserts 30,
not the walk doc's stale 29. The walk doc itself needs its own correction
pass, out of scope for this file.

Still not proven / out of this validator's floor:
  1. Both VBE-dependent walk-doc claims -- "absent VBE, all ten skip
     cleanly" and "present VBE, all ten resolve with path==iconPath" --
     have no live component here (see above). A full-list pass with
     `vanillaexpanded.backgrounds` actually active is the only way to
     prove either; out of this minimal-list smoke suite's floor.
  2. `Textures/UI/HeroArt/BGPlanet.png` (the no-VBE Core-planet-background
     override) and the `RimThemes/Utinni Shell/meta.xml` colour theme have
     no def, no debug action and no bridge tool that reads back an applied
     UI texture or Widgets colour -- genuinely untestable via the bridge,
     appearance-only, and squarely the walk doc's own `[S]` human-look step.
  3. The "no C#/Assemblies" structural claim in About.xml's own description
     is confirmed by directory listing (see above) at AUTHORING time, not
     re-proven live by this suite on every run -- a future commit adding a
     `Source/` folder would not be caught here.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("MenuShell")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

EXPECTED_TIP_COUNT = 30   # grep -c '<li>' Defs/TipSetDefs.xml, 2026-09-17 --
                          # the walk doc's own "29" is stale, see docstring
FIRST_TIP = ("Ash'karr turns but never spins - one face burns, one face "
             "freezes, and the clan lives on the line between.")


@suite.chain("tip_set_readback")
def tip_set_readback(t):
    """The one piece of this mod's content with no dependency at all:
    `RUT_TipSet_Jawa` is pure vanilla-compatible `TipSetDef` XML, read
    automatically by `GameplayTipWindow` with no registration beyond the
    def existing (per the file's own header comment). Proves the def
    loaded with its full tip list intact, not truncated by a `<li>` load
    trap (rimworld-custom-loader's own register)."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("tipset_full_and_correct", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="TipSetDef/RUT_TipSet_Jawa",
                          fields="tips")
        if t._guard():
            rows = (r or {}).get("defs") or []
            row = rows[0] if rows else None
            tips = (row or {}).get("fields", {}).get("tips")
            tips_list = tips if isinstance(tips, list) else []
            if row is None:
                raise ExpectationFailed(
                    "TipSetDef/RUT_TipSet_Jawa not found at all")
            if len(tips_list) != EXPECTED_TIP_COUNT:
                raise ExpectationFailed(
                    "RUT_TipSet_Jawa.tips has %d entries, expected %d "
                    "(counted directly from Defs/TipSetDefs.xml -- the "
                    "walk doc's own '29' is stale, see module docstring)"
                    % (len(tips_list), EXPECTED_TIP_COUNT))
            if not tips_list or tips_list[0] != FIRST_TIP:
                raise ExpectationFailed(
                    "RUT_TipSet_Jawa.tips[0] = %r, expected %r"
                    % (tips_list[0] if tips_list else None, FIRST_TIP))
        t.screenshot()
