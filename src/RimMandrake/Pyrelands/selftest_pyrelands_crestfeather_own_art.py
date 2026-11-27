#!/usr/bin/env python3
"""T_CRESTFEATHER_OWN_ART_OFFLINE: the pristine firehawk crestfeather has a look of its own (bar crestfeather_has_its_own_look,
Pyrelands vision.md 0.2.0 item 15; owner 2026-11-13: "That gives a great reason for players to hunt the Firehawk.").

What it reads, and the range it covers
  The def   src/RimMandrake/Pyrelands/Defs/ThingDefs_Items/RM_PristineFirehawkCrestfeather.xml. EVERY <texPath> in the def
            (not only the first), and every colour line (<color>, <colorTwo>) inside every <graphicData>. The game can only
            vary the picture through these: the item has no stuff, no quality graphic, no random graphic (Graphic_Single),
            so a ground, a stack size, a seed or a setting draws the same texture. The texPath must be the def's own path.
  Vanilla   a texPath whose last part or whole path names a vanilla texture (the ludeon.* rows of the bundle texture
            inventory, observed/inventory/bundle_textures/index.csv) is red, and so is "ThrumboHorn" anywhere in it. The
            picture's bytes are compared (sha256) with every vanilla texture of the same width and height, and its
            perceptual hash (artledger.dhash) with the borrowed thrumbo horn, so a byte copy or a rescaled copy of the old
            stand-in is red. When the inventory cannot be read the check says UNMEASURED and fails: it never passes blind.
  The file  Textures/<texPath>.png exists in the mod, is RGBA with real alpha: some pixels fully transparent (the item
            lies on the ground, the canvas is not a filled square) and some solid (alpha >= SOLID_ALPHA: the item is there).
  The judge the art ledger (infrastructure/state/art/events, folded by artledger.Index) holds the slot's LIVE event with the
            picture's own sha, put there by `art.py install` whose `why` cites a committed verdict file; that file records
            verdict keep for the same sha, by a judge whose agent is not the maker recorded for the render (the artpipe
            job that drew it), and "made_it": false.
Left out (and why): whether the picture is beautiful or reads as a feather is the judge's verdict, not this check's; an
  edited copy of some OTHER vanilla texture (not the horn) at another size is the judge's E1/E2 rule; the game load
  (does the texture load) is the live half (sc_firehawk_rewards).
Numbers: TRANSPARENT_MIN, OPAQUE_MIN and SOLID_ALPHA are our own rule for "real alpha" (a cut-out item, neither a filled square nor an
  empty canvas); NEAR_HORN is our own rule for a perceptual near-duplicate on the 16x16 dhash (256 bits), set between two
  readings measured 2026-11-26: the vanilla horn upscaled to 256 px and tinted ember-orange reads 10 from the horn (the
  art ledger's own ban fold, BAN_NEAR, is 10), the judged crestfeather render reads 84. Each prints its reading.

Run: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_crestfeather_own_art.py   (exit 0 = PASS)
"""
import csv
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))

DEF_XML = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_PristineFirehawkCrestfeather.xml")
DEFNAME = "RM_PristineFirehawkCrestfeather"
OWN = "Things/Item/Special/RM_PristineFirehawkCrestfeather/RM_PristineFirehawkCrestfeather"   # the bar's own path
MOD = "src/RimMandrake/Pyrelands"
TEX_ROOT = os.path.join(HERE, "Textures")
VANILLA_INV = os.environ.get("RM_VANILLA_TEX_INV",
                             "/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures")
HORN = "ThrumboHorn"
TRANSPARENT_MIN = 0.10   # our own rule: >= 10 % of the canvas fully transparent (a cut-out, not a filled square)
OPAQUE_MIN = 0.02        # our own rule: >= 2 % solid (an item is drawn, not a faint smear)
SOLID_ALPHA = 240        # our own rule: alpha >= 240 of 255 is solid (<= 6 % of the ground shows through, unseen at play
                         # zoom). Measured 2026-11-26: the judged render puts 90 % of its visible pixels at >= 240 but only
                         # 4.5 % at exactly 255 (opaque 0.010 of the canvas at 255, failing a 255 rule on a solid feather);
                         # the 204 vanilla item textures pass the same count at 240 as at 255 (140 of 204, least solid 0.074)
NEAR_HORN = 40           # our own rule, between measured 10 (tinted horn) and 84 (the render): at or under = the horn


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def read_def(path):
    raw = open(path, encoding="utf-8").read()
    root = ET.fromstring(raw)
    d = next((x for x in root.iter("ThingDef") if x.findtext("defName") == DEFNAME), None)
    return raw, d


def vanilla_rows():
    idx = os.path.join(VANILLA_INV, "index.csv")
    if not os.path.exists(idx):
        return None
    return [r for r in csv.DictReader(open(idx, encoding="utf-8")) if r["sourceKey"].startswith("ludeon.")]


