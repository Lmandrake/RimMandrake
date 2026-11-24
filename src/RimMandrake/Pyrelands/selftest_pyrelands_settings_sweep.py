#!/usr/bin/env python3
"""T_SETTINGS_SWEEP_OFFLINE (Pyrelands 0.1.0, RIMMANDRAKE_MOVE_PYRE_SETTINGS_SWEEP_OFFLINE): the settings sweep, off the game.

Static reads of the C# (comments stripped), for every public static bool/float/int/string of RM_PyrelandsSettings:
  scribed          exactly one Scribe_Values.Look, its key unique, its default equal to the field initializer
  shipped          the initializer equals the shipped behaviour: every switch on, except the ruled-off ones (world switch,
                   cross-biome, heavy ambient ash), and the ruled numbers (dry ash 0.70, watered 1.40, fresh-burn +0.50
                   on a 6-day clock)
  read             the field is read (RM_PyrelandsSettings.<name>) in a mechanic file outside the settings file
  gated            every switch the "Mod enabled" master declares is read only in files that consult
                   PyrelandsMechanicsGate.On (the static half of g10), and the declared set is the pinned set
  gate_wired       PyrelandsMechanicsGate.On feeds "Mod enabled" (pyrelandsEnabled) and the Baroque Biomes toggle under the
                   key "Pyrelands" into RM_FireEcoKernel.MechanicsOn (blind challenge cycle 2: a gate that ignored either
                   left every other check green); and ShellOn reads the shell's delegate under that key (blind cycle 3: a
                   ShellOn forced true left the Baroque Biomes toggle gating nothing, every check green)
  entry_gated      each pinned mechanic entry point (a Harmony postfix) consults the gate in ITS OWN body, not merely
                   somewhere in its file (cycle 2: an ungated postfix in a gated file stayed green); blind cycle 3 added the
                   furnace-beast heat-immunity prefix, and the wind carry's one predicate (MapComponent_BurnLine.WindCarries,
                   which both wind patches read) must consult the gate and its own switch in its own expression
  clock_label      the fire-clock checkbox's label and tooltip name the biome's own fire fronts, which it also stops
                   (RIMMANDRAKE_FIX_PYRELANDS_FIRE_CLOCK_LABEL_SAYS_TRIBES_ONLY: it read as a Tribes-only switch)
  checkboxes       every bool setting is the `ref` of exactly one checkbox on the settings screen (blind cycle 3: the wind
                   checkbox bound to burnLineEnabled left "The wind carries the fire" toggling the burn line, every check green)
  sliders          every slider's range holds its field's shipped default (a range that excludes it moves the value the
                   first time the settings window draws)
  kernel_gates     the kernel's own gate predicates, evaluated over every input (blind cycle 4: a MechanicsOn that ignored the
                   Baroque Biomes toggle and a BurnStampMay that ignored "Mod enabled" left every check here green):
                   MechanicsOn is master AND (no shell OR toggle); BurnStampMay is false whenever the gate or its own switch is off;
                   and each of the six gate predicates shuts on its gate argument first (a bare conjunct, or a leading guard)
  gate_args        every caller of a kernel gate predicate hands it PyrelandsMechanicsGate.On at the gate's place (blind cycle 4:
                   BurnStampMay(true, ...) in a postfix that consults the gate elsewhere stayed green)
  wind_reads_pred  the wind carry's one predicate is what the wind patches read: WindCarriedFire.Governs reads WindCarries, and
                   both wind patches call Governs (blind cycle 4: Governs without WindCarries carried fire with every switch off)
  own_switch_stops a mechanic stopped by its own switch only (not by "Mod enabled") opens its tick with `if (!switch ...) return;`
                   (blind cycle 6: a sprayer carrier that foamed with its switch off stayed green, the probe's read counted as `read`)
  job_ends_off     a job a switch starts fails in every toil once the gate or that switch goes off (in-game visit 8: a fire-hawk
                   with an ember in its beak dropped it and lit grass 500 ticks after "Mod enabled" went off; 236 fires a day on)
  wind_tooltip     "The wind carries the fire" does not promise one cell a fire, no sideways step or a line no wider than it was lit:
                   the kernel's CarryPlan heals a cell aside and its FlankPlan opens and closes the flanks
  master_tooltip   the "Mod enabled" tooltip names every switch that ships on and is not declared under it
Every planted fault must go red and the clean copy stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL
"""
import glob
import itertools
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_REL = "Source"
SETTINGS = "RM_PyrelandsMod.cs"
GATE = "PyrelandsMechanicsGate.On"
# Ruled values (owner): world switch OFF (card 2026-11-13); cross-biome off, labelled unsupported (2026-10-15);
# 6-day fresh-burn clock (card 2026-11-05); dry 70%, watered 140%, fresh-burn +50% (code values the g3 correction pinned).
RULED = {"biomeGenerationEnabled": False, "crossBiomeEnabled": False, "crossBiomeEverywhere": False, "ambientAshHeavy": False,
         "ashDryFertility": 0.70, "ashWateredFertility": 1.40, "freshBurnBonus": 0.50, "freshBurnDays": 6.0}
