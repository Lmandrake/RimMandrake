"""validation.py -- modcheck suite for RimUtinni: Droid Repair Jobs (mandrake.rut.droidrepairjobs).

First script (debug_process.md section 2), item DROID_REPAIR_JOBS_FIRST_SCRIPT_1. Walk:
design/validation_walks/RimUtinni/DroidRepairJobs.md (`## must be true`, each line ends in
`-> chain.component` or `-> UNCOVERED: why`). NEVER RUN LIVE YET: every live shape below that is unproven
degrades to UNMEASURED, never PASS.

Run offline: `python3 src/RimUtinni/DroidRepairJobs/validation.py` -> `STATIC: PASS (0 findings)`.
Live: modcheck/northstar_driver on a tier carrying HumanoidAlienRaces + Droidworks (hard dependency) +
this mod, all five DLCs, a plain open map on a world with a friendly settlement near it.

WHAT IT PROVES, by state read:
  * defs_resolve: every def the mod ships, and every Droidworks def its quest names (the three part-tier
    hediff lists, the four droid kinds), resolves live; a control probe reads absent.
  * flip_<field>: each Mod Settings field round-trips (numeric compare), generated from the settings class.
  * payment_scaling: with `wealthAndReputationScaling` off the quest the engine generates quotes exactly
    base 320 / fine 512 (x1.6) / shoddy 128 (x0.4), and `paymentMultiplier` 2 doubles all three (the doubled
    arm is also the control that the read can say "different").
  * fault_hediff: RUT_DroidJobFault lands on a Droidworks droid and a second, untouched droid lacks it.
NOT PROVEN HERE (UNMEASURED, named): the grading at pickup (a 5-9 day job timer and a quest signal no
bridge tool fires), the goodwill outcomes, the silver payout, the wealth/reputation arm of the payment (it
depends on which faction's settlement the generator picks), the quest's natural random-pool firing.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))      # `python3 validation.py` finds modcheck

SETTINGS = "RimMandrake.Utinni.DroidRepairJobs.DroidRepairJobsSettings"
QUEST = "RUT_DroidRepairJob"
FAULT = "RUT_DroidJobFault"
MOD_CS = os.path.join(HERE, "Source", "DroidRepairJobsMod.cs")
QUEST_XML = os.path.join(HERE, "Defs", "QuestScriptDefs", "Quest_DroidRepairJob.xml")
BASE, FINE_X, SHODDY_X = 320, 1.6, 0.4          # the base is parsed and cross-checked in static_checks


# --------------------------------------------------------------------------- parsed facts (never hand-listed)

def settings_defaults():
    """{field: (type, default)} parsed from the settings class's `public static` initialisers."""
    src = open(MOD_CS, encoding="utf-8").read()
    body = src.split("class DroidRepairJobsSettings")[1].split("ExposeData")[0]
    out = {}
    for typ, name, val in re.findall(r"public static (bool|float|int|string) (\w+)\s*=\s*([^;]+);", body):
        v = val.strip()
        if typ == "bool":
            out[name] = (typ, v == "true")
        elif typ == "float":
            out[name] = (typ, float(v.rstrip("f")))
        elif typ == "int":
            out[name] = (typ, int(v))
        else:
            out[name] = (typ, v.strip('"'))
    return out


def shipped_defs():
    """(defType, defName) for every concrete top-level def in the mod's own Defs/ XML."""
    out = []
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in sorted(files):
            if f.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, f)).getroot():
                    n = e.findtext("defName")
                    if n and e.get("Abstract") != "True":
                        out.append((e.tag.split(".")[-1], n))
    return out


def quest_dependency_defs():
    """Defs the quest names but another mod (Droidworks) ships: part-tier hediffs and droid kinds, from the XML."""
    root = ET.parse(QUEST_XML).getroot()
    out = []
    for tier in ("inferiorHediffs", "standardHediffs", "superiorHediffs"):
        for li in root.iter(tier):
            out += [("HediffDef", (x.text or "").strip()) for x in li.findall("li")]
    out += [("PawnKindDef", (k.text or "").strip()) for k in root.iter("kindDef")]
    seen, uniq = set(), []
    for d in out:
        if d[1] and d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def droid_kind():
    """A droid kind the quest itself generates (first one in the XML)."""
    return [n for ty, n in quest_dependency_defs() if ty == "PawnKindDef"][0]


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:                       # offline static run outside the modcheck path
    Suite = None

