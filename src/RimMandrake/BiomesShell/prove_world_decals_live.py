#!/usr/bin/env python3
"""Live, read-only proof of the biome decals (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, clause A1); the judge reads the
decal MATERIAL colour back, not only the remembered fade value.

Needs: RimMandrake.Biomes (BiomesShell + BlueDesert members) deployed at the proof sha, a world loaded (Playing) with
the world view shown, the bridge up with jawa/static_call. Reads only (RM_WorldDecals.Probe and .Info, both reviewed
READ_ONLY_STATIC_CALLS). PASS when:
  1. the shipped test atlas is found and read as the contract says (RM_BlueDesert 512x512, grid=2);
  2. the planet was built with decals on ("decals: N glyphs on M flat tiles ..."; N may be 0: a biome of ours on 0
     tiles is expected, owner 2026-09-20) and enabled=True;
  3. the fade alpha in force (alpha=) equals the C# rule for the camera altitude in force (full <= decalFullAlt, gone
     >= decalGoneAlt, smoothstep between); alpha -1 with glyphs built is a dead fade (FAIL); alpha -1 after a build
     that met land biomes but drew none is UNMEASURED (show the world view), never PASS;
  4. Info reports matAlpha= , the colour alpha of a live decal material (-1 when no decal material exists), and when a
     biome with an atlas is on the planet that alpha equals the rule too: the per-frame fade reaches the material the
     glyphs draw with. An Info without matAlpha FAILS: the material fade is then invisible to the live game proof.
     With no biome with an atlas on the planet there is no decal material to read: UNMEASURED, never PASS.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (no bridge / no world / nothing to read).

Today no biome with an atlas is painted on any planet (a biome of ours on 0 tiles is expected until the end paint), so
the read-only run can only read UNMEASURED. --stage makes A1 decidable on a disposable world: it paints STAGE_TILES flat
land tiles RM_BlueDesert, regenerates the planet (jawa/world_commit, which rebuilds the decals), shows the world view at a
close and a far altitude, judges Info at each (glyphs must now be > 0), then puts every tile back (the record says whether every restoring write answered) and returns to the map. A PASS
needs one reading at or below decalFullAlt and one at or above decalGoneAlt, as the camera reports them.
It writes the world, so run it holding the game: `game_lock.py run <game> --for "..." -- python3 <this> --stage`. The
companion refuses world writes on a canonical save; that reads UNMEASURED. Each staged run that reaches its readings writes its verdict to RESULT; a run stopped before them (no tiles,
a refused write) writes nothing, so an earlier verdict on the same bytes stands.
--verdict (offline, for the ticket's outcome check) exits 0 when RESULT holds a staged PASS made on the current bytes of
RM_WorldDecals.cs, else 1.

    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py            # live, read-only
    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py --stage    # live, staged (writes and restores tiles)
    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py --verdict  # offline: is there a staged PASS on these bytes
    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py --selftest # the judge on recorded Info strings, offline
"""
import datetime, json, os, re, subprocess, sys, time

T = "RimMandrake.Biomes.RM_WorldDecals"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "Source", "RM_WorldDecals.cs")
RESULT = os.path.join(REPO, "infrastructure", "state", "live_proofs", "WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE.result.json")
STAGE_BIOME = "RM_BlueDesert"
STAGE_TILES = 6
STAGE_ALTS = (300.0, 900.0)   # close (full, <= decalFullAlt 380) and far (gone, >= decalGoneAlt 620)
SCAN = 2000                   # tiles read to find flat dry land; the low ids of any planet hold some
PROBE_OK = "atlas RM_BlueDesert 512x512 grid=2"
BUILT = re.compile(r"decals: (\d+) glyphs on (\d+) flat tiles of (\d+) biomes with an atlas \((\d+) land biomes without one\)")


def fade(alt, full, gone):
    """Mirror of RM_WorldDecals.FadeAlpha (the selftest pins the C# against this rule)."""
    if gone <= full:
        return 1.0 if alt <= full else 0.0
    t = min(1.0, max(0.0, (alt - full) / (gone - full)))
    return 1.0 - t * t * (3 - 2 * t)


def num(info, key):
    m = re.search(r"(?:^|[\s|])" + key + r"=(-?[\d.]+(?:[Ee][+-]?\d+)?)", info)
    return None if m is None else float(m.group(1))


