#!/usr/bin/env python3
"""TAR_LOOK_TUNE_THICK_AND_SLOW — the offline half of live liquid-look tuning.

The owner tunes a liquid's surface live (bridge liquid_look_set) and the tuned look is pasted back from
liquid_look_dump. That round trip only holds if:

  1  the dump's field order (RM_LiquidLookProof.FieldOrder, C#) equals the generator's _LOOK_FIELDS, and both
     cover every public field of RM_LiquidSurfaceLook — a field missing from either is silently dropped on paste;
  2  the companion tools exist and call only RM_LiquidLookProof members that exist (they bind by reflection,
     so a renamed member is a runtime 'missing' instead of a build error);
  3  tar ships the tuning base: Solid over White (opaque dark grey, owner 2026-10-06), NO overlay film and no
     highlight (the "weird drifting motes of white stuff"), the vanilla ripple pass kept (rippleDensity or
     rippleIntensity >= 0), and RM_LiquidLooks.Apply keeps the ripple pass for a Solid look that asks for one.

    python3 src/RimMandrake/FlowWorks/selftest_liquid_look_tune.py
"""
import ast
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
COMPANION = HERE.parent / "bridgetools" / "JawaBench.BridgeTools" / "JawaBenchLiquidLookTools.cs"


def generator_look_fields():
    tree = ast.parse((HERE / "Tools" / "generate_liquid_suite.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "_LOOK_FIELDS" for t in node.targets):
            return [e.value for e in node.value.elts]
    raise AssertionError("_LOOK_FIELDS not found in generate_liquid_suite.py")


def class_fields():
    text = (SRC / "RM_LiquidSurface.cs").read_text(encoding="utf-8")
    body = text[text.index("public class RM_LiquidSurfaceLook"):text.index("public class RM_LiquidSurface :")]
    names = []
    for decl in re.findall(r"public\s+(?:float|bool|string|Color)\s+([^;]+);", body):
        for part in decl.split(","):
            m = re.match(r"\s*([A-Za-z_]\w*)", part)
            # "new Color(0.84f, 0.91f, 0.96f)" splits into numeric fragments; only identifiers are names
            if m and not part.strip()[0].isdigit():
                names.append(m.group(1))
    return names


def main():
    looks = (SRC / "RM_LiquidLooks.cs").read_text(encoding="utf-8")
    m = re.search(r"FieldOrder\s*=\s*\{(.*?)\};", looks, re.S)
    assert m, "RM_LiquidLookProof.FieldOrder not found"
    order = re.findall(r'"(\w+)"', m.group(1))
    gen = generator_look_fields()
    assert order == gen, "dump FieldOrder %s != generator _LOOK_FIELDS %s" % (order, gen)
    cls = class_fields()
    assert sorted(cls) == sorted(order), "RM_LiquidSurfaceLook fields %s vs FieldOrder: missing %s extra %s" % (
        len(cls), sorted(set(cls) - set(order)), sorted(set(order) - set(cls)))

    comp = COMPANION.read_text(encoding="utf-8")
    tools = re.findall(r'"jawa/(liquid_look_\w+)"', comp)
    assert sorted(tools) == ["liquid_look_dump", "liquid_look_get", "liquid_look_set"], tools
    called = set(re.findall(r'LlCall\(proof, "(\w+)"', comp)) | {"Resolve"}
    for name in called:
        assert re.search(r"public static [\w<>, ]+ %s\(string" % name, looks), "companion calls missing member " + name

    reg = ET.parse(HERE / "Defs" / "LiquidTypes" / "LiquidDefs" / "RM_LiquidDefRegistry.xml").getroot()
    tar = next(d for d in reg if d.findtext("defName") == "RM_Liquid_Tar")
    sl = {c.tag: c.text for c in tar.find("surfaceLook")}
    assert sl.get("shader") == "Solid" and sl.get("texture") == "White", "tar base must be Solid over White: %s" % sl
    assert sl.get("overlay", "false") == "false", "tar base must have no overlay film"
    assert float(sl.get("strength", "0.35")) == 0, "tar base must have highlight strength 0"
    assert max(float(sl.get("rippleDensity", -1)), float(sl.get("rippleIntensity", -1))) >= 0, \
        "tar base must keep the ripple pass (rippleDensity or rippleIntensity >= 0)"
    assert re.search(r"if \(flow \|\| \(solid && !ripple\)\)", looks), \
        "RM_LiquidLooks.Apply must keep the ripple pass for a Solid look that sets a ripple field"
    print("ok  liquid look tune: %d fields round-trip (dump == generator == class), 3 bridge tools bound, tar base "
          "Solid + ripple, no overlay" % len(order))
    return 0


if __name__ == "__main__":
    sys.exit(main())