if Suite is not None:
    suite = Suite("DroidRepairJobs")
    SD = settings_defaults()
    suite.toggles = [f for f, (ty, _) in SD.items() if ty == "bool"]

    # ----------------------------------------------------------------------- helpers

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _fail(msg):
        raise ExpectationFailed(msg)

    class _Unmeasured(Exception):
        pass

    def _unmeasured(t, why):
        t._why = why
        t._record("UNMEASURED", why)
        t.upstream_failed = True
        raise _Unmeasured(why)

    @contextlib.contextmanager
    def _comp(t, name, **kw):
        """t.component() with the UNMEASURED fix-up (verdict stays UNMEASURED, detail names the reason, the
        chain is not poisoned for an independent next component)."""
        before = t.upstream_failed
        t._why = None
        with t.component(name, **kw) as tt:
            yield tt
        why = getattr(t, "_why", None)
        if why and not before:
            t.components[-1].detail = "UNMEASURED: %s" % why
            t.upstream_failed = False
        t._why = None
        if t.session is not None:
            c = t.components[-1]
            print("[drj] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
                  file=sys.stderr, flush=True)

    def _sv(v):
        if isinstance(v, bool):
            return "True" if v else "False"
        if isinstance(v, float):
            return "%g" % v
        return str(v)

    def _same(got, want):
        if str(got).strip().lower() == str(want).strip().lower():
            return True
        try:
            return abs(float(got) - float(want)) < 1e-6
        except (TypeError, ValueError):
            return False

    def _put(t, field, value):
        s = t.session
        if s is None:
            return
        sv = _sv(value)
        r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=sv)
        if not (r or {}).get("success"):
            raise ExpectationFailed("mod_settings_field set %s=%r failed: %r" % (field, sv, r))
        g = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success") or not _same((g or {}).get("value"), sv):
            raise ExpectationFailed("mod_settings_field %s did not take: wrote %r, read back %r"
                                    % (field, sv, (g or {}).get("value")))

    def _get(t, field):
        g = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success"):
            raise ExpectationFailed("mod_settings_field get %s failed: %r" % (field, g))
        return g.get("value")

    @contextlib.contextmanager
    def _arm(t, **values):
        """Set settings for the body; ALWAYS restore each to its shipped (parsed) default."""
        try:
            for f, v in values.items():
                _put(t, f, v)
            yield
        finally:
            for f in values:
                try:
                    _put(t, f, SD[f][1])
                except Exception as e:
                    print("[drj] RESTORE FAILED %s: %s" % (f, e), file=sys.stderr, flush=True)

    def _ok(r, what):
        if not isinstance(r, dict) or r.get("success") is False:
            _fail("%s failed: %r" % (what, r))
        return r

    # ----------------------------------------------------------------------- 1. defs_resolve

    def _resolve(t, pairs, what):
        want = ["%s/%s" % x for x in pairs]
        for i in range(0, len(want), 25):
            chunk = want[i:i + 25]
            r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=100)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "get_defs could not be asked: %s" % str(r)[:140])
                if r.get("notFound") or r.get("foundCount") != len(chunk):
                    _fail("%s did not load (a def with an unresolvable field is discarded silently): "
                          "notFound=%r foundCount=%r of %d" % (what, r.get("notFound"), r.get("foundCount"), len(chunk)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        """Every def the mod ships, and every Droidworks def its quest names, resolves live; a control reads absent."""
        with _comp(t, "shipped_defs_resolve", beyond_toggle=True):
            _resolve(t, shipped_defs(), "shipped defs")
        with _comp(t, "droidworks_defs_the_quest_names_resolve", beyond_toggle=True):
            _resolve(t, quest_dependency_defs(), "Droidworks defs named by the quest (a missing one makes the quest unusable)")
        with _comp(t, "control_absent_def_reads_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="QuestScriptDef/RUT_DroidRepairJob_NoSuchControl")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "control ask failed: %s" % str(r)[:140])
                if r.get("foundCount") != 0 or not r.get("notFound"):
                    _fail("the probe cannot say absent: control returned %r" % r)

    # ----------------------------------------------------------------------- 2. settings round trips

    def _alt(typ, d):
        if typ == "bool":
            return not d
        if typ == "int":
            return d + 1
        if typ == "string":
            return "x"
        return d * 2 + 1

    def _make_flip(field, typ, default):
        def chain(t):
            with _comp(t, "%s_round_trips" % field, toggle=field if typ == "bool" else None, beyond_toggle=typ != "bool"):
                try:
                    _put(t, field, _alt(typ, default))
                    _put(t, field, default)
                finally:
                    if t.session is not None:
                        try:
                            _put(t, field, default)
                        except Exception as e:
                            print("[drj] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
        chain.__doc__ = "Write alt, read back, write default, read back (numeric compare) for %s." % field
        return chain

    for _f, (_ty, _d) in SD.items():
        suite.chain("flip_%s" % _f)(_make_flip(_f, _ty, _d))

    # ----------------------------------------------------------------------- 3. payment scaling

    def _quest_rows(t):
        r = _ok(t.bridge_call("jawa/quest_lifecycle", action="list"), "quest_lifecycle(list)")
        return r.get("quests") or []

    def _offer(t):
        """Fire the quest unaccepted; return the new quest row's JSON text. UNMEASURED when it cannot be made."""
        before = {json.dumps(q, sort_keys=True) for q in _quest_rows(t)}
        r = t.bridge_call("jawa/fire_quest", questDef=QUEST, accept=False)
        if not (r or {}).get("success"):
            _unmeasured(t, "fire_quest could not generate %s (QuestNode_GetNearbySettlement needs a visitable, non-hostile "
                           "settlement within 36 tiles of the map): %s" % (QUEST, str(r)[:300]))
        new = [q for q in _quest_rows(t) if json.dumps(q, sort_keys=True) not in before]
        mine = [q for q in new if QUEST.lower() in json.dumps(q).lower() or "droid" in json.dumps(q).lower()]
        if not mine:
            _unmeasured(t, "quest_lifecycle(list) shows no new droid-repair quest after fire_quest succeeded: %s" % str(r)[:200])
        return json.dumps(mine[0], sort_keys=True)

    def _quotes(txt, amounts):
        return [a for a in amounts if re.search(r"(?<![\d.])%d(?![\d.])" % a, txt)]

    @suite.chain("payment_scaling")
    def payment_scaling(t):
        flat = [BASE, int(round(BASE * FINE_X)), int(round(BASE * SHODDY_X))]
        double = [a * 2 for a in flat]
        box = {}
        with _comp(t, "flat_payment_quotes_320_512_128", toggle="wealthAndReputationScaling"):
            if _live(t):
                with _arm(t, wealthAndReputationScaling=False, paymentMultiplier=1.0):
                    txt = _offer(t)
                box["flat"] = txt
                if len(_quotes(txt, flat)) != 3:
                    if not re.search(r"descr|text|letter", txt, re.I):
                        _unmeasured(t, "quest_lifecycle rows carry no description text to read the quoted fees from: %s" % txt[:200])
                    _fail("with wealth/reputation scaling off and multiplier 1 the offered quest does not quote %s silver "
                          "(honest/fine/shoddy); quoted subset %s in %s" % (flat, _quotes(txt, flat), txt[:300]))
        with _comp(t, "payment_multiplier_scales_every_tier", toggle=None, beyond_toggle=True):
            if _live(t):
                if "flat" not in box:
                    _unmeasured(t, "the flat arm never produced a readable quote, so the multiplier arm has no baseline")
                with _arm(t, wealthAndReputationScaling=False, paymentMultiplier=2.0):
                    txt = _offer(t)
                if len(_quotes(txt, double)) != 3:
                    _fail("paymentMultiplier=2 with scaling off does not quote %s silver; quoted subset %s in %s"
                          % (double, _quotes(txt, double), txt[:300]))
                if _quotes(txt, [BASE]):
                    _fail("the doubled quote still carries the flat base %d: the read cannot tell the two apart" % BASE)
        with _comp(t, "wealth_and_reputation_arm_of_the_payment", toggle="wealthAndReputationScaling"):
            _unmeasured(t, "the scaled amount is base x tech-level factor x goodwill factor of whichever settlement the generator "
                           "picks; no bridge read names that faction before the quote, so only the flat arm is provable here")

    # ----------------------------------------------------------------------- 4. the fault hediff

    def _hed(t, pid):
        r = _ok(t.bridge_call("jawa/list_pawns", includeHealth=True, includeCorpses=False, limit=300), "list_pawns")
        row = {p.get("id"): p for p in (r.get("pawns") or [])}.get(pid)
        if row is None:
            _unmeasured(t, "seeded pawn %s is absent from list_pawns (dead or gone): not a statement about the hediff" % pid)
        return {h.get("def"): float(h.get("severity") or 0) for h in ((row.get("health") or {}).get("hediffs") or [])}

    @suite.chain("fault_hediff")
    def fault_hediff(t):
        P = {}
        with _comp(t, "site_ready_two_droids", beyond_toggle=True):
            if _live(t):
                t.clear_area(size=12)
                P["broken"] = t.spawn_pawn(droid_kind())
                x, z = t.anchor
                r = t.bridge_call("jawa/spawn_pawn", kindDef=droid_kind(), x=x + 4, z=z, faction="player", count=1)
                P["whole"] = ((_ok(r, "spawn_pawn").get("pawns") or [{}])[0]).get("id")
                if not P["broken"] or not P["whole"]:
                    _unmeasured(t, "could not spawn two %s droids (Droidworks/HAR not on this tier?)" % droid_kind())
        with _comp(t, "fault_lands_on_a_droid_and_only_that_droid", beyond_toggle=True):
            if _live(t):
                r = t.bridge_call("jawa/pawn_health", pawn=P["broken"], action="add", hediff=FAULT, severity=1.0)
                if not (r or {}).get("success"):
                    _unmeasured(t, "pawn_health add %s failed: %s" % (FAULT, str(r)[:160]))
                t.wait_ticks(60)
                if FAULT not in _hed(t, P["broken"]):
                    _fail("%s was added to the droid and is not on its hediff list: %s" % (FAULT, sorted(_hed(t, P["broken"]))))
                if FAULT in _hed(t, P["whole"]):
                    _fail("the untouched control droid carries %s: the read cannot tell a broken droid from a whole one" % FAULT)

    # ----------------------------------------------------------------------- 5. honest UNMEASURED

    def _um(chain, comp, why, toggle=None):
        def fn(t):
            with _comp(t, comp, toggle=toggle, beyond_toggle=toggle is None):
                _unmeasured(t, why)
        fn.__doc__ = "UNMEASURED: " + why
        suite.chain(chain)(fn)

    _um("pickup_grading", "fitted_part_tier_decides_fine_honest_shoddy_neglected",
        "grading runs at the PickupDue signal after a 5-9 day job timer (jobTicks); no bridge tool fires a quest signal, and a "
        "seeded part-effect hediff plus a faked timer would test the harness rather than the quest")
    _um("pickup_goodwill", "each_outcome_changes_goodwill_with_its_history_event",
        "needs a finished job (see pickup_grading) and a read of the faction tab's history-event line, which no bridge tool exposes")
    _um("pickup_payout", "silver_arrives_at_the_landing_spot_for_the_graded_tier",
        "needs a finished job; PaySilver drops stacks at the pickup spot only after PickupDue")
    _um("droid_kept_or_destroyed", "kept_and_destroyed_droid_outcomes_are_distinct_events",
        "needs the lodger droid to be arrested or killed during a live job and the lodgers.Arrested / .Destroyed signals to fire")
    _um("random_pool_firing", "quest_is_offered_by_the_storyteller_with_progress_score_4",
        "rootSelectionWeight 1.1, rootMinProgressScore 4 and minRefireDays 15 are storyteller-pool behaviour over days; "
        "fire_quest bypasses the pool, so selection itself is not provable on a bland map")

    @suite.chain("settings_restored")
    def settings_restored(t):
        """LAST: every field is back at its shipped (parsed) default; a leaked arm would corrupt the next run."""
        with _comp(t, "all_settings_at_shipped_defaults", beyond_toggle=True):
            if _live(t):
                bad = [(f, _get(t, f), _sv(d)) for f, (ty, d) in SD.items() if not _same(_get(t, f), _sv(d))]
                if bad:
                    _fail("settings left off their shipped default by an earlier arm: %s" % bad)
else:
    suite = None


# --------------------------------------------------------------------------- static (offline)

def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    sd = settings_defaults()
    if len(sd) < 1:
        bad.append("sanity probe: no settings fields parsed from DroidRepairJobsMod.cs (regex broke)")
    mod = open(MOD_CS, encoding="utf-8").read()
    for f in sd:
        if '"%s"' % f not in mod:
            bad.append("settings field %s is not Scribed in ExposeData" % f)
        if not re.search(r"\b%s\b" % f, mod.split("DoWindowContents")[1]):
            bad.append("settings field %s has no control in DoWindowContents" % f)
    proj = open(os.path.join(HERE, "Source", "RimMandrake.Utinni.DroidRepairJobs.csproj"), encoding="utf-8").read()
    listed = {c.replace("\\", "/") for c in re.findall(r'Compile Include="([^"]+)"', proj)}
    for cs in listed:
        if not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("csproj lists missing file " + cs)
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and f not in listed:
            bad.append("%s is not in the csproj (EnableDefaultCompileItems false: compiles into nothing)" % f)
    defs = shipped_defs()
    names = {n for _, n in defs}
    if len(defs) < 8:
        bad.append("sanity probe: only %d shipped defs parsed (expected quest + fault + 6 history events)" % len(defs))
    for n in (QUEST, FAULT):
        if n not in names:
            bad.append("script names def %s but the mod ships none" % n)
    # the quest's six goodwill reasons each have a HistoryEventDef, and every signal the custom node emits is consumed
    qtxt = open(QUEST_XML, encoding="utf-8").read()
    for reason in set(re.findall(r"<reason>(RUT_\w+)</reason>", qtxt)):
        if reason not in names:
            bad.append("quest names history event %s but no def ships it" % reason)
    if len(set(re.findall(r"<reason>(RUT_\w+)</reason>", qtxt))) != 6:
        bad.append("quest does not name the six distinct goodwill reasons")
    out_sigs = set(re.findall(r"<outSignal(?:Fine|Honest|Shoddy|Neglected)>(\w+)</", qtxt))
    in_sigs = set(re.findall(r"<inSignal>(\w+)</inSignal>", qtxt))
    if len(out_sigs) != 4 or not out_sigs <= in_sigs:
        bad.append("node out-signals %s are not all consumed by the quest (in-signals %s)" % (sorted(out_sigs), sorted(in_sigs)))
    # the slate defaults in XML are the C# multipliers applied to the base
    base = int(re.search(r"<basePayment>(\d+)</basePayment>", qtxt).group(1))
    cs = open(os.path.join(HERE, "Source", "QuestNode_DroidRepairJob.cs"), encoding="utf-8").read()
    fm = float(re.search(r"FineMultiplier = ([\d.]+)f", cs).group(1))
    sm = float(re.search(r"ShoddyMultiplier = ([\d.]+)f", cs).group(1))
    if (base, fm, sm) != (BASE, FINE_X, SHODDY_X):
        bad.append("script constants %s differ from the mod's base/multipliers %s" % ((BASE, FINE_X, SHODDY_X), (base, fm, sm)))
    for name, want in (("payHonest", base), ("payFine", int(round(base * fm))), ("payShoddy", int(round(base * sm)))):
        m = re.search(r"<name>%s</name>\s*<value>(\d+)</value>" % name, qtxt)
        if not m or int(m.group(1)) != want:
            bad.append("XML fallback %s is %s, expected %d (base x multiplier)" % (name, m.group(1) if m else None, want))
    # the three Droidworks tier lists are parallel (same five part stems, one per tier)
    root = ET.parse(QUEST_XML).getroot()
    stems = {}
    for tier in ("inferiorHediffs", "standardHediffs", "superiorHediffs"):
        el = next(root.iter(tier), None)
        stems[tier] = sorted(re.sub(r"_(Inferior|Standard|Superior)$", "", (x.text or "").strip()) for x in (el if el is not None else []))
    if not stems["inferiorHediffs"] or not (stems["inferiorHediffs"] == stems["standardHediffs"] == stems["superiorHediffs"]):
        bad.append("part-tier hediff lists are not parallel: %r" % stems)
    # the fault hediff must hurt a droid in a way a part install can be seen to cure
    hed = ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "HediffDefs_DroidRepairJob.xml")).getroot()[0]
    if hed.findtext("defName") != FAULT or hed.findtext("isBad") != "true" or hed.findtext("everCurableByItem") != "false":
        bad.append("%s must be a bad hediff that no item cures (only the part install resolves it)" % FAULT)
    # dependency declared
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    if "mandrake.rsw.droidworks" not in about:
        bad.append("About.xml lacks the Droidworks dependency")
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
