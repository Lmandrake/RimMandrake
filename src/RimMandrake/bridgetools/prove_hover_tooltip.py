#!/usr/bin/env python3
"""Live probe for PLAYER_HOVER_PROBE_TOOLTIP_DRAWN: does rimworld/set_hover_target make RimWorld DRAW a tooltip that a
screenshot can read — on a gizmo (A1), on a bill (A2) and on a map thing (A3)?

    python.exe src/RimMandrake/bridgetools/prove_hover_tooltip.py --clause A1 < /dev/null

Needs any throwaway Playing map (a dev quicktest is enough) on any list; no mod of ours is involved. The game is
paused for the whole probe so nothing moves between the two frames. For each target:
  1. clear the hover (rimworld/clear_hover_target), screenshot  -> the BASE frame;
  2. set_hover_target on the target (ui-element targetId; a map cell for A3), screenshot -> the HOVER frame;
  3. tooltip_detect.find_tooltip(base, hover): a new region that is a dark box holding light text pixels.
A1 hovers up to 4 gizmos of a selected colonist; A2 builds a ButcherSpot, adds a ButcherCorpseFlesh bill, opens the
Bills tab and hovers up to 8 controls of the bills surface; A3 hovers a colonist's cell and the ButcherSpot's cell and
counts a tooltip box OR a changed bottom-left mouse-over readout (vanilla's only hover text on the map).
Every frame pair, the crop of each found tooltip and a result.json go to
D:\\ClaudeWork\\rimmandrake\\scratch\\hover_probe\\<UTC stamp>\\ so a person or judge can read the text.
Exit 0 = the clause's target drew readable hover text, 1 = it did not (the answer "no", recorded), 2 = no verdict
(no bridge, no map, nothing to hover, a screenshot missing).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)
from PIL import Image  # noqa: E402

import tooltip_detect as td  # noqa: E402

OUT_ROOT_WIN = r"D:\ClaudeWork\rimmandrake\scratch\hover_probe"
SPOT, RECIPE = "ButcherSpot", "ButcherCorpseFlesh"   # Core: Buildings_Production.xml, Recipes_Butchery.xml
BILL_TABS = ("ITab_Bills", "RimWorld.ITab_Bills", "Bills")


class NoVerdict(Exception):
    pass


def out_root():
    root = OUT_ROOT_WIN if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/scratch/hover_probe"
    d = os.path.join(root, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    os.makedirs(d, exist_ok=True)
    return d


def walk(o, found):
    """Every dict carrying a targetId, depth first."""
    if isinstance(o, dict):
        if o.get("targetId"):
            found.append(o)
        for v in o.values():
            walk(v, found)
    elif isinstance(o, list):
        for v in o:
            walk(v, found)
    return found


class Probe:
    def __init__(self, c, outdir):
        self.c, self.outdir, self.n, self.log = c, outdir, 0, []

    def call(self, tool, params=None):
        r = self.c.call(tool, params or {}, check=False)
        self.log.append({"tool": tool, "params": params or {}, "reply": str(r)[:600]})
        return r if isinstance(r, dict) else {}

    def shot(self, tag):
        self.n += 1
        name = "hover_%02d_%s_%d" % (self.n, tag, int(time.time() * 1000) % 100000)
        r = self.call("rimworld/take_screenshot", {"fileName": name, "suppressMessage": True})
        p = r.get("path") or r.get("screenshotPath")
        for _ in range(20):
            if p and os.path.exists(p) and os.path.getsize(p) > 0:
                break
            time.sleep(0.5)
        if not (p and os.path.exists(p)):
            raise NoVerdict("screenshot %s has no readable file: %s" % (tag, str(r)[:300]))
        time.sleep(0.3)
        dst = os.path.join(self.outdir, os.path.basename(p))
        shutil.copyfile(p, dst)
        return dst

    def pair(self, tag, hover_params):
        """Base frame, hover, hover frame, clear. Returns the row."""
        self.call("rimworld/clear_hover_target")
        time.sleep(0.4)
        base = self.shot(tag + "_base")
        hp = dict(hover_params)
        hp.setdefault("durationMs", 10000)
        hp.setdefault("settleMs", 600)
        h = self.call("rimworld/set_hover_target", hp)
        time.sleep(0.8)
        hov = self.shot(tag + "_hover")
        self.call("rimworld/clear_hover_target")
        a, b = Image.open(base), Image.open(hov)
        tip = td.find_tooltip(a, b)
        ro = td.readout_changed(a, b)
        row = {"tag": tag, "hover": hp, "hoverReply": str(h)[:300], "hoverOk": h.get("success") is True,
               "base": base, "hoverFrame": hov, "tooltip": tip, "readout": ro}
        if tip["drawn"]:
            crop = os.path.join(self.outdir, "%s_TOOLTIP.png" % tag)
            b.crop(tuple(tip["box"])).save(crop)
            row["tooltipCrop"] = crop
        return row


HUD_WAIT_S = 25   # jawa/clear_ui's own lease is 20 s of realtime by default


def clear_ui(p, **kw):
    """jawa/clear_ui with the HUD left ON. clear_ui defaults hideHud=true (vanilla screenshot mode under a 20 s
    lease), and screenshot mode stops RimWorld drawing the gizmo grid, the inspect tabs and every tooltip: the
    2026-11-06 A1 run read an Inspect surface with 0 elements and no GizmoGridDrawer
    (GAMEENV_FIX_PROOFSITE_E94045E9_ITEMS_WAIT).
    hideHud=false never switches off a lease someone else took, so wait it out; still hidden -> no verdict."""
    kw["hideHud"] = False
    r = p.call("jawa/clear_ui", kw)
    end = time.time() + HUD_WAIT_S
    while r.get("hudHidden") and time.time() < end:
        time.sleep(1.0)
        r = p.call("jawa/clear_ui", {"devWindows": False, "clearSelection": False, "hideHud": False})
    if r.get("hudHidden"):
        raise NoVerdict("HUD still hidden (screenshot mode) after %d s: no gizmo, tab or tooltip is drawn: %s"
                        % (HUD_WAIT_S, str(r)[:200]))
    return r


def ensure_map(p):
    mi = p.call("jawa/map_info")
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
    if sx <= 20 or sz <= 20:
        raise NoVerdict("no Playing map: %s" % str(mi)[:200])
    p.call("rimworld/pause_game", {"pause": True})
    clear_ui(p, all=True, devWindows=True)
    return sx, sz


def colonist(p):
    cols = p.call("rimworld/list_colonists", {"currentMapOnly": True})
    lst = cols.get("colonists") or cols.get("pawns") or []
    if not lst:
        raise NoVerdict("no colonist on the map: %s" % str(cols)[:200])
    return lst[0]


def ui_targets(p, want):
    lay = p.call("rimworld/get_ui_layout")
    els = []
    for s in lay.get("surfaces") or []:
        kind = (str(s.get("type")) + " " + str(s.get("surfaceId") or s.get("id") or "")).lower()
        if any(w in kind for w in want):
            els.extend(walk(s, []))
    return [e for e in els if e is not None], lay


def clause_gizmo(p):
    pawn = colonist(p)
    pid = pawn.get("pawnId") or pawn.get("id")
    p.call("rimworld/select_pawn", {"pawnId": pid})
    p.call("rimworld/jump_camera_to_pawn", {"pawnId": pid})
    p.call("rimworld/list_selected_gizmos")
    els, lay = ui_targets(p, ("gizmo",))
    if not els:
        raise NoVerdict("no gizmo element in get_ui_layout: %s" % str(lay)[:400])
    return [p.pair("gizmo%d" % i, {"targetId": e["targetId"]}) for i, e in enumerate(els[:4])]


def stage_spot(p, sx, sz):
    cx, cz = sx // 2, sz // 2
    p.call("jawa/destroy_batch", {"rects": "%d,%d,5,5" % (cx - 2, cz - 2), "categories": "Plant,Item,Filth,Building"})
    b = p.call("jawa/build_batch", {"ops": "%s:%d,%d,0" % (SPOT, cx, cz), "faction": "player", "readBack": 1})
    # build_batch's read-back (things[]) carries def/x/z but NO ThingID (JawaBenchMapTools.cs BuildBatch), so
    # the id comes from jawa/list_things at the cell. Read `survived`, not `placed` (the tool's own warning).
    if not b.get("success") or int(b.get("survived") or 0) < 1:
        raise NoVerdict("could not place a %s: %s" % (SPOT, str(b)[:300]))
    lt = p.call("jawa/list_things", {"defName": SPOT, "rect": "%d,%d,1,1" % (cx, cz), "limit": 5})
    ids = [r.get("id") for r in (lt.get("things") or []) if isinstance(r, dict) and r.get("id")]
    if not ids:
        raise NoVerdict("placed a %s at %d,%d but jawa/list_things there names no id: %s"
                        % (SPOT, cx, cz, str(lt)[:300]))
    return ids[0], cx, cz


def clause_bill(p, sx, sz):
    sid, cx, cz = stage_spot(p, sx, sz)
    ba = p.call("jawa/bill_add", {"giverId": sid, "recipe": RECIPE})
    if ba.get("success") is False:
        raise NoVerdict("bill_add refused: %s" % str(ba)[:300])
    p.call("jawa/select_things", {"ids": str(sid), "action": "select", "jumpCamera": True})
    opened = None
    for tab in BILL_TABS:
        r = p.call("rimworld/open_inspect_tab", {"inspectTabId": tab})
        if r.get("success"):
            opened = tab
            break
    if not opened:
        raise NoVerdict("could not open the Bills tab: %s" % str(p.call("rimworld/list_inspect_tabs"))[:300])
    time.sleep(0.6)
    els, lay = ui_targets(p, ("bill",))
    if not els:   # the tab surface may be named for the inspect pane rather than for bills
        els, lay = ui_targets(p, ("itab", "inspect"))
    if not els:
        raise NoVerdict("no element on the bills surface: %s" % str(lay)[:400])
    return [p.pair("bill%d" % i, {"targetId": e["targetId"]}) for i, e in enumerate(els[:8])]


def clause_mapthing(p, sx, sz):
    _, cx, cz = stage_spot(p, sx, sz)
    clear_ui(p, all=True, clearSelection=True)
    p.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
    rows = [p.pair("spotcell", {"x": cx, "z": cz})]
    pawn = colonist(p)
    pid = pawn.get("pawnId") or pawn.get("id")
    p.call("rimworld/jump_camera_to_pawn", {"pawnId": pid})
    clear_ui(p, all=True, clearSelection=True)
    rows.append(p.pair("pawn", {"pawnId": pid}))
    return rows


def verdict(rows, readout_counts):
    # A "no" is only an answer if the bridge really set a hover; none accepted = nothing was asked.
    if rows and not any(r.get("hoverOk") for r in rows):
        raise NoVerdict("rimworld/set_hover_target succeeded on no target: %s" % rows[0].get("hoverReply"))
    for r in rows:
        if not r.get("hoverOk"):
            continue   # a box in a frame no hover was set for is not this hover's tooltip
        if r["tooltip"]["drawn"] or (readout_counts and r["readout"]["changed"]):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clause", choices=("A1", "A2", "A3"), required=True)
    a = ap.parse_args()
    import rimbridge_client as rb
    outdir = out_root()
    res = {"clause": a.clause, "outdir": outdir}
    code = 2
    p = None
    try:
        h, port, t = rb.resolve_endpoint()
        c = rb.RimBridge(host=h, port=port, token=t, timeout=120)
        c.connect()
        p = Probe(c, outdir)
        sx, sz = ensure_map(p)
        if a.clause == "A1":
            rows = clause_gizmo(p)
        elif a.clause == "A2":
            rows = clause_bill(p, sx, sz)
        else:
            rows = clause_mapthing(p, sx, sz)
        res["rows"] = rows
        ok = verdict(rows, readout_counts=(a.clause == "A3"))
        res["verdict"] = "DRAWN" if ok else "NOT_DRAWN"
        code = 0 if ok else 1
    except NoVerdict as e:
        res["verdict"] = "NO VERDICT: %s" % e
    except Exception as e:  # bridge down, endpoint missing
        res["verdict"] = "NO VERDICT: %s: %s" % (type(e).__name__, str(e)[:300])
    finally:
        if p is not None:
            try:
                p.call("rimworld/clear_hover_target")
            except Exception:
                pass
            res["calls"] = p.log
        with open(os.path.join(outdir, "result_%s.json" % a.clause), "w") as f:
            json.dump(res, f, indent=1, default=str)
    for r in res.get("rows") or []:
        print("%-10s tooltip=%s box=%s readoutChanged=%s crop=%s" % (
            r["tag"], r["tooltip"]["drawn"], r["tooltip"]["box"], r["readout"]["changed"], r.get("tooltipCrop", "-")))
    print("%s %s  (%s)" % (a.clause, res["verdict"], os.path.join(outdir, "result_%s.json" % a.clause)))
    return code


if __name__ == "__main__":
    sys.exit(main())
