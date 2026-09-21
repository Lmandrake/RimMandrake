"""
Render RimWorld-style orthographic facings (south/east/north) from a TripoSR
mesh, using matplotlib's Agg backend (no GL/EGL needed -- WSL2 here has no
/dev/dri node, so pyrender/EGL and GLX-based renderers are not viable).

Convention: TripoSR's own get_spherical_cameras() places azimuth=0 at +X,
increasing towards +Y, with the single input photo treated as the az=0 view.
So: south (front, matches input photo) = azimuth 0; east = azimuth 90;
north (back) = azimuth 180. A modest positive elevation is used to mimic
RimWorld's slightly-downward structure camera.
"""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.collections

MESH_PATH = sys.argv[1] if len(sys.argv) > 1 else "output/0/mesh.obj"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "output/0"
ELEV_DEG = 22.0
CANVAS_W, CANVAS_H = 512, 640

FACINGS = [
    ("south", 0.0),
    ("east", 90.0),
    ("north", 180.0),
]


def load_mesh_with_color(path):
    m = trimesh.load(path, force="mesh", process=False)
    if hasattr(m.visual, "vertex_colors") and m.visual.vertex_colors is not None:
        vc = np.asarray(m.visual.vertex_colors)[:, :3].astype(np.float32) / 255.0
    else:
        vc = np.tile(np.array([0.6, 0.6, 0.65], dtype=np.float32), (len(m.vertices), 1))
    return m, vc


def render_view(mesh, vcolors, azimuth_deg, elevation_deg, out_path, canvas_w, canvas_h):
    verts = mesh.vertices
    faces = mesh.faces

    az = np.radians(azimuth_deg)
    el = np.radians(elevation_deg)

    # camera direction on unit sphere, matching tsr.utils.get_spherical_cameras
    cam_dir = np.array([
        np.cos(el) * np.cos(az),
        np.cos(el) * np.sin(az),
        np.sin(el),
    ])
    dist = 2.5 * np.max(np.linalg.norm(verts - verts.mean(0), axis=1))
    cam_pos = cam_dir * dist

    forward = -cam_dir
    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, world_up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)

    rel = verts - cam_pos
    x_screen = rel @ right
    y_screen = rel @ true_up
    depth = rel @ forward  # larger = farther

    face_depth = depth[faces].mean(axis=1)
    order = np.argsort(-face_depth)  # painter's algorithm: farthest first

    face_colors = vcolors[faces].mean(axis=1)
    # simple directional shading for readability
    normals = mesh.face_normals
    light_dir = forward * -1.0
    ndl = np.clip((normals @ light_dir), 0.15, 1.0)
    shaded = np.clip(face_colors * (0.55 + 0.45 * ndl[:, None]), 0, 1)

    dpi = 100
    fig = plt.figure(figsize=(canvas_w / dpi, canvas_h / dpi), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("none")
    ax.set_aspect("equal")
    ax.axis("off")

    tris = np.stack([x_screen[faces], y_screen[faces]], axis=-1)  # (M,3,2)
    coll = matplotlib.collections.PolyCollection(
        tris[order], facecolors=shaded[order], edgecolors=shaded[order], linewidths=0.15,
        antialiaseds=True,
    )
    ax.add_collection(coll)

    span = np.max(np.abs(np.concatenate([x_screen, y_screen]))) * 1.15
    ax.set_xlim(-span, span)
    ax.set_ylim(-span * (canvas_h / canvas_w), span * (canvas_h / canvas_w))

    fig.savefig(out_path, transparent=True, dpi=dpi)
    plt.close(fig)


if __name__ == "__main__":
    mesh, vcolors = load_mesh_with_color(MESH_PATH)
    print(f"mesh: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")
    import os
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, az in FACINGS:
        out_path = os.path.join(OUT_DIR, f"facing_{name}.png")
        render_view(mesh, vcolors, az, ELEV_DEG, out_path, CANVAS_W, CANVAS_H)
        print(f"wrote {out_path}")
