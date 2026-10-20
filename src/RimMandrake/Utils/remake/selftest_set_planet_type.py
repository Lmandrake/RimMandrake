#!/usr/bin/env python3
"""Selftest for remake/set_planet_type.py on a fake Config dir (never touches the real one)."""
import contextlib
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import set_planet_type as S  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.main(list(argv))
    return rc, buf.getvalue()


def main():
    t = tempfile.mkdtemp(prefix="spt_selftest_")
    cfg = os.path.join(t, "Config")
    ws = os.path.join(t, "workshop")
    about = os.path.join(ws, S.MOD_FOLDER, "About")
    os.makedirs(about)
    with open(os.path.join(about, "About.xml"), "w") as fh:
        fh.write("<ModMetaData><packageId>7f.AlienWorlds</packageId></ModMetaData>")
    base = ["--config-dir", cfg, "--workshop", ws]
    path = S.settings_path(cfg)
    fails = []

    def expect(cond, what):
        if not cond:
            fails.append(what)

    rc, out = run(*base, "--check")
    expect(rc == 1 and "NOT SET" in out, f"check on missing file: {rc} {out}")
    rc, out = run(*base)
    expect(rc == 0 and "DRY RUN" in out and not os.path.exists(path), f"dry run wrote: {out}")
    rc, out = run(*base, "--apply")
    expect(rc == 0 and "WROTE" in out, f"apply: {rc} {out}")
    raw = open(path, "rb").read()
    expect(raw.startswith(b"\xef\xbb\xbf<?xml"), "file lacks BOM/xml header like the game's own")
    expect(b'Class="AlienWorlds.AlienWorldsSettings"' in raw
           and b"<selectedPlanetType>TidallyLocked</selectedPlanetType>" in raw, "content wrong")
    rc, out = run(*base, "--apply")
    expect(rc == 0 and "ALREADY SET" in out and open(path, "rb").read() == raw, f"not idempotent: {out}")
    rc, _ = run(*base, "--check")
    expect(rc == 0, "check after apply")
    expect(not [f for f in os.listdir(cfg) if ".bak-" in f], "idempotent run made a backup")
    # change value: backup made, read-back new
    rc, out = run(*base, "--apply", "--type", "Default")
    expect(rc == 0 and S.read_current(path)[0] == "Default", f"retype: {out}")
    expect(len([f for f in os.listdir(cfg) if ".bak-" in f]) == 1, "no backup on change")
    # a sibling setting in the block survives the rewrite
    open(path, "w", encoding="utf-8").write("<SettingsBlock><ModSettings Class='AlienWorlds.AlienWorldsSettings'>"
                                            "<selectedPlanetType>Default</selectedPlanetType><other>7</other></ModSettings></SettingsBlock>")
    rc, out = run(*base, "--apply")
    expect(rc == 0 and S.read_current(path)[0] == "TidallyLocked" and "<other>7</other>" in open(path, encoding="utf-8").read(), f"sibling lost: {out}")
    rc, out = run(*base, "--apply", "--type", "a<b")
    expect(rc == 2 and "REFUSED" in out and S.read_current(path)[0] == "TidallyLocked", f"bad type not refused: {out}")
    # a foreign/garbled file is refused, never overwritten
    open(path, "w").write("<SettingsBlock><ModSettings Class='Other.X'/></SettingsBlock>")
    rc, out = run(*base, "--apply")
    expect(rc == 2 and "REFUSED" in out, f"foreign block not refused: {out}")
    open(path, "w").write("<garbage")
    rc, out = run(*base, "--apply")
    expect(rc == 2 and "REFUSED" in out, f"garbage not refused: {out}")
    # wrong workshop folder identity refuses
    with open(os.path.join(about, "About.xml"), "w") as fh:
        fh.write("<ModMetaData><packageId>someone.else</packageId></ModMetaData>")
    rc, out = run(*base, "--check")
    expect(rc == 2 and "REFUSED" in out, f"wrong mod folder not refused: {out}")

    if fails:
        print("FAIL selftest_set_planet_type:\n  " + "\n  ".join(fails))
        return 1
    print("PASS selftest_set_planet_type (10 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