def judge(probe, info, staged=False):
    """-> (exit code, verdict line) for one Probe result and one Info result (both the raw bridge JSON or string).
    staged: the run painted atlas tiles, so a build with 0 glyphs or no atlas biome is a FAIL, not UNMEASURED."""
    errs, unmeasured = [], []
    if PROBE_OK not in probe:
        errs.append("test atlas not found or not read as a 2x2 atlas (probe: %s)" % probe[:120])
    m = BUILT.search(info)
    if not m:
        errs.append("planet not built with decals (lastInfo: %s)" % info[:120])
    elif staged and (int(m.group(1)) == 0 or int(m.group(3)) == 0):
        errs.append("tiles were painted %s but the build drew %s glyphs from %s biomes with an atlas"
                    % (STAGE_BIOME, m.group(1), m.group(3)))
    if "enabled=True" not in info:
        errs.append("setting Planet: biome decals is off")
    alt, alpha, full, gone = (num(info, k) for k in ("altitude", "alpha", "fullAlt", "goneAlt"))
    mat = num(info, "matAlpha")
    if None in (alt, alpha, full, gone):
        errs.append("Info lacks altitude/alpha/fullAlt/goneAlt")
    else:
        rule = fade(alt, full, gone)
        glyphs = int(m.group(1)) if m else 0
        atlased = int(m.group(3)) if m else 0
        met = atlased + int(m.group(4)) if m else 0
        if alpha < 0 and glyphs > 0:
            errs.append("glyphs built but the fade never ran (alpha -1)")
        elif alpha < 0 and met > 0:
            unmeasured.append("fade has not run since the build (alpha -1 with %d biomes met); show the world view" % met)
        elif alpha >= 0 and abs(alpha - rule) > 0.01:
            errs.append("alpha %.3f at altitude %.0f, the rule says %.3f (fade not running)" % (alpha, alt, rule))
        if mat is None:
            errs.append("Info does not report matAlpha (the decal material colour alpha): the per-frame material fade "
                        "is invisible to the live proof")
        elif atlased > 0 or glyphs > 0:
            if mat < 0:
                errs.append("a biome with an atlas is on the planet but no decal material reports a colour (matAlpha -1)")
            elif alpha >= 0 and abs(mat - rule) > 0.01:
                errs.append("material colour alpha %.3f at altitude %.0f, the rule says %.3f (the fade does not reach "
                            "the material)" % (mat, alt, rule))
        elif m:
            unmeasured.append("no biome with an atlas on this planet, so no decal material to read")
    if errs:
        return 1, "FAIL: " + "; ".join(errs)
    if unmeasured:
        return 2, "UNMEASURED: " + "; ".join(unmeasured)
    return 0, "PASS"


def live():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    from live_def_check import _bridge

    def call(method, args):
        r, why = _bridge("jawa/static_call", {"type": T, "method": method, "args": args}, 60, read_only_static=True)
        return None if r is None else json.dumps(r), why

    probe, why = call("Probe", "RM_BlueDesert")
    if probe is None:
        print("UNMEASURED: " + why); return 2
    info, why = call("Info", "")
    if info is None:
        print("UNMEASURED: " + why); return 2
    print("probe:", probe[:200])
    print("info:", info[:500])
    code, line = judge(probe, info)
    print(line)
    return code


# ---------------------------------------------------------------- offline: the judge on recorded strings
P = "atlas RM_BlueDesert 512x512 grid=2"
TAIL = " | size=0.3 spread=0.22 lift=0.0045 queue=3507 fullAlt=380 goneAlt=620 flipX=False"


def _info(built, alpha, alt, mat=None, enabled=True):
    s = built + " | enabled=%s alpha=%s altitude=%s atlases=1" % (enabled, alpha, alt)
    return s + TAIL + ("" if mat is None else " matAlpha=%s" % mat)


