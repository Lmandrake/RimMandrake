#!/usr/bin/env python3
"""Annotate FlowWorks water-scene screenshots with plain-language review text.
Input : Transient/fw_scenes/live/S*_p*.png + newest S*_<ts>.txt + S*_rows.json
Output: Transient/fw_scenes/live/annotated/<name>.png and index.html
Scene wording comes from design/RimMandrake/vv_methods/water_scenes_for_approval_2026-10-16.md.
Every picture also prints, from the walk's rows, the level-water expectation, the ProofReadout strings (verbatim, litres to the
litre) and the per-body surface gap (ProofLevelSurface) when the walk recorded them. Run: python3 annotate_water_scenes.py
[live-folder]; the live folder defaults to Transient/fw_scenes/live."""
import json, glob, os, re, html, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
LIVE = os.path.join(ROOT, "Transient/fw_scenes/live")
OUT = os.path.join(LIVE, "annotated")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

LEGEND_COMMON = ("Map from the left: the big dark-grey area is a LAKE (never runs out). "
                 "Thin strips of dug ground to its right are CANALS: 1 square deep, dry brown until water arrives (blue-grey).")
SCENES = {
 "S1": dict(title="S1. A canal dug from a lake fills end to end", status="",
   legend=LEGEND_COMMON + " Here: one 8-square canal touching the lake.",
   check=["Water should creep along the canal ONE square per pulse, starting at the lake end.",
          "The wet part must always be one unbroken run from the lake. No wet square with a dry gap before it.",
          "By pulse 10 all 8 squares are wet. The lake must not shrink."],
   passif="All 8 squares wet by pulse 10, never a gap, a wet square never dries again.",
   fails="Only the first square gets wet and then it stops (the 2026-10-16 bug)."),
 "S2": dict(title="S2. A shallow trench beside a lake-fed pond fills", status="",
   legend=LEGEND_COMMON + " Here: a dug 2x2 POND (4 deep) touching the lake, plus a 6-square 1-deep TRENCH off the pond's far side.",
   check=["The pond should fill first (4 levels in each of its 4 squares).",
          "Then water spills into the trench, one square per pulse, always one run from the pond end.",
          "After that, nothing changes."],
   passif="By pulse 30 pond full and all 6 trench squares wet; trench is one unbroken run.",
   fails="Pond fills but the trench stays dry, or only the trench's first square gets wet."),
 "S3": dict(title="S3. A pump fills a canal that touches no water", status="Ruled: a tap in a canal fills it; a tap on the surface needs a hose.",
   legend="Left: an enclosed POND (12 squares, 48 levels, touches no map edge). A HOSE with an Intake end sits in the pond, runs to a PUMP, then a second hose with an Outflow end sits in a 6-square CANAL on the right. Ground between pond and canal must stay dry.",
   check=["Pump OFF for 20 pulses: NOTHING moves, canal stays dry.",
          "Pump ON: canal fills one square per pulse; every litre the canal and hoses gain is a litre the pond lost.",
          "The ground between pond and canal never gets wet."],
   passif="Pump off = no water in canal. Pump on = all 6 canal squares wet in time; pond loss equals canal+hose gain.",
   fails="Water reaches the canal with the pump off, or the pond loses less than the canal gains."),
 "S4": dict(title="S4. A sluice gate shut, then open, then shut again", status="Ruled: water trapped behind a re-shut gate stays where it is.",
   legend=LEGEND_COMMON + " Here: 3 canal squares, a GATE square (sealed sluice, or the metal-grate kind that always lets water through), then 4 more squares.",
   check=["Gate SHUT: the 3 squares before the gate fill; the 4 after it stay DRY.",
          "Gate OPENED: the 4 downstream squares fill.",
          "Gate shut again: water already downstream stays put.",
          "Metal-grate gate (never opened): downstream fills anyway."],
   passif="Sealed gate blocks water while shut; opens and passes it; grate always passes.",
   fails="Water gets past a SHUT sealed gate, or a grate holds water back."),
 "S5": dict(title="S5. Nothing created or destroyed: a closed pond pays for its canal, by gravity and by pump",
   status="Level water (third draft, awaiting the owner's verdict): every body stands at ONE surface; amounts are litres to the decilitre.",
   legend="Closed ponds with canals dug off them, nothing touching a map edge. A: 3x3 pond 2 m deep (36,000 L) + 10-square 0.5 m canal. "
          "B: 1-square pond (4,000 L) + the same canal. F: 1-square pond beside one 2 m canal square. G: 1-square pond, a pump and a 6-square canal. "
          "D: an isolated 3-square run, full. E: a 6x6 basin 1 m deep with 8,000 L heaped in its middle.",
   check=["A and B: water flows downhill only. The canal gets a thin even sheet over ALL its squares (A: 0.24 m, B: 4.5 cm), the pond drops to the same surface.",
          "Pond + canal always add up to the starting litres. Nothing is created or lost.",
          "F: the pond square and the 2 m canal square end with 1.00 m of water each (2,000 L each).",
          "C: filling in a canal square that holds a sheet moves its water elsewhere; the total stays 4,000 L, no overflow message.",
          "D: filling in the middle square of the isolated run destroys exactly 1,000 L and the message says so.",
          "E: the heap spreads to a smooth even sheet over all 36 squares (0.11 m, 222 L each), never 0, deep, 0.",
          "G: the pump empties the pond (bar what the hoses hold) into the canal; all 6 canal squares end at the same depth (0.33 m); the ground between stays dry."],
   passif="Totals conserved to the decilitre; one surface per body (gap under 1 cm); D destroys exactly 1,000 L.",
   fails="Any total changes except D's 1,000 L; two squares of one body at different heights; a canal square wet that is not dug."),
 "S6": dict(title="S6. Save and reload mid-flow, and the flow carries on", status="Ruled: the reloaded run must match on totals and END state (not every pulse).",
   legend="The same pond + canal and gate scenes as S5 part A and S4, saved partway and reloaded. Compare the 'run 1' (never saved) and 'run 2' (saved and reloaded) pictures.",
   check=["Right after reload, every square, the pond stock and the gate open/shut state look exactly like before the save.",
          "The flow must CONTINUE from where it was, not restart from the lake end.",
          "At pulse 30 run 2 looks identical to run 1."],
   passif="Same totals, same end state at pulse 30; gate keeps its state.",
   fails="Fill restarts, water appears or vanishes, a shut gate comes back open."),
}
# image name -> (scene, step key or None, pulse, what this moment is)
IMGS = {
 "S1_p00": ("S1", None, 0, "Start: canal dug, completely dry."),
 "S1_p03": ("S1", None, 3, "Pulse 3: expect the first 3 squares wet."),
 "S1_p10": ("S1", None, 10, "Pulse 10 (deadline): all 8 squares wet."),
 "S1_p14": ("S1", None, 14, "Pulse 14: settled, nothing should have changed since pulse 10."),
 "S2_p00": ("S2", None, 0, "Start: pond and trench dug, all dry."),
 "S2_p10": ("S2", None, 10, "Pulse 10: pond already full, trench filling (first 2 squares)."),
 "S2_p30": ("S2", None, 30, "Pulse 30 (deadline): pond full, all 6 trench squares wet."),
 "S2_p60": ("S2", None, 60, "Pulse 60: still settled."),
 "S3_p00": ("S3", None, None, "Start: pump switched OFF, everything dry."),
 "S3A_p20": ("S3", "A", 20, "Pump OFF, pulse 20: canal must still be dry."),
 "S3B_p06": ("S3", "B", 6, "Pump ON, pulse 6: canal part-filled."),
 "S3B_p16": ("S3", "B", 16, "Pump ON, pulse 16: canal full, pond lower than at start."),
 "S3q_p10": ("S3", None, None, "Ruling check: a tap standing beside a dug canal. RULED: it fills the canal directly."),
 "S4_p00": ("S4", None, None, "Start: gate shut, canal dry."),
 "S4A_p06": ("S4", "A", 6, "Gate SHUT, pulse 6: upstream wet, downstream dry."),
 "S4A_p12": ("S4", "A", 12, "Gate SHUT, pulse 12: the metal-grate twin should already be wet downstream; the sealed gate must not."),
 "S4A_p20": ("S4", "A", 20, "Gate SHUT, pulse 20: downstream still dry behind the sealed gate."),
 "S4B_p08": ("S4", "B", 8, "Gate OPENED, 8 pulses later: all 4 downstream squares wet."),
 "S4B_p20": ("S4", "B", 20, "Gate still open, pulse 20: everything full."),
 "S4C_p20": ("S4", "C", 20, "Gate SHUT AGAIN, pulse 20: downstream water stays (ruled)."),
 "S5_p00": ("S5", None, None, "Start: ponds A, B, F, G with their canals dug dry; the isolated run D full; pump G off."),
 "S5AB_p10": ("S5", "AB", 10, "Pulse 10: B and F should be settled; A's canal still filling."),
 "S5AB_p20": ("S5", "AB", 20, "Pulse 20: A settled: pond lower, 10 canal squares at one even depth."),
 "S5AB_p54": ("S5", "AB", 54, "Pulse 54: all of A, B, F at rest; B's canal has not moved for 40 pulses."),
 "S5C_p01": ("S5", "C", 1, "Part C, one pulse after filling in canal B's first square."),
 "S5_D_message": ("S5", None, None, "Part D: the isolated run after its middle square was filled in; the overflow message is top-left."),
 "S5E_p20": ("S5", "E", 20, "Part E, pulse 20: the heaped basin should be one even sheet over all 36 squares."),
 "S5G_p10": ("S5", "G", 10, "Part G, pump on, pulse 10: canal filling from the pond."),
 "S5G_p30": ("S5", "G", 30, "Part G, pulse 30: pond empty (bar the hoses), six canal squares level."),
 "S6_p00": ("S6", None, None, "Run 1 start (never saved)."),
 "S6_run1_p30": ("S6", None, None, "Run 1 (never saved) at pulse 30: this is the target end state."),
 "S6_run2_p30": ("S6", None, None, "Run 2 (saved, reloaded) at pulse 30: must look the same as run 1."),
}

