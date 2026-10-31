"""selftest_rustcathedral_forcedoff.py -- CATHEDRAL_FORCEDOFF_FIX_SAVED_AS_CHOICE, L0 (static wiring + planted breaks).

PatchApplier (_Shared/HarmonyResilience/PatchApplier.cs) is `internal` and linked into each RustCathedral kit DLL, so every
kit DLL has its OWN copy and its own remembered player values. Verse registers exactly one ModSettings for this mod
(RM_RustCathedralSettings), so a feature forced off by a failed Harmony patch is saved as the player's choice unless that
class calls, for EVERY kit DLL that links PatchApplier:
  - <Kit>.PatchBeforeExpose() before base.ExposeData() and before any Scribe call,
  - <Kit>.PatchAfterExpose() after the last Scribe call,
and RM_RustCathedralMod.DoSettingsWindowContents calls <Kit>.PatchReforceOff() after the tab dispatch.
Each kit exposes the three hooks. A kit's own ExposeData is never called (kept only as the Scribe inventory
Utils/selftest_settings_screens.py audits); it must not call PatchApplier, or it reads as wired when it is not.

The check runs on the shipped Source, then on temp copies with each break planted; every break must redden it."""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
HOOKS = ("PatchBeforeExpose", "PatchAfterExpose", "PatchReforceOff")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _body(text, signature):
    """The brace-balanced body of the first method whose header contains `signature`, or None."""
    i = text.find(signature)
    if i < 0:
        return None
    j = text.find("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    return None


def _code(body):
    """Body with // comments stripped, so a hook named only in a comment does not count."""
    return "\n".join(line.split("//", 1)[0] for line in body.splitlines())


def problems(source_root):
    out = []
    kits = []  # (settings class name, settings file)
    for kit in sorted(os.listdir(source_root)):
        kdir = os.path.join(source_root, kit)
        if not os.path.isdir(kdir) or kit in ("RustCathedral", "SelfTest"):
            continue
        projs = [f for f in os.listdir(kdir) if f.endswith(".csproj")]
        if not any("PatchApplier.cs" in _read(os.path.join(kdir, p)) for p in projs):
            continue
        hits = []
        for f in sorted(os.listdir(kdir)):
            if f.endswith(".cs"):
                m = re.search(r"public\s+class\s+(\w+)\s*:\s*ModSettings\b", _read(os.path.join(kdir, f)))
                if m:
                    hits.append((m.group(1), os.path.join(kdir, f)))
        if len(hits) != 1:
            out.append("kit %s links PatchApplier but has %d ModSettings classes" % (kit, len(hits)))
            continue
        kits.append(hits[0])
    if len(kits) < 2:
        out.append("instrument: found %d PatchApplier kits, expected Hum and Walls" % len(kits))
    for cls, path in kits:
        text = _read(path)
        for h in HOOKS:
            if not re.search(r"public\s+static\s+void\s+%s\s*\(\s*\)\s*\{[^}]*PatchApplier\.%s\s*\(" % (h, h[5:]), text):
                out.append("%s lacks hook %s forwarding to PatchApplier" % (cls, h))
        dead = _body(text, "override void ExposeData(")
        if dead is not None and "PatchApplier" in _code(dead):
            out.append("%s's never-called ExposeData calls PatchApplier (it looks wired and is not)" % cls)

    host = _read(os.path.join(source_root, "RustCathedral", "RM_RustCathedralMod.cs"))
    expose = _body(host, "override void ExposeData(")
    window = _body(host, "override void DoSettingsWindowContents(")
    if expose is None or window is None:
        return out + ["instrument: host ExposeData or DoSettingsWindowContents not found"]
    expose, window = _code(expose), _code(window)
    first_scribe = min([p for p in (expose.find("base.ExposeData"), expose.find("Scribe_")) if p >= 0] or [len(expose)])
    last_scribe = max(expose.rfind("Scribe_"), expose.rfind("base.ExposeData"))
    dispatch = window.rfind("DoWindowContents(")
    for cls, _ in kits:
        b = expose.find(cls + ".PatchBeforeExpose()")
        a = expose.find(cls + ".PatchAfterExpose()")
        r = window.find(cls + ".PatchReforceOff()")
        if b < 0 or b > first_scribe:
            out.append("host ExposeData must call %s.PatchBeforeExpose() before any scribing" % cls)
        if a < 0 or a < last_scribe:
            out.append("host ExposeData must call %s.PatchAfterExpose() after the last scribe" % cls)
        if r < 0 or r < dispatch:
            out.append("host settings window must call %s.PatchReforceOff() after drawing the tab" % cls)
    return out


def _plant(root, rel, old, new):
    path = os.path.join(root, rel)
    text = _read(path)
    assert old in text, (rel, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))


def main():
    src = os.path.join(HERE, "Source")
    shipped = problems(src)
    check("shipped wiring clean", not shipped, "; ".join(shipped))

    host = os.path.join("RustCathedral", "RM_RustCathedralMod.cs")
    breaks = [
        ("hum before-hook removed", host, "RustCathedralHumSettings.PatchBeforeExpose();", ""),
        ("walls after-hook removed", host, "RustCathedralWallsSettings.PatchAfterExpose();", ""),
        ("before-hook moved after base.ExposeData", host,
         "RustCathedralHumSettings.PatchBeforeExpose();\n            RustCathedralWallsSettings.PatchBeforeExpose();\n            base.ExposeData();",
         "RustCathedralWallsSettings.PatchBeforeExpose();\n            base.ExposeData();\n            RustCathedralHumSettings.PatchBeforeExpose();"),
        ("walls reforce removed from window", host, "RustCathedralWallsSettings.PatchReforceOff();", ""),
        ("hum reforce only in a comment", host, "RustCathedralHumSettings.PatchReforceOff();", "// RustCathedralHumSettings.PatchReforceOff();"),
        ("walls kit hook deleted", os.path.join("Walls", "RustCathedralWallsSettings.cs"),
         "public static void PatchAfterExpose() { RimMandrake.Shared.PatchApplier.AfterExpose(); }", ""),
        ("PatchApplier call back in the dead hum ExposeData", os.path.join("Hum", "RustCathedralHumSettings.cs"),
         "\t\t\tbase.ExposeData();", "\t\t\tRimMandrake.Shared.PatchApplier.BeforeExpose(GetType());\n\t\t\tbase.ExposeData();"),
    ]
    for name, rel, old, new in breaks:
        tmp = tempfile.mkdtemp(prefix="rc_forcedoff_")
        try:
            root = os.path.join(tmp, "Source")
            shutil.copytree(src, root, ignore=shutil.ignore_patterns("bin", "obj"))
            _plant(root, rel, old, new)
            got = problems(root)
            check("break caught: " + name, bool(got), "check stayed clean")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
