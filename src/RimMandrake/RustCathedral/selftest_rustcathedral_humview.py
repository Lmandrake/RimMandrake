"""selftest_rustcathedral_humview.py -- the Cathedral hum plays only over the map on screen, paused or not. L0 (static).

The hum layers are MapOnly sustainers spawned SoundInfo.OnCamera (no source map), so SoundDefHelper.CorrectContextNow
never tells the Cathedral map from another: RM_MapComponent_BiomeAttitude must end them itself when Find.CurrentMap is
another map. MapComponentTick does so, but ticks stop while the game is paused, and a PerTick sustainer only expires
when TicksGame advances (Sustainer.SustainerUpdate) -- so a map switch made while paused kept the hum playing over the
other map until unpause. MapComponentUpdate runs every frame for every map (Map.MapUpdate, 1.6), paused or not, and must
end the layers on look-away.

The check runs on the shipped source, then on copies with each break planted; every break must redden it."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "Hum", "RM_MapComponent_BiomeAttitude.cs")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _body(text, signature):
    """The brace-balanced body of the first method whose header contains `signature`, comments stripped; None if absent."""
    i = text.find(signature)
    if i < 0:
        return None
    j = text.find("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return "\n".join(line.split("//", 1)[0] for line in text[j + 1:k].splitlines())
    return None


def problems(text):
    out = []
    upd = _body(text, "override void MapComponentUpdate(")
    if upd is None:
        return ["no MapComponentUpdate: a paused map switch keeps the hum over the other map"]
    if "Find.CurrentMap != map" not in upd or "EndAllSustainers()" not in upd:
        out.append("MapComponentUpdate does not end the layers when Find.CurrentMap != map")
    tick = _body(text, "override void MapComponentTick(")
    if tick is None or "Find.CurrentMap != map" not in tick:
        out.append("MapComponentTick lost its look-away gate")
    return out


def main():
    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    shipped = problems(text)
    check("shipped hum is ended on look-away, paused or not", not shipped, "; ".join(shipped))
    breaks = [
        ("MapComponentUpdate renamed away", "override void MapComponentUpdate(", "void UnusedUpdate("),
        ("look-away end only in a comment", "\t\t\t\tEndAllSustainers();\n\t\t\t}\n\t\t}\n\n\t\tpublic override void MapComponentTick",
         "\t\t\t\t// EndAllSustainers();\n\t\t\t}\n\t\t}\n\n\t\tpublic override void MapComponentTick"),
    ]
    for name, old, new in breaks:
        check("planted break applies: " + name, old in text, "anchor text not found")
        check("break caught: " + name, bool(problems(text.replace(old, new, 1))), "check stayed clean")
    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
