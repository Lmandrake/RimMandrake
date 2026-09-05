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
    with open(args.out, "wb") as f:
        f.write(img)
    print("wrote %s (%d bytes), model=%s, refs=%d" % (
        args.out, len(img), args.model, len(args.ref or [])))


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
    g.set_defaults(fn=generate)
    p = sub.add_parser("probe")
    p.set_defaults(fn=probe)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
