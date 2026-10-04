"""mod_static.py -- the offline half every first north-star script repeats, plus a live settings round-trip.

Written for the RimUtinni first scripts (NORTHSTAR_EVERYWHERE_PROGRAM_1). Three things every mod owes and a
script can check without the game:

  * every Defs/ and Patches/ XML file parses;
  * no top-level `<Operation MayRequire=...>` in Patches/ -- the 1.6 engine ignores that attribute there, so the
    guard is inert (CLAUDE.md, PATCH_MAYREQUIRE_GUARD_INERT_1; it reset ModsConfig.xml to Core twice);
  * when the csproj lists its sources explicitly, every Source/*.cs is in it (a missing one compiles into
    nothing, with no error);
  * when the mod has C#, a `ModSettings` subclass exists and every field it Scribes is named again after a
    `DoWindowContents`/`DoSettingsWindowContents` (a Scribed setting with no control is a hidden knob).

`add_settings_chain` registers one live component per bool setting: flip it through `jawa/mod_settings_field`,
read it back (Session.set_setting's independent read), restore the default. It proves the settings class name
and every field resolve in the running game -- a renamed class or field fails it.
"""
import glob
import os
import re
import xml.etree.ElementTree as ET

_SCRIBE = re.compile(r'Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,\s*"(\w+)"\s*(?:,\s*([^;]*?))?\)\s*;', re.S)
_NS = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
_CLASS = re.compile(r"class\s+(\w+)\s*:\s*ModSettings\b")


def _read(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


def sources(mod_dir):
    return sorted(glob.glob(os.path.join(mod_dir, "Source", "**", "*.cs"), recursive=True))


def settings_class(mod_dir):
    """(Type.FullName, {field: default literal or None}) of the mod's ModSettings subclass, or (None, {})."""
    for p in sources(mod_dir):
        txt = _read(p)
        m = _CLASS.search(txt)
        if not m:
            continue
        ns = _NS.search(txt)
        body = txt[m.end():]
        fields = {}
        for f, _key, default in _SCRIBE.findall(body):
            fields[f] = (default or "").strip() or None
        return ("%s.%s" % (ns.group(1), m.group(1)) if ns else m.group(1)), fields
    return None, {}


def static_findings(mod_dir):
    bad = []
    for sub in ("Defs", "Patches"):
        for p in sorted(glob.glob(os.path.join(mod_dir, sub, "**", "*.xml"), recursive=True)):
            rel = os.path.relpath(p, mod_dir)
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError as e:
                bad.append("%s does not parse: %s" % (rel, e))
                continue
            if sub == "Patches":
                for op in root.findall("Operation"):
                    if op.get("MayRequire") or op.get("MayRequireAnyOf"):
                        bad.append("%s: top-level <Operation MayRequire=...> is ignored by the engine (inert guard)" % rel)
    srcs = sources(mod_dir)
    if not srcs:
        return bad
    for proj in glob.glob(os.path.join(mod_dir, "Source", "*.csproj")):
        txt = _read(proj)
        listed = set(os.path.basename(x).lower() for x in re.findall(r'Compile\s+Include="([^"]+)"', txt))
        if listed:
            for s in srcs:
                if os.path.basename(s).lower() not in listed:
                    bad.append("%s is not in %s (compiles into nothing)" % (os.path.basename(s), os.path.basename(proj)))
    cls, fields = settings_class(mod_dir)
    if cls is None:
        bad.append("no ModSettings subclass in Source/ (every mod ships Mod Settings, owner 2026-09-12)")
        return bad
    ui = ""
    for s in srcs:
        txt = _read(s)
        hits = [i for i in (txt.find("DoSettingsWindowContents"), txt.find("DoWindowContents")) if i >= 0]
        if hits:
            ui += txt[min(hits):]
    for f in fields:
        if not re.search(r"\b%s\b" % re.escape(f), ui):
            bad.append("setting %s is Scribed but has no control in the settings window" % f)
    return bad


def bool_settings(mod_dir):
    _cls, fields = settings_class(mod_dir)
    return {f: d == "true" for f, d in fields.items() if d in ("true", "false")}


def add_settings_chain(suite, validation_file, name="mod_settings"):
    """One component per bool setting: flip, read back, restore. Registers nothing when the mod has none."""
    mod_dir = os.path.dirname(os.path.abspath(validation_file))
    cls, _ = settings_class(mod_dir)
    bools = bool_settings(mod_dir)
    if not cls or not bools:
        return

    def chain(t):
        for field, default in sorted(bools.items()):
            with t.component("setting_%s_round_trips" % field, beyond_toggle=True):
                try:
                    t.set_setting(cls, {field: str(not default).lower()})
                finally:
                    t.set_setting(cls, {field: str(default).lower()})

    suite.chain(name)(chain)


_HPATCH = re.compile(r'\[HarmonyPatch\(\s*typeof\(\s*([\w.]+)\s*\)\s*,\s*(?:nameof\(\s*[\w.]*?(\w+)\s*\)|"(\w+)")')
_HID = re.compile(r'new\s+Harmony\(\s*"([^"]+)"|HarmonyId\s*=\s*"([^"]+)"')


def harmony_targets(mod_dir):
    """(harmony id or None, [(type, method)]) from the mod's attribute-declared patches."""
    hid, targets = None, []
    for p in sources(mod_dir):
        txt = _read(p)
        m = _HID.search(txt)
        if m and not hid:
            hid = m.group(1) or m.group(2)
        for ty, nm, lit in _HPATCH.findall(txt):
            targets.append((ty.split(".")[-1], nm or lit))
    return hid, sorted(set(targets))


def add_harmony_chain(suite, validation_file, name="harmony_patches_installed"):
    """One component per attribute-declared patch: `jawa/harmony_patches` lists this mod's Harmony id as an owner."""
    mod_dir = os.path.dirname(os.path.abspath(validation_file))
    hid, targets = harmony_targets(mod_dir)
    if not hid or not targets:
        return
    from modcheck import ExpectationFailed

    def chain(t):
        for ty, meth in targets:
            with t.component("patched_%s_%s" % (ty, meth), beyond_toggle=True):
                r = t.bridge_call("jawa/harmony_patches", typeName=ty, methodName=meth)
                if t._guard() and (not isinstance(r, dict) or r.get("success") is not True or hid not in repr(r)):
                    raise ExpectationFailed("%s.%s does not list %s as a Harmony owner: %r" % (ty, meth, hid, r))

    suite.chain(name)(chain)


def incident_defs(mod_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(mod_dir, "Defs", "**", "*.xml"), recursive=True)):
        for el in ET.parse(p).getroot():
            if el.tag == "IncidentDef" and el.get("Abstract") != "True" and el.findtext("defName"):
                out.append(el.findtext("defName"))
    return out


def add_incident_chain(suite, validation_file, name="incidents_answer"):
    """One component per shipped IncidentDef: a `jawa/fire_incident` dry run answers with a `canFireNow` key (the
    def resolves and its worker runs CanFireNow without throwing). Whether it CAN fire on the site is not judged."""
    mod_dir = os.path.dirname(os.path.abspath(validation_file))
    incs = incident_defs(mod_dir)
    if not incs:
        return
    from modcheck import ExpectationFailed

    def chain(t):
        for inc in incs:
            with t.component("dry_run_%s" % inc, beyond_toggle=True):
                r = t.bridge_call("jawa/fire_incident", incidentDef=inc, dryRun=True)
                if t._guard() and "canFireNow" not in (r or {}):
                    raise ExpectationFailed("fire_incident dryRun %s gave no canFireNow: %r" % (inc, r))

    suite.chain(name)(chain)
