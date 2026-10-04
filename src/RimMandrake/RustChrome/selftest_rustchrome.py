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
    print("selftest_rustchrome: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
