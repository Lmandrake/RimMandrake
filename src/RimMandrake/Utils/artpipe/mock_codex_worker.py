#!/usr/bin/env python3
"""mock_codex_worker.py — stands in for codex_image.py in artpiped selftests.

NEVER calls codex.exe, real Codex, or any network — that channel is off
limits here (the calibration agent owns it). Mirrors just the CLI surface
artpiped.py drives against codex_image.py: `generate`/`edit` subcommands with
`--prompt`/`--out`/`--codex-home`/`--timeout`/`--output-schema`/
`--output-last-message`/`--image`/`--force`/`--model`/`--reasoning-effort`/
`--verbose`. Point `--worker-script` (or $ARTPIPE_WORKER_SCRIPT) at this file
and no other artpiped.py code path changes.

Behaviour is looked up by job id — which is `Path(args.out).stem`, since
artpiped.py always names the output `<job_id>.png` — in a control file named
by $ARTPIPE_MOCK_CONTROL: a JSON object `{job_id: "behavior"}` (or
`{job_id: {"behavior": "...", ...overrides}}`). An id not listed there, or no
control file at all, behaves as "ok".

Behaviors:
    ok            generate a candidate PNG that is a small pixel-level
                  mutation of the --image reference (same canvas/alpha
                  geometry, different bytes — passes validate_sprite.py and
                  is not byte-identical), a schema-shaped manifest at
                  --output-last-message, and a rollout JSONL with healthy
                  rate_limits under --codex-home.
    bad_image     writes a manifest CLAIMING "ok", but the PNG is fully
                  opaque with no working alpha — proves the daemon
                  re-validates rather than trusting the worker's own report.
    no_manifest   exits 0, writes NOTHING — the `--`-trap no-op (row 5).
    rate_limited  exits 1, stderr names TooManyRequests (row 1).
    weekly_high   like ok, but the rollout reports secondary.used_percent at
                  the given override (default 95).
    five_h_high   like ok, but the rollout reports primary.used_percent at
                  the given override (default 92), resets_at 2s out.
    tool_error    exits 1, a generic (non-throttle) stderr message, writes
                  NOTHING — a plain worker failure, distinct from row 1.
    tool_error_echo_prompt
                  like tool_error, but its stderr ALSO echoes the exact
                  --prompt text back verbatim (as codex_image.py's own
                  "--- last codex output ---" dump routinely does) — proves
                  a benign prompt phrase can't cause a false rate-limit
                  hard-stop.
    fail_with_image
                  exits 1 with a generic error, but STILL writes a
                  genuinely valid-looking image to --out (no manifest) —
                  simulating a killed/partial run that left a file behind.
                  Proves the daemon never trusts an image over a nonzero
                  exit code.
    ok_ignore_reference
                  exits 0 with a valid manifest and a synthetic image, but
                  never reads --image at all — used to put a BAD reference
                  path on the job without the worker itself tripping over
                  it, so the daemon's own re-validation is what discovers
                  the reference is unusable.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# this file -> artpipe -> Utils -> RimMandrake -> src -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "skills" / "generating-images" / "scripts"))
import pnglib  # noqa: E402

DEFAULT_WEEKLY_HIGH = 95.0
DEFAULT_FIVE_H_HIGH = 92.0


def control_for(job_id: str) -> dict:
    path = os.environ.get("ARTPIPE_MOCK_CONTROL")
    if not path:
        return {"behavior": "ok"}
    try:
        table = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {"behavior": "ok"}
    entry = table.get(job_id, "ok")
    return entry if isinstance(entry, dict) else {"behavior": entry}


def write_rollout(codex_home: Path, weekly: float, five_h: float, resets_at=None) -> None:
    """Emit a rollout-*.jsonl line in the SAME shape
    skills/generating-images/scripts/codex_grumpiness.py actually reads:
    `rate_limits` sits at `payload.rate_limits`, a SIBLING of `payload.info`
    inside a `token_count` event — not a bare top-level key. artpiped.py
    reuses that module's read path rather than re-implementing it, so a mock
    rollout in the wrong shape would make read_meters() silently see nothing
    (read_last_rate_limits() returns None, not an error) and every
    meter-driven detector test would have been exercising nothing at all."""
    now = time.gmtime()
    day_dir = codex_home / "sessions" / time.strftime("%Y/%m/%d", now)
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / f"rollout-{time.time_ns()}-mock.jsonl"
    record = {
        "payload": {
            "type": "token_count",
            "info": {},
            "rate_limits": {
                "primary": {"used_percent": five_h, "window_minutes": 300,
                            "resets_at": resets_at or int(time.time()) + 3600},
                "secondary": {"used_percent": weekly, "window_minutes": 10080,
                              "resets_at": int(time.time()) + 86400},
                "credits": {"has_credits": False, "unlimited": False, "balance": "0"},
            },
        },
    }
    path.write_text(json.dumps(record) + "\n")


def mutate_reference(ref_path: Path, out_path: Path) -> tuple[int, int]:
    """A candidate that keeps the reference's exact geometry/alpha but is
    not byte-identical — every validate_sprite.py check that matters here is
    a ratio against the SAME reference, so this reliably passes."""
    w, h, px = pnglib.read_png(str(ref_path))
    px = bytearray(px)
    for i in range(0, len(px), 4):
        if px[i + 3] >= 32:
            px[i] = px[i] - 5 if px[i] >= 250 else 255 - px[i]
    pnglib.write_rgba(str(out_path), w, h, bytes(px))
    return w, h


def write_opaque_bad_image(ref_path: Path | None, out_path: Path) -> tuple[int, int]:
    """Canvas matches (if a reference exists), but every pixel is fully
    opaque — no usable alpha. validate_sprite.py rejects this regardless of
    the reference's own content, which is what makes it a deterministic bad
    case for the daemon's re-validation to catch."""
    if ref_path is not None and ref_path.is_file():
        w, h, _ = pnglib.read_png(str(ref_path))
    else:
        w, h = 64, 64
    rgba = bytes((200, 40, 40, 255)) * (w * h)
    pnglib.write_rgba(str(out_path), w, h, rgba)
    return w, h


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common_args(p):
        p.add_argument("--out", required=True)
        p.add_argument("--prompt", required=True)
        p.add_argument("--timeout", type=int, default=900)
        p.add_argument("--model", default=None)
        p.add_argument("--reasoning-effort", default="low")
        p.add_argument("--codex-home", default=None)
        p.add_argument("--force", action="store_true")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--verbose", action="store_true")
        p.add_argument("--output-schema", default=None)
        p.add_argument("--output-last-message", default=None)

    g = sub.add_parser("generate")
    common_args(g)
    g.set_defaults(image=[])

    e = sub.add_parser("edit")
    common_args(e)
    e.add_argument("--image", action="append", required=True)

    args = ap.parse_args(argv)

    if args.dry_run:
        print(f"mock: would run {args.cmd} -> {args.out}")
        return 0

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    job_id = out.stem
    ctrl = control_for(job_id)
    behavior = ctrl.get("behavior", "ok")
    home = Path(args.codex_home).resolve() if args.codex_home else None
    images = [Path(i) for i in (getattr(args, "image", None) or [])]
    reference = images[0] if images else None

    def write_manifest(status, note, **extra):
        if not args.output_last_message:
            return
        m = {"id": job_id, "status": status,
             "out": str(out) if out.is_file() else None, "attempts": 1,
             "note": note[:200]}
        m.update(extra)
        Path(args.output_last_message).write_text(json.dumps(m))

    if behavior == "rate_limited":
        print("codex: TooManyRequests — image generation request was rate limited",
              file=sys.stderr)
        return 1

    if behavior == "no_manifest":
        return 0  # the `--`-trap no-op: exit 0, touch nothing at all.

    if behavior == "tool_error":
        print("codex: internal error — the sandbox setup step failed", file=sys.stderr)
        return 1

    if behavior == "tool_error_echo_prompt":
        print("--- last codex output ---", file=sys.stderr)
        print(args.prompt, file=sys.stderr)
        return 1

    if behavior == "fail_with_image":
        if reference is not None:
            mutate_reference(reference, out)
        else:
            w, h = 64, 64
            pnglib.write_rgba(str(out), w, h, bytes(4 * w * h))
        print("codex: internal error after the image tool already ran", file=sys.stderr)
        return 1  # no manifest either — this is what an actually killed run looks like.

    if behavior == "ok_ignore_reference":
        w, h = 64, 64
        pnglib.write_rgba(str(out), w, h, bytes(4 * w * h))
        write_manifest("ok", "mock: produced output without reading --image at all",
                        width=w, height=h, has_alpha=True, corners_transparent=True,
                        background_used="transparent")
        print(f"OK {out}")
        return 0

    if home is not None:
        weekly = ctrl.get("weekly", DEFAULT_WEEKLY_HIGH if behavior == "weekly_high" else 3.0)
        five_h = ctrl.get("five_h", DEFAULT_FIVE_H_HIGH if behavior == "five_h_high" else 5.0)
        resets_at = (int(time.time()) + 2) if behavior == "five_h_high" else None
        write_rollout(home, weekly=weekly, five_h=five_h, resets_at=resets_at)

    if behavior == "bad_image":
        w, h = write_opaque_bad_image(reference, out)
        write_manifest("ok", "mock: reports ok — this manifest is a lie the "
                              "daemon must catch by re-validating", width=w,
                        height=h, has_alpha=False, corners_transparent=False,
                        background_used="transparent")
        print(f"OK {out}")
        return 0

    # ok / weekly_high / five_h_high all produce a genuinely valid candidate.
    if reference is not None:
        w, h = mutate_reference(reference, out)
    else:
        w, h = 64, 64
        pnglib.write_rgba(str(out), w, h, bytes(4 * w * h))
    write_manifest("ok", "mock: mutated the reference for a deterministic, "
                          "non-identical, geometrically-honest candidate",
                    width=w, height=h, has_alpha=True, corners_transparent=True,
                    background_used="transparent")
    print(f"OK {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