def newest_log(s):
    fs = sorted(glob.glob(f"{LIVE}/{s}_2*.txt"))
    return fs[-1] if fs else None

def pulse_line(s, step, pulse):
    if pulse is None: return None
    f = newest_log(s)
    if not f: return None
    cur = None
    for ln in open(f, errors="replace"):
        m = re.match(r"\s*step ([A-Z]+):", ln)
        if m: cur = m.group(1)
        m = re.match(r"\s*(?:([ABC]) )?pulse\s+(\d+)\s+(.*)", ln)
        if m and int(m.group(2)) == pulse:
            k = m.group(1) or cur
            if step is None or k == step or k is None:
                return f"pulse {pulse}: " + re.sub(r"\s+", " ", m.group(3)).strip()
    return None

def rows(s):
    p = f"{LIVE}/{s}_rows.json"
    return json.load(open(p)) if os.path.exists(p) else []

def measured(s, step, pulse):
    out = []
    pl = pulse_line(s, step, pulse)
    if pl: out.append("Raw game readout at this moment (squares, 0 = dry, 1 = wet): " + pl)
    elif pulse is not None: out.append("UNMEASURED: no raw readout for pulse %d was found in the walk's log (picture only)" % pulse)
    for r in rows(s):
        if r["status"] == "OPEN RULING": continue
        st = {"MATCHES": "MATCHES the rule", "DIFFERS": "DIFFERS from the rule", "UNMEASURED": "not measured"}.get(r["status"], r["status"])
        # rows without a doc claim (S3.audit's MEASURED ledger, a scene's CRASHED row) are named by their id
        out.append(f"{st}: {r.get('doc', r.get('id', ''))}  Game: {r.get('game','')}")
        if r.get("level"):
            out.append(f"   Level-water expectation ({r.get('id','')}): {r['level']}")
        if r.get("readout"):
            out.append(f"   Readout ({r.get('id','')}), litres to the litre: " + " | ".join(r["readout"]))
        if r.get("gaps"):
            out.append(f"   Surface gap per body ({r.get('id','')}): " + "; ".join(r["gaps"]))
    return out

