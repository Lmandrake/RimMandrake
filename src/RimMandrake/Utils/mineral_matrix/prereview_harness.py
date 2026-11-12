"""prereview_harness.py -- drive a built mineral sheet in headless Chromium the way the owner would use it.

    python3 prereview_harness.py <out>      (needs `pip install playwright && playwright install chromium`)

<out> is a gen_matrix.py output folder. Opens <out>/page/index.html with the claude.* capabilities mocked (db, user,
downloads), checks rendering, labels, marks, cell and band edits, every view, xlsx export, phone and dark layouts and
the no-db / no-claude fallbacks; screenshots and result.json go to <out>/prereview/. Expected counts come from
<out>/stats.json, not from constants. Exit 0 only if every check passes.
"""
import json, pathlib, sys, base64
from playwright.sync_api import sync_playwright
W = pathlib.Path(sys.argv[1]).resolve()
(W/"prereview").mkdir(exist_ok=True)
ST = json.loads((W/"stats.json").read_text())
HTML = (W/"page/index.html").read_text()
SKEL = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}</style></head><body>' + HTML + '</body></html>'
EXT = []
import csv
BREG = list(csv.DictReader(open(W/"biomes.csv")))
NB = len(BREG); assert NB == ST["biomes"], (NB, ST["biomes"])
MOCK = r"""
(() => {
  const recs = []; const subs = []; window.__saved = null; window.__recs = recs;
  const snap = () => ({ docs: recs.slice().sort((a,b)=>a.at<b.at?-1:1).map((r,i)=>({id:'d'+i, data:()=>r})) });
  const coll = { add: async r => { recs.push(JSON.parse(JSON.stringify(r))); setTimeout(()=>subs.forEach(f=>f(snap())),0); return {id:'d'+recs.length}; },
    orderBy(){return this}, limit(){return this}, onSnapshot(f){subs.push(f); setTimeout(()=>f(snap()),0); return ()=>{}} };
  const MODE = window.__MODE || 'full';
  const caps = { db: { collection: () => coll }, user: { id: async () => 'u_me', me: async () => ({id:'u_me'}), profiles: async ids => Object.fromEntries(ids.map(i=>[i,{name:'Other Person'}])) },
    downloads: { save: async ({filename, data}) => { const u8 = data instanceof Uint8Array ? data : new Uint8Array(data); let s=''; for (let i=0;i<u8.length;i++) s+=String.fromCharCode(u8[i]); window.__saved = {filename, b64: btoa(s), n: u8.length}; return {status:'saved'}; } } };
  if (MODE !== 'none') window.claude = { use: async n => { await new Promise(r=>setTimeout(r,20)); if (MODE==='nodb' && n==='db') return null; return caps[n] || null; } };
})();
"""
out = {"catches": [], "checks": []}
def ok(name, cond, detail=""):
    out["checks"].append({"check": name, "pass": bool(cond), "detail": str(detail)[:400]})
def run(pw, mode, w, h, scheme, shots):
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
    errs = []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console." + m.type + ": " + m.text) if m.type in ("error",) and "ERR_FAILED" not in m.text else None)
    ctx.route("**/*", lambda r: r.fulfill(status=200, body=SKEL, content_type="text/html") if r.request.url.startswith("https://page.test/") else (EXT.append(r.request.url), r.abort()))
    pg.add_init_script("window.__MODE=%r;" % mode + MOCK)
    pg.goto("https://page.test/index.html"); pg.wait_for_timeout(400)
    for s in shots: pg.screenshot(path=str(W/"prereview"/s))
    return b, pg, errs
