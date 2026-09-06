#!/usr/bin/env python3
"""verify_frozen.py — does a `.frozen.json` still describe the file it guards?

🔴 **WHY THIS EXISTS.** `world/ASHKARR_WORLDMAP_tiles.csv.frozen.json` carries `sha256`,
`rows` and `bytes` precisely so the freeze can detect its own staleness — it was rewritten
on 2026-08-22 for that reason, after an audit found it asserting a rain figure that was
false. **On 2026-08-23 the stamp was found 96,961 bytes stale anyway**: a surgical edit had
landed without restamping and nothing reported it, *because nothing checked*.

⇒ A stamp nobody verifies is a comment. This is the check, and it is a command rather than
a habit.

⛔ It never writes the artifact and never writes the marker. It reports, and exits non-zero
when a stamp does not match, so a hook or a pre-commit can use it.

    python3 src/RimMandrake/Utils/verify_frozen.py                 # every marker in the repo
    python3 src/RimMandrake/Utils/verify_frozen.py <artifact>      # just this one
    python3 src/RimMandrake/Utils/verify_frozen.py --restamp <artifact>   # after a deliberate edit
"""
from __future__ import annotations
import argparse, csv, glob, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def measure(path: str) -> dict:
    b = open(path, 'rb').read()
    out = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
    if path.lower().endswith('.csv'):
        with open(path, encoding='utf-8') as fh:
            out['rows'] = sum(1 for _ in csv.DictReader(fh))
    return out


def check(marker: str, restamp: bool = False) -> bool:
    d = json.load(open(marker, encoding='utf-8'))
    art = os.path.join(ROOT, d.get('artifact') or marker[:-len('.frozen.json')])
    if not os.path.exists(art):
        print(f"🔴 MISSING  {d.get('artifact')} — the marker guards a file that is not there")
        return False
    now = measure(art)
    bad = [k for k in ('sha256', 'rows', 'bytes') if k in d and d[k] != now.get(k)]
    name = d.get('artifact') or os.path.basename(art)
    if not bad:
        print(f"✅ CURRENT  {name}  sha {now['sha256'][:12]} · {now.get('rows','-')} rows")
        return True
    if restamp:
        d.update({k: now[k] for k in bad if k in now})
        json.dump(d, open(marker, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f"♻️  RESTAMPED {name} — " + ", ".join(bad)
              + "\n   ⚠️ Restamping records that YOU changed it. It does not make the change correct,"
                "\n   and it does not update `frozenMeaning` — do that by hand if the meaning moved.")
        return True
    print(f"🔴 STALE    {name} — " + ", ".join(
        f"{k}: stamped {d[k]} · actual {now.get(k)}" for k in bad))
    print(f"   Either the artifact was edited without restamping, or the marker was written wrong."
          f"\n   If the edit was deliberate: verify_frozen.py --restamp {d.get('artifact')}")
    return False


def warn_if_stale(artifact_path: str) -> bool:
    """Library entry point for a READER of a frozen artifact.

    Call this right after resolving the path to a frozen CSV/etc, before you read it,
    from any script that only reads the file (a writer should call `check()` above, or
    just run this module with --restamp after a deliberate edit). Non-fatal: prints a
    one-line warning to stderr and returns False on a stale/missing stamp, but never
    raises and never blocks the caller — a reader that cannot look at its own data is a
    worse failure than a reader that looked at slightly-unstamped data and said so.

    Returns True if there is no marker at all (nothing to warn about) or if the stamp
    matches; False if the marker exists and disagrees with the file on disk.
    """
    marker = artifact_path + '.frozen.json'
    if not os.path.exists(marker):
        return True
    try:
        d = json.load(open(marker, encoding='utf-8'))
        now = measure(artifact_path)
        bad = [k for k in ('sha256', 'rows', 'bytes') if k in d and d[k] != now.get(k)]
    except Exception as e:  # fail open — a reader must never crash on this check
        print(f"⚠️  could not verify freeze stamp for {artifact_path}: {e}", file=sys.stderr)
        return True
    if bad:
        print(f"⚠️  STALE FREEZE STAMP on {os.path.basename(artifact_path)} — "
              + ", ".join(bad) + f". You are reading data the stamp does not describe.\n"
              f"   python3 src/RimMandrake/Utils/verify_frozen.py {os.path.relpath(artifact_path, ROOT)}"
              f"  for details.", file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('artifact', nargs='?', help='the guarded file, or its .frozen.json')
    ap.add_argument('--restamp', action='store_true',
                    help='update the stamp to what is on disk — only after a DELIBERATE edit')
    a = ap.parse_args()

    if a.artifact:
        m = a.artifact if a.artifact.endswith('.frozen.json') else a.artifact + '.frozen.json'
        m = m if os.path.exists(m) else os.path.join(ROOT, m)
        if not os.path.exists(m):
            print(f"UNMEASURED no freeze marker at {m} — this artifact is not frozen")
            return 2
        markers = [m]
    else:
        markers = sorted(glob.glob(os.path.join(ROOT, '**', '*.frozen.json'), recursive=True))
        if not markers:
            print("UNMEASURED no .frozen.json anywhere under the repo")
            return 2

    ok = all([check(m, a.restamp) for m in markers])
    print(f"\n{len(markers)} marker(s) checked")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
