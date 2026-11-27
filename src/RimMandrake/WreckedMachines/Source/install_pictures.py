#!/usr/bin/env python3
"""install_pictures.py: put a judged machine's pictures into Textures through the art ledger. Dev tooling, not shipped.

    python3 Source/install_pictures.py <Short> [--root DIR] [--dry-run]

Run from src/RimMandrake/WreckedMachines/. It reads the judge's verdicts <root>/<Short>/_judge/verdicts.json and the packet's
FACTS.json (Source/judge_packet.py), writes the record design/concepts/WreckedMachines/version/evidence/art/<Short>.json
(judge_packet.py --record), and installs every KEPT slot of that record with `src/RimMandrake/Utils/art/art.py install`
(the only door into Textures). A file is copied into Transient/wm_install/<Short>/ first, because the art ledger takes a
PNG inside the clone. After each install it reads the slot back and compares its sha256 with the record's.

A slot the judge did not keep is not installed, and the line says which. The last line is
  INSTALL <Short>: <n> installed, <m> already there, <k> not kept, <f> failed
Exit 0 every kept slot is in Textures with the judged bytes; 1 a slot failed or none was kept; 2 COULD NOT LOOK.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(MOD, "..", "..", ".."))
RECORDS = os.path.join("design", "concepts", "WreckedMachines", "version", "evidence", "art")
TEX = "src/RimMandrake/WreckedMachines/Textures/"
RULING = "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("short")
    ap.add_argument("--root")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root or os.environ.get("WM_ART_ROOT") or os.path.join(MOD, "art_source"))
    jdir = os.path.join(root, a.short, "_judge")
    verdicts = os.path.join(jdir, "verdicts.json")
    if not os.path.isfile(verdicts):
        print("COULD NOT LOOK: no %s (the judge has not written its verdicts)" % verdicts)
        return 2
    rec_rel = os.path.join(RECORDS, a.short + ".json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "judge_packet.py"), a.short, "--root", root, "--record", verdicts,
                        "--out", rec_rel], cwd=MOD, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip())
        return r.returncode
    rec = json.load(open(os.path.join(REPO, rec_rel), encoding="utf-8"))
    facts = json.load(open(os.path.join(jdir, "FACTS.json"), encoding="utf-8"))
    packet = {f["slot"]: os.path.join(jdir, f["packet_path"]) for f in facts["files"]}
    stage = os.path.join(REPO, "Transient", "wm_install", a.short)
    done = same = failed = 0
    for s in rec["slots"]:
        slot, want = s["slot"], s["sha"]
        dst = os.path.join(REPO, slot)
        if os.path.isfile(dst) and sha(dst) == want:
            same += 1
            continue
        if a.dry_run:
            print("would install %s" % slot)
            continue
        tmp = os.path.join(stage, s["tier"], os.path.basename(slot))
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        shutil.copyfile(packet[slot], tmp)
        why = "delegated: art: %s %s %s, kept by the art judge (%s)" % (a.short, s["tier"], s["facing"], rec_rel)
        r = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "Utils", "art", "art.py"), "install",
                            "WreckedMachines", slot[len(TEX):], "--file", os.path.relpath(tmp, REPO),
                            "--per-ruling", RULING, "--why", why], cwd=REPO, capture_output=True, text=True)
        if r.returncode == 0 and os.path.isfile(dst) and sha(dst) == want:
            done += 1
        else:
            failed += 1
            print("FAILED %s: rc %d %s" % (slot, r.returncode, (r.stdout + r.stderr).strip()[-400:]))
    shutil.rmtree(stage, ignore_errors=True)
    print("INSTALL %s: %d installed, %d already there, %d not kept, %d failed" % (a.short, done, same, len(rec.get("not_kept") or []), failed))
    return 0 if not failed and rec["slots"] else 1


if __name__ == "__main__":
    sys.exit(main())
