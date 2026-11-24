"""imagecall.py: one picture asked of the one Codex door, for the art daemon.

The daemon keeps the queue, the prompt, the gates and the retries; everything about Codex is the door's
(`~/dev/Dispatch`, through the image command line codex_image.py). Page:
design/specs/2026-11-24-art-daemon-over-the-one-door/boundary.md."""
from __future__ import annotations

import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_door  # noqa: E402

GRACE_S = 30            # on top of the picture deadline, so the outer kill never beats the door's own
SLOT_WAIT_S = 3600      # danger: a stuck image-slot holder would hold a daemon worker for ever
VERDICT_RX = re.compile(r"^\[image\] VERDICT=(\w+) KIND=(\w+) exit=(\d+)\s*$", re.M)


@dataclass
class Call:
    code: int
    out: str
    err: str
    elapsed: float
    timed_out: bool
    outcome: str | None = None      # the door's typed outcome; None: the worker gave no verdict line
    kind: str | None = None         # answered | failed | no_answer_in_time | could_not_start | None

    @property
    def not_run(self) -> bool:
        """The door could not draw for a reason that is not the job's: it could not start, or its login is dead. A bad
        input (a reference that is not there) is the job's own fault and fails the job."""
        return (self.kind == "could_not_start" and self.outcome != "BAD_INPUT") or self.outcome == "AUTH"


def verdict(stderr: str) -> tuple[str | None, str | None]:
    m = VERDICT_RX.findall(stderr or "")
    return (m[-1][0], m[-1][1]) if m else (None, None)


def worst_case_s(timeout: float) -> float:
    return timeout + SLOT_WAIT_S + GRACE_S


def call(worker_script: Path, subcmd: str, prompt: str, out_png: Path, timeout: int, schema_path: Path,
         last_msg_path: Path, reference, model, reasoning_effort, verbose: bool, codex_home=None) -> Call:
    cmd = [sys.executable, str(worker_script), subcmd, "--prompt", prompt, "--out", str(out_png),
           "--timeout", str(timeout), "--slot-wait", str(SLOT_WAIT_S), "--force",
           "--reasoning-effort", reasoning_effort, "--output-schema", str(schema_path),
           "--output-last-message", str(last_msg_path)]
    if codex_home:
        cmd += ["--codex-home", str(codex_home)]
    if model:
        cmd += ["--model", model]
    if reference:
        cmd += ["--image", str(reference)]
    if verbose:
        cmd.append("--verbose")
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=worst_case_s(timeout))
        code, out, err, timed_out = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as exc:
        def text(x):
            return x.decode(errors="replace") if isinstance(x, bytes) else (x or "")
        code, out, err, timed_out = 124, text(exc.stdout), text(exc.stderr), True
    outcome, kind = verdict(err)
    return Call(code, out, err, time.monotonic() - t0, timed_out or kind == "no_answer_in_time", outcome, kind)


def home(override=None) -> Path:
    """The one sign-in folder. Raises the door's EnvError or DoorMissing by name."""
    return Path(override) if override else Path(dispatch_door.load().default_home("linux"))


def ready(override=None) -> tuple[bool, str]:
    """Could a picture be asked for now? A file read: no launch, no network. An EXPIRED token is not a refusal, because
    the door renews it before the call."""
    try:
        door = dispatch_door.load()
        door.find_codex("linux")
        st = door.status("linux", override)
    except Exception as exc:  # noqa: BLE001 - any cause is a named refusal, never a daemon crash
        return False, f"{type(exc).__name__}: {exc}"
    if st["state"] in ("SIGNED_IN", "EXPIRED"):
        return True, f"one sign-in, {st['state']} in {st['home']}"
    return False, (f"{st['state']} in {st['home']}{': ' + st['why'] if st.get('why') else ''}; renew: python3 "
                   f"{dispatch_door.BIN / 'gpt_door.py'} renew")


def png_info(path: Path) -> dict:
    return dispatch_door.load("image_guard").png_info(Path(path))
