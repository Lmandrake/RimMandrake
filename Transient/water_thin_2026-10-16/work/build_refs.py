"""RM_WaterThin review inputs (pond_depth_design §4, D4): offline approximations of vanilla water as drawn, a drying-pond
mock strip, and the art_sheet texture manifest. Vanilla water draws through Map/WaterDepth from a 64px *Ramp, so its
in-game look is APPROXIMATED here as the ramp's mean colour with vanilla Ripples at low contrast; Mud/Lakebed are real.
Texture repeat is UNMEASURED (terrain UVs are world-space in the shader): shown at 8 cells per 1024 repeat, the
same assumption as Transient/pond_hollow_looks_2026-10-13/render_mockup.py."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
C = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core")
THIN = REPO / "src/RimMandrake/FlowWorks/art_source/WaterThin/RM_WaterThin_master.png"
LAKE = REPO / "src/RimMandrake/FlowWorks/Textures/Terrain/FlowWorks/RM_Lakebed_Shallow.png"
rgb = lambda p: np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
rip = rgb(C / "Ripples.png").mean(2) / 255 - .5

def water(ramp, name):
    col = rgb(C / ramp).reshape(-1, 3).mean(0)
    a = col[None, None] * (1 + .10 * rip[..., None])
    p = HERE / f"{name}_approx.png"
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
    return p, col

shallow, scol = water("WaterShallowRamp.png", "WaterShallow")
deep, dcol = water("WaterDeepRamp.png", "WaterDeep")
# mock strip: 40x8 cells at 32 px/cell, deep | shallow | thin | mud | lakebed, rough blended borders
PX, TC = 32, 8
W, H = 40 * PX, 8 * PX
def tiled(p):
    t = Image.open(p).convert("RGB").resize((TC * PX,) * 2, Image.LANCZOS)
    return np.tile(np.asarray(t).astype(np.float32), (H // (TC * PX) + 1, W // (TC * PX) + 1, 1))[:H, :W]
layers = [tiled(deep), tiled(shallow), tiled(THIN), tiled(C / "Mud.png"), tiled(LAKE)]
x = np.arange(W)[None, :].repeat(H, 0).astype(np.float32)
n = np.asarray(Image.fromarray((np.random.default_rng(5).random((H // 8, W // 8)) * 255).astype(np.uint8))
               .resize((W, H), Image.BICUBIC)).astype(np.float32) / 255 - .5
out = layers[0]
for i, L in enumerate(layers[1:], 1):
    edge = i * 8 * PX + n * PX * 1.4
    m = np.clip((x - edge) / (PX * .5) + .5, 0, 1)[..., None]
    out = out * (1 - m) + L * m
im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(im)
for i, t in enumerate(["WaterDeep (approx)", "WaterShallow (approx)", "RM_WaterThin (new)", "Mud", "RM_Lakebed_Shallow"]):
    d.rectangle([i * 8 * PX + 4, 4, i * 8 * PX + 8 + 7 * len(t), 18], fill=(0, 0, 0))
    d.text((i * 8 * PX + 7, 5), t, fill=(255, 255, 255))
im.save(HERE / "drying_pond_strip.png")

def standin(res, label, src, path):
    return {"res": res, "label": label, "source": src, "faces": {"single": str(path)}}
sz = lambda src: {"drawSize": [8, 8], "footprint": [8, 8], "source": src}
REP = "one 1024 repeat shown as 8x8 cells — terrain repeat UNMEASURED (world-space UVs), lakebed-mockup assumption"
rows = [
 {"key": "RM_WaterThin", "label": "RM_WaterThin — ankle-deep water over the pond bed (NEW, procedural)", "part": "Pond water, depth 1",
  "look": "thin", "section": "terrain", "resources": ["Terrain/FlowWorks/RM_WaterThin"], "size": sz(REP),
  "jobs": ["rm_waterthin"], "render_match": "rm_waterthin",
  "standin": standin("Terrain/FlowWorks/RM_WaterThin", "placeholder: the def points at vanilla WaterShallowRamp until approved (offline approximation of how it draws)",
                     "vanilla Core WaterShallowRamp mean colour + Ripples (Transient/water_thin_2026-10-16/work/build_refs.py)", shallow)},
]
lead = ("<p><b>RM_WaterThin, ruling D4 (by card 2026-10-16).</b> The one new texture of the pond-depth design (§4): depth 1, "
        "ankle-deep still water with the bed showing, between vanilla WaterShallow (depth 2) and Mud (just exposed). "
        "A plain tiled terrain picture like vanilla Marsh (no waterDepthShader), so the bed shows. Nothing is installed: "
        "The IN GAME column is the placeholder (vanilla WaterShallow, the deeper neighbour); the scale panels sit on vanilla Mud (the drier neighbour). Pick the render column to approve it, or reject and depth 1 falls back to WaterShallow.</p>"
        "<p>Vanilla water's look is an offline approximation (it draws through a shader from a 64 px ramp). "
        "Texture repeat is shown at 8 cells per 1024 px (unmeasured). The drying-pond strip, deep to dry, is "
        "<code>drying_pond_strip.png</code> beside this sheet's work folder: "
        "D:\\Luke\\dev\\RimMandrake\\Transient\\water_thin_2026-10-16\\work\\drying_pond_strip.png</p>")
(HERE / "water_thin.textures.json").write_text(json.dumps({"rows": rows, "lead_html": lead, "ground_terrain": "Mud"}, indent=1))
print("ok", scol.round(1), dcol.round(1))
