"""validation.py -- modcheck suite for RimStarWars: Gizka Stowaway (mandrake.rsw.gizkastowaway).

First north-star script (GIZKA_STOWAWAY_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/GizkaStowaway.md.
The KotOR ship-pest as a found-aboard EVENT: four player-action hooks (gravship landing, wreck deconstruction,
completed trade, quest success; Harmony, owner mandrake.rsw.gizkastowaway) deliver exactly one tame gizka; event
lineage carries the per-pawn hediff RSW_GizkaFecundity (replicates while fed AND warm, capped); the Infestation
stage chews powered buildings; five exits (cull guilt, sell, poison bait, cold, farm). Separately the DONOR gizka's
own breeding is patched wild-wide (Patches/RSW_GizkaDonorPatches.xml, MarketValue 100 -> 15) and scaled by the
global breeding slider. The creature itself is the donor's (Star Wars Animal Collection) or SWBestiary's RSW_Gizka.

CHAINS
  defs_resolve        every def under Defs/ resolves live; a control name reads notFound; the fecundity comp loaded.
  settings_roundtrip  every public field of RSW_GizkaSettings (static fields since the SettingsKit retrofit; the tool reads both kinds), found by
                      regex; bool / int / float round-tripped numerically.
  harmony_wiring      each of the five patched engine methods carries a patch owned by mandrake.rsw.gizkastowaway.
  fecundity_state     a gizka given RSW_GizkaFecundity carries it, a control gizka does not.
  bait_poison         the poison hediff, given to a gizka, advances (state read); the bait item and recipe resolve.
  donor_patch         the donor/port gizka def exists and its MarketValue reads 15 (UNMEASURED when no gizka is loaded).
  mechanics_unmeasured  the four discovery triggers, replication and its cap, chewing, cold stall, cull guilt, the
                      global rate slider: each says what it needs.

STATIC (offline): `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.StarWars.GizkaStowaway.RSW_GizkaSettings"
HARMONY_ID = "mandrake.rsw.gizkastowaway"
FECUNDITY = "RSW_GizkaFecundity"
POISON = "RSW_GizkaBaitPoison"
GIZKA_KINDS = ("Gizka", "RSW_Gizka")          # donor (mlie.starwarsanimalcollection) / SWBestiary port
CONTROL_ABSENT = "ThingDef/RSW_GizkaNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+(?:static\s+)?(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
# the toggle that gates each hook (None: the master switch)
HOOK_TOGGLE = {"PostGravshipLanded": "triggerGravship", "Destroy": "triggerSalvage", "TryExecute": "triggerTrade",
               "End": "triggerQuest", "Kill": "cullGuiltEnabled"}


def shipped_defs():
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def _read(rel):
    return open(os.path.join(HERE, *rel.split("/")), encoding="utf-8").read()


def _settings_body():
    src = re.sub(r"//[^\n]*", "", _read("Source/RSW_GizkaSettings.cs"))
    return src.split("class RSW_GizkaSettings", 1)[1].split("DoWindowContents", 1)[0]


def settings_fields():
    """{name: (type, initializer)} for every scalar field of RSW_GizkaSettings (before ExposeData's methods)."""
    body = _settings_body().split("ExposeData", 1)[0]
    return dict((m.group(2), (m.group(1), m.group(3).strip())) for m in _FIELD.finditer(body))


def hooks():
    """[(TargetType, method)] for every [HarmonyPatch(typeof(X), nameof(X.M))] in the C#."""
    return re.findall(r"\[HarmonyPatch\(typeof\((\w+)\),\s*nameof\(\w+\.(\w+)\)\)\]",
                      _read("Source/RSW_GizkaHarmonyPatches.cs"))


def _num(s):
    return float(s.strip().rstrip("fF"))


def static_checks():
    bad = []
    if len(SHIPPED) < 5:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no field (sanity probe failed)"]
    body = _settings_body()
    scribed = body.split("ExposeData", 1)[1].split("public void", 1)[0]
    ui = _read("Source/RSW_GizkaSettings.cs").split("public void DoWindowContents", 1)[1]
    for n, (ty, init) in fields.items():
        m = re.search(r'Scribe_Values\.Look\(ref\s+%s,\s*"%s",\s*([^)]+)\)' % (n, n), scribed)
        if not m:
            bad.append("settings field %s is not Scribed under its own name" % n)
        else:
            d = m.group(1).strip()
            same = (d.lower() == init.lower()) if ty == "bool" else abs(_num(d) - _num(init)) < 1e-9
            if not same:
                bad.append("settings field %s: Scribe default %s differs from initializer %s" % (n, d, init))
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in the settings window" % n)
    proj = _read("Source/RimMandrakeGizkaStowaway.csproj")
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    hk = hooks()
    if len(hk) != 5:
        bad.append("expected 5 Harmony patches, parsed %d (%r)" % (len(hk), hk))
    for _ty, m in hk:
        if m not in HOOK_TOGGLE:
            bad.append("hook method %s has no entry in this script's HOOK_TOGGLE" % m)
    if '"%s"' % HARMONY_ID not in _read("Source/RSW_GizkaHarmonyPatches.cs"):
        bad.append("Harmony id is no longer %s" % HARMONY_ID)
    if any(ty == "IncidentDef" for ty, _n in SHIPPED):
        bad.append("an IncidentDef shipped: the design rejects a storyteller threat roll")
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("HediffDef", "ThingDef", "RecipeDef", "ThoughtDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    # the fecundity numbers the design rules
    h = [e for e in ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RSW_GizkaHediffs.xml")).getroot()
         if e.findtext("defName") == FECUNDITY][0]
    c = h.find("comps/li")
    if not 0 < float(c.findtext("baseReplicateIntervalDays")) <= 10:
        bad.append("fecundity base interval is outside the slow-burn band (0, 10] days")
    if float(c.findtext("intervalStretchAtCap")) <= 1:
        bad.append("interval does not stretch toward the cap (anti-exponential law)")
    if float(c.findtext("minBreedingTemperature")) <= 0:
        bad.append("minBreedingTemperature is not above freezing: venting a room would not be an exit")
    pz = [e for e in ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RSW_GizkaHediffs.xml")).getroot()
          if e.findtext("defName") == POISON][0]
    if not float(pz.findtext("lethalSeverity")) <= float(pz.findtext("maxSeverity")):
        bad.append("poison lethalSeverity is unreachable")
    if POISON not in _read("Defs/ThingDefs_Items/RSW_GizkaBait.xml"):
        bad.append("bait does not give the poison hediff")
    # donor patches: guarded by FindMod, never MayRequire on an Operation; scam stays pocket change
    p = _read("Patches/RSW_GizkaDonorPatches.xml")
    ET.fromstring(p.encode("utf-8"))
    if re.search(r"<Operation[^>]*MayRequire", p):
        bad.append("donor patch uses MayRequire on an Operation (inert in 1.6)")
    if p.count("<MarketValue>15</MarketValue>") != 2:
        bad.append("MarketValue 15 is not patched on both Gizka and RSW_Gizka")
    for dn in GIZKA_KINDS + ("EggGizkaFertilized", "RSW_EggGizkaFertilized"):
        if 'defName="%s"' % dn not in p:
            bad.append("donor patch does not target %s" % dn)
    if 'GizkaDefNames' not in _read("Source/RSW_GizkaSettings.cs"):
        bad.append("global-rate tuning table is gone")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimStarWars", "GizkaStowaway.md")):
        bad.append("walk missing")
    return bad


# ============================================================================ behaviour rules, offline
# GIZKASTOWAWAY_COVERAGE_GAPS_1 (offline half). Pure reads of the shipped C#/XML; every function takes the source dict so
# selftest_gizkastowaway.py can plant a break in memory. Live behaviour (a landing delivering a gizka, game-days of
# replication, chewing a real building) stays UNMEASURED and is listed by mechanics_unmeasured.

def load_srcs():
    d = os.path.join(HERE, "Source")
    strip = lambda txt: re.sub(r"(?m)^\s*//.*$", "", txt)      # full-line comments only: prose must not satisfy or trip a check
    return dict((f, strip(open(os.path.join(d, f), encoding="utf-8").read())) for f in sorted(os.listdir(d)) if f.endswith(".cs"))


def method_body(src, header_re):
    """First brace-balanced block after the first match of header_re (or the text to ';' for an expression member)."""
    m = re.search(header_re, src)
    if not m:
        return None
    i, semi = src.find("{", m.end()), src.find(";", m.end())
    if semi >= 0 and (i < 0 or semi < i):
        return src[m.end():semi]
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        depth += (src[j] == "{") - (src[j] == "}")
        if depth == 0:
            return src[i:j + 1]
    return None


MGR, FEC, INF, PAT, POP = ("RSW_GizkaStowawayManager.cs", "HediffComp_GizkaFecundity.cs", "MapComponent_GizkaInfestation.cs",
                           "RSW_GizkaHarmonyPatches.cs", "RSW_GizkaPopulation.cs")
# (notify method, the trigger setting it must read, the chance constant it must roll) -- chances ordered by design:
# the gravship landing is the flagship, a completed trade the rarest.
TRIGGERS = [("Notify_GravshipLanded", "triggerGravship", "ChanceGravship"), ("Notify_SalvageDeconstructed", "triggerSalvage", "ChanceSalvage"),
            ("Notify_TradeCompleted", "triggerTrade", "ChanceTrade"), ("Notify_QuestCompleted", "triggerQuest", "ChanceQuest")]


def _const(src, name):
    m = re.search(r"const (?:float|int) %s = ([0-9.]+)f?;" % name, src)
    return float(m.group(1)) if m else None


def trigger_findings(srcs):
    out, m = [], srcs.get(MGR, "")
    ready = method_body(m, r"private bool Ready\(bool triggerEnabled\)") or ""
    for need in ("!RSW_GizkaSettings.stowawayEventsEnabled", "!triggerEnabled", "RSW_GizkaPopulation.Kind == null", "DiscoveryCooldownTicks"):
        if need not in ready:
            out.append("Ready() no longer checks %s (master switch / trigger toggle / donor absent / cooldown)" % need)
    if _const(m, "DiscoveryCooldownTicks") != 900000:
        out.append("discovery cooldown is %s ticks, ruled 900000 (15 days)" % _const(m, "DiscoveryCooldownTicks"))
    chances = {}
    for name, setting, const in TRIGGERS:
        body = method_body(m, r"public void %s\(" % name)
        if body is None:
            out.append("%s missing" % name)
            continue
        if "Ready(RSW_GizkaSettings.%s)" % setting not in body:
            out.append("%s does not gate on %s (a toggle with no effect, or default-on when settings are null)" % (name, setting))
        if "Roll(%s)" % const not in body:
            out.append("%s does not roll %s" % (name, const))
        if body.count("Discover(") != 1:
            out.append("%s calls Discover %d times: a trigger must deliver exactly one gizka" % (name, body.count("Discover(")))
        chances[const] = _const(m, const)
    if all(v is not None for v in chances.values()) and len(chances) == 4:
        order = [chances[c] for c in ("ChanceGravship", "ChanceSalvage", "ChanceQuest", "ChanceTrade")]
        if order != sorted(order, reverse=True) or len(set(order)) != 4:
            out.append("trigger chances %s are not gravship > salvage > quest > trade" % order)
    roll = method_body(m, r"private bool Roll\(float baseChance\)") or ""
    if "Mathf.Clamp01(baseChance * f)" not in roll or "RSW_GizkaSettings.discoveryFrequency" not in roll:
        out.append("Roll is no longer clamp01(baseChance * discoveryFrequency) defaulting to 1")
    disc = method_body(m, r"private void Discover\(") or ""
    if "SpawnStowaway(map, cell, Faction.OfPlayer, newborn: false)" not in disc or "lastDiscoveryTick = Find.TickManager.TicksGame" not in disc:
        out.append("Discover must spawn ONE tame (player-faction, adult) stowaway and stamp the shared cooldown")
    # the hooks reach Notify_* and nothing else delivers
    pat = srcs.get(PAT, "")
    for name, _s, _c in TRIGGERS:
        if "Instance?.%s(" % name not in pat:
            out.append("no Harmony hook calls %s" % name)
    if "IncidentDef" in m:
        out.append("an IncidentDef route exists: discovery must ride a player action, never a storyteller roll")
    return out


def discovery_chance(base, freq):
    return min(1.0, max(0.0, base * freq))


def replicate_interval_days(base_days, stretch_at_cap, pop, cap, rate):
    """Mirror of HediffComp_GizkaFecundity.ResetInterval without the +-15 percent jitter, in days."""
    rate = 1.0 if rate <= 0.01 else rate
    fill = 1.0 if cap <= 0 else min(1.0, max(0.0, float(pop) / cap))
    stretch = 1.0 + (max(1.0, stretch_at_cap) - 1.0) * fill
    return base_days * stretch / rate


def fecundity_findings(srcs, props):
    """props = (baseReplicateIntervalDays, intervalStretchAtCap, minBreedingTemperature, minFoodLevel) from the hediff XML."""
    out, f = [], srcs.get(FEC, "")
    base, stretch, mint, minfood = props
    tick = method_body(f, r"public override void CompPostTickInterval\(") or ""
    order = [tick.find(x) for x in ("!RSW_GizkaSettings.stowawayEventsEnabled", "CurLifeStageIndex", "ticksUntilReplicate < 0", "IsComfortable(pawn)",
                                    "ticksUntilReplicate -= delta", "TryReplicate(pawn)")]
    if -1 in order or order != sorted(order):
        out.append("CompPostTickInterval order is not master switch -> adult only -> init -> comfort gate -> burn fuse -> replicate (%s)" % order)
    if "if (!IsComfortable(pawn)) return;" not in tick:
        out.append("a cold or hungry gizka is not stalled: the comfort gate must return BEFORE the fuse burns")
    com = method_body(f, r"private bool IsComfortable\(") or ""
    if "temp < Props.minBreedingTemperature) return false" not in com or "food.CurLevelPercentage < Props.minFoodLevel) return false" not in com:
        out.append("IsComfortable no longer refuses below minBreedingTemperature / minFoodLevel")
    rep = method_body(f, r"private void TryReplicate\(") or ""
    if "CountOnMap(pawn.Map) >= cap) return;" not in rep or rep.find(">= cap) return;") > rep.find("SpawnStowaway"):
        out.append("TryReplicate can spawn at or above the population cap")
    if "pawn.Faction, newborn: true" not in rep:
        out.append("an offspring must inherit the parent's faction and be a newborn")
    ri = method_body(f, r"private int ResetInterval\(") or ""
    for need in ("RSW_GizkaSettings.breedingRate <= 0.01f) ? 1f", "Mathf.Lerp(1f, Mathf.Max(1f, Props.intervalStretchAtCap), fill)",
                 "Props.baseReplicateIntervalDays * stretch / rate", "Mathf.Max(2500,", "* 60000f *", "Rand.Range(0.85f, 1.15f)"):
        if need not in ri:
            out.append("ResetInterval lost `%s`" % need)
    # the numbers: slow burn at an empty map, 8x slower at the cap, breedingRate divides, the cap clamps
    if replicate_interval_days(base, stretch, 0, 22, 1.0) != base:
        out.append("an empty map does not replicate at the base interval")
    if abs(replicate_interval_days(base, stretch, 22, 22, 1.0) - base * stretch) > 1e-9:
        out.append("at the cap the interval does not stretch to base x intervalStretchAtCap")
    if not replicate_interval_days(base, stretch, 0, 22, 1.0) < replicate_interval_days(base, stretch, 11, 22, 1.0) < replicate_interval_days(base, stretch, 22, 22, 1.0):
        out.append("the interval is not strictly increasing toward the cap (the anti-exponential flattening)")
    if abs(replicate_interval_days(base, stretch, 5, 22, 2.0) * 2 - replicate_interval_days(base, stretch, 5, 22, 1.0)) > 1e-9:
        out.append("breedingRate 2x does not halve the interval")
    if not (mint > 0 and 0 < minfood < 1):
        out.append("comfort gate numbers are not usable (minBreedingTemperature %s, minFoodLevel %s)" % (mint, minfood))
    return out


def stage_for(srcs, count, cap):
    b = method_body(srcs.get(INF, ""), r"public static GizkaStage StageFor\(") or ""
    m = [(a, c) for c, a in re.findall(r"Mathf\.Max\((\d+), Mathf\.RoundToInt\(cap \* ([0-9.]+)f\)\)", b)]
    if len(m) != 3 or "if (cap < 4) cap = 4;" not in b:
        return None
    if count <= 0:
        return 0
    plague, infest, under = [(float(a), int(c)) for a, c in m]
    rnd = lambda x: int(x + 0.5) if x - int(x) != 0.5 else (int(x) if int(x) % 2 == 0 else int(x) + 1)   # Mathf.RoundToInt: banker's
    cap = max(cap, 4)
    p = max(plague[1], rnd(cap * plague[0]))
    if "int plague = Mathf.Min(cap, " in b:          # each clamp mirrored only while the source carries it
        p = min(cap, p)
    i = max(infest[1], rnd(cap * infest[0]))
    if "int infest = Mathf.Min(plague - 1, " in b:
        i = min(p - 1, i)
    u = max(under[1], rnd(cap * under[0]))
    if "int under = Mathf.Min(infest - 1, " in b:
        u = min(i - 1, u)
    for lvl, floor in ((4, p), (3, i), (2, u)):
        if count >= floor:
            return lvl
    return 1


def plague_unreachable_caps(srcs):
    """Population caps on the settings slider (4..80) at which Plague is never reached at a full map (breeding halts AT
    the cap). Was [4, 5] before the 2026-10-04 clamp (floor 6 > cap); the bar below now requires []."""
    return [c for c in range(4, 81) if stage_for(srcs, c, c) != 4]


def skipped_stage_caps(srcs):
    """Caps (4..80) at which counting 0..cap does not pass through every stage 0..4 ("no stage skips", spec)."""
    return [c for c in range(4, 81) if sorted(set(stage_for(srcs, n, c) for n in range(0, c + 1))) != [0, 1, 2, 3, 4]]


def infestation_findings(srcs):
    out, f = [], srcs.get(INF, "")
    if stage_for(srcs, 5, 22) is None:
        return ["StageFor no longer has the parsed shape (three fractions-of-cap bands with floors)"]
    names = [stage_for(srcs, n, 22) for n in (0, 1, 3, 7, 16)]
    if names != [0, 1, 2, 3, 4]:
        out.append("stage bands at the shipped cap 22 are %s for counts 0,1,3,7,16 (want 0,1,2,3,4: none, cute, underfoot, infestation, plague)" % names)
    if plague_unreachable_caps(srcs):
        out.append("Plague is unreachable at a full map for caps %s (the stage that says 'population has peaked')" % plague_unreachable_caps(srcs))
    if skipped_stage_caps(srcs):
        out.append("a stage is skipped on the way to the cap for caps %s (spec: no stage skips)" % skipped_stage_caps(srcs)[:8])
    for cap in (6, 8, 22, 80):
        seq = [stage_for(srcs, n, cap) for n in range(0, cap + 1)]
        if seq != sorted(seq) or seq[-1] != 4:
            out.append("stage is not monotone in count (or never reaches Plague at the cap) for cap %d" % cap)
    mc = method_body(f, r"public override void MapComponentTick\(\)") or ""
    if "TicksGame % CheckIntervalTicks != 0" not in mc or "!RSW_GizkaSettings.stowawayEventsEnabled" not in mc:
        out.append("MapComponentTick lost its cadence gate or the master switch")
    if "if (RSW_GizkaSettings.chewingEnabled && stage >= GizkaStage.Infestation)" not in mc:
        out.append("chewing is not gated on chewingEnabled AND the Infestation stage")
    if "if (stage > lastStage) AnnounceStage" not in mc:
        out.append("a stage is announced when it steps DOWN (the warning must be re-earned, never repeated on the way down)")
    ch = method_body(f, r"private void DoChewing\(") or ""
    for need in ("brk.BrokenDown) continue", "!power.PowerOn) continue", "perRoom.TryGetValue(room, out int here)",
                 "ChewMtbTicksPerGizka / here", "brk.DoBreakdown();", "return;   // at most one chewed building per check"):
        if need not in ch:
            out.append("DoChewing lost `%s`" % need)
    if "r.UsesOutdoorTemperature) continue" not in ch:
        out.append("gizka outdoors can chew: an outdoor cell has no room to share with a building")
    if _const(f, "ChewMtbTicksPerGizka") != 900000 or _const(f, "CheckIntervalTicks") != 2000:
        out.append("chew cadence constants moved (ChewMtbTicksPerGizka %s, CheckIntervalTicks %s)" % (_const(f, "ChewMtbTicksPerGizka"), _const(f, "CheckIntervalTicks")))
    pop = srcs.get(POP, "")
    ls = method_body(pop, r"public static int CountOnMap\(") or ""
    if "IsStowawayGizka(pawns[i])" not in ls:
        out.append("the population count includes gizka that are not stowaway lineage (bought gizka would fill the cap)")
    iw = method_body(pop, r"public static bool IsStowawayGizka\(") or ""
    if "GetFirstHediffOfDef(Fecundity) != null" not in iw or "p.Dead" not in iw:
        out.append("IsStowawayGizka is not 'alive and carries the fecundity hediff'")
    return out


def cull_findings(srcs):
    out = []
    b = method_body(srcs.get(PAT, ""), r"public static void Prefix\(Pawn __instance\)") or ""
    if "!RSW_GizkaSettings.stowawayEventsEnabled || !RSW_GizkaSettings.cullGuiltEnabled) return;" not in b:
        out.append("cull guilt is not gated on the master switch AND cullGuiltEnabled")
    for need in ("IsStowawayGizka(victim)", "WitnessRadius", "GenSight.LineOfSight(", "FreeColonistsSpawned", "TryGainMemory(thought)"):
        if need not in b:
            out.append("cull guilt lost `%s`" % need)
    if _const(srcs.get(PAT, ""), "WitnessRadius") != 12:
        out.append("witness radius moved from 12")
    if "typeof(Pawn), nameof(Pawn.Kill)" not in srcs.get(PAT, ""):
        out.append("cull guilt is not a Pawn.Kill prefix")
    return out


def slider_findings(srcs):
    """Each gameplay slider's range contains its shipped default, and discoveryFrequency can reach 0 (the off arm of discovery)."""
    src = srcs.get("RSW_GizkaSettings.cs", "")
    fields = dict((m.group(2), (m.group(1), m.group(3).strip())) for m in _FIELD.finditer(src.split("ExposeData", 1)[0]))
    out = []
    rng = dict((m.group(1), (float(m.group(2)), float(m.group(3)))) for m in re.finditer(
        r"(\w+) = (?:Mathf\.RoundToInt\(|\(int\))?list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)", src))
    if len(rng) < 4:
        return ["only %d sliders parsed from the settings window: parse failure" % len(rng)]
    for n, (lo, hi) in rng.items():
        d = _num(fields[n][1]) if n in fields else None
        if d is None or not lo <= d <= hi:
            out.append("slider %s range %s..%s does not contain its default %s" % (n, lo, hi, d))
    if rng.get("discoveryFrequency", (1, 1))[0] != 0:
        out.append("discoveryFrequency cannot be slid to 0: no way to silence discovery short of the master switch")
    return out


def behaviour_props():
    h = [e for e in ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RSW_GizkaHediffs.xml")).getroot()
         if e.findtext("defName") == FECUNDITY][0]
    c = h.find("comps/li")
    return tuple(float(c.findtext(k)) for k in ("baseReplicateIntervalDays", "intervalStretchAtCap", "minBreedingTemperature", "minFoodLevel"))



try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


class _Unmeasured(Exception):
    pass


def _live(t):
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    t._why = why
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw):
        yield
    if getattr(t, "_why", None) and not before:
        t.upstream_failed = False
        t.upstream_reason = None
    t._why = None


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _same(ty, a, b):
    if ty == "bool":
        return str(a).lower() == str(b).lower()
    try:
        return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


def _raw(t, action, field, value=None):
    kw = dict(typeName=SETTINGS, action=action, field=field)
    if value is not None:
        kw["value"] = str(value)
    r = t.session.call("jawa/mod_settings_field", **kw)
    return r if isinstance(r, dict) else {}


def _map_centre(t):
    r = t.bridge_call("jawa/map_info")
    if _live(t) and isinstance(r, dict) and r.get("sizeX") and r.get("sizeZ"):
        return int(r["sizeX"]) // 2, int(r["sizeZ"]) // 2
    return t.anchor


def _spawn(t, kind, x, z, faction="player"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn: %r" % (kind, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _snap(t, pid):
    r = t.bridge_call("jawa/pawn_get", pawn=pid)
    if not _live(t):
        return {}
    snap = (r or {}).get("pawn") or r or {}
    return snap if isinstance(snap, dict) else {}


def _hediff_row(snap, name):
    if "hediffs" not in snap:
        return "unreadable", None
    for h in snap["hediffs"] or []:
        if isinstance(h, dict):
            if name in (h.get("def"), h.get("defName"), h.get("hediff")):
                return "present", h
        elif str(h) == name:
            return "present", {}
    return "absent", None


def _gizka_kind(t):
    """The first gizka PawnKindDef that resolves live, or None (neither the donor nor SWBestiary is loaded)."""
    for k in GIZKA_KINDS:
        r = t.bridge_call("jawa/get_defs", defs="PawnKindDef/" + k, fields="defName", limit=2)
        if _live(t) and isinstance(r, dict) and r.get("success") is not False and int(r.get("foundCount", 0)) == 1:
            return k
    return None


def _build_suite():
    suite = Suite("GizkaStowaway")
    suite.toggles = sorted(settings_fields())

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with _comp(t, "control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                _ok(r, "get_defs control")
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    _fail("control def reads as present: %r" % r)
        with _comp(t, "every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=60)
            if _live(t):
                _ok(r, "get_defs")
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    _fail("%d of %d defs resolved; notFound=%r" % (int(r.get("foundCount", 0)), len(names),
                                                                  (r.get("notFound") or [])[:8]))
        with _comp(t, "fecundity_comp_type_loaded", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="HediffDef/" + FECUNDITY, fields="comps", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs fecundity comps")
                blob = str((((r.get("defs") or [{}])[0]).get("fields") or {}).get("comps"))
                if "GizkaFecundity" not in blob:
                    _unmeasured(t, "get_defs comps did not name GizkaFecundity (shape %s)" % blob[:120])

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with _comp(t, "settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                _fail("settings probe found no field (blind regex)")
        for field, (ty, _init) in sorted(settings_fields().items()):
            with _comp(t, "%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    _fail("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        _fail("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        _fail("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    _fail("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("harmony_wiring")
    def harmony_wiring(t):
        for ty, method in hooks():
            with _comp(t, "%s_%s_patched_by_this_mod" % (ty, method), toggle=HOOK_TOGGLE.get(method)):
                r = t.bridge_call("jawa/harmony_patches", typeName=ty, methodName=method)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked about %s.%s: %s" % (ty, method, str(r)[:160]))
                owners = []
                for m in (r.get("methods") or []):
                    for kind in ("prefixes", "postfixes"):
                        owners.extend(p.get("owner") for p in (m.get(kind) or []))
                if HARMONY_ID not in owners:
                    _fail("%s.%s carries no patch from %s (owners: %s)"
                          % (ty, method, HARMONY_ID, sorted(set(o for o in owners if o))[:8]))

    @suite.chain("fecundity_state")
    def fecundity_state(t):
        with _comp(t, "gizka_with_fecundity_carries_it_control_does_not", toggle="stowawayEventsEnabled"):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka PawnKindDef (Gizka / RSW_Gizka) resolves: neither the donor nor SWBestiary is loaded")
            cx, cz = _map_centre(t)
            t.clear_area(size=12)
            if _live(t):
                sick = _spawn(t, kind, cx, cz)
                ctrl = _spawn(t, kind, cx + 4, cz, faction="player")
                _ok(t.bridge_call("jawa/pawn_health", pawn=sick, action="add", hediff=FECUNDITY, severity=1.0),
                    "pawn_health add")
                state, _r = _hediff_row(_snap(t, sick), FECUNDITY)
                if state == "unreadable":
                    _unmeasured(t, "jawa/pawn_get has no hediffs list")
                if state != "present":
                    _fail("a gizka given %s does not carry it" % FECUNDITY)
                if _hediff_row(_snap(t, ctrl), FECUNDITY)[0] == "present":
                    _fail("the control gizka carries %s without being given it" % FECUNDITY)

    @suite.chain("bait_poison")
    def bait_poison(t):
        with _comp(t, "bait_item_and_recipe_resolve", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RSW_GizkaBait;RecipeDef/RSW_MakeGizkaBait;HediffDef/" + POISON,
                              fields="defName", limit=6)
            if _live(t):
                _ok(r, "get_defs bait")
                if r.get("notFound") or int(r.get("foundCount", 0)) != 3:
                    _fail("bait defs did not all resolve: %r" % r)
        with _comp(t, "poison_hediff_advances_on_a_gizka", beyond_toggle=True):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka PawnKindDef resolves (donor / SWBestiary not loaded)")
            cx, cz = _map_centre(t)
            if _live(t):
                pid = _spawn(t, kind, cx + 8, cz)
                _ok(t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=POISON, severity=0.15), "pawn_health add")
                s0 = _hediff_row(_snap(t, pid), POISON)[1] or {}
                if "severity" not in s0:
                    _unmeasured(t, "pawn_get hediff rows carry no severity field")
                t.wait_ticks(1500)
                s1 = _hediff_row(_snap(t, pid), POISON)[1]
                if s1 is None:
                    _fail("the poison hediff vanished from a live gizka after 1500 ticks")
                if float(s1.get("severity", -1)) <= float(s0["severity"]):
                    _fail("poison severity did not advance (%s -> %s)" % (s0["severity"], s1.get("severity")))

    @suite.chain("donor_patch")
    def donor_patch(t):
        with _comp(t, "gizka_market_value_flattened_to_15", beyond_toggle=True):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka def resolves: the FindMod-guarded donor patch correctly no-ops without a donor")
            if _live(t):
                r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + kind, fields="statBases", deep=True, limit=2)
                _ok(r, "get_defs gizka statBases")
                sb = (((r.get("defs") or [{}])[0]).get("fields") or {}).get("statBases")
                if not isinstance(sb, list) or not all(isinstance(x, dict) for x in sb):
                    _unmeasured(t, "get_defs returned statBases in an unreadable shape: %r" % (sb,))
                mv = [x for x in sb if "MarketValue" in (str(x.get("stat")), str(x.get("defName")), str(x.get("name")))]
                if not mv:
                    _unmeasured(t, "no MarketValue row in statBases: %r" % (sb[:6],))
                if abs(float(mv[0].get("value", -1)) - 15.0) > 1e-6:
                    _fail("%s MarketValue reads %r, patched to 15 (patch did not apply / stale deploy)" % (kind, mv[0]))

    @suite.chain("behaviour_rules")
    def behaviour_rules(t):
        """GIZKASTOWAWAY_COVERAGE_GAPS_1 offline half: the four triggers each read their own toggle and chance, replication
        halts while cold/hungry and at the cap, the interval formula, stage bands, chewing gates, cull guilt gates and slider
        ranges. Cheap-and-wrong first (a failing component marks later ones UNMEASURED)."""
        srcs = load_srcs()
        with _comp(t, "sliders_reach_their_defaults_and_discovery_can_be_silenced", beyond_toggle=True):
            if len(srcs) < 6:
                _fail("read only %d source files: parse failure" % len(srcs))
            bad = slider_findings(srcs)
            if bad:
                _fail("; ".join(bad[:4]))
        with _comp(t, "four_triggers_each_gate_on_their_toggle_and_deliver_one", toggle="stowawayEventsEnabled"):
            bad = trigger_findings(srcs)
            if bad:
                _fail("; ".join(bad[:4]))
        with _comp(t, "replication_stalls_cold_and_hungry_and_stops_at_the_cap", toggle="populationCap"):
            bad = fecundity_findings(srcs, behaviour_props())
            if bad:
                _fail("; ".join(bad[:4]))
        with _comp(t, "stage_bands_and_chewing_gates_hold", toggle="chewingEnabled"):
            bad = infestation_findings(srcs)
            if bad:
                _fail("; ".join(bad[:4]))
        with _comp(t, "cull_guilt_gates_and_witness_rules_hold", toggle="cullGuiltEnabled"):
            bad = cull_findings(srcs)
            if bad:
                _fail("; ".join(bad[:4]))

    @suite.chain("mechanics_unmeasured")
    def mechanics_unmeasured(t):
        for name, toggle, why in (
            ("gravship_landing_delivers_one_tame_gizka", "triggerGravship",
             "needs a real gravship landing (Scenario.PostGravshipLanded) and a 35 percent roll; the postfix is attached (harmony_wiring)"),
            ("salvage_trade_quest_hooks_deliver", "triggerSalvage",
             "wreck deconstruction, a completed trade and a quest success each need a driven game event and a chance roll"),
            ("fecundity_replicates_while_fed_and_warm", "breedingRate",
             "a replication interval of ~4 days needs game days of ticks and a fed warm gizka"),
            ("population_cap_stops_breeding", "populationCap",
             "needs a colony grown to the cap (22 per map) over game days"),
            ("infestation_stage_chews_powered_buildings", "chewingEnabled",
             "needs the Infestation stage (~3x the cute count) with a powered building in a shared room"),
            ("cold_below_breeding_gate_stalls_replication", "stowawayEventsEnabled",
             "needs a gizka room vented below 12 C and days of ticks; no verb sets a room temperature"),
            ("cull_weighs_on_watching_colonists", "cullGuiltEnabled",
             "needs a slaughter with colonist witnesses; the Pawn.Kill prefix is attached (harmony_wiring)"),
            ("global_breeding_slider_rescales_donor_fields", "globalBreedingRate",
             "RSW_GizkaDonorTuning.Apply runs on WriteSettings or its button, not on a bridge field write; the live "
             "egg-layer fields have no reader here"),
        ):
            with _comp(t, name, toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