def check(def_xml=DEF_XML, tex_root=TEX_ROOT, index=None, verdict_root=REPO):
    """-> list of (name, ok, reading). Every check prints its reading, its limit and its case count."""
    out = []
    raw, d = read_def(def_xml)
    if d is None:
        return [("def exists", False, "no ThingDef %s in %s" % (DEFNAME, def_xml))]
    texs = [t.text.strip() for t in d.iter("texPath") if t.text]
    gds = list(d.iter("graphicData"))
    main = (d.findtext("graphicData/texPath") or "").strip()
    out.append(("texPath is the def's own path", main == OWN and bool(texs),
                "graphicData/texPath=%r, limit %r; %d texPath tag(s) read" % (main, OWN, len(texs))))
    horn = [t for t in texs if HORN.lower() in t.lower()]
    out.append(("no ThrumboHorn", not horn, "%d of %d texPath(s) name %s: %s" % (len(horn), len(texs), HORN, horn or "none")))
    tints = [(c.tag, (c.text or "").strip()) for g in gds for c in g if c.tag in ("color", "colorTwo")]
    out.append(("no colour tint line", not tints, "%d colour line(s) in %d graphicData: %s" % (len(tints), len(gds), tints or "none")))

    vrows = vanilla_rows()
    if vrows is None:
        out.append(("no vanilla texture", False, "UNMEASURED: vanilla inventory %s unreadable" % VANILLA_INV))
    else:
        vnames = {r["m_Name"].lower() for r in vrows}
        named = [t for t in texs if t.rsplit("/", 1)[-1].lower() in vnames]
        out.append(("texPath names no vanilla texture", not named and len(vnames) > 1000,
                    "%d of %d texPath(s) end in one of %d vanilla texture names: %s"
                    % (len(named), len(texs), len(vnames), named or "none")))

    png = os.path.join(tex_root, OWN + ".png")
    if not os.path.isfile(png):
        out.append(("picture exists", False, "missing: %s" % os.path.relpath(png, REPO)))
        return out
    data = open(png, "rb").read()
    sha = _sha(data)
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(data))
    a = im.convert("RGBA").getchannel("A")
    n = im.width * im.height
    hist = a.histogram()
    t_frac, o_frac = hist[0] / n, sum(hist[SOLID_ALPHA:]) / n
    out.append(("picture exists with real alpha",
                im.mode in ("RGBA", "LA", "P") and "A" in im.convert("RGBA").getbands() and t_frac >= TRANSPARENT_MIN
                and o_frac >= OPAQUE_MIN,
                "%s %dx%d mode %s: transparent %.3f (limit >= %.2f), solid (alpha >= %d) %.3f (limit >= %.2f) of %d px"
                % (os.path.basename(png), im.width, im.height, im.mode, t_frac, TRANSPARENT_MIN, SOLID_ALPHA, o_frac,
                   OPAQUE_MIN, n)))

    if vrows is not None:
        same = [r for r in vrows if r["width"] == str(im.width) and r["height"] == str(im.height)]
        hit, read = [], 0
        for r in same:
            p = os.path.join(VANILLA_INV, r["file"])
            if os.path.exists(p):
                read += 1
                if _sha(open(p, "rb").read()) == sha:
                    hit.append(r["file"])
        out.append(("picture is no vanilla byte copy", not hit and read == len(same),
                    "%d of %d same-size (%dx%d) vanilla textures read; %d identical: %s"
                    % (read, len(same), im.width, im.height, len(hit), hit or "none")))
        import artledger as L
        hp = os.path.join(VANILLA_INV, "ludeon.rimworld.core", HORN + ".png")
        if os.path.exists(hp):
            dist = L.hamming(L.dhash(data)[0], L.dhash(open(hp, "rb").read())[0])
            out.append(("picture is not the horn redrawn", dist > NEAR_HORN,
                        "dhash distance to vanilla %s = %d (limit > %d of 256 bits)" % (HORN, dist, NEAR_HORN)))
        else:
            out.append(("picture is not the horn redrawn", False, "UNMEASURED: %s unreadable" % hp))

    # the judge: the art ledger's live event for the slot, its why -> a committed verdict file
    import artledger as L
    if index is None:
        index = L.Index()
    ev = index.live.get((MOD, OWN + ".png"))
    live_ok = bool(ev) and ev.get("sha") == sha
    out.append(("art ledger: live event holds this picture", live_ok,
                "live event %s sha %s, file sha %s; %d live slots folded"
                % ((ev or {}).get("id"), ((ev or {}).get("sha") or "-")[:12], sha[:12], len(index.live))))
    why = (ev or {}).get("why") or ""
    m = re.match(r"delegated: art (\S+\.json)", why)
    vpath = os.path.join(verdict_root, m.group(1)) if m else None
    if not (vpath and os.path.isfile(vpath)):
        out.append(("art ledger cites a judge's verdict file", False, "live why=%r (needs 'delegated: art <verdict .json>' "
                                                                       "naming a file in the repo)" % why[:160]))
        return out
    v = json.load(open(vpath, encoding="utf-8"))
    judge, maker = v.get("judge") or {}, v.get("maker") or {}
    j_agent, m_agent = str(judge.get("agent") or ""), str(maker.get("agent") or "")
    ok = (v.get("sha") == sha and str(v.get("verdict", "")).lower() == "keep" and j_agent and m_agent
          and j_agent != m_agent and judge.get("made_it") is False and m_agent not in j_agent and j_agent not in m_agent)
    out.append(("judge's keep verdict for this sha, by a judge that did not make it", bool(ok),
                "%s: verdict %r, sha %s (file %s), judge %r (made_it=%r), maker %r"
                % (os.path.relpath(vpath, verdict_root), v.get("verdict"), str(v.get("sha"))[:12], sha[:12], j_agent,
                   judge.get("made_it"), m_agent)))
    return out


def main():
    rows = check()
    bad = [r for r in rows if not r[1]]
    for name, ok, reading in rows:
        print("%s  %s: %s" % ("PASS" if ok else "FAIL", name, reading))
    worst = bad[0][0] if bad else "none"
    print("T_CRESTFEATHER_OWN_ART_OFFLINE: %s: %d of %d checks failed (worst: %s)"
          % ("FAIL" if bad else "PASS", len(bad), len(rows), worst))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
