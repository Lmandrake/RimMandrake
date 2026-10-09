#!/usr/bin/env python3
"""Planted-defect selftest for lint_rustchrome_defs.py: clean on the real mod, then one planted defect at a time is caught.

    python3 src/RimMandrake/Utils/selftest_rustchrome_lint.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack_lint_harness as H  # noqa: E402

C = "Source/RustChromeColors.cs"
M = "Source/RustChromeMod.cs"
PLANTS = [
    ("settings key differs from field", M, 'Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);', 'Scribe_Values.Look(ref themeEnabled, "theme", true);', "settings-scribed"),
    ("settings default differs from initialiser", M, 'Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);', 'Scribe_Values.Look(ref themeEnabled, "themeEnabled", false);', "settings-scribed"),
    ("setting Scribed twice", M, 'Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);', 'Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);\n            Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);', "settings-scribed"),
    ("a source file missing from the csproj", "Source/RustChrome.csproj", '    <Compile Include="RustChromeMod.cs" />\n', "", "compile-listed"),
    ("a field overwritten but never restored", C, 'RestoreColorField("MenuSectionBGFillColor", vanillaSectionFill);', "", "rustchrome-recolour"),
    ("a field overwritten but never captured", C, 'vanillaSectionBorder = GetColorField(typeof(Widgets), "MenuSectionBGBorderColor");', "", "rustchrome-recolour"),
    ("tab texture cache dropped", C, "themedInspectTabTex ?? (themedInspectTabTex = SolidColorMaterials.NewSolidColorTexture(WindowFill))", "SolidColorMaterials.NewSolidColorTexture(WindowFill)", "rustchrome-recolour"),
]

if __name__ == "__main__":
    sys.exit(H.run("RustChrome", "lint_rustchrome_defs.py", PLANTS, keep=("Textures",)))