def wrap(d, text, font, w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if d.textlength(t, font=font) <= w: cur = t
            else: lines.append(cur); cur = word
        lines.append(cur)
    return lines

def build(name):
    s, step, pulse, moment = IMGS[name]
    sc = SCENES[s]
    im = Image.open(f"{LIVE}/{name}.png").convert("RGB")
    W = 1600; im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    PW = 1000; pad = 30
    fh, fb, ft = (ImageFont.truetype(FB, 34), ImageFont.truetype(FR, 25), ImageFont.truetype(FB, 25))
    blocks = [("t", sc["title"]), ("m", moment)]
    if sc["status"]: blocks.append(("s", sc["status"]))
    blocks += [("h", "WHAT YOU ARE LOOKING AT"), ("p", sc["legend"]), ("h", "WHAT TO CHECK")]
    blocks += [("p", "- " + c) for c in sc["check"]]
    blocks += [("h", "PASS IF"), ("p", sc["passif"]), ("h", "FAILS IF"), ("p", sc["fails"]), ("h", "WHAT THE GAME MEASURED")]
    blocks += [("p", "- " + m) for m in measured(s, step, pulse)]
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lay, y = [], pad
    for k, t in blocks:
        f = {"t": fh, "h": ft}.get(k, fb)
        ls = wrap(tmp, t, f, PW - 2 * pad)
        lh = f.size + 8
        if k == "h": y += 14
        lay.append((k, ls, f, y)); y += lh * len(ls) + (4 if k != "h" else 2)
    H = max(im.height, y + pad)
    cv = Image.new("RGB", (W + PW, H), (250, 247, 240))
    cv.paste(im, (0, 0))
    d = ImageDraw.Draw(cv)
    col = {"t": (30, 30, 30), "m": (0, 70, 140), "s": (170, 60, 0), "h": (90, 60, 20), "p": (25, 25, 25)}
    for k, ls, f, y0 in lay:
        for i, l in enumerate(ls):
            d.text((W + pad, y0 + i * (f.size + 8)), l, font=f, fill=col[k])
    os.makedirs(OUT, exist_ok=True)
    cv.save(f"{OUT}/{name}.png")
    return s, name, moment, sc, measured(s, step, pulse)

def main(live=None, out=None):
    global LIVE, OUT
    if live:
        LIVE = os.path.abspath(live)
        OUT = os.path.abspath(out) if out else os.path.join(LIVE, "annotated")
    res = [build(n) for n in IMGS if os.path.exists(f"{LIVE}/{n}.png")]
    e = html.escape
    h = ["<!doctype html><meta charset=utf-8><title>FlowWorks water scenes</title><style>body{font:18px sans-serif;background:#2b2118;color:#eee;margin:20px auto;max-width:1700px}"
         "section{background:#faf7f0;color:#222;padding:16px 24px;margin:24px 0;border-radius:6px}img{width:100%;border:1px solid #888}"
         "h2{margin:0 0 6px}.st{color:#a63c00;font-weight:bold}.cap{color:#04508c;font-weight:bold;margin:10px 0 4px}"
         "td{padding:2px 12px 2px 0;vertical-align:top}.v{margin-top:12px;font-size:20px}</style><h1>FlowWorks water scenes: what to evaluate</h1>"]
    seen = set()
    for s, name, moment, sc, meas in res:
        if s not in seen:
            if seen: h.append("</section>")
            seen.add(s)
            h.append(f"<section><h2>{e(sc['title'])}</h2>")
            if sc["status"]: h.append(f"<p class=st>{e(sc['status'])}</p>")
            h.append(f"<p><b>What you are looking at.</b> {e(sc['legend'])}</p><p><b>What to check</b></p><ul>" + "".join(f"<li>{e(c)}</li>" for c in sc["check"]) + "</ul>")
            h.append(f"<p><b>Pass if:</b> {e(sc['passif'])}<br><b>Fails if:</b> {e(sc['fails'])}</p>")
            h.append(f"<p><b>What the game measured</b></p><ul>" + "".join(f"<li>{e(m)}</li>" for m in measured(s, None, None)) + "</ul>")
            h.append("<p class=v>"+e(s)+": &#9744; looks right &nbsp; &#9744; looks wrong &nbsp; note: <input size=70></p>")
            h.append("</section><section style='background:#3a2e22;color:#eee;padding:8px'>")
            first = True
        h.append(f"<div class=cap style='color:#9cf'>{e(moment)}</div><img src='{e(name)}.png'><br>")
    h.append("</section>")
    # close sections properly: simple structure, browsers tolerate
    with open(f"{OUT}/index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    print(len(res), "annotated ->", OUT)
    return res


if __name__ == "__main__":
    main(*sys.argv[1:2])
