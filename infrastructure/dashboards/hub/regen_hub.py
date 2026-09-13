#!/usr/bin/env python3
"""regen_hub.py — regenerate the Utinni Control Room dashboard hub's entire
publish set in one command, with zero LLM involvement (owner, 2026-09-13:
"make the sheet regeneration a large, single Python script effort that
coordinates it without any LLM involvement... it needs to take a short time").

    python3 infrastructure/dashboards/hub/regen_hub.py            # fast path (default, seconds)
    python3 infrastructure/dashboards/hub/regen_hub.py --full     # also rebuild upstream sources first
    python3 infrastructure/dashboards/hub/regen_hub.py --check    # validate only; regenerates nothing

A Python script cannot publish an Artifact — that is one Artifact tool call
by a Claude session. This script's job is everything up to and including a
ready-to-publish, fully-validated package, so the session's publish step is
a single call with nothing left to think about: read
`infrastructure/dashboards/hub/data/publish_ready.json` and pass its
`files[].published`/`source` pairs to the Artifact tool verbatim.

FAST PATH (default; --full runs this too, after the upstream rebuild below)
=============================================================================
Two independent subprocess steps, run concurrently:

  * `make_tab_data.py health maturity worldmap artsheets` — rebuilds
    hub/data/{health,maturity,worldmap,artsheets}.json from whatever
    Transient/*.json and world/_audit/*.json sources are on disk right now.
  * `artreg.py render` — rebuilds infrastructure/artpipe/art_status.{json,html},
    published as data/art.json.

WHAT --full COVERS (investigated 2026-09-13; not guessed)
=============================================================================
--full reruns the upstream generators the health and maturity tabs are
downstream of, BEFORE the fast path above:

  1. `codebase_health_publish.py --force` — the full-repo scan. Rebuilds
     Transient/codebase_health.json + Transient/codebase_health_artifact.html
     from scratch (this is the slow step this script exists to make
     optional) and, as its own last step, already regenerates
     hub/data/health.json itself.
  2. `retheme_health.py` — reapplies the hub's brown palette to the artifact
     step 1 just rebuilt, writing hub/tabs/health.html. Grepped the whole
     repo (2026-09-13): NOTHING ELSE calls this automatically, so without
     this step tabs/health.html goes stale the moment codebase_health's
     artifact regenerates. Must run after step 1, so it is not parallelized
     with it.
  3. `project_maturity_dashboard.py` — rebuilds
     Transient/project_maturity_dashboard.{json,html} from the rimflow
     ledger + GOAL_SHEET.md, and (same pattern as step 1) already
     regenerates hub/data/maturity.json itself. Independent of steps 1-2,
     so it runs concurrently with step 1.

Both upstream generators were read end to end for this script: neither
calls `input()` or otherwise blocks for a human, so --full is a plain,
non-interactive subprocess chain — nothing here was guessed.

NOT covered by --full: `world/_audit/post_freeze_*.json`, the worldmap
tab's source. That audit is a manual verification pass against a frozen
save (see ashkarr-audit-artifact / worldmap-studio-review-method) — there
is no generator script to shell out to, and no --full flag should invent
automated worldgen-adjacent tooling. The fast path still republishes
whatever audit file already exists.

VALIDATION (always runs; --check runs ONLY this, against whatever is on
disk right now)
=============================================================================
Subsumes hub_check.py's freshness lamps, plus what that check does not do:

  * every data/*.json (health, maturity, worldmap, artsheets, art) parses
    as JSON, is non-empty (a 0-byte or `{}` file is a FAILURE), and carries
    a `generatedAt` field (its age is reported, never silently assumed
    current);
  * every published file (index.html, the publish_manifest.json entries,
    the data/*.json above) exists on disk;
  * every text file (`.html .json .js .css .xml .svg`) in the set is
    scanned for U+FFFD, reporting file/line/col on a hit — today's publish
    was blocked once by exactly this, caught only by the artifact host's
    own rejection;
  * per-file size <= 15 MB, total publish set <= 60 MB.

Failing any of the above is a non-zero exit and a one-line reason per
failure; nothing regenerates a broken publish_ready.json silently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = HERE / "data"

MAKE_TAB_DATA = HERE / "make_tab_data.py"
RETHEME_HEALTH = HERE / "retheme_health.py"
PUBLISH_MANIFEST = DATA / "publish_manifest.json"
PUBLISH_READY = DATA / "publish_ready.json"

CODEBASE_HEALTH_PUBLISH = REPO / "src/RimMandrake/Utils/codebase_health_publish.py"
PROJECT_MATURITY_DASHBOARD = REPO / "src/RimMandrake/Utils/project_maturity_dashboard.py"
ARTREG = REPO / "src/RimMandrake/Utils/artpipe/artreg.py"
ART_STATUS_JSON = REPO / "infrastructure/artpipe/art_status.json"

MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_TOTAL_BYTES = 60 * 1024 * 1024
TEXT_SUFFIXES = {".html", ".htm", ".json", ".js", ".css", ".xml", ".svg"}
DATA_JSON_TABS = ("health", "maturity", "worldmap", "artsheets")


def die(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------- regeneration
def run_step(name: str, cmd: list) -> bool:
    t0 = time.monotonic()
    r = subprocess.run([sys.executable] + cmd, cwd=REPO, capture_output=True, text=True)
    dt = time.monotonic() - t0
    ok = r.returncode == 0
    print(f"{'OK  ' if ok else 'FAIL'} {name} ({dt:.1f}s)")
    if not ok:
        tail = (r.stdout + r.stderr).strip().splitlines()[-15:]
        for line in tail:
            print(f"    {line}")
    return ok


def full_upstream() -> None:
    """Rebuild the two upstream generators health/maturity are downstream of.

    codebase_health_publish.py and project_maturity_dashboard.py touch
    disjoint Transient/ files and don't call each other — safe to run
    concurrently. retheme_health.py reads the artifact the health publish
    step just wrote, so it must run after, not alongside, that step.
    """
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_health = ex.submit(run_step, "codebase_health_publish.py --force",
                              [str(CODEBASE_HEALTH_PUBLISH), "--force"])
        f_maturity = ex.submit(run_step, "project_maturity_dashboard.py",
                                [str(PROJECT_MATURITY_DASHBOARD)])
        ok_health = f_health.result()
        ok_maturity = f_maturity.result()
    if not ok_health:
        die("codebase_health_publish.py --force failed — see output above")
    if not ok_maturity:
        die("project_maturity_dashboard.py failed — see output above")
    if not run_step("retheme_health.py", [str(RETHEME_HEALTH)]):
        die("retheme_health.py failed — see output above")


def fast_path() -> None:
    """The two tab-data steps every run does — independent, run concurrently."""
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_tabs = ex.submit(run_step, "make_tab_data.py (health maturity worldmap artsheets)",
                            [str(MAKE_TAB_DATA), *DATA_JSON_TABS])
        f_art = ex.submit(run_step, "artreg.py render", [str(ARTREG), "render"])
        ok_tabs = f_tabs.result()
        ok_art = f_art.result()
    if not ok_tabs:
        die("make_tab_data.py failed — see output above")
    if not ok_art:
        die("artreg.py render failed — see output above")


# ------------------------------------------------------------------ publish set
def build_publish_set() -> dict:
    """published-path -> absolute source Path, merging the manifest with the
    two feeds make_tab_data.py/artreg.py don't route through it."""
    pub = {"index.html": HERE / "index.html"}
    manifest = json.loads(PUBLISH_MANIFEST.read_text(encoding="utf-8"))
    for published, rel in manifest.items():
        pub[published] = REPO / rel
    for tab in DATA_JSON_TABS:
        pub.setdefault(f"data/{tab}.json", DATA / f"{tab}.json")
    pub["data/art.json"] = ART_STATUS_JSON
    return pub


