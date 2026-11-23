#!/usr/bin/env python3
"""Blind lane 1 for the offline bars no_hose / no_hose_in_gss: an independent scan of what Gimme Some Slack SHIPS.
Reads no builder test. Prints one JSON row per line (id, bars, kind, verdict, cases, detail).
    python3 blind_no_hose.py [--mod <mod dir>] [--self-check]
--self-check plants a fault of each kind in a throwaway copy and reports which row goes FAIL (a guard is untested until seen red)."""
import argparse, hashlib, json, os, re, shutil, struct, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack"); FW = os.path.join(REPO, "src/RimMandrake/FlowWorks")
BARS = ["no_hose", "no_hose_in_gss"]
WORDS = re.compile(r"(?i)hose(?![a-z])|hose(?=[A-Z_]|s\b)|(?<![a-z])hoses?|hosereel|(?<![a-z])reels?(?![a-z])|spool|nozzle")
CAMEL = lambda s: re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", s)
HOSE = {"hose", "hoses", "reel", "reels", "hosereel", "spool", "spools", "nozzle", "nozzles"}
PIPE = {"pipe", "pipes", "pipeline", "piping"}
def words(s): return {w.lower() for w in CAMEL(s)}
def hit(s, bank): return bool(words(s) & bank) or ("hose" in bank and any(w.startswith("hose") for w in words(s)))
def row(i, kind, bad, cases, detail, info=False):
    v = "INFO" if info else ("FAIL" if bad else "PASS")
    return {"id": i, "bars": BARS, "kind": kind, "verdict": v, "cases": cases,
            "detail": detail + ((" | found: " + "; ".join(sorted(bad)[:12]) + " | would pass: none of these ships") if bad and not info else "")
            + ((" | seen: " + "; ".join(sorted(bad)[:12])) if bad and info else "")}
def shipped_xml(mod):
    for d, ds, fs in os.walk(mod):
        ds[:] = [x for x in ds if x not in ("Source", "northstar", "northstar_matrix", "art_source", "review", "tools", "live_probes")]
        for f in fs:
            if f.lower().endswith(".xml"): yield os.path.join(d, f)
