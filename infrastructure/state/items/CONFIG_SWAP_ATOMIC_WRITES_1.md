# CONFIG_SWAP_ATOMIC_WRITES_1 — both profile swappers can truncate live game config

Code review finding, 2026-09-02, on the two tools written that day.

## spec

`src/RimMandrake/Utils/cherrypicker_swap.py` and
`src/RimMandrake/Utils/modlist_swap.py` both write live game config with a bare
`shutil.copy2`, which truncates the destination before writing it. An interrupt,
a full disk or a 9p hiccup mid-copy leaves the owner's `ModsConfig.xml` or his
1509-key Cherry Picker profile truncated in place.

Recovery exists — the snapshot runs first, and both profiles are in git — but
recovery is not the same as not breaking it, and the window is real on a 9p mount.

🔑 **`model.write_bridge_file` in `src/RimMandrake/rimflow/model.py` already solves
this correctly in this repo**: per-call unique temp name, then `os.replace`, with a
long comment explaining why a fixed `<target>.tmp` is wrong (O_TRUNC fires at
`open()`, before any lock, and two writers to the same inode interleave). Copy that
shape rather than inventing a second one.

⚠️ There is no lock either. The game itself rewrites both files, and four threads
share this checkout.

## verify
- Kill the process mid-write (or point it at a path that fails partway) and confirm
  the destination is either the old content or the new, never a prefix of the new.
- Both tools' existing round trips still pass: `cherrypicker_swap.py --status`
  reports SHIP after a SHIP→REVIEW→SHIP cycle, and `modlist_swap.py --status`
  still recognises FULL and MINIMAL by key list.

## criteria
Neither tool can leave a config file in a state the game or the next swap would
misread, and the temp+replace shape matches `write_bridge_file`'s rather than being
a second, subtly different implementation.