# The switches "Mod enabled" stops (RM_PyrelandsSettings.Masters, SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST, 2026-10-14).
GATED = {"ashDustingEnabled", "scorchFruitEnabled", "ashfallAccumulationEnabled", "freshBurnBonusEnabled", "ambientAshEnabled",
         "plantGrowthStagesEnabled", "wildPlantAllowlistEnabled", "scorchedRuinsEnabled", "burnLineEnabled",
         "fireHawkSpreadEnabled", "furnaceThermalEnabled", "fireClockEnabled", "burrowOnFireEnabled", "ashWaterFertilityEnabled",
         "blackRainDousingEnabled"}


def _strip(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def _val(v, typ, consts):
    v = v.strip()
    v = consts.get(v, v)
    if typ == "bool":
        return v == "true"
    if typ == "string":
        return v.strip('"')
    return round(float(v.rstrip("fFdD")), 6)


GATE_FILE = "PyrelandsMechanicsGate.cs"
GATE_EXPR = "RM_FireEcoKernel.MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled, ShellPresent, ShellOn)"
# (file, class, method): mechanic entry points that must consult the gate themselves.
ENTRY_POINTS = [("PyrelandsAshField.cs", "PyrelandsAshFieldPatches", "FertilityPostfix"),
                ("FireEcologyHook.cs", "Patch_FireTick_BlackRainDouses", "Postfix"),
                ("FireEcologyHook.cs", "Patch_FireTick_AshAndScorchFruit", "Postfix"),
                ("FireEcologyHook.cs", "Patch_FilthMaker_NoAshOnAsh", "Postfix"),
                ("PyrelandsNoOrdinaryRain.cs", "PyrelandsNoOrdinaryRain", "Postfix_ChooseNextWeather"),
                ("Patch_FurnaceBeastHeatImmunity.cs", "Patch_FurnaceBeastHeatImmunity", "Prefix")]
# (file, property, the setting it must also read): expression-bodied predicates every entry point of a mechanic reads.
ENTRY_PROPERTIES = [("MapComponent_BurnLine.cs", "WindCarries", "windCarriesFireEnabled")]
# (file, class, method, switch): the entry point of a mechanic only its own switch stops; its first statement returns on that switch.
SWITCH_GUARDS = [("PyrelandsFoamPath.cs", "MapComponent_RM_FoamPath", "MapComponentTick", "sprayerFoamsPathEnabled")]
# (file, job driver class, switch): a job a switch starts ends when that switch or the gate goes off, so no job lands an effect after it.
JOB_GUARDS = [("JobDriver_RUT_FireHawkCarryEmber.cs", "JobDriver_RUT_FireHawkCarryEmber", "fireHawkSpreadEnabled")]
# A switch "Mod enabled" does not stop, and the words its tooltip names it by.
MASTER_LEAVES = {"sandShovelEnabled": "sand shovelling", "furnaceBeastGiant": "giant furnace-beast", "ullaiEnabled": "ullai spawning",
                 "sprayerFoamsPathEnabled": "firefoam sprayer"}
SHELL_ON_EXPR = r"\bShellOn\s*=>\s*shellEnabled\s*==\s*null\s*\|\|\s*shellEnabled\(RosterKey\)\s*;"


def _block(s, start):
    """The brace-matched body that opens at or after index start, or None."""
    i = s.find("{", start)
    if i < 0:
        return None
    d, j = 1, i + 1
    while d and j < len(s):
        d += {"{": 1, "}": -1}.get(s[j], 0)
        j += 1
    return s[i + 1:j - 1] if d == 0 else None


def _method_body(s, cls, meth):
    m = re.search(r"\bclass %s\b" % re.escape(cls), s)
    body = _block(s, m.end()) if m else None
    if body is None:
        return None
    mm = re.search(r"\b%s\s*\([^;{}]*\)\s*\{" % re.escape(meth), body)
    return _block(body, mm.end() - 1) if mm else None


def _num(v, consts):
    v = consts.get(v.strip(), v.strip())
    m = re.match(r"^(\w+)\s*\*\s*([\d.]+)f?$", v)
    if m and m.group(1) in consts:
        return float(consts[m.group(1)].rstrip("fFdD")) * float(m.group(2))
    try:
        return float(v.rstrip("fFdD"))
    except ValueError:
        return None


def facts(mod):
    out = []

    def fact(name, bad, detail=""):
        out.append((name, not bad, "; ".join(bad)[:400] if bad else detail))

    src_dir = os.path.join(mod, SRC_REL)
    ms = _strip(open(os.path.join(src_dir, SETTINGS)).read())
    consts = dict(re.findall(r"public const \w+ (\w+)\s*=\s*([^;]+);", ms))
    fields = {n: (t, _val(v, t, consts)) for t, n, v in re.findall(r"public static (bool|float|int|string) (\w+)\s*=\s*([^;]+);", ms)}
    looks = re.findall(r"Scribe_Values\.Look\(ref (\w+),\s*\"(\w+)\",\s*([^)]+)\)", ms)
    bad = []
    for n, (t, v) in fields.items():
        mine = [l for l in looks if l[0] == n]
        if len(mine) != 1:
            bad.append("%s: %d Scribe lines" % (n, len(mine)))
        elif _val(mine[0][2], t, consts) != v:
            bad.append("%s: Scribe default %s, initializer %s" % (n, mine[0][2].strip(), v))
    keys = [l[1] for l in looks]
    bad += ["duplicate Scribe key %s" % k for k in set(keys) if keys.count(k) > 1]
    bad += ["Scribe of unknown field %s" % l[0] for l in looks if l[0] not in fields]
    fact("scribed", bad, "%d fields, %d Scribe lines" % (len(fields), len(looks)))
    bad = []
    for n, (t, v) in fields.items():
        want = RULED.get(n, True if t == "bool" else None)
        if want is not None and v != want:
            bad.append("%s ships %s, ruled %s" % (n, v, want))
    fact("shipped", bad, "%d switches on, %d ruled values" % (sum(1 for t, v in fields.values() if t == "bool" and v), len(RULED)))
    code = {}
    for f in glob.glob(os.path.join(src_dir, "**", "*.cs"), recursive=True):
        if os.path.basename(f) == SETTINGS or os.sep + "SelfTest" + os.sep in f:
            continue
        code[os.path.relpath(f, src_dir)] = _strip(open(f, errors="replace").read())
    readers = {n: [f for f, s in code.items() if re.search(r"\bRM_PyrelandsSettings\.%s\b" % n, s)] for n in fields}
    fact("read", ["%s has no reader outside the settings file" % n for n, r in readers.items() if not r and n != "pyrelandsEnabled"]
         + ([] if any("pyrelandsEnabled" in s and "MechanicsOn" in s for s in code.values()) else ["pyrelandsEnabled not fed to the gate"]),
         "%d fields read" % sum(1 for r in readers.values() if r))
    m = re.search(r'\.Declare\("pyrelandsEnabled",([^)]*)\)', ms)
    declared = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    bad = ["declared gated set differs: +%s -%s" % (sorted(declared - GATED), sorted(GATED - declared))] if declared != GATED else []
    for n in sorted(GATED):
        for f in readers.get(n, []):
            if GATE not in code[f]:
                bad.append("%s read in %s, which never consults %s" % (n, f, GATE))
    fact("gated", bad, "%d gated switches, %d read sites" % (len(GATED), sum(len(readers.get(n, [])) for n in GATED)))
    g = code.get(GATE_FILE, "")
    bad = []
    if not re.search(r"\bOn\s*=>\s*" + re.escape(GATE_EXPR), g):
        bad.append("PyrelandsMechanicsGate.On is not " + GATE_EXPR)
    if not re.search(r'RosterKey\s*=\s*"Pyrelands"\s*;', g):
        bad.append('the roster key is not "Pyrelands"')
    if not re.search(SHELL_ON_EXPR, g):
        bad.append("ShellOn does not read the Baroque Biomes delegate under RosterKey")
    fact("gate_wired", bad, "On = MechanicsOn(Mod enabled, shell, toggle \"Pyrelands\")")
    bad = []
    for f, cls, meth in ENTRY_POINTS:
        body = _method_body(code.get(f, ""), cls, meth)
        if body is None:
            bad.append("%s.%s not found in %s" % (cls, meth, f))
        elif GATE not in body:
            bad.append("%s.%s never consults %s" % (cls, meth, GATE))
    for f, prop, setting in ENTRY_PROPERTIES:
        m = re.search(r"\b%s\s*=>([^;]*);" % re.escape(prop), code.get(f, ""))
        if not m:
            bad.append("%s not found in %s" % (prop, f))
            continue
        if GATE not in m.group(1):
            bad.append("%s never consults %s" % (prop, GATE))
        if "RM_PyrelandsSettings.%s" % setting not in m.group(1):
            bad.append("%s never reads its switch %s" % (prop, setting))
    fact("entry_gated", bad, "%d entry points and %d predicates consult the gate" % (len(ENTRY_POINTS), len(ENTRY_PROPERTIES)))
    clock = re.findall(r"CheckboxLabeled\(([^;]*?),\s*ref fireClockEnabled\s*,([^;]*)\);", ms)
    fact("clock_label", ["no fire-clock checkbox"] if not clock else
         ["the fire-clock %s does not name the biome's fire fronts it stops" % w for w, x in
          (("label", clock[0][0]), ("tooltip", clock[0][1])) if not re.search(r"fire fronts?", x, re.I)])
    def tip(name):
        m = re.search(r"CheckboxLabeled\([^;]*?,\s*ref %s\s*,([^;]*)\);" % name, ms)
        return "".join(re.findall(r'"([^"]*)"', m.group(1))) if m else ""

    wind = tip("windCarriesFireEnabled")
    fact("wind_tooltip", ["no wind tooltip"] if not re.search(r"downwind", wind, re.I) else
         ["the wind tooltip says %r" % m.group(0) for m in
          re.finditer(r"never spreads? back or sideways|never sideways|as wide as what was lit|lights one cell", wind, re.I)])
    under = {m.group(1): set(re.findall(r'"(\w+)"', m.group(2))) for m in re.finditer(r'\.Declare\("(\w+)",([^)]*)\)', ms)}
    stopped, todo = set(), ["pyrelandsEnabled"]
    while todo:
        new = under.get(todo.pop(), set()) - stopped
        stopped |= new
        todo += new
    left = [n for n, (t, v) in fields.items() if t == "bool" and v and n != "pyrelandsEnabled" and n not in stopped]
    master = tip("pyrelandsEnabled").lower()
    fact("master_tooltip", ["\"Mod enabled\" leaves %s on and its tooltip does not name it" % n for n in left
                            if n not in MASTER_LEAVES or MASTER_LEAVES[n] not in master], "%d switches left on, each named" % len(left))
    refs = re.findall(r"CheckboxLabeled\([^;]*?,\s*ref (\w+)", ms)
    bools = [n for n, (t, v) in fields.items() if t == "bool"]
    fact("checkboxes", ["%s is the ref of %d checkboxes" % (n, refs.count(n)) for n in bools if refs.count(n) != 1]
         + ["a checkbox binds %s, not a bool setting" % r for r in sorted(set(refs)) if r not in bools],
         "%d bool settings, each bound by exactly one checkbox" % len(bools))
    bad = []
    sliders = re.findall(r"(\w+)\s*=\s*(?:Mathf\.RoundToInt\(|\(int\)\s*)?list\.Slider\((\w+),\s*([^,]+),\s*([^)]+)\)", ms)
    for target, arg, lo, hi in sliders:
        if target not in fields:
            continue
        d, l, h = fields[target][1], _num(lo, consts), _num(hi, consts)
        if l is None or d < l - 1e-6 or (h is not None and d > h + 1e-6):
            bad.append("%s ships %s outside its slider [%s, %s]" % (target, d, lo.strip(), hi.strip()))
    fact("sliders", bad if sliders else ["no slider found"], "%d sliders hold their defaults" % len(sliders))
    kern = code.get(os.path.join("Kernel", "RM_FireEcoKernel.cs"), "")
    bad = []
    for meth, ok_fn in KERNEL_GATES:
        names, expr = _return_expr(kern, meth)
        if expr is None:
            bad.append("%s is not one `return <bool expression>;` in RM_FireEcoKernel.cs" % meth)
            continue
        for combo in itertools.product((False, True), repeat=len(names)):
            env = dict(zip(names, combo))
            try:
                got = bool(eval(expr, {"__builtins__": {}}, env))
            except Exception as e:  # an expression the reader cannot evaluate is not a passed gate
                bad.append("%s: cannot evaluate %r (%s)" % (meth, expr, e))
                break
            want = ok_fn(*combo)
            if want is not None and got != want:
                bad.append("%s%s = %s, wants %s" % (meth, combo, got, want))
                break
    # each kernel gate predicate shuts on its own gate argument: a bare conjunct of its one return, or a guard that returns
    # false / 0 first (blind cycle 4: BlackRainDouseAmount without `!gateOn ||` stayed green here)
    kernels = {k: v for k, v in code.items() if k.startswith("Kernel" + os.sep)}
    for meth, pos in GATE_ARGS:
        src = next((v for v in kernels.values() if re.search(r"\bstatic\s+\w+\s+%s\s*\(" % re.escape(meth), v)), None)
        m = re.search(r"\bstatic\s+\w+\s+%s\s*\(([^)]*)\)\s*\{" % re.escape(meth), src or "")
        if not m:
            bad.append("%s not found in the kernels" % meth)
            continue
        params = [x.split()[-1] for x in m.group(1).split(",") if x.strip()]
        gate = params[pos] if len(params) > pos else None
        body = re.sub(r"\s+", " ", _block(src, m.end() - 1) or "")
        conj = re.match(r"^ ?return ([^;]+);", body)
        ok = bool(conj) and "||" not in conj.group(1) and gate in [t.strip() for t in conj.group(1).split("&&")]
        g = re.match(r"^ ?if \(([^{};]*?)\) \{? ?return (false|0f?|0\.0f?);", body)
        ok = ok or bool(g) and ("!" + gate) in [t.strip().replace("! ", "!") for t in g.group(1).split("||")]
        if not ok:
            bad.append("%s does not shut on its gate argument %s first" % (meth, gate))
    fact("kernel_gates", bad, "%d kernel gate predicates hold over every input; %d shut on their gate argument" % (len(KERNEL_GATES), len(GATE_ARGS)))
    bad = []
    for meth, pos in GATE_ARGS:
        calls = 0
        for f, s in code.items():
            if f.startswith("Kernel" + os.sep):
                continue
            for m in re.finditer(r"\.%s\(" % re.escape(meth), s):
                args = _call_args(s, m.end() - 1)
                calls += 1
                if args is None or len(args) <= pos or args[pos] != GATE:
                    bad.append("%s in %s: gate argument %r, not %s" % (meth, f, args[pos] if args and len(args) > pos else None, GATE))
        if not calls:
            bad.append("%s has no caller (renamed?)" % meth)
    fact("gate_args", bad, "%d kernel gate predicates take %s from every caller" % (len(GATE_ARGS), GATE))
    hook = code.get("FireEcologyHook.cs", "")
    bad = []
    gov = _method_body(hook, "WindCarriedFire", "Governs")
    if gov is None or not re.search(r"\.WindCarries\b", gov):
        bad.append("WindCarriedFire.Governs does not read MapComponent_BurnLine.WindCarries")
    for cls, meth in (("Patch_FireTick_WindCarries", "Postfix"), ("Patch_FireTrySpread_WindInstead", "Prefix")):
        b = _method_body(hook, cls, meth)
        if b is None or "WindCarriedFire.Governs(" not in b:
            bad.append("%s.%s does not ask WindCarriedFire.Governs" % (cls, meth))
    fact("wind_reads_pred", bad, "both wind patches ask Governs, and Governs reads WindCarries")
    bad = []
    for f, cls, meth, switch in SWITCH_GUARDS:
        body = re.sub(r"\s+", " ", _method_body(code.get(f, ""), cls, meth) or "")
        g = re.match(r"^ ?if \(([^{};]*?)\) \{? ?return ?;", body)
        terms = [t.strip().replace("! ", "!") for t in g.group(1).split("||")] if g else []
        if "!RM_PyrelandsSettings.%s" % switch not in terms:
            bad.append("%s.%s does not return first on %s off" % (cls, meth, switch))
    fact("own_switch_stops", bad, "%d mechanics stop on their own switch" % len(SWITCH_GUARDS))
    bad = []
    for f, cls, switch in JOB_GUARDS:
        body = re.sub(r"\s+", "", _method_body(code.get(f, ""), cls, "MakeNewToils") or "")
        head = body.split("yieldreturn", 1)[0]   # before the first toil: every toil of the job fails on it
        ends = [set(m.group(1).split("||")) for m in re.finditer(r"this\.FailOn\(\(\)=>([^;&?]+)\);", head)]
        want = {"!" + GATE, "!RM_PyrelandsSettings.%s" % switch}
        if want not in ends:
            bad.append("%s does not fail every toil on %s off or %s off" % (cls, GATE, switch))
    fact("job_ends_off", bad, "%d job(s) in flight end when their switch or the gate goes off" % len(JOB_GUARDS))
    return out


# (kernel method, the truth it must hold: args in signature order -> expected bool, or None = any)
KERNEL_GATES = [
    ("MechanicsOn", lambda master, shell, toggle: master and (not shell or toggle)),
    ("BurnStampMay", lambda gate, bonusOn, spawned, attached, scorchable:
        False if not gate or not bonusOn else (True if spawned and not attached and scorchable else None)),
]
# (kernel gate predicate, index of its gate argument at the call)
GATE_ARGS = [("BurnStampMay", 0), ("FireTickMayRoll", 0), ("BlackRainDouseAmount", 0), ("RainBecomesBlackRain", 2),
             ("DomeOnHeatHit", 2), ("TryClaimSighting", 2)]


def _return_expr(s, meth):
    """(parameter names, the body's one return expression as Python) of a `static bool meth(...)`, or (names, None)."""
    m = re.search(r"\bstatic\s+bool\s+%s\s*\(([^)]*)\)\s*\{" % re.escape(meth), s)
    if not m:
        return [], None
    names = [p.split()[-1] for p in m.group(1).split(",") if p.strip()]
    body = _block(s, m.end() - 1)
    r = re.fullmatch(r"\s*return\s+([^;]+);\s*", body or "")
    if not r:
        return names, None
    e = r.group(1)
    if re.search(r"[^\w\s&|!()]", e):
        return names, None
    e = e.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"!(?!=)", " not ", e)
    return names, e


