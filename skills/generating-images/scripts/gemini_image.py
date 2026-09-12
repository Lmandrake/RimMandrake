#!/usr/bin/env python3
"""Gemini image channel — the replacement for the Codex $imagegen channel.

Reads the key from ~/.config/rwgfx/gemini.key (never a CLI arg, never printed).
Model default is Nano Banana Pro (gemini-3-pro-image) — best identity-across-
angles, which is why it was chosen for RimWorld multi-facing. Reference images
condition the generation (that is the whole point vs. the old channel), so a
hero sprite can drive its own other facings.

No native alpha — pair with rembg (~/.venvs/rwgfx) downstream for a cutout.

  gemini_image.py generate --prompt "..." --out a.png [--ref hero.png ...] [--model gemini-3-pro-image]
  gemini_image.py probe        # key + model reachability, no generation
"""
import argparse
import base64
import json
import os
import sys
import urllib.request

KEY_FILE = os.path.expanduser("~/.config/rwgfx/gemini.key")
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
DEFAULT_MODEL = "gemini-3-pro-image"


def _key():
    try:
        with open(KEY_FILE) as f:
            k = f.read().strip()
        if not k:
            sys.exit("empty key at " + KEY_FILE)
        return k
    except FileNotFoundError:
        sys.exit("no key at " + KEY_FILE + " — create it, one line, the API key")


def _post(model, parts):
    body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }).encode()
    req = urllib.request.Request(
        API.format(model=model, key=_key()),
        data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def _extract_image(resp):
    for c in resp.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d and d.get("data"):
                return base64.b64decode(d["data"])
    return None


def generate(args):
    parts = [{"text": args.prompt}]
    for ref in (args.ref or []):
        with open(ref, "rb") as f:
            parts.append({"inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(f.read()).decode()}})
    resp = _post(args.model, parts)
    if "error" in resp:
        e = resp["error"]
        sys.exit("API error %s %s: %s" % (e.get("code"), e.get("status"), e.get("message", "")[:300]))
    img = _extract_image(resp)
    if img is None:
        # surface any text the model returned instead of an image (refusals etc.)
        txt = ""
        for c in resp.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                txt += p.get("text", "")
        sys.exit("no image in response. finishReason=%s text=%s" % (
            (resp.get("candidates") or [{}])[0].get("finishReason"), txt[:300]))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    # The API's inline_data mime is not trustworthy and the model returns JPEG
    # today (measured 2026-09-09) — sniff the real format via PIL and always
    # write a genuine PNG, since every consumer here validates the PNG header.
    import io
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(img))
        im.load()
    except Exception as exc:
        sys.exit("API returned bytes PIL cannot read as an image: %s" % exc)
    src_size = im.size
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    if getattr(args, "cutout", False):
        # Gemini has no native alpha (this file's own header): the designed
        # pairing is a rembg cutout, run at NATIVE resolution before any
        # downscale so the alpha edge survives the LANCZOS. Refuse rather
        # than deliver an opaque image every downstream validator rejects.
        # rembg_cut.py owns the ONNX-concurrency flock (REMBG_CONCURRENCY_CAP_1)
        # so every caller serializes on the same lock instead of each
        # reimplementing it — shell out to it rather than duplicate the call.
        import subprocess, tempfile
        rembg_py = os.path.expanduser("~/.venvs/rwgfx/bin/python")
        if not os.path.isfile(rembg_py):
            sys.exit("--cutout: no rembg venv at " + rembg_py)
        rembg_cut_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rembg_cut.py")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            opaque = tf.name
        cut = opaque + ".cut.png"
        im.save(opaque, "PNG")
        r = subprocess.run([rembg_py, rembg_cut_py, "--input", opaque, "--out", cut],
                            capture_output=True, text=True, timeout=300)
        os.unlink(opaque)
        if r.returncode != 0:
            sys.exit("--cutout: rembg failed: " + (r.stderr or r.stdout)[-300:])
        im = Image.open(cut)
        im.load()
        os.unlink(cut)
    if args.size:
        try:
            w, h = (int(x) for x in args.size.lower().split("x"))
        except ValueError:
            sys.exit("--size must look like 256x256, got %r" % args.size)
        if src_size[0] < w or src_size[1] < h:
            sys.exit("API returned %dx%d, smaller than requested %dx%d — "
                     "refusing to upscale-mangle" % (*src_size, w, h))
        if im.size != (w, h):
            im = im.resize((w, h), Image.LANCZOS)
    im.save(args.out, "PNG")
    print("wrote %s (%d bytes api, %s %s -> %dx%d png), model=%s, refs=%d" % (
        args.out, len(img), im.format or "reencoded", "%dx%d" % src_size,
        im.width, im.height, args.model, len(args.ref or [])))


def probe(args):
    k = _key()
    url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + k
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.load(r)
    imgs = [m["name"] for m in d.get("models", []) if "image" in m["name"].lower()]
    print("key OK — %d models, %d image-capable. default=%s%s" % (
        len(d.get("models", [])), len(imgs), DEFAULT_MODEL,
        "" if ("models/" + DEFAULT_MODEL) in imgs else "  ⚠ default not in list"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--ref", action="append", help="reference image(s); repeatable")
    g.add_argument("--model", default=DEFAULT_MODEL)
    g.add_argument("--size", help="WxH the caller actually needs, e.g. 256x256. "
                   "The API ignores requested dimensions (measured 2026-09-09: "
                   "gemini-3-pro-image returns 1024x1024 JPEG regardless), so the "
                   "returned image is converted to real PNG and LANCZOS-DOWNSCALED "
                   "to exactly this; a return SMALLER than this refuses rather than "
                   "upscale-mangle. Without --size the bytes are still format-"
                   "sniffed and re-encoded as PNG at whatever size came back.")
    g.add_argument("--cutout", action="store_true",
                   help="run a rembg background cutout (rwgfx venv) on the result "
                        "so it carries real alpha — gemini emits none natively")
    g.set_defaults(fn=generate)
    p = sub.add_parser("probe")
    p.set_defaults(fn=probe)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
