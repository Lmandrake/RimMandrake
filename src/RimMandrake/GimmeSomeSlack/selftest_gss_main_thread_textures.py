#!/usr/bin/env python3
"""T_MAIN_THREAD_TEXTURES_OFFLINE (supports bar pole_buttons_show_icons; RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD, his walk of
2026-11-20 row 9): a source census of Source/ (SelfTest/ excluded) for a texture, material or graphic fetched in a STATIC FIELD
INITIALIZER, or in a static constructor of a class without [StaticConstructorOnStartup].

Why: a static field initializer runs when the CLR first initialises its type, which Harmony patching or the mod constructor can
cause on the loading thread. There ContentFinder answers null and logs "Tried to get a resource ... from a different thread"; the
pole's Link wire / Unlink wire / Unlink all buttons then drew the missing-texture square (the walk's Player.log, lines 518-519).
A fetch in a getter (`x ??= ContentFinder...`), a method, or the static constructor of a [StaticConstructorOnStartup] class runs
on the main thread and is not refused.

The range read: every .cs under Source/ outside SelfTest/, every static field initializer (to its `;`, over lines) and every
static constructor body. Loaders: ContentFinder<..>.Get, MaterialPool.MatFrom, GraphicDatabase.Get, SolidColorMaterials.*,
SafeTex.Get, Resources.Load, TexButton.*. Left out: a loader reached through a helper method called from an initializer (the
live row sc_pole_icons_loaded reads Player.log for that). --plant (also run on every normal run): the pre-fix icon fields, and a
loader in the static constructor of an unmarked class, must each be refused. Exit 0 PASS, 1 FAIL.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_main_thread_textures.py
"""
import glob
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
LOADER = re.compile(r"\b(ContentFinder\s*<[^>]+>\s*\.\s*Get|MaterialPool\s*\.\s*MatFrom|GraphicDatabase\s*\.\s*Get|"
                    r"SolidColorMaterials\s*\.|SafeTex\s*\.\s*Get|Resources\s*\.\s*Load|TexButton\s*\.)")
# a static field with an initializer: modifiers, a type, a name, '=' (not '=>'), up to the ending ';'
FIELD = re.compile(r"(?:^|(?<=[{;}]))[ \t]*(?:\[[^\]]*\]\s*)*(?:(?:public|private|internal|protected|readonly|static|new)\s+)*static\s+"
                   r"(?:(?:readonly)\s+)?[\w<>\[\],. ?]+?\s+(\w+)\s*=(?!>)([^;]*);", re.M | re.S)
CLASS = re.compile(r"((?:\[[^\]]*\]\s*)*)(?:(?:public|private|internal|protected|sealed|static|abstract|partial)\s+)*class\s+(\w+)", re.S)


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def census(text, name):
    """Refusals in one file's text: (name, line, what)."""
    t = strip_comments(text)
    out = []
    for m in FIELD.finditer(t):
        if LOADER.search(m.group(2)):
            out.append((name, t.count("\n", 0, m.start()) + 1, "static field %s fetches a texture in its initializer" % m.group(1)))
    for c in CLASS.finditer(t):
        marked = "StaticConstructorOnStartup" in c.group(1)
        cn = c.group(2)
        for k in re.finditer(r"\bstatic\s+%s\s*\(\s*\)\s*\{" % re.escape(cn), t):
            depth, i = 1, k.end()
            while depth and i < len(t):
                depth += {"{": 1, "}": -1}.get(t[i], 0)
                i += 1
            if not marked and LOADER.search(t[k.end():i]):
                out.append((name, t.count("\n", 0, k.start()) + 1, "static constructor of %s (no [StaticConstructorOnStartup]) fetches a texture" % cn))
    return out


PLANTS = {
    "pre-fix icon fields": 'namespace X { [StaticConstructorOnStartup] public class CompAerialAnchor : ThingComp {\n'
                           '  private static readonly Texture2D IconLink = ContentFinder<Texture2D>.Get("UI/Commands/TryReconnect", false);\n} }',
    "loader in an unmarked static ctor": 'class Holder { static Material M; static Holder() { M = MaterialPool.MatFrom("a/b"); } }',
    "initializer over two lines": 'class H { private static readonly Material Wire =\n    MaterialPool.MatFrom("x", ShaderDatabase.Transparent); }',
}
KEEPS = {
    "lazy getter": 'class C { private static Texture2D i; private static Texture2D I => i ??= ContentFinder<Texture2D>.Get("a", false); }',
    "marked static ctor": '[StaticConstructorOnStartup] class C { static Material M; static C() { M = MaterialPool.MatFrom("a"); } }',
    "comment": 'class C { // private static readonly Texture2D I = ContentFinder<Texture2D>.Get("a");\n }',
}


def main():
    ok = True
    for nm, src in PLANTS.items():
        r = census(src, nm)
        print("%s plant %-36s refused %d" % ("PASS" if r else "FAIL", nm, len(r)))
        ok &= bool(r)
    for nm, src in KEEPS.items():
        r = census(src, nm)
        print("%s keep  %-36s refused %d" % ("PASS" if not r else "FAIL", nm, len(r)))
        ok &= not r
    files = [f for f in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True))
             if os.sep + "SelfTest" + os.sep not in f and os.sep + "obj" + os.sep not in f and os.sep + "bin" + os.sep not in f]
    refused, fields = [], 0
    for f in files:
        txt = open(f, encoding="utf-8-sig").read()
        fields += len(FIELD.findall(strip_comments(txt)))
        refused += census(txt, os.path.relpath(f, SRC))
    for r in refused:
        print("REFUSED %s:%d %s" % r)
    if not files or not fields:
        print("FAIL could not look: %d files, %d static initializers read" % (len(files), fields))
        return 1
    print("main-thread textures: %d files, %d static field initializers read; refused %d (limit 0)" % (len(files), fields, len(refused)))
    ok &= not refused
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