# ------------------------------------------------------------------ validation
def find_fffd(text: str):
    """Return (line, col) of the first U+FFFD in text, or None."""
    i = text.find("�")
    if i == -1:
        return None
    line = text.count("\n", 0, i) + 1
    col = i - text.rfind("\n", 0, i)
    return line, col


def decode_text(data: bytes):
    """Return (text, None) or (None, error-string) — never silently swallows a
    genuine bad-encoding byte sequence by falling back to errors='replace'."""
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        line = data.count(b"\n", 0, exc.start) + 1
        last_nl = data.rfind(b"\n", 0, exc.start)
        col = exc.start - last_nl
        return None, f"invalid UTF-8 at byte {exc.start} (line {line}, col {col}): {exc.reason}"


def parse_generated_at(value) -> float:
    """Hours-old, or raise ValueError — same tz-aware discipline as hub_check.py."""
    if not isinstance(value, str) or not value:
        raise ValueError("missing or not a string")
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        raise ValueError(f"no timezone: {value!r}")
    return (datetime.now(timezone.utc) - ts).total_seconds() / 3600


def validate_file(published: str, source: Path) -> dict:
    entry = {"published": published, "source": str(source)}
    if not source.exists():
        entry["error"] = "MISSING: source does not exist"
        return entry
    data = source.read_bytes()
    entry["bytes"] = len(data)
    entry["sha256_12"] = hashlib.sha256(data).hexdigest()[:12]
    if len(data) == 0:
        entry["error"] = "EMPTY: 0 bytes"
        return entry
    if len(data) > MAX_FILE_BYTES:
        entry["error"] = f"TOO LARGE: {len(data)} bytes > {MAX_FILE_BYTES} per-file cap"
        return entry

    text = None
    if source.suffix in TEXT_SUFFIXES:
        text, err = decode_text(data)
        if err:
            entry["error"] = err
            return entry
        hit = find_fffd(text)
        if hit:
            entry["error"] = f"U+FFFD replacement char at {source} line {hit[0]}, col {hit[1]}"
            return entry

    is_data_json = published.startswith("data/") and published.endswith(".json")
    if is_data_json:
        if text is None:
            text, err = decode_text(data)
            if err:
                entry["error"] = err
                return entry
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            entry["error"] = f"INVALID JSON: {exc}"
            return entry
        if not parsed:
            entry["error"] = "EMPTY: parses to an empty {}/[] — that is a failure, not a footnote"
            return entry
        gen_at = parsed.get("generatedAt") if isinstance(parsed, dict) else None
        try:
            entry["ageHours"] = parse_generated_at(gen_at)
        except ValueError as exc:
            entry["error"] = f"generatedAt unusable: {exc}"
            return entry

    entry["ok"] = True
    return entry


