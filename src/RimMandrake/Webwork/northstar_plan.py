"""northstar_driver plan for Webwork (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Webwork \\
      --plan src/RimMandrake/Webwork/northstar_plan.py --mock-skip-site
Live (python.exe, bridge held, game up on a tier carrying mandrake.rm.biomes, e.g. `desertplants`): same without
--mock / --mock-skip-site, narrowed with --chains (runbook 2026-10-22 rows 2.3-2.6, 2.10):
  --chains defs_resolve,settings_roundtrip,thrixweave_and_front   any map
  --chains urraveth_remains | traction_lance | siege                 a plain quicktest map; siege's
      spider_spins_a_web_on_an_unexposed_cell reads UNMEASURED until it runs on a shaded RM_Webwork map.
The suite stages its own sites; it never edits ModsConfig.xml (unlike `modcheck run`)."""
MOD = "Webwork"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rm.biomes",)     # folded into RimMandrake: Baroque Biomes (Biomes.compose.json); standalone id is mandrake.rm.webwork
NEED_GOD = False
RECT = None


# --- offline mock: the driver's generic MockGame answers every tool alike and knows no `jawa/static_call`, so every chain's first
# row died "mock: unknown tool jawa/static_call" and the rest read UNMEASURED (1 PASS / 11 FAIL / 75 UNMEASURED, a HARNESS fault, not
# a mod fault). The per-chain working-mod models already live in validation.py (its own `--mock`); route to them.
_ROUTES = {}


def _models():
    if not _ROUTES:
        import importlib.util, os
        here = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location("ns_webwork_validation", os.path.join(here, "validation.py"))
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        _ROUTES.update({"RimMandrake.Webwork.RM_UrravethProof": v._MockUrravethSession(),
                        "RimMandrake.CreatureBehaviors.RM_TractionLanceProof": v._MockLanceSession(),
                        "RimMandrake.Webwork.RM_WebworkSiegeProof": v._MockSiegeSession(),
                        "RimMandrake.Webwork.RM_WebworkProof": v._MockSession(),
                        "jawa/get_defs": v._MockThrixSession(), "_types": v.settings_fields()})
    return _ROUTES


_THRIX_SPECS = ("ThingDef/Hyperweave", "TraderKindDef/Orbital_Exotic", "ThingDef/RM_Webwork_Anchor", "ThingDef/RM_Webwork_Web",
                "ThingDef/RM_Webwork_Gutter")
_SETTINGS = {}


def _from_disk(spec, fields):
    """A single-def field read answered from this mod's own Defs XML (what a loaded, working mod would serve). None if not found."""
    import os, glob
    import xml.etree.ElementTree as ET
    if ";" in spec or "/" not in spec:
        return None
    name = spec.split("/", 1)[1]
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.findtext("defName") == name:
                out = {}
                for fld in fields.split(","):
                    e = d.find(fld)
                    if e is None:
                        return None
                    out[fld] = e.text.strip() if len(e) == 0 and e.text else ET.tostring(e, encoding="unicode")
                return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": name, "fields": out}]}
    return None


def _field_types():
    return _models()["_types"]


def mock_extension(game, tool, p):
    """None = fall through to the generic mock."""
    if tool == "jawa/static_call":
        s = _models().get(p.get("type"))
        return s.call(tool, **p) if s is not None else None
    if tool == "jawa/get_defs":
        spec = str(p.get("defs") or "")
        if spec.startswith("ThingDef/RM_WebworkNoSuchDef"):      # the control: an absent def must read as absent
            return {"success": True, "foundCount": 0, "notFound": [spec], "defs": []}
        if p.get("fields") == "defName":                         # existence probes: every named def is present
            names = [n for n in spec.split(";") if n]
            return {"success": True, "foundCount": len(names), "notFound": [],
                    "defs": [{"defName": n.split("/", 1)[-1]} for n in names]}
        if spec.startswith(_THRIX_SPECS):
            return _models()["jawa/get_defs"].call(tool, **p)
        if spec == "HediffDef/RM_Webwork_SunScald":
            return {"success": True, "foundCount": 1, "notFound": [],
                    "defs": [{"defName": "RM_Webwork_SunScald", "fields": {p.get("fields"): "RimMandrake.CreatureBehaviors.RM_Hediff_SunScald"}}]}
        return _from_disk(spec, str(p.get("fields") or ""))
    if tool == "jawa/biome_probe":      # the resolved roster is a live fact (patch-added casts); echoing the XML back would pass by construction
        return {"success": True, "biomes": [{"defName": p.get("biomes"), "animals": []}]}
    if tool == "jawa/mod_settings_field":
        f = p.get("field")
        if p.get("action") == "set":
            _SETTINGS[f] = p.get("value")
        elif f not in _SETTINGS and _field_types().get(f) not in (None, "bool"):   # a numeric setting reads as a number
            return {"success": True, "value": "1"}
        return {"success": True, "value": _SETTINGS.get(f, "True")}
    return None
