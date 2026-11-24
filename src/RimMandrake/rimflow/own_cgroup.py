#!/usr/bin/env python3
"""own_cgroup.py: run one command to its end in a cgroup of its own, when the caller is a user service.
Page: design/specs/2026-11-24-tick-children-own-cgroup/boundary.md. Starts no model.

    own_cgroup.run(argv, **subprocess_run_keywords) -> CompletedProcess
"""
import os
import shutil
import subprocess

# Guards the WSL VM (the games, the helpers) against a git child that grows without bound: a tick's children read a 4.5G
# swap peak at 2026-11-24 01:23. A clone checkout is file cache the kernel takes back at the line, so it does not die of it.
MEMORY_MAX = "4G"
REFUSED = "Failed to start transient scope unit"


def my_service(path="/proc/self/cgroup"):
    """The user service this process is in, or None (a seat scope, a login shell)."""
    with open(path, encoding="utf-8") as f:     # /proc/self/cgroup: unreadable raises, never reads as "no service"
        name = f.read().strip().rsplit("/", 1)[-1]
    return name if name.endswith(".service") and not name.startswith("user@") else None


def scoped(argv, service):
    return ["systemd-run", "--user", "--scope", "--quiet", "--collect", "--expand-environment=no",     # a message keeps its $
            "--property=MemoryMax=" + MEMORY_MAX, "--property=BindsTo=" + service, "--"] + list(argv)


def run(argv, **kw):
    service = my_service()
    if not service or not shutil.which("systemd-run"):
        return subprocess.run(argv, **kw)
    r = subprocess.run(scoped(argv, service), **kw)
    err = r.stderr if isinstance(r.stderr, str) else (r.stderr or b"").decode("utf-8", "replace")
    if r.returncode and err.lstrip().startswith(REFUSED):
        return subprocess.run(argv, **kw)
    return r
