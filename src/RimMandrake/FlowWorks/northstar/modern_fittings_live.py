"""MODERN FITTINGS live capture (MODERN_FITTINGS_PROBE_FAUCET_NEVER_SEEN): the Modern faucet, sprinkler head and pipe span
were never seen in game (bridge run 1 built them on non-Modern pipe, so the heads came out rusty, and placed no second pole).
This script stages driver 5's recipe (ledger note 2026-10-24), reads what each thing actually DRAWS and photographs it.

  python.exe src/RimMandrake/FlowWorks/northstar/modern_fittings_live.py [--origin X,Z] [--out-dir DIR] [--fresh-map]

Minimal list: FlowWorks + Gimme Some Slack (the pipe pole's span is GSS's aerial link) + ModernFittingsCandidates (the
harness-only overlay carrying the round-3 candidates) + their About.xml dependencies, all five DLC; a quicktest map is enough. The bridge must be held. Exit 0 = every row PASS; 1 = a FAIL; 2 = a row unmeasured.

Scene (plot from --origin, default 140,140; reset and prepared 15 x 7 from (-1,-1)):
  pipe   RM_UniversalPipe x = 0..12, z = 0, each cell styled RM_UniversalPipe_Modern FIRST (jawa/set_thing_props)
  heads  RM_PipeFaucet (3,0) and RM_SprinklerHead (8,0), built AFTER the pipe is Modern: SpawnSetup's
         RM_SprinklerLook.MatchPipeUnder gives a new head the look of the pipe under it (Defs/Sprinklers/RM_Sprinklers.xml)
  poles  RM_PipePole (0,4) and (10,4) (10 cells, under the default pipePoleMaxSpan 12), styled RM_PipePole_Modern, then
         strung through GSS's own CompAerialAnchor.TryLink (RM_LineProofs.ProofLinkPoles)
Rows:
  CANDIDATES_SWAPPED_IN  the candidates (Transient/modern_style_20261023/cand_r3 RM_PipeFaucet, RM_SprinklerHead, PipeSpan)
        are what the game draws: jawa/running_mods has mandrake.rm.modernfittingscandidates loaded AFTER
        mandrake.rm.flowworks (a loose texture at the same path is taken from the LAST loaded mod; traps-art.md "Our own mods
        shadow each other"), and each file under the RUNNING overlay folder hashes to the candidate in the repo. The
        candidates are the same sizes as the installed art, so textureSize cannot tell them apart; the load order and bytes
        can. A redeploy after launch changes the bytes but not the loaded texture: the live round deploys before it loads.
  FAUCET_DRAWS_MODERN / SPRINKLER_DRAWS_MODERN  jawa/thing_graphic: resolvedPath is .../Faucet/Modern/RM_PipeFaucet,
        .../Sprinkler/Modern/RM_SprinklerHead, badTex false. The draw is Thing.Graphic (RM_PipeSeat.Print prints
        onPipe.Graphic), so this is the art on screen. detail.matchedPipe says whether MatchPipeUnder did it; when it did
        not, the style is set explicitly and the row still FAILS (the mod's own look-matching is what a player gets).
  SPAN_STRUNG_MODERN  ProofLinkPoles strung=True and both poles draw .../PipePole/Modern/...: the span's look is
        AerialLineProfiles.LookOfThing(pole) (the pole's style), and its texture is RM_PipePoles.xml's spanTexPath with
        {look} = Modern, i.e. RimMandrake/FlowWorks/PipePole/Modern/PipeSpan (installed; the selftest checks the file).
  CAPTURE_WRITTEN  rimworld/screenshot_cell_rect of the whole scene and of the two heads, copied into --out-dir, each a
        readable non-uniform image. The capture is what the art pipeline judges afterwards (captures.json lists them with
        their subjects): judging is an LLM run that cannot sit inside a 600 s live proof holding the bridge.
LIES: a head built on unstyled pipe draws Scrapper and still "exists" (the run-1 defect): the row reads the drawn path. A span
  that GSS auto-linked before the poles were styled reads strung either way; the pole look is read after styling, and the
  span's look is computed at draw time from it (no cached look per span). A screenshot tool that answers success with no
  file reads CAPTURE UNMEASURED/HARNESS, never PASS.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
ITEM = "MODERN_FITTINGS_PROBE_FAUCET_NEVER_SEEN"
DEFAULT_OUT = r"D:\ClaudeWork\rimmandrake\live\MODERN_FITTINGS_PROBE_FAUCET_NEVER_SEEN"
TEX = "RimMandrake/FlowWorks/"
WANT = {"RM_PipeFaucet": TEX + "Faucet/Modern/RM_PipeFaucet",
        "RM_SprinklerHead": TEX + "Sprinkler/Modern/RM_SprinklerHead"}
POLE_MODERN = TEX + "PipePole/Modern/"
SPAN_TEX = TEX + "PipePole/Modern/PipeSpan"
STYLE = {"RM_UniversalPipe": "RM_UniversalPipe_Modern", "RM_PipeFaucet": "RM_PipeFaucet_Modern",
         "RM_SprinklerHead": "RM_SprinklerHead_Modern", "RM_PipePole": "RM_PipePole_Modern"}
HEADS = {"RM_PipeFaucet": (3, 0), "RM_SprinklerHead": (8, 0)}
POLES = ((0, 4), (10, 4))
PIPE_X = range(0, 13)
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CAND_DIR = os.path.join(REPO, "Transient", "modern_style_20261023", "cand_r3")
OVERLAY = "mandrake.rm.modernfittingscandidates"
FLOWWORKS = "mandrake.rm.flowworks"
CANDIDATES = {"Faucet/Modern/RM_PipeFaucet": "RM_PipeFaucet.png", "Sprinkler/Modern/RM_SprinklerHead": "RM_SprinklerHead.png",
              "PipePole/Modern/PipeSpan": "PipeSpan.png"}   # texPath under TEX -> candidate file in CAND_DIR
ROW_OF = {"RM_PipeFaucet": "FAUCET_DRAWS_MODERN", "RM_SprinklerHead": "SPRINKLER_DRAWS_MODERN"}


def parse(txt):
    """'WORD k=v k=v' -> {k: v}."""
    return dict(t.split("=", 1) for t in str(txt).split()[1:] if "=" in t)


def drawn(g):
    """The path a thing_graphic row says is on screen."""
    return str(g.get("variantPath") or g.get("resolvedPath") or g.get("graphicPath") or "")


def v_head(defname, g, matched):
    """(status, cls, why) for one head's thing_graphic row (None = no row)."""
    if not g:
        return "UNMEASURED", "SITE", "%s not on the map / not read" % defname
    if g.get("error"):
        return "UNMEASURED", "HARNESS", "thing_graphic: %s" % g.get("error")
    if g.get("badTex"):
        return "FAIL", "MOD", "%s draws BadTex" % defname
    if drawn(g) != WANT[defname]:
        return "FAIL", "MOD", "%s draws %s, want %s" % (defname, drawn(g), WANT[defname])
    if not matched:
        return "FAIL", "MOD", "%s draws Modern only after an explicit style: MatchPipeUnder did not match the Modern pipe" % defname
    return "PASS", "MOD", "%s draws %s, matched from the pipe under it" % (defname, drawn(g))