def _call_args(s, i):
    """The top-level arguments of the call whose '(' is at index i, stripped, or None."""
    d, j, start, args = 0, i, i + 1, []
    while j < len(s):
        c = s[j]
        if c in "([{":
            d += 1
        elif c in ")]}":
            d -= 1
            if d == 0:
                args.append(s[start:j].strip())
                return [re.sub(r"\s+", " ", a) for a in args]
        elif c == "," and d == 1:
            args.append(s[start:j].strip())
            start = j + 1
        j += 1
    return None


S = "Source/"
MUTANTS = [
    ("fire clock reads as Tribes-only", "Source/RM_PyrelandsMod.cs", "Fire clock (the biome's fire fronts, flame",
     "Fire clock (flame"),
    ("Scribe default flipped", S + SETTINGS, 'Look(ref burnLineEnabled, "burnLineEnabled", true)', 'Look(ref burnLineEnabled, "burnLineEnabled", false)'),
    ("initializer flipped", S + SETTINGS, "public static bool burnLineEnabled = true;", "public static bool burnLineEnabled = false;"),
    ("world switch shipped on", S + SETTINGS, "public static bool biomeGenerationEnabled = false;", "public static bool biomeGenerationEnabled = true;"),
    ("dry ash 0.6", S + SETTINGS, "public static float ashDryFertility = 0.70f;", "public static float ashDryFertility = 0.60f;"),
    ("Scribe line dropped", S + SETTINGS, 'Scribe_Values.Look(ref ullaiEnabled, "ullaiEnabled", true);', ""),
    ("duplicate Scribe key", S + SETTINGS, '"ullaiHerdSizeMultiplier", 1f', '"ullaiEnabled", 1f'),
    ("reader dropped", S + "RM_TerrainDig.cs", "RM_PyrelandsSettings.sandShovelYieldMultiplier", "1f"),
    ("reader only in a comment", S + "RM_PyrelandsGiants.cs", "RM_PyrelandsSettings.furnaceBeastGiant", "true /* RM_PyrelandsSettings.furnaceBeastGiant */"),
    ("gate dropped at a read site", S + "PlantGrowthStages.cs", GATE, "true"),
    ("switch undeclared from the master", S + SETTINGS, '"burrowOnFireEnabled", "ashWaterFertilityEnabled", "blackRainDousingEnabled")', '"ashWaterFertilityEnabled", "blackRainDousingEnabled")'),
    ("gate ignores Mod enabled", S + GATE_FILE, "MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled,", "MechanicsOn(true,"),
    ("roster key misspelt", S + GATE_FILE, 'RosterKey = "Pyrelands";', 'RosterKey = "Pyrelandz";'),
    ("ash-field postfix ungated", S + "PyrelandsAshField.cs", "if (___map == null || !PyrelandsMechanicsGate.On) return;", "if (___map == null) return;"),
    ("black-rain douse ungated", S + "FireEcologyHook.cs", "BlackRainDouseAmount(PyrelandsMechanicsGate.On,", "BlackRainDouseAmount(true,"),
    ("rain swap ungated", S + "PyrelandsNoOrdinaryRain.cs", "pyre, PyrelandsMechanicsGate.On)", "pyre, true)"),
    ("slider range excludes its default", S + SETTINGS, "list.Slider(blackRainDousing, 0f, 100f)", "list.Slider(blackRainDousing, 50f, 100f)"),
    # blind challenge cycle 3 (each one stayed green before)
    ("shell toggle forced on", S + GATE_FILE, "public static bool ShellOn => shellEnabled == null || shellEnabled(RosterKey);", "public static bool ShellOn => true;"),
    ("heat immunity ungated", S + "Patch_FurnaceBeastHeatImmunity.cs", "if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled)", "if (false)"),
    ("wind carry ungated", S + "MapComponent_BurnLine.cs", "WindCarries => IsPyrelandsMap && PyrelandsMechanicsGate.On &&", "WindCarries => IsPyrelandsMap &&"),
    ("wind carry ignores its switch", S + "MapComponent_BurnLine.cs", "&& RM_PyrelandsSettings.windCarriesFireEnabled;", ";"),
    ("wind checkbox bound to the burn line", S + SETTINGS, '"The wind carries the fire", ref windCarriesFireEnabled,', '"The wind carries the fire", ref burnLineEnabled,'),
    # blind challenge cycle 4 (each one stayed green before)
    ("kernel gate ignores the roster toggle", S + "Kernel/RM_FireEcoKernel.cs", "return modMaster && (!shellPresent || shellOn);", "return modMaster;"),
    ("burn stamp kernel ignores the master", S + "Kernel/RM_FireEcoKernel.cs", "return pyrelandsEnabled && bonusOn && spawned && !attachedToPawn && scorchable;",
     "return bonusOn && spawned && !attachedToPawn && scorchable;"),
    ("burn stamp caller passes true", S + "FireEcologyHook.cs", "BurnStampMay(PyrelandsMechanicsGate.On,", "BurnStampMay(true,"),
    ("wind patches ignore the wind predicate", S + "FireEcologyHook.cs", "if (burn == null || !burn.WindCarries) return false;", "if (burn == null) return false;"),
    ("dousing kernel ignores the gate", S + "Kernel/RM_FireEcoKernel.cs", "if (!gateOn || !enabled || !exposed", "if (!enabled || !exposed"),
    ("hawk letter kernel ignores the gate", S + "Kernel/RM_FireHawkRewardsKernel.cs", "|| !mechanicsOn ||", "||"),
    # blind challenge cycle 6 (each one stayed green before)
    ("wind tooltip as wide as lit", S + SETTINGS, "as a front whose edges wander", "as a line as wide as what was lit"),
    ("master tooltip drops the sprayer", S + SETTINGS, "the firefoam sprayer carrier's own foam, ", ""),
    ("sprayer carrier ignores its switch", S + "PyrelandsFoamPath.cs", "if (!RM_PyrelandsSettings.sprayerFoamsPathEnabled || SprayerDef == null) return;", "if (SprayerDef == null) return;"),
    ("sprayer carrier needs both", S + "PyrelandsFoamPath.cs", "if (!RM_PyrelandsSettings.sprayerFoamsPathEnabled || SprayerDef == null) return;", "if (!RM_PyrelandsSettings.sprayerFoamsPathEnabled && SprayerDef == null) return;"),
    # in-game visit 8
    ("ember carry outlives the switches", S + "JobDriver_RUT_FireHawkCarryEmber.cs", "this.FailOn(() => !PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.fireHawkSpreadEnabled);", ""),
    ("ember carry outlives the gate", S + "JobDriver_RUT_FireHawkCarryEmber.cs", "!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.fireHawkSpreadEnabled);", "!RM_PyrelandsSettings.fireHawkSpreadEnabled);"),
    ("ember carry needs both off", S + "JobDriver_RUT_FireHawkCarryEmber.cs", "On || !RM_PyrelandsSettings.fireHawkSpreadEnabled);", "On && !RM_PyrelandsSettings.fireHawkSpreadEnabled);"),
]


