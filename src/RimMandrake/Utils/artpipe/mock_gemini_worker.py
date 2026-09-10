#!/usr/bin/env python3
"""mock_gemini_worker.py — stands in for gemini_image.py in artpiped
selftests (GEMINI_WORKER_BACKEND_1).

NEVER calls the real Gemini API, costs real money, or reads a real API key
— that channel is off limits here (the calibration agent owns it). Mirrors
just the CLI surface artpiped.py drives against gemini_image.py: `generate
--prompt --out [--ref ...] --model`. Reuses mock_codex_worker.py's PNG
helpers rather than duplicating them.

Behaviour is looked up by job id — `Path(args.out).stem`, since
artpiped.py always names the output `<job_id>.png` under its per-job
scratch dir — via $ARTPIPE_MOCK_CONTROL, same convention as the codex mock.

Behaviors:
    ok            writes a candidate PNG (mutated reference, or synthetic if
                  no --ref) and prints gemini_image.py's own success line
                  ("wrote <path> (<n> bytes), model=<m>, refs=<k>"), so the
                  daemon's model/cost parsing is exercised for real.
    bad_image     writes a fully opaque, no-alpha PNG — re-validation must
                  catch it exactly like the codex channel's bad_image does.
    wrong_size    writes a PNG at 32x32 regardless of the job's own canvas —
                  proves the daemon's own size check independent of
                  validate_sprite.py (which is skipped entirely when there's
                  no reference).
    api_error     exits 1 with a message mimicking gemini_image.py's own
                  sys.exit() on an API error — no file written, and the
                  daemon must not bill this attempt.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mock_codex_worker as _codex_mock  # noqa: E402 — reuse its PNG helpers + control_for

REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "skills" / "generating-images" / "scripts"))
import pnglib  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--ref", action="append")
    g.add_argument("--model", default="gemini-3-pro-image")
    args = ap.parse_args(argv)

    out = Path(args.out).resolve()
    job_id = out.stem
    ctrl = _codex_mock.control_for(job_id)
    behavior = ctrl.get("behavior", "ok")
    refs = [Path(r) for r in (args.ref or [])]
    reference = refs[0] if refs else None

    if behavior == "api_error":
        print("API error 429 RESOURCE_EXHAUSTED: rate limit exceeded", file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)

    if behavior == "bad_image":
        w, h = _codex_mock.write_opaque_bad_image(reference, out)
    elif behavior == "wrong_size":
        w, h = 32, 32
        pnglib.write_rgba(str(out), w, h, bytes(4 * w * h))
    elif reference is not None:
        w, h = _codex_mock.mutate_reference(reference, out)
    else:
        w, h = 64, 64
        pnglib.write_rgba(str(out), w, h, bytes(4 * w * h))

    # The EXACT format gemini_image.py's own generate() prints on success —
    # the daemon parses "model=<x>" out of this to know which model
    # actually ran (and therefore what to bill it at).
    print("wrote %s (%d bytes), model=%s, refs=%d" % (
        out, out.stat().st_size, args.model, len(refs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