def sha256(path):
    """Hex sha256 of a file, None if it cannot be read."""
    import hashlib
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def v_candidates(rm):
    """(status, cls, why) + detail: the running overlay sits after FlowWorks and its files are the candidates' bytes."""
    det = {}
    if not rm or not rm.get("success") or not isinstance(rm.get("mods"), list):
        return ("UNMEASURED", "HARNESS", "jawa/running_mods gave no mods[]: %s" % str(rm)[:200]), det
    by = {str(m.get("packageId") or "").lower(): m for m in rm["mods"]}
    ov, fw = by.get(OVERLAY), by.get(FLOWWORKS)
    if fw is None:
        return ("UNMEASURED", "SITE", "FlowWorks is not in the running load"), det
    if ov is None:
        return ("FAIL", "SITE", "%s is not in the running load: the installed art is drawn, not the candidates" % OVERLAY), det
    det.update(overlayOrder=ov.get("loadOrder"), flowworksOrder=fw.get("loadOrder"), folder=ov.get("folder"))
    try:
        after = int(ov.get("loadOrder")) > int(fw.get("loadOrder"))
    except (TypeError, ValueError):
        return ("UNMEASURED", "HARNESS", "loadOrder unreadable: %s" % det), det
    if not after:
        return ("FAIL", "SITE", "%s loads BEFORE FlowWorks (%s <= %s): FlowWorks' art wins" % (
            OVERLAY, det["overlayOrder"], det["flowworksOrder"])), det
    bad = []
    for tex, cand in CANDIDATES.items():
        want = sha256(os.path.join(CAND_DIR, cand))
        got = sha256(os.path.join(local(ov.get("folder")), "Textures", *(TEX + tex + ".png").split("/")))
        det[tex] = {"candidate": want, "running": got}
        if want is None:
            return ("UNMEASURED", "HARNESS", "candidate %s missing from the repo" % cand), det
        if got != want:
            bad.append("%s %s" % (tex, "missing" if got is None else "is not the candidate's bytes"))
    if bad:
        return ("FAIL", "SITE", "running overlay: " + "; ".join(bad)), det
    return ("PASS", "SITE", "%s loaded after FlowWorks (%s > %s); its %d textures are the cand_r3 bytes" % (
        OVERLAY, det["overlayOrder"], det["flowworksOrder"], len(CANDIDATES))), det


