"""Run aerial --live and require its fresh exact M15f MOD PASS. Retain every attempt."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROW = "M15f_restring_joined_run_one_look"


def read_result(path, started, finished, mode, *, fields=None):
    """Unique output plus a creation-window check prevents a previous run from satisfying A1."""
    path = Path(path)
    if not path.is_file() or not started <= path.stat().st_mtime <= finished:
        raise ValueError("no fresh aerial output")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("malformed aerial result")
    if result.get("script") != "validation_aerial.py" or result.get("mode") != mode or result.get("aborted"):
        raise ValueError("wrong or aborted aerial driver")
    rows = result.get("rows")
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise ValueError("malformed rows")
    if fields and any(result.get(key) != value for key, value in fields.items()):
        raise ValueError("wrong aerial driver options")
    return rows


def check_result(path, started, finished):
    rows = read_result(path, started, finished, "live")
    exact = [r for r in rows if r.get("id") == ROW]
    if len(exact) != 1 or exact[0].get("status") != "PASS" or exact[0].get("class") != "MOD":
        raise ValueError("requires exactly one %s MOD PASS" % ROW)
    detail = exact[0].get("detail")
    if not isinstance(detail, dict) or type(detail.get("schema")) is not int or detail["schema"] != 1 or \
            detail.get("jobDef") != "RM_RestringSpan":
        raise ValueError("requires the colonist-job M15f evidence schema")
    return exact[0]


def run_proof(argv, *, mode, prefix, check, driver_args=()):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-seconds", type=int, default=900)
    args = parser.parse_args(argv)
    if args.max_seconds <= 0:
        parser.error("--max-seconds must be positive")
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix=prefix, dir=args.out_dir)).resolve()
    output = attempt / "aerial.json"
    command = [sys.executable, str(Path(__file__).with_name("validation_aerial.py")), "--" + mode,
               *driver_args, "--out", str(output)]
    receipt = {"command": command, "started": time.time(), "timeout": args.max_seconds}
    code = 1
    try:
        with (attempt / "stdout.txt").open("wb") as stdout, (attempt / "stderr.txt").open("wb") as stderr:
            child = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                   timeout=args.max_seconds, check=False)
        receipt["driverReturncode"] = child.returncode
        receipt["finished"] = time.time()
        row = check(output, receipt["started"], receipt["finished"])
        receipt["row"] = row
        if child.returncode != 0:
            raise ValueError("aerial driver returned %s" % child.returncode)
        code = 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as ex:
        receipt["error"] = "%s: %s" % (type(ex).__name__, ex)
    receipt["finished"] = time.time()
    receipt["returncode"] = code
    (attempt / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempt": str(attempt), **receipt}, indent=2))
    return code


def main(argv=None):
    return run_proof(argv, mode="live", prefix="a1-", check=check_result)


if __name__ == "__main__":
    sys.exit(main())
