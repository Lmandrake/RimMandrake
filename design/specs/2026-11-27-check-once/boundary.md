# BOUNDARY: the ticket lane's outcome checks, run once and kept until a read changes, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/check_once.py` (all of it), `src/RimMandrake/rimflow/check_reads_hook/sitecustomize.py`
(all of it), the batch call in `src/RimMandrake/rimflow/list_effect.py` (`_tick`) and in
`src/RimMandrake/rimflow/list_dispatch.py` (`gather`), and `holds_text` in `src/RimMandrake/rimflow/list_shape.py`.
Item: `RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS` (rows 2, 7 and 8 of
`design/specs/2026-11-26-slow-actions/one_page.md`: one lane tick 218 s, 193 s of it 48 checks one after the other, the
same checks again by the second timer). Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_check_once.py`. What a check means, its forms and its verdicts stay on
`design/specs/2026-11-22-list-outcome-checks/boundary.md`.

Offline simulation: yes. The selftest runs the real `run_many` against fake checks in a throwaway root that count
their runs, with a throwaway store. It does not simulate the two timers' units: the real beat on the dispatch clone is
the live pass.

## ACCEPTS (the only inputs this is built for)

- **the-checks-of-one-beat.** A list of check texts (the three forms of `list_effect.parse`), the clone root that they
  run in, and the ledger world that the beat already read (or none).
- **a-store-folder.** `<list_effect state dir>/check_kept/`, one JSON file and one lock file per check. Both timers run
  from the dispatch clone and use the same folder. A store that cannot be made or read is no store: every check runs.

## DOES NOT SURVIVE (not promised)

- **a-verdict-that-turns-on-the-clock-or-the-environment-alone.** A check whose answer changes with the time of day or
  an environment variable, while no file that it reads changes, keeps its old answer for up to `KEEP_S` (one hour).
- **a-folder-whose-time-is-read.** A folder is keyed by its sorted names, not by its time. A check that reads a
  folder's modified time keeps its answer while the names stay the same.
- **a-read-that-python-does-not-audit.** A python check is named from the audit events `open`, `os.listdir` and
  `os.scandir`, from `os.stat`, `os.lstat` and `os.access`, and from `ctypes.dlopen` by path. A read by a C extension
  that raises no audit event (a C library that opens a file itself) is not seen. `os.open` with `dir_fd` is resolved
  against the working folder.
- **a-program-on-path-that-changes.** `python3` is found on PATH by bash. A new `python3` earlier on PATH is not a read.

## PROMISES (each one is owed a test of the same name)

- **both-timers-in-one-window-run-each-check-once.** Two beats on one store (the rm-list-effect and the rm-list-dispatch
  timer) run each named check once: the second beat gives the same verdicts from the kept results. Two beats at the same
  moment also run it once: a lock per check makes the second wait, then read the first one's result.
- **checks-run-in-parallel-under-a-bound.** `run_many` runs the distinct checks of a beat `workers` at a time (the
  beat's bound is `WORKERS`, with its danger beside it), never more, and more than one at a time.
- **a-result-is-kept-until-a-read-file-changes.** A kept result is used again only when the check text and root are the
  same, it is younger than `KEEP_S`, and each path that the check read has the key that it had when the check first read
  it: a file's time, size, inode and mode; a folder's sorted names; a missing path stays missing. A changed file, a file
  that appears where the check looked, a new name in a listed folder, a changed imported module and a file read by a
  python child each run the check again. A replace inside a listed folder that keeps its names keeps the result. An open
  that only writes (`w`, `a`) is not a read. `test -f S && python3 S` keeps its fails until S appears.
- **a-check-whose-reads-cannot-be-named-runs-every-time.** A check runs every time when its command has a pipe, a
  redirection, a `;`, a group, a glob, a `$` or backtick outside single quotes, an assignment, a test of another form, or
  a program other than `python3` and `test`; when python runs with `-I` or other flags that skip the recorder; when a
  python process runs another program, opens a socket, reads `/proc`, `/sys` or `/dev`, lists a folder by descriptor,
  starts a python child that does not record, or ends without its record (`os._exit`, a signal, a deadline). A path
  check runs every time (one file: cheap). The reading names each check that ran every time, with its reason
  (`checks.unnamed_why`).
- **unmeasured-stays-unmeasured.** An unmeasured result (any exit but 0 and 1, a deadline, a check that could not start)
  is given as unmeasured and is never kept. A store that cannot be used gives each check's own verdict. A kept read that
  no longer matches runs the check again. A dry beat (`write=False`) keeps nothing new.
- **the-hook-and-the-beat-key-a-path-alike.** The key that the hook records at a first read equals the key that
  `check_once.sig` gives for the same unchanged path, for a file, a folder and a missing path.
- **a-shape-check-is-answered-in-the-beat-with-its-parts-in-the-batch.** With the beat's world,
  `cmd:python3 src/RimMandrake/rimflow/list_shape.py holds <ID>` (exactly that form) is answered by
  `list_shape.holds_text` in the beat's process: the same text and verdict that the command prints and exits with. Its
  parts' checks run in the same batch, so the ledger is not replayed once per such check. An item that the world lacks
  is unmeasured.
- **the-ticks-run-their-checks-through-one-batch.** `list_effect._tick` and `list_dispatch.gather` call
  `check_once.run_many` once per beat, not `list_effect.run` per item. The reading of each tick carries the batch's
  counts (`checks`: ran, kept, unnamed, path, in_process, seconds).

## LIMITS

- `WORKERS = 4`: the danger is a machine at load 22 to 52 on 14 cores (slow-actions page, 2026-11-26), where each check
  is a python process; 81 checks at once would add 81 runnable processes and their memory.
- `KEEP_S = 3600`: a refresh (it ends no work). The danger is a verdict that turns on the clock alone, which no recorded
  read shows.
- A check's own deadline stays `list_effect.CMD_TIMEOUT_S`.
