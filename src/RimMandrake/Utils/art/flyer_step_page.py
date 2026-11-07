#!/usr/bin/env python3
"""flyer_step_page.py - an offline page to LOOK at flyer flip-books one frame at a time, for the owner or a judge.

Owner 2026-11-07, of a flapping review page: "it goes by so quickly I just see strange static-like noise where the problem
is." So every candidate plays at the true game rate and at quarter speed, pauses, and steps a frame at a time (buttons or
arrow keys), with each facing shown full size beside a true-scale view next to a vanilla human at 64 px a cell. West is
east mirrored, as the engine draws it (Pawn_FlightTracker.GetBestFlyAnimation returns the east animation for west).
Timing copies the engine: ticksPerFrame per frame, the last frame held double. Exact PNGs, no GIF quantising.

It is a viewing page with no picks: his answer goes back through the Conductor. It never serves itself and never writes
src/. Usage:
  flyer_step_page.py --out DIR --title T [--intro TEXT]
      --cand "NAME|DIR|PREFIX|FRAMES|TICKS|CELLS|what changed" ...
CELLS is the drawn size in cells of the whole canvas (flyingAnimationDrawSize, times canvas/256 if a candidate's canvas
grew). Exit 0 written, 2 bad input.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scale_panel as SP  # noqa: E402

FACINGS = ("north", "east", "south")
GROUND = (92, 84, 66, 255)
GREY = (120, 120, 120, 255)


def scene(png: Path, cells: float, human, hm: int, hoff: int, mirror: bool) -> Image.Image:
    """Bird and a vanilla human at 64 px a cell over plain ground, the bird's mesh centred beside the human."""
    sz = max(1, round(cells * SP.SCENE_PPC))
    w, h = hm + sz + 24, max(hm + hoff, sz) + 8
    bg = Image.new("RGBA", (w, h), GROUND)
    bg.alpha_composite(human, (0, h - hm - hoff - 4))
    a = Image.open(png).convert("RGBA").resize((sz, sz), Image.LANCZOS)
    if mirror:
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    bg.alpha_composite(a, (hm + 16, (h - sz) // 2))
    return bg


def full(png: Path, mirror: bool) -> Image.Image:
    a = Image.open(png).convert("RGBA")
    if mirror:
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    up = 2 if a.width <= 160 else 1
    if up > 1:
        a = a.resize((a.width * up, a.height * up), Image.NEAREST)
    base = Image.new("RGBA", a.size, GREY)
    base.alpha_composite(a)
    return base


def build(out: Path, title: str, intro: str, cands: list[dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    human, hm, hoff = SP.human_sprite(SP.SCENE_PPC)
    data = []
    for c in cands:
        src, d = Path(c["dir"]), out / c["name"]
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        views = {}
        for facing in FACINGS + ("west",):
            real = "east" if facing == "west" else facing
            mirror = facing == "west"
            files = []
            for i in range(1, c["frames"] + 1):
                png = src / f"{c['prefix']}{i}_{real}.png"
                if not png.exists():
                    raise SystemExit(f"missing {png}")
                f1, f2 = f"{facing}_{i}.png", f"{facing}_{i}_scale.png"
                full(png, mirror).save(d / f1)
                scene(png, c["cells"], human, hm, hoff, mirror).save(d / f2)
                files.append([f"{c['name']}/{f1}", f"{c['name']}/{f2}"])
            views[facing] = files
        ticks = [c["ticks"]] * (c["frames"] - 1) + [2 * c["ticks"]]
        data.append(dict(name=c["name"], note=c["note"], ticks=ticks, views=views))
    page = TEMPLATE.replace("__TITLE__", html.escape(title)).replace("__INTRO__", html.escape(intro))
    page = page.replace("__DATA__", json.dumps(data))
    (out / "index.html").write_text(page)


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><title>__TITLE__</title>
<style>
body{background:#1e1e1e;color:#ddd;font:14px system-ui,sans-serif;margin:16px}
h1{font-size:20px} h2{font-size:17px;margin:22px 0 4px} .note{max-width:1100px;color:#cfc;margin:4px 0 8px}
.bar{position:sticky;top:0;background:#1e1e1e;padding:6px 0;z-index:2} button{font-size:14px;margin-right:4px}
.row{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end} figure{margin:0;text-align:center}
figcaption{color:#ff6}.full{position:relative;display:inline-block}
.full img{display:block;image-rendering:pixelated}.hx,.vx{position:absolute;background:rgba(0,230,255,.55)}
.hx{left:0;right:0;height:1px}.vx{top:0;bottom:0;width:1px}.state{font-family:monospace;color:#9cf}
</style></head><body><h1>__TITLE__</h1><p class="note">__INTRO__</p>
<p>Keys: space plays or pauses the candidate under the mouse, left and right arrows step a frame. Each candidate starts
paused on frame 1. The crosshair is fixed on the canvas, so a head that moves shows against it.</p>
<div id="all"></div>
<script>
const DATA=__DATA__;const TICK_MS=1000/60;let hover=null;
function mk(t,c,txt){const e=document.createElement(t);if(c)e.className=c;if(txt!==undefined)e.textContent=txt;return e}
DATA.forEach(c=>{
  const sec=mk('section');sec.appendChild(mk('h2','',c.name));sec.appendChild(mk('p','note',c.note));
  const bar=mk('div','bar');const st={k:0,speed:0,timer:null};
  const b=[['Play 1x',1],['Play 1/4x',0.25],['Pause',0]];
  b.forEach(([t,s])=>{const x=mk('button','',t);x.onclick=()=>play(s);bar.appendChild(x)});
  const prev=mk('button','','< Frame');prev.onclick=()=>{play(0);show(st.k-1)};bar.appendChild(prev);
  const next=mk('button','','Frame >');next.onclick=()=>{play(0);show(st.k+1)};bar.appendChild(next);
  const lab=mk('span','state');bar.appendChild(lab);sec.appendChild(bar);
  const imgs=[];const row=mk('div','row');
  ['north','east','west','south'].forEach(f=>{
    const fig=mk('figure');fig.appendChild(mk('figcaption','',f+(f==='west'?' (east mirrored, as the engine draws it)':'')));
    const box=mk('div','full');const im=mk('img');box.appendChild(im);
    const h=mk('div','hx');h.style.top='50%';const v=mk('div','vx');v.style.left='50%';box.appendChild(h);box.appendChild(v);
    fig.appendChild(box);const sc=mk('img');sc.style.display='block';sc.style.marginTop='6px';fig.appendChild(sc);
    fig.appendChild(mk('div','','beside a vanilla human, 64 px a cell'));row.appendChild(fig);imgs.push([f,im,sc]);
    c.views[f].forEach(p=>{new Image().src=p[0];new Image().src=p[1]});
  });
  sec.appendChild(row);document.getElementById('all').appendChild(sec);
  sec.onmouseenter=()=>{hover=api};
  function show(k){const n=c.ticks.length;st.k=((k%n)+n)%n;
    imgs.forEach(([f,im,sc])=>{im.src=c.views[f][st.k][0];sc.src=c.views[f][st.k][1]});
    lab.textContent=' frame '+(st.k+1)+' of '+n+', on screen '+c.ticks[st.k]+' ticks'+(st.speed?' (playing at '+st.speed+'x)':' (paused)')}
  function tick(){show(st.k+1);st.timer=setTimeout(tick,c.ticks[st.k]*TICK_MS/st.speed)}
  function play(s){clearTimeout(st.timer);st.speed=s;if(s)st.timer=setTimeout(tick,c.ticks[st.k]*TICK_MS/s);show(st.k)}
  const api={play:play,show:show,st:st};show(0);
});
document.addEventListener('keydown',e=>{if(!hover)return;
  if(e.key===' '){e.preventDefault();hover.play(hover.st.speed?0:1)}
  if(e.key==='ArrowRight'){hover.play(0);hover.show(hover.st.k+1)}
  if(e.key==='ArrowLeft'){hover.play(0);hover.show(hover.st.k-1)}});
</script></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--intro", default="")
    ap.add_argument("--cand", action="append", required=True)
    a = ap.parse_args()
    cands = []
    for s in a.cand:
        parts = s.split("|")
        if len(parts) != 7:
            print(f"--cand needs 7 fields separated by |, got {len(parts)}: {s}", file=sys.stderr)
            return 2
        name, d, prefix, frames, ticks, cells, note = parts
        cands.append(dict(name=name, dir=d, prefix=prefix, frames=int(frames), ticks=int(ticks), cells=float(cells), note=note))
    build(Path(a.out), a.title, a.intro, cands)
    print(f"wrote {Path(a.out) / 'index.html'}: {len(cands)} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