B1 = "decals: 120 glyphs on 48 flat tiles of 1 biomes with an atlas (13 land biomes without one), 4 ms"
B0 = "decals: 0 glyphs on 0 flat tiles of 0 biomes with an atlas (14 land biomes without one), 3 ms"
CASES = [   # (name, probe, info, wanted exit)
    ("close zoom, material at full", P, _info(B1, 1, 300, 1), 0),
    ("far zoom, material gone", P, _info(B1, 0, 900, 0), 0),
    ("mid zoom, material on the smoothstep", P, _info(B1, round(fade(500, 380, 620), 4), 500, round(fade(500, 380, 620), 4)), 0),
    # the checker's gaps, as Info would read under each mutant
    ("current Info: no matAlpha", P, _info(B1, 1, 300), 1),
    ("colour ignores fade (alpha 1f into the material)", P, _info(B1, 0, 900, 1), 1),
    ("fade forgotten on the material", P, _info(B1, 0.5, 500, 1), 1),
    ("material never made though an atlas biome is on the planet", P, _info(B1, 1, 300, -1), 1),
    ("fade guard always true (glyphs, alpha -1)", P, _info(B1, -1, 300, 1), 1),
    ("fade not from altitude", P, _info(B1, 1, 900, 1), 1),
    ("never built", P, _info("never built", -1, 0, -1), 1),
    ("decals off", P, _info(B1, 1, 300, 1, enabled=False), 1),
    ("atlas missing", "atlas RM_BlueDesert none", _info(B1, 1, 300, 1), 1),
    ("atlas misread", "atlas RM_BlueDesert 512x512 grid=4", _info(B1, 1, 300, 1), 1),
    # what cannot be read is never a PASS
    ("0 glyphs, no atlas biome on the planet (expected today)", P, _info(B0, 1, 300, -1), 2),
    ("0 glyphs, fade not yet run (map view)", P, _info(B0, -1, 0, -1), 2),
]


def selftest():
    bad = 0
    for name, probe, info, want in CASES:
        got, line = judge(json.dumps({"result": probe}), json.dumps({"result": info}))
        ok = got == want
        bad += not ok
        print(("ok  " if ok else "FAIL") + " %-62s exit %d (want %d)  %s" % (name, got, want, line[:110]))
    # the C# must give the judge something to read: Info() emits matAlpha= from a decal material's colour
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", "RM_WorldDecals.cs"), encoding="utf-8").read()
    body = re.search(r"public static string Info\(\)\s*\{(.*?)\n        \}", src, re.S)
    emits = bool(body) and '" matAlpha="' in body.group(1) and ".color.a" in body.group(1)
    bad += not emits
    print(("ok  " if emits else "FAIL") + " RM_WorldDecals.Info() emits matAlpha= read from a decal material's color.a"
          + ("" if emits else ": it does not, so the live A1 judge FAILs on today's build"))
    # staged runs painted an atlas biome: nothing drawn is a FAIL there, never UNMEASURED
    for name, info, want in (("staged, drawn, close", _info(B1, 1, 300, 1), 0),
                             ("staged, drawn, far", _info(B1, 0, 900, 0), 0),
                             ("staged, painted but 0 glyphs", _info(B0, 1, 300, -1), 1),
                             ("staged, fade dead", _info(B1, -1, 300, 1), 1)):
        got, line = judge(json.dumps({"result": P}), json.dumps({"result": info}), staged=True)
        bad += got != want
        print(("ok  " if got == want else "FAIL") + " %-62s exit %d (want %d)  %s" % (name, got, want, line[:110]))
    rows = [{"tile": 0, "biome": "Ocean", "hilliness": "Flat", "waterCovered": True},
            {"tile": 1, "biome": "Desert", "hilliness": "SmallHills", "waterCovered": False},
            {"tile": 2, "biome": "Desert", "hilliness": "Flat", "waterCovered": False},
            {"tile": 3, "biome": None, "hilliness": "Flat", "waterCovered": False},
            {"tile": 4, "biome": "TemperateForest", "hilliness": "Flat", "waterCovered": False}]
    for name, got, want in (("pick: flat dry land only", pick_tiles(rows, 6), [2, 4]),
                            ("pick: capped at n", pick_tiles(rows, 1), [2]),
                            ("pick: none on an all-water strip", pick_tiles(rows[:1], 6), []),
                            ("restore: one write per original value",
                             restore_groups([rows[2], rows[4], dict(rows[2], tile=9)]),
                             {("Desert", "Flat"): [2, 9], ("TemperateForest", "Flat"): [4]})):
        bad += got != want
        print(("ok  " if got == want else "FAIL") + " %-62s %s" % (name, got))
    for name, got, want in (("span: one close, one far", span([160.0, 900.0], 380, 620), True),
                            ("span: camera stuck close", span([160.0, 160.0], 380, 620), False),
                            ("span: camera stuck far", span([900.0, 900.0], 380, 620), False),
                            ("span: an altitude unread", span([160.0, None], 380, 620), False),
                            ("span: limits unread", span([160.0, 900.0], None, 620), False),
                            ("restore: every write and the commit answered", restore_ok([{"success": True}] * 3), True),
                            ("restore: one write refused", restore_ok([{"success": True}, {"success": False}]), False),
                            ("restore: nothing written", restore_ok([]), False)):
        bad += got != want
        print(("ok  " if got == want else "FAIL") + " %-62s %s" % (name, got))
    import tempfile
    d = tempfile.mkdtemp()
    for name, rec, blob, want in (("verdict: PASS on these bytes", {"verdict": "PASS", "src_blob": "abc"}, "abc", 0),
                                  ("verdict: PASS on older bytes", {"verdict": "PASS", "src_blob": "old"}, "abc", 1),
                                  ("verdict: last run FAIL", {"verdict": "FAIL", "src_blob": "abc"}, "abc", 1),
                                  ("verdict: last run UNMEASURED", {"verdict": "UNMEASURED", "src_blob": "abc"}, "abc", 1),
                                  ("verdict: no record", None, "abc", 1),
                                  ("verdict: hash unreadable", {"verdict": "PASS", "src_blob": None}, "", 1)):
        f = os.path.join(d, name.replace(" ", "_").replace(":", "") + ".json")
        if rec is not None:
            json.dump(rec, open(f, "w"))
        got = verdict(f, blob)
        bad += got != want
        print(("ok  " if got == want else "FAIL") + " %-62s exit %d (want %d)" % (name, got, want))
    print("RESULT %s: %d judge cases + Info source + staging and verdict cases, %d wrong" % ("PASS" if not bad else "FAIL", len(CASES), bad))
    return 1 if bad else 0


