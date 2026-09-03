#!/usr/bin/env python3
"""atomic_copy.py — copy a file so the destination is never a prefix of the new one.

🔑 ONE SHAPE, NOT TWO. `model.write_bridge_file` in `src/RimMandrake/rimflow/model.py`
already solved this for the bridge mirror: per-call unique temp name, exclusive create,
lock, write, `os.replace`. The two profile swappers (`modlist_swap.py`,
`cherrypicker_swap.py`) overwrite the owner's LIVE game config and needed the same
guarantee, so it lives here once instead of being reimplemented subtly differently in
each (CONFIG_SWAP_ATOMIC_WRITES_1).

🔴 THE TEMP NAME MUST BE PER-CALL UNIQUE, NOT A FIXED `<dst>.tmp`. `O_TRUNC` fires at
`open()`, BEFORE any lock is requested, and truncation is not fd-local — two writers
naming the same tmp path truncate each other's inode and the second `os.replace` can
chase a tmp the first already renamed away. Four agent threads share this checkout and
RimWorld rewrites both of these files itself.

⚠️ `shutil.copy2` is what this replaces, and it truncates the destination in place then
streams into it. An interrupt, a full disk or a 9p hiccup mid-copy leaves a live config
file half written — recoverable from the snapshot, but broken meanwhile.

⚠️ THIS IS NOT A LOCK AGAINST THE GAME. `os.replace` is atomic against a *reader*: the
destination is always either the whole old file or the whole new one. It does not stop
RimWorld or RimSort writing the same path a moment later.
"""
import fcntl
import os
import shutil
import time

__all__ = ["atomic_copy"]


def atomic_copy(src, dst):
    """Copy `src` over `dst` atomically. Returns `dst`.

    The temp file is created beside `dst` — same directory, therefore same
    filesystem, which is what makes `os.replace` a rename rather than a copy.
    """
    tmp = "%s.tmp.%d.%d" % (dst, os.getpid(), time.time_ns())
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
        except OSError:
            pass  # DrvFs/9p may refuse advisory locks; O_EXCL already made the name ours.
        try:
            with open(src, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    os.write(fd, chunk)
            os.fsync(fd)
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
    except BaseException:
        os.close(fd)
        # Never leave a stray tmp behind for the next snapshot()'s md5 sweep to find.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    os.close(fd)
    shutil.copystat(src, tmp)   # copy2's other half: mtime/mode, before it is published
    os.replace(tmp, dst)
    return dst
