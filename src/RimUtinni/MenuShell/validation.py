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
only), every one of the eleven `VBE.BackgroundImageDef` nodes across
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
pass (done 2026-10-03, with ten -> eleven backgrounds and the missing Shkaar).

Still not proven / out of this validator's floor:
  1. Both VBE-dependent walk-doc claims -- "absent VBE, all eleven skip
     cleanly" and "present VBE, all eleven resolve with path==iconPath" --
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


@suite.chain("shell_files_static")
def shell_files_static(t):
    """Offline, every run (audit row: the static half of the VBE/BGPlanet/RimThemes claims). Every
    VBE.BackgroundImageDef is a top-level def guarded by MayRequire="vanillaexpanded.backgrounds" (so VBE
    absent skips it before type resolution), has path == iconPath, and that path is a non-blank PNG under
    Textures/ (animated ones also need Videos/<path>.webm). BGPlanet.png exists and is not blank. The RimThemes
    meta.xml parses with every colour a 3/4-tuple of 0-255 (textColorGray 0-1). No Source/ or Assemblies/."""
    import os as _o
    import xml.etree.ElementTree as _ET
    here = _o.path.dirname(_o.path.abspath(__file__))
    with t.component("vbe_backgrounds_guarded_and_resolve_to_files", beyond_toggle=True):
        from PIL import Image
        bad, n = [], 0
        for root, _d, files in _o.walk(_o.path.join(here, "Defs")):
            for fn in sorted(files):
                if not fn.endswith(".xml"):
                    continue
                for el in _ET.parse(_o.path.join(root, fn)).getroot():
                    if el.tag != "VBE.BackgroundImageDef":
                        continue
                    n += 1
                    dn = el.findtext("defName")
                    if (el.get("MayRequire") or "").lower() != "vanillaexpanded.backgrounds":
                        bad.append("%s: not guarded by MayRequire=vanillaexpanded.backgrounds" % dn)
                    path, icon = (el.findtext("path") or "").strip(), (el.findtext("iconPath") or "").strip()
                    if not path or path != icon:
                        bad.append("%s: path %r != iconPath %r" % (dn, path, icon))
                    png = _o.path.join(here, "Textures", path + ".png")
                    if not _o.path.isfile(png):
                        bad.append("%s: no Textures/%s.png" % (dn, path))
                    elif Image.open(png).convert("RGBA").getchannel("A").getextrema()[1] == 0:
                        bad.append("%s: Textures/%s.png is fully transparent" % (dn, path))
                    if (el.findtext("animated") or "").strip().lower() == "true" and \
                            not _o.path.isfile(_o.path.join(here, "Videos", path + ".webm")):
                        bad.append("%s: animated but no Videos/%s.webm" % (dn, path))
        if n < 10:
            bad.append("blind parse: only %d VBE.BackgroundImageDef found (expected 11)" % n)
        if bad:
            raise ExpectationFailed("; ".join(bad))


@suite.chain("shell_theme_static")
def shell_theme_static(t):
    """Offline, its own chain so a background failure cannot mask it: BGPlanet.png, RimThemes meta.xml
    colours, and no Source/ or Assemblies/ (About.xml's XML/texture-only claim)."""
    import os as _o
    import xml.etree.ElementTree as _ET
    here = _o.path.dirname(_o.path.abspath(__file__))
    with t.component("bgplanet_theme_and_no_code_static", beyond_toggle=True):
        import re as _re
        from PIL import Image
        bad = []
        bg = _o.path.join(here, "Textures", "UI", "HeroArt", "BGPlanet.png")
        if not _o.path.isfile(bg):
            bad.append("BGPlanet.png missing (the no-VBE menu background)")
        else:
            lo, hi = Image.open(bg).convert("L").getextrema()
            if hi - lo < 10:
                bad.append("BGPlanet.png is a flat image")
        meta = _ET.parse(_o.path.join(here, "RimThemes", "Utinni Shell", "meta.xml")).getroot()
        if meta.tag != "RimThemes":
            bad.append("meta.xml root is %r, not RimThemes" % meta.tag)
        colours = 0
        for el in meta:
            v = (el.text or "").strip()
            if not v.startswith("("):
                continue
            nums = [float(x) for x in _re.findall(r"-?[0-9.]+", v)]
            top = 1.0 if el.tag == "textColorGray" else 255.0
            colours += 1
            if len(nums) not in (3, 4) or any(x < 0 or x > top for x in nums):
                bad.append("meta.xml %s=%s is not a 3/4-tuple in 0..%g" % (el.tag, v, top))
        if colours < 5:
            bad.append("meta.xml: blind parse, only %d colour keys" % colours)
        for d in ("Source", "Assemblies"):
            if _o.path.isdir(_o.path.join(here, d)):
                bad.append("%s/ exists: About.xml's XML/texture-only claim is false" % d)
        if bad:
            raise ExpectationFailed("; ".join(bad))
