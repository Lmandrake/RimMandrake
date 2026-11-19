#!/usr/bin/env python3
"""Selftest for RIMMANDRAKE_GUARD_USAGE_POLL_WIPES_LATEST_ON_EMPTY_REGISTRY: account_usage.poll() with the switcher
registry (accounts.tsv) missing or unreadable refuses to publish and keeps the previous latest.json, instead of
replacing every good reading with accounts {}. "Could not read the registry" and "the registry names no account"
are different outcomes: both publish nothing, each names its own cause. Fixture dirs; no claude, no credentials."""
import atexit
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_au_registry_"))
atexit.register(shutil.rmtree, ROOT, True)
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ["RM_ACCOUNT_USAGE_DIR"] = str(ROOT / "data")
os.environ["RM_ACCOUNT_USAGE_CONF"] = str(ROOT / "conf.json")
os.environ["RM_LIVE_CLAUDE_JSON"] = str(ROOT / "live.claude.json")
os.environ["RM_PULSE_STATE"] = str(ROOT / "pulse")
os.environ["RM_CLAUDE_ACCOUNT"] = str(ROOT / "no-such-claude-account")
os.environ["RM_CLAUDE_BIN"] = str(ROOT / "no-such-claude")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_usage as au  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


(ROOT / "data").mkdir()
GOOD = {"schema": 1, "updated": "2026-11-18T17:00:00-08:00",
        "accounts": {"steven": {"account": "steven", "source": "MEASURED", "week_pct_used": 39.0}}}


def reset():
    (ROOT / "data" / "latest.json").write_text(json.dumps(GOOD))


def poll_outcome():
    try:
        au.poll()
        return "published"
    except au.RegistryUnreadable as e:
        return "unreadable: " + str(e)
    except au.RegistryEmpty as e:
        return "empty: " + str(e)


# missing registry file
reset()
out = poll_outcome()
kept = json.loads((ROOT / "data" / "latest.json").read_text())
check("registry missing: poll refuses as UNREADABLE", out.startswith("unreadable"), out)
check("registry missing: latest.json keeps steven", bool(kept.get("accounts", {}).get("steven")), kept)
check("registry missing: the cause names the registry path", "accounts.tsv" in out, out)
check("registry missing: no series line was appended", not (ROOT / "data" / "series.jsonl").exists())

# readable, but names no account (comments only)
(ROOT / "acc").mkdir()
(ROOT / "acc" / "accounts.tsv").write_text("# name email\n")
reset()
out = poll_outcome()
kept = json.loads((ROOT / "data" / "latest.json").read_text())
check("registry empty: poll refuses as EMPTY (its own outcome, not unreadable)", out.startswith("empty"), out)
check("registry empty: latest.json keeps steven", bool(kept.get("accounts", {}).get("steven")), kept)

# unreadable (a directory where the file should be)
(ROOT / "acc" / "accounts.tsv").unlink()
(ROOT / "acc" / "accounts.tsv").mkdir()
reset()
out = poll_outcome()
check("registry unreadable (a directory): poll refuses as UNREADABLE", out.startswith("unreadable"), out)
(ROOT / "acc" / "accounts.tsv").rmdir()

# the readers that tolerate a missing registry still get {} (registry() itself is unchanged for them)
check("registry() for readers: missing file is still an empty dict", au.registry() == {})
try:
    au.registry(strict=True)
    check("registry(strict=True): a missing file raises RegistryUnreadable", False)
except au.RegistryUnreadable:
    check("registry(strict=True): a missing file raises RegistryUnreadable", True)

# the CLI says so and exits non-zero, printing nothing that could pass for a reading
reset()
import contextlib  # noqa: E402
import io  # noqa: E402
buf, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
    rc = au.main(["poll"])
check("poll CLI: registry missing exits 3 (cause-specific)", rc == 3, rc)
check("poll CLI: stdout empty, cause on stderr", buf.getvalue() == "" and "accounts.tsv" in err.getvalue(),
      (buf.getvalue(), err.getvalue()))

print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
