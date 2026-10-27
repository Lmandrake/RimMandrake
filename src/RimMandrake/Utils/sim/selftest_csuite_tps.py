#!/usr/bin/env python3
"""Selftest for csuite_tps.py's scene key (TPS_SCENE_KEY_ENFORCE_LIKE_FOR_LIKE): every reading carries its scene
(save, map count, map sizes/biomes, pawn count, mod-list hash), readings of unlike scenes are never pooled, and
--compare refuses them with "NOT COMPARABLE: <diff>". Synthetic records in the sampler's own row shapes (session,
game, context, sample, menu - as JawaBenchTpsSampler.cs writes them); no game, no real record read."""
import io, json, os, sys, tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import csuite_tps as C  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        FAILS.append(name)


def session_rows(sess, digest, mods=300):
    return [{"seq": 1, "session": sess, "kind": "session", "mods": mods, "modDigest": digest}]


def game(sess, seq, save=""):
    return {"seq": seq, "session": sess, "kind": "game", "game": 1, "save": save, "maps": 1}


def ctx(sess, seq, save, maps):
    return {"seq": seq, "session": sess, "kind": "context", "save": save, "mapCount": len(maps),
            "maps": [{"id": i, "size": s, "biome": b, "pawns": p, "current": i == 0} for i, (s, b, p) in enumerate(maps)]}


def sample(sess, seq, tps, utc="2026-10-26T10:00:00.000Z"):
    return {"seq": seq, "session": sess, "kind": "sample", "utc": utc, "tps": tps, "dTicks": 300, "ratio": tps / 360.0,
            "mult": 6, "fps": 60.0, "heapMB": 3000.0}


def write(d, name, rows):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


ONE = [("250x250", "AridShrubland", 10)]
TWO = [("250x250", "RUT_TheRot", 8), ("325x325", "RUT_TheRot", 0)]


def main():
    with tempfile.TemporaryDirectory() as d:
        # session A: one-map scene; first sample precedes the game's first context (look-ahead)
        a = session_rows("aaaa1111", "0aa9a9ae") + [game("aaaa1111", 2, "calm"), sample("aaaa1111", 3, 355.0),
             ctx("aaaa1111", 4, "calm", ONE), sample("aaaa1111", 5, 354.0), sample("aaaa1111", 6, 356.0)]
        # session B: same scene, same mods -> comparable
        b = session_rows("bbbb2222", "0aa9a9ae") + [game("bbbb2222", 2, "calm"), ctx("bbbb2222", 3, "calm", ONE),
             sample("bbbb2222", 4, 354.0), sample("bbbb2222", 5, 353.0)]
        # session P: the 2-map PerfSite scene the bisect caught pooled with 1-map runs
        p = session_rows("pppp3333", "0aa9a9ae") + [game("pppp3333", 2, "leaf"), ctx("pppp3333", 3, "leaf", TWO),
             sample("pppp3333", 4, 141.0)]
        # session M: same scene as A, other mod list
        m = session_rows("mmmm4444", "53310528", mods=14) + [game("mmmm4444", 2, "calm"), ctx("mmmm4444", 3, "calm", ONE),
             sample("mmmm4444", 4, 400.0)]
        # session G: a game that never wrote a context row, then a second game whose context must not leak backwards
        g = session_rows("gggg5555", "0aa9a9ae") + [game("gggg5555", 2, "calm"), sample("gggg5555", 3, 350.0),
             game("gggg5555", 4, "calm"), ctx("gggg5555", 5, "calm", ONE), sample("gggg5555", 6, 351.0)]
        for n, rows in (("a", a), ("b", b), ("p", p), ("m", m), ("g", g)):
            write(d, "tps_2026_%s_000.jsonl" % n, rows)
        rs = C.readings(C.read_rows(d))
        by = {}
        for r in rs:
            by.setdefault(r["session"], []).append(r)

        check("every reading carries a scene key field", all("scene" in r for r in rs))
        ka = by["aaaa1111"][0]["scene"]
        check("a scene key holds save, map count, sizes/biomes, pawns, mod hash",
              ka == {"save": "calm", "mapCount": 1, "maps": "250x250:AridShrubland", "pawns": 10, "mods": "0aa9a9ae"}, ka)
        check("the first window of a game takes the game's first context (look-ahead)",
              by["aaaa1111"][0]["scene"] == by["aaaa1111"][1]["scene"])
        check("a game with no context row has no scene", by["gggg5555"][0]["scene"] is None)
        check("a later game's context never keys an earlier game's readings",
              by["gggg5555"][0]["scene"] is None and by["gggg5555"][1]["scene"] == ka)
        check("map order is no scene difference", C.scene_key({}, ctx("x", 1, "s", TWO))["maps"]
              == C.scene_key({}, ctx("x", 1, "s", list(reversed(TWO))))["maps"])

        check("same scene: comparable", C.comparable(ka, by["bbbb2222"][0]["scene"]) is None)
        r2 = C.comparable(ka, by["pppp3333"][0]["scene"])
        check("2-map vs 1-map: NOT COMPARABLE naming map count, maps, pawns and save",
              r2 is not None and r2.startswith("NOT COMPARABLE: ") and all(f in r2 for f in ("mapCount: 1 != 2", "maps:", "pawns: 10 != 8", "save: calm != leaf"))
              and "mods:" not in r2, r2)
        r3 = C.comparable(ka, by["mmmm4444"][0]["scene"])
        check("other mod list: NOT COMPARABLE on mods only", r3 == "NOT COMPARABLE: mods: 0aa9a9ae != 53310528", r3)
        check("an unknown scene is like nothing, itself included", C.comparable(None, None) is not None and C.comparable(None, ka) is not None)
        check("one pawn more is a different scene", C.comparable(ka, dict(ka, pawns=11)) == "NOT COMPARABLE: pawns: 10 != 11")

        def run_compare(x, y):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = C.main(["--dir", d, "--compare", x, y])
            return code, buf.getvalue()

        code, txt = run_compare("aaaa", "bbbb")
        check("--compare like scenes: exit 0 with medians and delta", code == 0 and "medTPS=355.0" in txt and "delta=" in txt, (code, txt))
        code, txt = run_compare("aaaa", "pppp")
        check("--compare unlike scenes: exit 2, prints NOT COMPARABLE: <diff>, no delta",
              code == 2 and txt.startswith("NOT COMPARABLE: ") and "mapCount: 1 != 2" in txt and "delta" not in txt, (code, txt))
        code, txt = run_compare("2026-10-26", "bbbb")
        check("--compare refuses a side that pools several scenes", code == 2 and "NOT COMPARABLE: 2026-10-26 spans" in txt, (code, txt))
        code, txt = run_compare("zzzz", "bbbb")
        check("--compare with no readings says so (exit 1)", code == 1 and "NO READINGS" in txt, (code, txt))

        buf = io.StringIO()
        with redirect_stdout(buf):
            C.main(["--dir", d])
        lines = [ln for ln in buf.getvalue().splitlines()[1:] if ln.strip()]
        check("the census never pools unlike scenes: one row per scene, scene printed",
              len(lines) == 4 and sum("maps=2[" in ln for ln in lines) == 1 and sum("(no scene)" in ln for ln in lines) == 1, lines)
        calm = [ln for ln in lines if "save=calm maps=1" in ln and "mods=0aa9a9ae" in ln]
        check("like scenes across sessions pool into one row (A+B+G's second game: 6 readings)",
              len(calm) == 1 and calm[0].split()[3] == "6", calm)

    print("\n%d failed" % len(FAILS) if FAILS else "\nall passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
