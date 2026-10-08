"""selftest_rustchrome.py -- override_texture_problems is clean on the shipped Textures/ and reddens on each
break it exists to catch (planted in a temp copy, never the shipped files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    from PIL import Image
    spec = importlib.util.spec_from_file_location("rc_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    shipped = v.override_texture_problems()
    check("shipped: 14 overrides clean", shipped == [], shipped)
    check("table covers 14 paths", len(v.VANILLA_UI_SIZES) == 14, len(v.VANILLA_UI_SIZES))
    tmp = tempfile.mkdtemp()
    try:
        root = os.path.join(tmp, "Textures")
        shutil.copytree(os.path.join(HERE, "Textures"), root)
        w = os.path.join(root, "UI", "Widgets")
        os.remove(os.path.join(w, "CheckOn.png"))
        Image.new("RGBA", (64, 64), (0, 0, 0, 0)).save(os.path.join(w, "CheckOff.png"))
        Image.new("RGBA", (64, 64), (9, 9, 9, 255)).save(os.path.join(w, "TabAtlas.png"))
        Image.new("RGBA", (64, 32), (9, 9, 9, 255)).save(os.path.join(w, "ButtonBG.png"))
        Image.new("RGBA", (8, 8), (9, 9, 9, 255)).save(os.path.join(w, "Stray.png"))
        got = dict(v.override_texture_problems(root))
        check("break: missing override", got.get("UI/Widgets/CheckOn") == "missing", got)
        check("break: blank override", got.get("UI/Widgets/CheckOff") == "fully transparent", got)
        check("break: atlas resized", "atlas" in got.get("UI/Widgets/TabAtlas", ""), got)
        check("break: plain bg wrong aspect", "aspect" in got.get("UI/Widgets/ButtonBG", ""), got)
        check("break: stray png", "stray" in got.get("UI/Widgets/Stray.png", ""), got)
        check("no false reds on untouched files", len(got) == 5, got)
    finally:
        shutil.rmtree(tmp)
    check("theme_static_findings clean on the shipped source", v.theme_static_findings() == [], v.theme_static_findings())
    check("palette parsed: window fill 18,16,22 and selected option 107,82,41", v.palette().get("WindowFill") == "18,16,22" and v.palette().get("OptionSelectedFill") == "107,82,41", v.palette())
    src = open(os.path.join(HERE, "Source", "RustChromeColors.cs"), encoding="utf-8").read()
    modsrc = open(os.path.join(HERE, "Source", "RustChromeMod.cs"), encoding="utf-8").read()
    for tag, old, new in (
            ("restore of one field dropped", 'RestoreColorField("MenuSectionBGFillColor", vanillaSectionFill);', ""),
            ("restore wrong value", 'RestoreColorField("WindowBGFillColor", vanillaWindowFill);', 'SetColorField(typeof(Widgets), "WindowBGFillColor", WindowFill);'),
            ("tab texture restore dropped", 'SetTexField(typeof(InspectPaneUtility), "InspectTabButtonFillTex", vanillaInspectTabTex);', ""),
            ("theme field not applied", 'SetColorField(typeof(Widgets), "OptionSelectedBGFillColor", OptionSelectedFill);', ""),
            ("vanilla never captured", 'vanillaSectionBorder = GetColorField(typeof(Widgets), "MenuSectionBGBorderColor");', "")):
        check("source break (%s) is findable" % tag, old in src, old)
        got = v.theme_static_findings(src.replace(old, ""if not new else new), modsrc)
        check("source break %-30s reddens theme_static_findings" % tag, bool(got), got)
    check("checkbox no longer re-applying reddens", bool(v.theme_static_findings(src, modsrc.replace("RustChromeColors.Apply(themeEnabled);", ""))))
    # mock proof: clean passes, each break reddens (own Suite: the legacy chains screenshot the real desktop)
    import runner
    from modcheck import Suite
    from northstar_driver.session import FastSession
    from northstar_driver.transport import MockGame, MockTransport
    pal = v.palette()
    van = dict(wfill="10,10,10", wborder="40,40,40", sfill="12,12,12", sborder="50,50,50", ounsel="20,20,20", osel="60,60,60")

    def text(brk):
        d = {"setting": "True"}
        for k in van:
            d["van_" + k] = van[k]
        for k, _f, c in v.FIELDS:
            d["on_" + k] = van[k] if "theme_noop" in brk else pal[c]
            d["off_" + k] = pal[c] if "off_keeps_theme" in brk else van[k]
        d["tex_on"] = pal["WindowFill"]
        d["tex_off_is_vanilla"] = "False" if "tex_not_restored" in brk else "True"
        if "wrong_palette" in brk:
            d["on_wborder"] = "1,2,3"
        if "off_one_field" in brk:
            d["off_sborder"] = pal["SectionBorder"]
        return " ".join("%s=%s" % kv for kv in d.items())

    def run(brk=(), stale=False):
        suite = Suite("RustChromeTheme")
        suite.chain("theme_toggle_applies_and_restores")(v.theme_toggle_applies_and_restores)
        game = MockGame()
        game.ext = lambda g, tool, p: (None if tool != "jawa/static_call" else
                                       ({"success": False, "message": "no method"} if stale else {"success": True, "result": text(set(brk))}))
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])

    got = run()
    check("mock clean: all 4 theme bars PASS", set(got.values()) == {"PASS"} and len(got) == 4, got)
    check("mock stale DLL: proof bars UNMEASURED, never PASS", run(stale=True)["themeEnabled_off_restores_the_captured_vanilla_colours_and_texture"] == "UNMEASURED")
    for brk, comp in (("wrong_palette", "theme_on_sets_the_six_fields_and_the_tab_fill_to_the_palette"),
                      ("off_keeps_theme", "themeEnabled_off_restores_the_captured_vanilla_colours_and_texture"),
                      ("off_one_field", "themeEnabled_off_restores_the_captured_vanilla_colours_and_texture"),
                      ("tex_not_restored", "themeEnabled_off_restores_the_captured_vanilla_colours_and_texture"),
                      ("theme_noop", "the_theme_actually_differs_from_vanilla")):
        check("mock break %-16s reddens %s" % (brk, comp), run((brk,)).get(comp) == "FAIL", run((brk,)))
    print("selftest_rustchrome: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
