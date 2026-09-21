import sys, os
sys.path.insert(0, '/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/972b3ee3-1ba9-45de-a633-3f994183c3c0/scratchpad/instantmesh_spike/InstantMesh')

import transformers.pytorch_utils as pu
import torch
import numpy as np
from PIL import Image
from torchvision.transforms import v2

def find_pruneable_heads_and_indices(heads, n_heads, head_size, already_pruned_heads):
    mask = torch.ones(n_heads, head_size)
    heads = set(heads) - already_pruned_heads
    for head in heads:
        head = head - sum(1 if h < head else 0 for h in already_pruned_heads)
        mask[head] = 0
    mask = mask.view(-1).contiguous().eq(1)
    index = torch.arange(len(mask))[mask].long()
    return heads, index
pu.find_pruneable_heads_and_indices = find_pruneable_heads_and_indices

from src.models.lrm import InstantNeRF
from src.utils.camera_util import get_zero123plus_input_cameras
from src.models.encoder.dino import ViTModel as _ViTModel
def _get_head_mask(self, head_mask, num_hidden_layers, is_attention_chunked=False):
    return [None] * num_hidden_layers
_ViTModel.get_head_mask = _get_head_mask

REFDIR = "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/WreckedMachines/art_source/AutomatedSmelter/repaired"
CKPT = "/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/972b3ee3-1ba9-45de-a633-3f994183c3c0/scratchpad/instantmesh_spike/ckpt/instant_nerf_large.ckpt"
OUT = "/mnt/d/Luke/dev/Rimworld/Transient/meshfuse_multiview"
os.makedirs(OUT, exist_ok=True)

device = torch.device('cuda')

print("Building model...")
model = InstantNeRF(encoder_feat_dim=768, encoder_freeze=False, encoder_model_name='facebook/dino-vitb16',
                     transformer_dim=1024, transformer_layers=16, transformer_heads=16,
                     triplane_low_res=32, triplane_high_res=64, triplane_dim=80,
                     rendering_samples_per_ray=128)

print("Loading checkpoint...")
sd = torch.load(CKPT, map_location='cpu')['state_dict']
sd = {k[14:]: v for k, v in sd.items() if k.startswith('lrm_generator.')}
missing, unexpected = model.load_state_dict(sd, strict=False)
print("missing:", len(missing), "unexpected:", len(unexpected))
model = model.to(device).eval()

def load_view(name, square=320):
    im = Image.open(os.path.join(REFDIR, f"AutomatedSmelter_{name}.png")).convert("RGBA")
    # composite onto white bg (matches zero123++ white-bg convention), square-pad, resize
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    s = max(im.size)
    canvas = Image.new("RGB", (s, s), (255, 255, 255))
    canvas.paste(im, ((s - im.size[0]) // 2, (s - im.size[1]) // 2))
    canvas = canvas.resize((square, square), Image.LANCZOS)
    arr = np.asarray(canvas, dtype=np.float32) / 255.0
    t = torch.from_numpy(arr).permute(2, 0, 1).contiguous().float()
    return t

# Real 4 facings -> the model's trained 4-view slot convention (indices [0,2,4,5] of the
# 6-view zero123++ set: azimuths [30,150,270,330], elevations [20,20,20,-10]).
# We cannot reproduce those exact camera angles (ours are 0/90/180/270 orthographic-ish,
# single elevation) -- this maps our 4 real facings 1:1 onto those 4 trained SLOTS anyway,
# accepting the camera-embedding mismatch, purely to test what the network does with real
# (not zero123++-generated) multi-view conditioning.
order = ["south", "west", "north", "east"]  # -> slot azimuths 30,150,270,330 (rough 90 deg cadence)
images = torch.stack([load_view(n) for n in order], dim=0).unsqueeze(0).to(device)  # (1,4,3,320,320)

input_cameras_full = get_zero123plus_input_cameras(batch_size=1, radius=4.0).to(device)
indices = torch.tensor([0, 2, 4, 5]).long().to(device)
input_cameras = input_cameras_full[:, indices]

# save the composited inputs actually fed to the network, for the contact sheet
for n, im_t in zip(order, images[0]):
    Image.fromarray((im_t.permute(1,2,0).cpu().numpy()*255).astype(np.uint8)).save(os.path.join(OUT, f"fed_{n}.png"))

print("Running forward_planes...")
with torch.no_grad():
    planes = model.forward_planes(images, input_cameras)
    print("planes:", planes.shape)
    mesh_out = model.extract_mesh(planes, use_texture_map=False, mesh_threshold=10.0, mesh_resolution=256, render_resolution=384)

vertices, faces, vertex_colors = mesh_out
print("verts:", vertices.shape, "faces:", faces.shape)

import trimesh
pointnp = vertices
facenp = faces[:, [2, 1, 0]]
mesh = trimesh.Trimesh(vertices=pointnp, faces=facenp, vertex_colors=vertex_colors)
mesh_path = os.path.join(OUT, "instantmesh_multiview.obj")
mesh.export(mesh_path)
print("SAVED", mesh_path, "verts", len(mesh.vertices), "faces", len(mesh.faces))