# ---------------------------------------------------------------- staged: paint, look at two zooms, put back
def src_hash():
    r = subprocess.run(["git", "-C", REPO, "hash-object", SRC], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def pick_tiles(rows, n):
    """-> up to n tile ids that the decal build draws on once painted: dry land (not water covered), flat."""
    ok = [r for r in rows if not r.get("waterCovered") and r.get("hilliness") == "Flat" and r.get("biome")]
    return [r["tile"] for r in ok[:n]]


def restore_groups(rows):
    """-> {(biome, hilliness): [tile ids]} so each original value is written back in one call."""
    g = {}
    for r in rows:
        g.setdefault((r["biome"], r["hilliness"]), []).append(r["tile"])
    return g


def span(alts, full, gone):
    """-> True when the readings were taken at one altitude at or below full and one at or above gone: the camera really
    moved, so a PASS shows the fade both ways (a camera that ignored the asked altitude reads twice at one zoom)."""
    if full is None or gone is None or not alts or None in alts:
        return False
    return min(alts) <= full and max(alts) >= gone


def restore_ok(replies):
    """-> True when every restoring write and the commit after them answered success."""
    return bool(replies) and all(r.get("success") for r in replies)


def _connect():
    """-> call(tool, **params) -> reply dict. The bridge binds Windows loopback, so each call runs the client under
    Windows Python (live_def_check._bridge); a call that did not answer is a reply with success False and its cause."""
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import live_def_check as L
    client = subprocess.run(["wslpath", "-w", L.CLIENT], capture_output=True, text=True).stdout.strip()

    def call(tool, **p):
        # the staging writes are this proof's purpose, so they pass the client's live-write flag; reads stay reads
        flag = ["--read-only-static"] if tool == "jawa/static_call" else ["--yes-i-know-this-is-live"]
        try:
            # budget: danger=a world_commit regenerates every planet layer and a hung call holds the game; 300 s is a hang guard
            r = subprocess.run(["python.exe", client, "--timeout", "300", "--call", tool, "--json", json.dumps(p)] + flag,
                               capture_output=True, text=True, timeout=330, stdin=subprocess.DEVNULL)
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            return {"success": False, "error": "the bridge call did not finish: %s" % e}
        if r.returncode:
            return {"success": False, "error": "bridge call exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[:400])}
        try:
            r = json.loads(r.stdout)
        except ValueError:
            return {"success": False, "error": "not JSON: %s" % r.stdout[:300]}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                pass
        return r if isinstance(r, dict) else {"result": r}
    return call


def game_name():
    """-> the name of the game this run drove (RM_GAME_INSTANCE through the one name map; unset is ArchBig)."""
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))
    import game_names
    return game_names.show(os.environ.get("RM_GAME_INSTANCE") or "a")


def _static(call, method, args):
    return json.dumps(call("jawa/static_call", type=T, method=method, args=args))