def validate(pub: dict) -> tuple:
    entries = []
    total_bytes = 0
    ok = True
    width = max(len(p) for p in pub)
    for published in sorted(pub):
        e = validate_file(published, pub[published])
        entries.append(e)
        total_bytes += e.get("bytes", 0)
        if e.get("error"):
            ok = False
            print(f"FAIL  {published:{width}}  {e['error']}")
        else:
            age = f"  age={e['ageHours']:.1f}h" if "ageHours" in e else ""
            print(f"OK    {published:{width}}  {e['bytes']:>10} bytes{age}")
    if total_bytes > MAX_TOTAL_BYTES:
        ok = False
        print(f"FAIL  publish set total is {total_bytes} bytes > {MAX_TOTAL_BYTES} cap")
    return ok, entries, total_bytes


def write_publish_ready(pub: dict, entries: list, ok: bool, total_bytes: int) -> None:
    files = [{"published": e["published"], "source": str(pub[e["published"]].resolve()),
              "bytes": e.get("bytes"), "sha256_12": e.get("sha256_12")} for e in entries]
    ready = {
        "generatedAt": now_iso(),
        "status": "READY" if ok else "FAILED",
        "totalBytes": total_bytes,
        "files": files,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    PUBLISH_READY.write_text(json.dumps(ready, indent=1) + "\n", encoding="utf-8")
    print(f"\n{'-' * 60}\nPUBLISH SET  (published-path -> absolute source path)")
    width = max(len(f["published"]) for f in files)
    for f in files:
        print(f"  {f['published']:{width}}  {f['source']}")
    print(f"\n{PUBLISH_READY} written — {ready['status']}")


# ------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="regen_hub.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true",
                     help="also rebuild the upstream health/maturity generators first "
                          "(slow full-repo scan) — see --help body for exactly what runs")
    ap.add_argument("--check", action="store_true",
                     help="validate the existing publish set only; regenerate nothing")
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    if not args.check:
        if args.full:
            full_upstream()
        fast_path()

    pub = build_publish_set()
    ok, entries, total_bytes = validate(pub)
    write_publish_ready(pub, entries, ok, total_bytes)

    dt = time.monotonic() - t0
    print(f"\n{'READY' if ok else 'NOT READY'} — {len(entries)} files, "
          f"{total_bytes} bytes, {dt:.1f}s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
