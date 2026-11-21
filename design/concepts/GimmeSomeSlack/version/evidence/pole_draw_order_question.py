import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
out = sys.argv[1]; tex = sys.argv[2]
im = Image.open(tex).convert("RGBA")
fig, axes = plt.subplots(1, 3, figsize=(13, 6.2))
def mast(ax, x, z, front_of=None, label="mast (BuildingOnTop now)", zo=5, head_only_over=False):
    ax.imshow(im, extent=(x + 0.5 - 1, x + 0.5 + 1, z, z + 4), zorder=zo)
    if head_only_over:
        W, H = im.size
        ax.imshow(im.crop((0, 0, W, H // 4)), extent=(x + 0.5 - 1, x + 0.5 + 1, z + 3, z + 4), zorder=8)
    ax.add_patch(Rectangle((x, z), 1, 1, fill=False, ls=":", ec="k", zorder=9))
    ax.text(x + 0.5, z - 0.35, label, ha="center", fontsize=8, zorder=9)
def thing(ax, x0, z0, w, h, color, label, zo, foot):
    ax.add_patch(Rectangle((x0, z0), w, h, fc=color, ec="k", alpha=0.85, zorder=zo))
    ax.text(x0 + w + 0.15 if w < 2 else x0 + 0.15, z0 + h - 0.3, label, ha="left", va="top", fontsize=8, zorder=11,
            bbox=dict(fc="white", alpha=0.8, ec="none"))
    ax.add_patch(Rectangle((foot[0], foot[1]), foot[2], 1, fill=False, ls="--", ec="k", zorder=9))
cases = [
    ("FIXED: tree NORTH of the mast\nmast (south) now drawn in front", lambda ax: (thing(ax, 2.0, 6.0, 3, 3.5, "#6a9a4a", "oak, foot 1 cell north\n(common layer, lower lift)", 3, (3, 6, 1)), mast(ax, 3, 5))),
    ("OPEN (BUILDING_LAYER_REACH):\nBuilding-layer picture reaching north from\nthe cell SOUTH of the mast: drawn behind it,\nthe bar wants it in front", lambda ax: (mast(ax, 3, 5), thing(ax, 3, 4, 1, 2.5, "#b08a5a", "tall building\n(Building layer,\ndrawOffset 0.75)", 3, (3, 4, 1)))),
    ("OPEN (HEAD_OVER_SOUTHERN_PICTURE):\na tree 12 cells tall south of the mast:\nits canopy is drawn behind the mast head,\nwhich draws above pawns like the wires", lambda ax: (thing(ax, 0.5, 3.0, 6, 10, "#4f7d3a", "greatbole-class tree\n(visual 12, foot 2 cells south)\ncovers the mast body (correct)", 6, (3, 3, 1)), mast(ax, 3, 5, zo=4, head_only_over=True),
        ax.add_patch(Rectangle((2.5, 8.0), 2, 1, fc="none", ec="red", lw=2, zorder=10)), ax.text(4.7, 8.5, "head overlay\n(PawnState)", color="red", fontsize=8, zorder=10))),
]
for ax, (title, draw) in zip(axes, cases):
    draw(ax)
    ax.set_xlim(-0.5, 7.5); ax.set_ylim(2.5, 13.5); ax.set_aspect("equal")
    ax.set_xticks(range(0, 8)); ax.set_yticks(range(3, 14)); ax.grid(alpha=0.25)
    ax.set_title(title, fontsize=9); ax.set_xlabel("cell x"); ax.set_ylabel("cell z (north up)")
fig.suptitle("Gimme Some Slack 0.1.1, bar poles_draw_in_front_when_south: what the mast's own layer fixes and what it cannot\n"
             "(drawn order = printed altitude from selftest_gss_pole_south_draws_front.py; dashed square = each thing's foot cell)", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(out, dpi=110)