def stage():
    call = _connect()
    probe = _static(call, "Probe", STAGE_BIOME)
    if '"success": false' in probe and "atlas" not in probe:
        print("UNMEASURED: no bridge: %s" % probe[:300]); return 2
    got = call("jawa/world_tile_get", range="0-%d" % (SCAN - 1), limit=SCAN)
    rows = got.get("tiles") or []
    if not rows:
        print("UNMEASURED: no world tiles read: %s" % json.dumps(got)[:300]); return 2
    ids = pick_tiles(rows, STAGE_TILES)
    if not ids:
        print("UNMEASURED: no flat dry land tile in tiles 0-%d" % (SCAN - 1)); return 2
    before = [r for r in rows if r["tile"] in ids]
    readings, code, line = [], 2, "UNMEASURED: not run"
    try:
        w = call("jawa/world_tile_set", tiles=",".join(map(str, ids)), biome=STAGE_BIOME, hilliness="Flat")
        if not w.get("success"):
            print("UNMEASURED: the world refused the staging write (a canonical save refuses it): %s" % json.dumps(w)[:300])
            return 2
        c = call("jawa/world_commit")
        print("staged %s on tiles %s; commit: %s" % (STAGE_BIOME, ids, [s.get("step") + ":" + s.get("status") for s in c.get("steps", [])][:3]))
        codes, alts, limits = [], [], (None, None)
        for alt in STAGE_ALTS:
            call("jawa/world_view", show=True, centerTile=ids[0], altitude=alt, northUp=True)
            time.sleep(2.0)   # the fade runs in the terrain layer's Alpha getter, once per drawn frame
            info = _static(call, "Info", "")
            k, ln = judge(probe, info, staged=True)
            readings.append({"altitude": alt, "read_altitude": num(info, "altitude"), "info": info[:600], "verdict": ln})
            print("altitude %.0f (read %s): %s\n  info: %s" % (alt, num(info, "altitude"), ln, info[:400]))
            codes.append(k)
            alts.append(num(info, "altitude"))
            limits = (num(info, "fullAlt"), num(info, "goneAlt"))
        if not span(alts, *limits):
            readings.append({"verdict": "UNMEASURED: the camera read altitudes %s, not one at or below fullAlt and one at or "
                                        "above goneAlt %s, so the fade was not seen both ways" % (alts, limits)})
            codes.append(2)
        code = 1 if 1 in codes else (2 if 2 in codes else 0)
        line = "PASS" if code == 0 else ("FAIL" if code == 1 else "UNMEASURED") + ": " + " | ".join(r["verdict"] for r in readings)
    finally:
        back = [call("jawa/world_tile_set", tiles=",".join(map(str, tl)), biome=biome, hilliness=hill)
                for (biome, hill), tl in restore_groups(before).items()]
        back.append(call("jawa/world_commit"))
        call("jawa/world_view", show=False)
        restored = restore_ok(back)
        print(("restored tiles %s" % ids) if restored else
              "WARNING: tiles %s may not be restored: %s" % (ids, [r.get("error") for r in back if not r.get("success")]))
    rec = {"verdict": "PASS" if code == 0 else ("FAIL" if code == 1 else "UNMEASURED"), "line": line,
           "src": "src/RimMandrake/BiomesShell/Source/RM_WorldDecals.cs", "src_blob": src_hash(),
           "game": game_name(), "probe": probe[:200], "tiles": ids, "restored": restored, "readings": readings,
           "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(RESULT, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(line)
    print("recorded: %s" % RESULT)
    return code


def verdict(path=RESULT, blob=None):
    """-> exit 0 when the recorded staged run PASSED on the current bytes of RM_WorldDecals.cs, else 1."""
    blob = src_hash() if blob is None else blob
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("FAIL: no staged live run recorded (%s)" % e); return 1
    if rec.get("verdict") != "PASS":
        print("FAIL: the last staged run read %s: %s" % (rec.get("verdict"), rec.get("line", "")[:300])); return 1
    if not blob or rec.get("src_blob") != blob:
        print("FAIL: the staged PASS was made on RM_WorldDecals.cs %s, the file is now %s" % (rec.get("src_blob"), blob)); return 1
    print("PASS: staged live A1 PASS at %s on %s, on the current RM_WorldDecals.cs" % (rec.get("at"), rec.get("game"))); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(selftest() if "--selftest" in a else stage() if "--stage" in a else verdict() if "--verdict" in a else live())
