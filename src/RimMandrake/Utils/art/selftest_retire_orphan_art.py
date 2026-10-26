#!/usr/bin/env python3
"""selftest_retire_orphan_art.py — retire_orphan_art.py removes art from a mod, so it must:
  * refuse an owner-KEPT picture (dry run and --apply), leaving it untouched and uncopied;
  * refuse any file a def, patch or C# file still names — including XML in a LoadFolders/version folder
    (`1.6/Defs`), a `Staged/` mod tree, a facing set (`X_north.png` named as `X`), a Graphic_Random folder, and a
    C# literal that builds the path from a folder prefix (`"Things/A/" + name`);
  * MOVE a true orphan: a byte-identical copy under the retired-trees root (RETIRED_TREES_DIR) and in the art
    store BEFORE the repo file goes, plus a `live` event with sha None — never a bare delete;
  * change nothing on a dry run.
Runs entirely in a temp tree (ART_SRC_ROOT / ART_LEDGER_DIR / ARTSTORE / RETIRED_TREES_DIR)."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def w(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    (p.write_bytes if isinstance(data, bytes) else p.write_text)(data)
    return p


def png(tag: str) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + tag.encode() * 8


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="selftest_retire_orphan_"))
    os.environ.update(ART_SRC_ROOT=str(tmp / "src"), ART_LEDGER_DIR=str(tmp / "ledger"),
                      ARTSTORE=str(tmp / "store"), RETIRED_TREES_DIR=str(tmp / "retired"), RIMFLOW_SEAT="SELFTEST")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import artledger as A  # noqa: E402
    import retire_orphan_art as R  # noqa: E402

    mod = tmp / "src" / "RimX" / "ModA"
    tex = mod / "Textures" / "Things" / "A"
    files = {k: w(tex / f"{k}.png", png(k)) for k in
             ("orphan", "kept", "named", "staged", "version", "dyn_x")}
    files["face_north"] = w(tex / "Face" / "Face_north.png", png("face"))
    files["rand_a"] = w(tex / "Rand" / "Rand_a.png", png("rand"))
    files["dryrun"] = w(tex / "dryrun.png", png("dryrun"))
    w(mod / "Defs" / "d.xml", "<Defs><ThingDef><graphicData><texPath>Things/A/named</texPath></graphicData>"
                              "<x><texPath>Things/A/Face/Face</texPath></x><y><texPath>Things/A/Rand</texPath></y>"
                              "</ThingDef></Defs>")
    w(mod / "1.6" / "Defs" / "v.xml", "<Defs><texPath>Things/A/version</texPath></Defs>")
    w(tmp / "src" / "RimX" / "ModB" / "Staged" / "Sub" / "Defs" / "s.xml", "<Defs><texPath>Things/A/staged</texPath></Defs>")
    (tex / "Dyn").mkdir()
    files["dyn"] = w(tex / "Dyn" / "Beam.png", png("dyn"))
    w(mod / "Source" / "G.cs", 'class G { string P(string n) => "Things/A/Dyn/" + n; }')
    # the owner keep on the 'kept' picture
    kept_sha = hashlib.sha256(files["kept"].read_bytes()).hexdigest()
    w(tmp / "ledger" / "events" / "OWNER.jsonl",
      json.dumps({**A.owner_keep_ruling(kept_sha, owner_said="keep this one"), "ts": "2026-10-26T00:00:00"}) + "\n")

    def run(*args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = R.main(["--item", "SELFTEST_ITEM", *args])
        return rc, buf.getvalue()

    # dry run touches nothing
    rc, out = run(str(files["dryrun"]))
    check(rc == 0 and "WOULD" in out and files["dryrun"].is_file() and not (tmp / "retired").exists(),
          "dry run reports WOULD and moves nothing")

    # owner-kept: refused both ways, file untouched, no copy anywhere
    rc, out = run(str(files["kept"]))
    check(rc != 0 and "KEPT" in out, "dry run: an owner-kept picture is refused (non-zero exit)")
    rc, out = run("--apply", str(files["kept"]))
    check(rc != 0 and files["kept"].is_file() and files["kept"].read_bytes() == png("kept"),
          "--apply: an owner-kept picture is refused and stays byte-identical in the mod")
    check(not list((tmp / "retired").rglob("kept.png")) if (tmp / "retired").exists() else True,
          "--apply: an owner-kept picture is not copied to retired-trees")

    # still-named files are refused
    for k, why in (("named", "Defs texPath"), ("version", "1.6/Defs (LoadFolders) texPath"),
                   ("staged", "Staged/ mod tree texPath"), ("face_north", "facing set named by its base path"),
                   ("rand_a", "Graphic_Random folder"), ("dyn", "C# folder-prefix literal")):
        rc, out = run("--apply", str(files[k]))
        check(rc != 0 and files[k].is_file() and "READ" in out, f"refused, still named by a {why}")

    # the true orphan is moved, never just deleted
    data = files["orphan"].read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    rc, out = run("--apply", str(files["orphan"]))
    copies = list((tmp / "retired").rglob("orphan.png")) if (tmp / "retired").exists() else []
    check(rc == 0 and not files["orphan"].exists(), "an orphan is removed from the mod")
    check(len(copies) == 1 and copies[0].read_bytes() == data, "a byte-identical copy sits under retired-trees")
    check(bool(copies) and copies[0].as_posix().endswith("RimX/ModA/Textures/Things/A/orphan.png"),
          "the retired copy keeps <mod>/Textures/<rel> so it can be put back by hand")
    check(A.store_has(sha), "the bytes are archived in the art store")
    evs = [json.loads(x) for f in (tmp / "ledger" / "events").glob("*.jsonl") for x in f.read_text().splitlines() if x]
    check(any(e.get("type") == "live" and e.get("sha") is None and e.get("prev") == sha for e in evs),
          "a live event with sha None records the retire")
    shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