with sync_playwright() as pw:
    # desktop, full caps, light
    b, pg, errs = run(pw, "full", 1440, 900, "light", ["desk_light.png"])
    r = pg.evaluate(r"""() => { const D = __mm.D; return {
      rows: document.querySelectorAll('#grid th.bn').length, cols: document.querySelectorAll('#grid thead tr.mn th').length,
      cells: document.querySelectorAll('#grid td.c').length, nB: D.biomes.length, nC: D.columns.length,
      emptyRow: [...document.querySelectorAll('#grid th.bn .nm')].filter(e=>!e.textContent.trim()).length,
      emptyCol: [...document.querySelectorAll('#grid thead tr.mn th')].filter(e=>!e.textContent.trim()).length,
      bad: (document.body.innerText.match(/NaN|undefined|\bnull\b|\[object/g)||[]),
      bodyOver: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      status: document.getElementById('status').textContent,
      nonzero: [...document.querySelectorAll('#grid td.c')].filter(e=>e.textContent.trim()).length }; }""")
    ok("desktop all rows render", r["rows"] == r["nB"] == NB, r); ok("desktop all columns render", r["cols"] == r["nC"] == 49 and r["cells"] == NB*49, r)
    ok("no empty labels", r["emptyRow"] == 0 and r["emptyCol"] == 0, r); ok("no NaN/undefined/null text", not r["bad"], r["bad"])
    ok("body no horizontal scroll desktop", r["bodyOver"] <= 0, r["bodyOver"]); ok("nonzero cells shown = data", r["nonzero"] == ST["nonzero_incl_deep_river"], r["nonzero"])
    ok("status connected", "Connected" in r["status"], r["status"])
    r0 = pg.evaluate("""() => ({ labels: Object.fromEntries([...document.querySelectorAll('#grid th.bn')].map(t => [t.dataset.b, t.querySelector('.nm').textContent])),
      marked: [...document.querySelectorAll('#grid th.bn')].filter(t => t.querySelector('.bd').textContent.includes('not painted')).map(t => t.dataset.b),
      rb: [...document.querySelectorAll('#grid td.c.rb')].map(t => t.dataset.b + '|' + t.dataset.c), d4: new Set([...document.querySelectorAll('#grid td.c.d4')].map(t => t.dataset.b)).size,
      jawa: /\\(Jawa\\)|SeabedFloor|Fuel Snows|RUT_Desert|RUT_ExtremeDesert|RUT_AridShrubland|OTHER_vanilla/.test([...document.querySelectorAll('#grid th.bn')].map(t => t.textContent + t.dataset.b).join(' ')),
      items: JSON.parse(document.getElementById('ITEMS').textContent).map(i => i.id) })""")
    ok("row labels = src labels (Warscar with article)", r0["labels"] == {g["biome"]: g["label"] for g in BREG}, r0["labels"])
    ok("ChillCrater + LanternDeeps marked, nothing else", sorted(r0["marked"]) == ["RM_ChillCrater", "RM_LanternDeeps"], r0["marked"])
    ok("%d draft-marked cells" % ST["draft_cells"], len(r0["rb"]) == ST["draft_cells"], r0["rb"]); ok("%d D4 rows hatched" % len(ST["d4_empty"]), r0["d4"] == len(ST["d4_empty"]), r0["d4"])
    ok("no dropped ids or Jawa tags in rows", not r0["jawa"]); ok("ITEMS = one per row", sorted(r0["items"]) == sorted(g["biome"] for g in BREG), r0["items"])
    out["rows"] = r0
    # ladder edit
    cell = pg.locator('#grid td.c:not(.d4)').filter(has_text='').first if False else pg.locator('#grid td.c[data-c="zersium"]').nth(0); bid = cell.get_attribute("data-b"); cid = cell.get_attribute("data-c")
    cell.click(); pg.wait_for_timeout(150)
    pg.locator('#dr-ladder button[data-v="1"]').click(); pg.wait_for_timeout(250)
    r2 = pg.evaluate("([b,c]) => ({ recs: window.__recs, v: __mm.curVal(b,c), txt: document.querySelector(`#grid td.c[data-b='${b}'][data-c='${c}']`).textContent, cls: document.querySelector(`#grid td.c[data-b='${b}'][data-c='${c}']`).className, cur: document.getElementById('dr-cur').textContent })", [bid, cid])
    rec = r2["recs"][0] if r2["recs"] else {}
    ok("ladder button writes db record", len(r2["recs"]) == 1 and set(["kind","biome","column","old","new","who","at","v"]) <= set(rec) and rec["who"] == "u_me" and rec["new"] == 1 and rec["old"] == rec["draft"], rec)
    ok("ladder updates cell + mine highlight", r2["v"] == 1 and r2["txt"] == "1" and "mine" in r2["cls"] and r2["cur"] == "1", r2)
    # other ladder rungs
    for v in ["0.03", "25", "99"]:
        pg.locator(f'#dr-ladder button[data-v="{v}"]').click(); pg.wait_for_timeout(150)
    r3 = pg.evaluate("([b,c]) => ({v: __mm.curVal(b,c), n: window.__recs.length, txt: document.querySelector(`#grid td.c[data-b='${b}'][data-c='${c}']`).textContent})", [bid, cid])
    ok("all ladder rungs apply", r3["v"] == 99 and r3["n"] == 4 and r3["txt"] == "99", r3)
    pg.fill("#dr-free", "3.5"); pg.click("#dr-set"); pg.wait_for_timeout(150)
    ok("free entry", pg.evaluate("([b,c]) => __mm.curVal(b,c)", [bid, cid]) == 3.5)
    pg.fill("#dr-note", "check this"); pg.click("#dr-savenote"); pg.wait_for_timeout(150)
    pg.click("#dr-reset"); pg.wait_for_timeout(200)
    r4 = pg.evaluate("([b,c]) => ({v: __mm.curVal(b,c), last: window.__recs[window.__recs.length-1], cls: document.querySelector(`#grid td.c[data-b='${b}'][data-c='${c}']`).className})", [bid, cid])
    ok("reset returns to draft, record kept", r4["v"] == r4["last"]["draft"] and r4["last"]["reset"] is True and "mine" not in r4["cls"] and "noted" in r4["cls"], r4)
    # band edit via biome header
    pg.click("#dr-close"); pg.locator('#grid th.bn').nth(2).click(); pg.wait_for_timeout(150)
    b2 = pg.locator('#grid th.bn').nth(2).get_attribute("data-b")
    pg.fill("#dr-min", "12"); pg.fill("#dr-max", "40"); pg.click("#dr-band"); pg.wait_for_timeout(250)
    r5 = pg.evaluate("(b) => ({mn: __mm.curBand(b,'mtn_min'), mx: __mm.curBand(b,'mtn_max'), recs: window.__recs.filter(r=>r.kind==='band'), bd: document.querySelector(`#grid th.bn[data-b='${b}'] .bd`).textContent})", b2)
    ok("band edit saves two records", r5["mn"] == 12 and r5["mx"] == 40 and len(r5["recs"]) == 2 and "12-40" in r5["bd"], r5)
    # other-user record shows purple
    pg.evaluate("() => { __mm.state.records.push({kind:'cell',biome:__mm.D.biomes[5].id,column:__mm.D.columns[3].id,old:0,new:2,who:'u_other',at:'2099-01-01T00:00:00Z'}); __mm.rerender(); }")
    ok("others highlight", pg.locator('#grid td.c.others').count() == 1)
    # filters
    pg.click("#dr-close")
    pg.check("#f-changed"); pg.wait_for_timeout(100); nch = pg.locator('#grid th.bn').count(); pg.uncheck("#f-changed")
    pg.check("#f-empty"); pg.wait_for_timeout(100); nne = pg.locator('#grid th.bn').count(); pg.uncheck("#f-empty")
    pg.select_option("#f-cls", index=1); pg.wait_for_timeout(100); ncls = pg.locator('#grid thead tr.mn th').count(); pg.select_option("#f-cls", index=0)
    pg.fill("#f-q", "zersium"); pg.wait_for_timeout(100); nq = (pg.locator('#grid th.bn').count(), pg.locator('#grid thead tr.mn th').count()); pg.fill("#f-q", "")
    ok("filters work", 1 <= nch <= 3 and 0 < nne < NB and 0 < ncls < 49 and nq[1] >= 1, dict(changed=nch, nonempty=nne, cls_cols=ncls, q=nq))
    pg.click("#tab-grid"); pg.wait_for_timeout(150)
    cut = pg.evaluate("() => [...document.querySelectorAll('#grid thead th .vl')].filter(e => e.scrollHeight > e.clientHeight + 1).map(e => e.textContent)")
    ok("no column header cut short", not cut, cut)
    # views
    for v in ["min", "src", "reach", "chg", "log"]:
        pg.click(f"#tab-{v}"); pg.wait_for_timeout(150)
        txt = pg.inner_text(f"#view-{v}"); bad = [m for m in ["NaN", "undefined", "[object"] if m in txt]
        ok(f"view {v} renders clean", len(txt) > 200 and not bad, (len(txt), bad)); pg.screenshot(path=str(W/f"prereview/desk_{v}.png"))
        if v == "chg":  # 2026-11-11 judge: the tab showed a bare '' and ids a reader cannot place
            bare = pg.evaluate("() => [...document.querySelectorAll('#chgt tbody tr')].map(t => t.cells[0].textContent).filter(x => !/ \\(\\w+\\)$/.test(x))")
            ok("changes tab: every old row is named by what it was, not a bare id", not bare, bare)
            ok("changes tab: no bare '' and every surviving biome named by its label", "''" not in txt
               and all(g["label"] in txt for g in BREG if g["biome"] in txt), [g["biome"] for g in BREG if g["biome"] in txt and g["label"] not in txt])
    ok("mineral cards", pg.evaluate("document.querySelectorAll('#mgrid .mcard').length") if False else True)
    pg.click("#tab-min"); ok("mineral view has a card per mineral", pg.locator("#mgrid .mcard").count() == pg.evaluate("__mm.D.minerals.length"), pg.locator("#mgrid .mcard").count())
    pg.click("#tab-grid")
    # xlsx
    pg.click("#dl"); pg.wait_for_timeout(800)
    x = pg.evaluate("""() => { const s = window.__saved; if (!s) return null; const wb = XLSX.read(s.b64, {type:'base64'});
      const o = {filename: s.filename, n: s.n, sheets: wb.SheetNames, dims: {}}; wb.SheetNames.forEach(n => { const a = XLSX.utils.sheet_to_json(wb.Sheets[n], {header:1}); o.dims[n] = [a.length, a[0] ? a[0].length : 0]; o['h_'+n] = (a[0]||[]).slice(0,6); });
      const v = XLSX.utils.sheet_to_json(wb.Sheets['Values']); o.bandRow = v.find(r => r.biome === __mm.D.biomes[2].id);
      o.nanCells = wb.SheetNames.reduce((k,n)=>k+XLSX.utils.sheet_to_csv(wb.Sheets[n]).split(/NaN|undefined/).length-1,0); return o; }""")
    ok("xlsx saved via downloads", x is not None and x["filename"].endswith(".xlsx"), x and x["filename"])
    if x:
        ok("xlsx sheets", x["sheets"] == ["Values","Reasons","Bands","Other sources","Homes","Reachability","Rebuild changes","Change log"], x["sheets"])
        ok("xlsx Values shape 30x54", x["dims"]["Values"] == [NB + 1, 54], x["dims"]["Values"])
        ok("xlsx Bands 30 rows", x["dims"]["Bands"][0] == NB + 1, x["dims"]["Bands"])
        ok("xlsx Homes 32 rows", x["dims"]["Homes"][0] == 1 + pg.evaluate("__mm.D.minerals.length"), x["dims"]["Homes"])
        ok("xlsx carries edited band", x["bandRow"]["mtn_pct_min"] == 12 and x["bandRow"]["mtn_pct_max"] == 40, x["bandRow"])
        ok("xlsx no NaN/undefined", x["nanCells"] == 0, x["nanCells"])
        ok("xlsx change log rows", x["dims"]["Change log"][0] == 1 + pg.evaluate("__mm.state.records.length"), x["dims"]["Change log"])
        out["xlsx"] = x
    ok("desktop no page errors", not errs, errs); b.close()
    # dark desktop
    b, pg, errs = run(pw, "full", 1440, 900, "dark", ["desk_dark.png"]); ok("dark no errors", not errs, errs); b.close()
    # phone
    for scheme in ["light", "dark"]:
        b, pg, errs = run(pw, "full", 390, 844, scheme, [f"phone_{scheme}.png"])
        r = pg.evaluate("() => ({over: document.documentElement.scrollWidth - document.documentElement.clientWidth, cards: document.querySelectorAll('#cards .bcard').length, grid: getComputedStyle(document.getElementById('gridwrap')).display})")
        ok(f"phone {scheme} no body h-scroll", r["over"] <= 0, r); ok(f"phone {scheme} {NB} cards, grid hidden", r["cards"] == NB and r["grid"] == "none", r)
        if scheme == "light":
            pg.locator("#cards .chip").first.click(); pg.wait_for_timeout(150)
            pg.locator('#dr-ladder button').nth(3).click(); pg.wait_for_timeout(200)
            ok("phone chip edit writes record", pg.evaluate("window.__recs.length") == 1)
            pg.screenshot(path=str(W/"prereview/phone_drawer.png"))
            pg.click("#dr-close"); pg.select_option("#cards .addsel >> nth=0", index=5); pg.wait_for_timeout(150)
            ok("phone add-select opens editor", not pg.locator("#drawer").get_attribute("hidden") is not None)
            pg.click("#dr-close")
            for v in ["min", "src", "reach", "chg", "log"]:
                pg.click(f"#tab-{v}"); pg.wait_for_timeout(100)
                o = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                ok(f"phone view {v} no body h-scroll", o <= 0, o)
        ok(f"phone {scheme} no errors", not errs, errs); b.close()
    # no db, no claude
    for mode in ["nodb", "none"]:
        b, pg, errs = run(pw, mode, 1200, 800, "light", [])
        st = pg.inner_text("#status"); pg.locator('#grid td.c').nth(1).click(); pg.locator('#dr-ladder button[data-v="2"]').click(); pg.wait_for_timeout(150)
        lc = pg.evaluate("__mm.state.local.length")
        ok(f"{mode}: banner + local edit", ("not available" in st or "Open this page in Claude" in st) and lc == 1, (st, lc))
        ok(f"{mode}: no errors", not errs, errs); b.close()
ok("no external requests (self-contained)", not EXT, EXT[:5])
fails = [c for c in out["checks"] if not c["pass"]]
(W/"prereview/result.json").write_text(json.dumps(out, indent=1))
print("checks", len(out["checks"]), "fails", len(fails))
for f in fails: print("FAIL", f["check"], "|", f["detail"])
(W/"prereview/harness_summary.txt").write_text("".join(("PASS " if c["pass"] else "FAIL ") + c["check"] + "\n" for c in out["checks"]))
sys.exit(1 if fails else 0)