def dll_strings(p):
    b = open(p, "rb").read(); i = b.find(b"BSJB")
    if i < 0: raise SystemExit("UNMEASURED: no CLI metadata in " + p)
    n = struct.unpack_from("<I", b, i + 12)[0]; q = i + 16 + n; cnt = struct.unpack_from("<H", b, q + 2)[0]; q += 4; st = {}
    for _ in range(cnt):
        off, size = struct.unpack_from("<II", b, q); e = b.index(b"\0", q + 8); name = b[q + 8:e].decode(); st[name] = b[i + off:i + off + size]
        q = q + 8 + ((e - q - 8) // 4 + 1) * 4
    names = [s.decode("utf8", "replace") for s in st["#Strings"].split(b"\0") if s]
    us, h, k = [], st["#US"], 1
    while k < len(h):
        c = h[k]
        if c & 0x80 == 0: L, k = c, k + 1
        elif c & 0xC0 == 0x80: L, k = ((c & 0x3F) << 8) | h[k + 1], k + 2
        else: L, k = ((c & 0x1F) << 24) | (h[k + 1] << 16) | (h[k + 2] << 8) | h[k + 3], k + 4
        if L: us.append(h[k:k + L - 1].decode("utf-16-le", "replace"))
        k += max(L, 0)
        if L == 0: continue
    return names, us
def scan(mod):
    out = []
    # 1 every element, attribute and text of every shipped xml that names code, a def or a picture
    bad, pipe, n, files = set(), set(), 0, 0
    for p in shipped_xml(mod):
        files += 1
        for el in ET.parse(p).iter():
            if not isinstance(el.tag, str): continue
            for s in [el.tag, *el.attrib.values(), el.text or ""]:
                s = s.strip(); n += 1
                prose = el.tag in ("description", "label", "jobString", "customLabel", "reportString")
                if not s: continue
                if hit(s, HOSE) and os.path.basename(p) != "About.xml": bad.add(os.path.relpath(p, mod) + ":" + el.tag + "=" + s[:60])
                if hit(s, PIPE) and not prose and os.path.basename(p) != "About.xml": pipe.add(os.path.relpath(p, mod) + ":" + el.tag + "=" + s[:60])
    out.append(row("NH_XML_NO_HOSE_OR_REEL", "fixed", bad, n, "%d shipped xml files, every tag/attribute/text (About.xml prose aside)" % files))
    out.append(row("NH_XML_NO_PIPE_DEF", "fixed", pipe, n, "no def, class or picture path of a pipe in shipped xml (prose aside)"))
    # 2 picture names
    pics = [os.path.relpath(os.path.join(d, f), mod) for d, _, fs in os.walk(os.path.join(mod, "Textures")) for f in fs]
    out.append(row("NH_TEXTURE_NAMES", "fixed", {p for p in pics if hit(p, HOSE | PIPE)}, len(pics), "file and folder names under Textures"))
    # 3 pictures copied from the hose mod (bytes, then 16x16 alpha-grey thumbnails of hose/reel/pipe pictures)
    h = {}
    fwp = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(FW, "Textures")) for f in fs if f.lower().endswith(".png")]
    for p in fwp: h.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.relpath(p, FW))
    hosepics = [p for p in fwp if hit(os.path.relpath(p, FW), HOSE)]
    bad = set(); near = set()
    from PIL import Image
    def thumb(p):
        im = Image.open(p).convert("RGBA").resize((16, 16)); return im.tobytes()
    ht = [(os.path.relpath(p, FW), thumb(p)) for p in hosepics]
    for p in pics:
        full = os.path.join(mod, p)
        if not full.lower().endswith(".png"): continue
        k = hashlib.sha256(open(full, "rb").read()).hexdigest()
        if k in h and (hit(h[k], HOSE | PIPE)): bad.add(p + " == " + h[k])
        t = thumb(full)
        for name, t2 in ht:
            if sum(abs(x - y) for x, y in zip(t, t2)) / len(t) < 2.0 and any(t): near.add(p + " ~ " + name)
    out.append(row("NH_TEXTURE_BYTES_NOT_HOSE_ART", "fixed", bad | near, len(pics) * max(1, len(ht)), "no GSS picture is byte-equal or near-equal (mean abs diff < 2 of 255 at 16x16) to one of FlowWorks' %d hose/reel pictures (%d pictures hashed)" % (len(ht), len(fwp))))
    # 4 compiled assembly: the names and literals that really ship
    dlls = [os.path.join(d, f) for d, _, fs in os.walk(mod) for f in fs if f.lower().endswith(".dll") and "/obj/" not in d and "/bin/" not in d]
    bad, pipe, lit, total = set(), set(), set(), 0
    # members of the shared draw-order table (both mods compile it: altitudes and queues, it draws nothing)
    table = set(re.findall(r"\b(\w*Hose\w*)\b", re.sub(r"//.*", "", open(os.path.join(REPO, "src/RimMandrake/_Shared/SlackGeometry/DrawOrder.cs")).read())))
    for p in dlls:
        names, us = dll_strings(p); total += len(names) + len(us)
        if not any("CordBuilder" in x for x in names): raise SystemExit("UNMEASURED: sanity probe failed, CordBuilder absent from " + p)
        bad |= {x for x in names if hit(x, HOSE) and x not in table}; pipe |= {x for x in names if hit(x, PIPE)}
        lit |= {x[:120] for x in us if hit(x, HOSE)}
    out.append(row("NH_DLL_NO_HOSE_IDENTIFIER", "fixed", bad, total, "type/member names in %d shipped dll(s) [sanity: CordBuilder seen]; left out: the numbers of _Shared DrawOrder.cs, which draw nothing: %s" % (len(dlls), ", ".join(sorted(table)))))
    out.append(row("NH_DLL_HOSE_LITERALS", "info", lit, total, "string literals in the dll naming a hose or reel (read by hand: legacy names / settings prose vs a picture or def)", info=True))
    out.append(row("NH_DLL_LITERAL_PICTURE_OR_DEF", "fixed", {x for x in lit if re.fullmatch(r"[A-Za-z0-9_./]+", x) and ("/" in x or x.startswith(("RM_", "RimMandrake")))}, total, "no literal that is a hose/reel picture path or def name"))
    out.append(row("NH_PIPE_IDENTIFIERS", "info", pipe, total, "pipe names in the dll: the aerial kernel carries AerialLineKind.Pipe for FlowWorks' pipe poles; VERSION.json out_of_scope names the wording ticket RIMMANDRAKE_REWORD_GSS_NO_HOSE_BAR_POLES_DRAW_PIPES", info=True))
    # 5 what the mod pulls in from outside its own folder
    cs = os.path.join(mod, "Source/RimMandrake_GimmeSomeSlack.csproj"); inc = re.findall(r'Include="([^"]+)"', open(cs).read())
    out.append(row("NH_CSPROJ_LINKS_NO_HOSE", "fixed", {i for i in inc if hit(i, HOSE)}, len(inc), "csproj includes"))
    return out
ap = argparse.ArgumentParser(); ap.add_argument("--mod", default=MOD); ap.add_argument("--self-check", action="store_true"); a = ap.parse_args()
if not a.self_check:
    rows = scan(a.mod)
    for r in rows: print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)
plants = {
 "def": lambda m: open(os.path.join(m, "Defs/Z.xml"), "w").write("<Defs><ThingDef><defName>RM_HoseReel</defName></ThingDef></Defs>"),
 "pipe_def": lambda m: open(os.path.join(m, "Defs/Z.xml"), "w").write("<Defs><ThingDef><defName>RM_FloorPipe</defName></ThingDef></Defs>"),
 "texture_folder": lambda m: (os.makedirs(os.path.join(m, "Textures/RimMandrake/GimmeSomeSlack/Hose")), shutil.copy(os.path.join(m, "Textures/RimMandrake/GimmeSomeSlack/PowerSwitch.png"), os.path.join(m, "Textures/RimMandrake/GimmeSomeSlack/Hose/A.png"))),
 "dll": lambda m: (lambda p, b: open(p, "wb").write(b.replace(b"\0CordReach\0", b"\0HoseReach\0", 1)))(os.path.join(m, "Assemblies/RimMandrakeGimmeSomeSlack.dll"), open(os.path.join(m, "Assemblies/RimMandrakeGimmeSomeSlack.dll"), "rb").read()),
}
ok = True
for k, f in plants.items():
    t = tempfile.mkdtemp(); m = os.path.join(t, "GimmeSomeSlack"); shutil.copytree(MOD, m, ignore=shutil.ignore_patterns("northstar*", "review", "*.json"))
    try:
        f(m)
        try: red = [r["id"] for r in scan(m) if r["verdict"] == "FAIL"]
        except SystemExit as e: red = ["STOPPED: " + str(e)]
    finally: shutil.rmtree(t)
    print("plant", k, "->", red or "MISSED"); ok &= bool(red)
sys.exit(0 if ok else 1)