def v_span(link_kv, pole_rows):
    if not link_kv:
        return "UNMEASURED", "HARNESS", "ProofLinkPoles gave no answer"
    if len(pole_rows) != 2:
        return "UNMEASURED", "SITE", "%d pipe poles read, want 2" % len(pole_rows)
    bad = [drawn(g) for g in pole_rows if g.get("badTex") or not drawn(g).startswith(POLE_MODERN)]
    if bad:
        return "FAIL", "MOD", "pole(s) not drawn Modern: %s" % bad
    if link_kv.get("strung") != "True":
        return "FAIL", "MOD", "no span strung between the poles: %s" % link_kv
    return "PASS", "MOD", "span strung, both poles Modern, span texture %s" % SPAN_TEX


def image_problem(path):
    """None if path is a readable image with more than one colour; else why not."""
    if not path or not os.path.isfile(path) or os.path.getsize(path) == 0:
        return "no capture file at %s" % path
    try:
        from PIL import Image
        with Image.open(path) as im:
            lo_hi = im.convert("L").getextrema()
    except Exception as e:  # noqa: BLE001  an unreadable file is exactly what this reports
        return "unreadable image %s: %s" % (path, e)
    if lo_hi[0] == lo_hi[1]:
        return "uniform image %s (value %s)" % (path, lo_hi[0])
    return None


def v_capture(paths):
    if not paths:
        return "UNMEASURED", "HARNESS", "no screenshot path returned"
    probs = [p for p in (image_problem(x) for x in paths) if p]
    if probs:
        return "UNMEASURED", "HARNESS", "; ".join(probs)
    return "PASS", "MOD", "%d captures readable" % len(paths)