def main():
    bad = 0
    for name, ok, det in facts(HERE):
        print("%-10s %s  %s" % (name, "ok  " if ok else "FAIL", det))
        bad += not ok
    tmp = tempfile.mkdtemp(prefix="pyre_settings_mut_")
    red = 0
    try:
        base = os.path.join(tmp, "base")
        shutil.copytree(os.path.join(HERE, "Source"), os.path.join(base, "Source"))
        if not all(ok for _, ok, _ in facts(base)):
            print("FAIL: the unchanged copy is not green")
            return 1
        for i, (label, rel, old, new) in enumerate(MUTANTS):
            m = os.path.join(tmp, "m%d" % i)
            shutil.copytree(base, m)
            p = os.path.join(m, rel)
            t = open(p, errors="replace").read()
            if old not in t:
                print("mutant %-36s ANCHOR MISSING (%r)" % (label, old))
                bad += 1
                continue
            open(p, "w").write(t.replace(old, new))
            fails = [n for n, ok, _ in facts(m) if not ok]
            print("mutant %-36s %s %s" % (label, "red " if fails else "NOT CAUGHT", ",".join(fails)))
            bad += not fails
            red += bool(fails)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("FAIL: %d fact(s) or mutant(s) wrong" % bad)
        return 1
    print("PASS: every Pyrelands setting scribed, shipped as ruled, read and gated; %d of %d mutants red, the clean copy green"
          % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
