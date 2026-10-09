#!/usr/bin/env python3
"""canon_check_labelset.py — owner-labelled graded renders for validating canon_check modes.
Join: owner ruling target.shas / rejected.sha  ->  sha256 of each graded manifest's render PNG.
Labels: keep -> 'keep'; redo|reject (incl. `rejected` events) -> 'reject'. Prints a JSON list to stdout."""
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

EV = common.REPO_ROOT / "infrastructure/state/art/events"


DESC_ONLY = re.compile(r"regenerate the description to match the appearance", re.I)


def owner_labels() -> dict:
    """sha -> (label, said, conflicted). A real reject event beats a keep (14 of the 23 rejects were ALSO keep-ruled in a sheet, so they carry conflicted=True
    and must be reported as a separate stratum). Rejects that only say "regenerate the description to match the
    appearance" keep the ART and count as neither."""
    seen = {}
    for s in ("BENCH", "FOUNDRY"):
        for l in (EV / f"{s}.jsonl").read_text().splitlines():
            e = json.loads(l)
            if e.get("by") != "owner":
                continue
            v = e.get("verdict")
            if e.get("type") == "rejected" and v in ("redo", "reject"):
                shas = [e["sha"]]
            elif e.get("type") == "ruling" and e.get("trust") in ("ruled", "flawed-sheet") and v in ("keep", "redo", "reject"):
                t = e.get("target") or {}
                shas = (t.get("shas") or []) + ([t["sha"]] if t.get("sha") else [])
            else:
                continue
            for sh in shas:
                seen.setdefault(sh, []).append((e.get("ts", ""), "keep" if v == "keep" else "reject", e.get("said") or e.get("note") or ""))
    out = {}
    for sh, l in seen.items():
        rej = [x for x in l if x[1] == "reject" and not DESC_ONLY.search(x[2])]
        if rej:  # any real reject wins; `conflicted` marks a sha the owner ALSO keep-ruled (usually earlier or later in the same sheet)
            out[sh] = ("reject", max(rej)[2], any(x[1] == "keep" for x in l))
        elif any(x[1] == "keep" for x in l):
            out[sh] = ("keep", max(l)[2], False)
    return out


def build() -> list:
    lab = owner_labels()
    out = []
    for mp in sorted(common.DEFAULT_DONE.glob("*.manifest.json")):
        try:
            m = json.loads(mp.read_text())
        except ValueError:
            continue
        cc = m.get("canon_check") or {}
        if cc.get("status") != "graded":
            continue
        jid = mp.name[:-len(".manifest.json")]
        png = common.DEFAULT_ARTSRC / jid / f"{jid}.png"
        if not png.is_file():
            continue
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        if sha in lab:
            out.append({"id": jid, "label": lab[sha][0], "owner_said": lab[sha][1][:200], "sha": sha, "conflicted": lab[sha][2],
                        "v1": cc["verdict"], "slug": cc.get("slug"), "kind": cc.get("kind")})
    return out


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