def local(path):
    """A path the screenshot tool returned (Windows) as this interpreter can open it."""
    p = str(path or "")
    if os.name != "nt" and len(p) > 2 and p[1] == ":":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def run(B, V, a):
    out_dir = a.out_dir
    os.makedirs(out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    rows = []
    res = {"script": "modern_fittings_live.py", "item": ITEM, "started": stamp, "rows": rows, "args": vars(a)}
    out = os.path.join(out_dir, "result_%s.json" % stamp)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, verdict, det=None):
        st, cls, why = verdict
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "why": why, "detail": det or {}})
        print("%-24s %-10s %-8s %s" % (rid, st, cls, why[:300]), flush=True)
        save()

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    rect = (ox - 1, oz - 1, 15, 7)
    rect_s = "%d,%d,%d,%d" % rect

    def graphics(defs):
        r = B.call("jawa/thing_graphic", rect=rect_s, defs=defs, limit=100) or {}
        return r.get("things") or [], r

    def style(g, defname):
        """True when the thing now carries the Modern StyleDef (styleDefAfter; success alone is also given on a skip)."""
        r = B.call("jawa/set_thing_props", thing=g.get("id"), style=STYLE[defname]) or {}
        return r.get("success") is True and r.get("styleDefAfter") == STYLE[defname]

    def ticks(n):
        B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=60000)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("FAUCET_DRAWS_MODERN", ("UNMEASURED", "HARNESS", "no game in Playing"))
        return 2
    cand_verdict, cand_det = v_candidates(B.call("jawa/running_mods", assembly="", details=True) or {})
    row("CANDIDATES_SWAPPED_IN", cand_verdict, cand_det)
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "modern_fittings_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("FAUCET_DRAWS_MODERN", ("UNMEASURED", "SITE", "site not prepared: %s" % str(site_rows[:2])[:200]))
        return 2

    # 1. the pipe run, Modern before anything is built on it
    built = B.call("jawa/build_batch", ops=";".join("RM_UniversalPipe:%s" % xz(P(x, 0)) for x in PIPE_X),
                   faction="player", wipeExisting=False, readBack=0) or {}
    ticks(2)
    pipes, _ = graphics("RM_UniversalPipe")
    res["pipes"] = len(pipes)
    if len(pipes) != len(PIPE_X):
        row("FAUCET_DRAWS_MODERN", ("UNMEASURED", "SITE", "%d of %d pipe cells built" % (len(pipes), len(PIPE_X))),
            {"build": str(built)[:400]})
        return 2
    res["pipeStyled"] = sum(style(g, "RM_UniversalPipe") for g in pipes)
    if res["pipeStyled"] != len(pipes):
        row("FAUCET_DRAWS_MODERN", ("UNMEASURED", "SITE", "%d of %d pipe cells took RM_UniversalPipe_Modern"
                                    % (res["pipeStyled"], len(pipes))))
        return 2
    # 2. the heads, on the Modern pipe
    hb = B.call("jawa/build_batch", ops=";".join("%s:%s" % (d, xz(P(*c))) for d, c in HEADS.items()),
                faction="player", wipeExisting=False, readBack=0) or {}
    ticks(2)
    first = {g.get("defName"): g for g in graphics(",".join(HEADS))[0]}
    matched = {d: drawn(first.get(d) or {}) == WANT[d] for d in HEADS}
    for d in HEADS:
        if first.get(d) and not matched[d]:
            style(first[d], d)          # still a FAIL row; styled so the capture shows the art under judgement
    # 3. two poles, Modern, strung
    pb = B.call("jawa/build_batch", ops=";".join("RM_PipePole:%s" % xz(P(*c)) for c in POLES),
                faction="player", wipeExisting=False, readBack=0) or {}
    ticks(2)
    styled = [style(g, "RM_PipePole") for g in graphics("RM_PipePole")[0]]
    if styled.count(True) != len(POLES):
        row("SPAN_STRUNG_MODERN", ("UNMEASURED", "SITE", "%d of %d pipe poles built and styled RM_PipePole_Modern"
                                   % (styled.count(True), len(POLES))), {"build": str(pb)[:400]})
        return 2
    lk = B.call("jawa/static_call", type=LPROOF, method="ProofLinkPoles",
                args="%s;%s" % (xz(P(*POLES[0])), xz(P(*POLES[1]))), _answer=True) or {}
    link_txt = str(lk.get("result") or lk.get("message") or lk.get("error") or "")
    link_kv = parse(link_txt) if link_txt.startswith("LINK") else {}
    ticks(30)
    pipes_after = len(graphics("RM_UniversalPipe")[0])
    final = {}
    for g in graphics(",".join(HEADS))[0]:
        final[g.get("defName")] = g
    poles = graphics("RM_PipePole")[0]
    res.update(headsBuild=str(hb)[:300], polesBuild=str(pb)[:300], link=link_txt, pipesAfterHeads=pipes_after,
               matched=matched, drawn={d: drawn(g) for d, g in final.items()}, poles=[drawn(g) for g in poles])
    for d in HEADS:
        row(ROW_OF[d], v_head(d, final.get(d), matched[d]), {"first": drawn(first.get(d) or {}), "final": final.get(d)})
    row("SPAN_STRUNG_MODERN", v_span(link_kv, poles), {"link": link_txt, "poles": poles})

    # 4. the captures
    B.call("jawa/clear_ui", all=True)
    caps = {}
    for name, r in (("scene", rect), ("heads", (ox + 2, oz - 1, 8, 3)), ("span", (ox - 1, oz + 3, 13, 3))):
        s = B.call("rimworld/screenshot_cell_rect", x=r[0], z=r[1], width=r[2], height=r[3], paddingCells=1,
                   fileName="modern_fittings_%s_%s" % (name, stamp), suppressMessage=True) or {}
        src = local(s.get("path"))
        if src:
            crop = os.path.splitext(src)[0] + "__cell_rect" + (os.path.splitext(src)[1] or ".png")
            src = crop if os.path.isfile(crop) else src
        if src and os.path.isfile(src):
            dst = os.path.join(out_dir, "modern_fittings_%s_%s.png" % (name, stamp))
            shutil.copyfile(src, dst)
            caps[name] = dst
        else:
            caps[name] = src or None
    verdict = v_capture([p for p in caps.values() if p] if all(caps.values()) else [])
    res["captures"] = caps
    row("CAPTURE_WRITTEN", verdict, caps)
    manifest = {"item": ITEM, "stamp": stamp, "result": out, "captures": caps,
                "candidatesSwappedIn": cand_verdict[0] == "PASS",
                "subjects": {"RM_PipeFaucet_Modern": {"texPath": WANT["RM_PipeFaucet"], "panel": caps.get("heads"),
                                                      "candidate": CANDIDATES["Faucet/Modern/RM_PipeFaucet"]},
                             "RM_SprinklerHead_Modern": {"texPath": WANT["RM_SprinklerHead"], "panel": caps.get("heads"),
                                                         "candidate": CANDIDATES["Sprinkler/Modern/RM_SprinklerHead"]},
                             "RM_PipeSpan_Modern": {"texPath": SPAN_TEX, "panel": caps.get("span"),
                                                    "candidate": CANDIDATES["PipePole/Modern/PipeSpan"]}},
                "candidateDir": "Transient/modern_style_20261023/cand_r3",
                "note": "in-game captures for the art-eval machine template's assembled panel"}
    with open(os.path.join(out_dir, "captures.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    sts = [r["status"] for r in rows]
    return 0 if all(s == "PASS" for s in sts) else (1 if "FAIL" in sts else 2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origin", default="140,140")
    ap.add_argument("--out-dir", default=DEFAULT_OUT if os.name == "nt" else local(DEFAULT_OUT))
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args(argv)
    import proof_hose as PH  # noqa: E402  (bridge-side imports only on a live run)
    try:
        return run(PH.PB(), PH.V, a)
    except Exception as e:  # noqa: BLE001  a transport fault is UNMEASURED (2), never Python's 1 = a mod FAIL
        print("UNMEASURED HARNESS %s: %s" % (type(e).__name__, e), flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
