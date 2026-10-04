"""validation.py -- first script for RimUtinni: Scarlands Ladder (mandrake.rut.scarlandsladder).

WARSCAR_PILGRIM_CAMPS_1: the pilgrim camps are the gate of the Scarlands lore ladder. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run ScarlandsLadder

Environment: minimal + every DLC + mandrake.rm.lorestages + mandrake.rut.patches (RUT_Scarlands) + this mod.

WHAT IT PROVES (state reads through jawa/static_call proofs):
  * reading_walks_the_ladder: five journals read in sequence walk rungs 1-5, a sixth moves nothing, and
    RUT_Scarlands' live description is rung 5's ruled text.
  * reading_off_teaches_nothing: with journalsAdvanceLadder off a read leaves the ladder where it was.
  * camps_place: the camp genstep places a cold fire, the pilgrim's body and a journal per camp.
NOT PROVEN HERE: a camp generating on a real RUT_Scarlands map through the biome's extraGenSteps (first
poke: generate a RUT_Scarlands quicktest and list RUT_PilgrimJournal), the read JOB itself (a colonist
ordered to read it), the letter text on screen. ProofReadSequence resets the ladder to 0: test maps only.

STATIC (offline): `python3 validation.py` checks the five shipped rung texts equal the ruled cast bible
section 6B, the journal pages equal its journal column, and every setting is Scribed and exposed.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BIBLE = os.path.join(REPO, "design", "Jawa", "worldbuilding", "biomes", "warscar_bedazzle_cast_2026-09-30.md")
NS = "RimMandrake.Utinni.ScarlandsLadder."
SETTINGS_TYPE = NS + "ScarlandsLadderSettings"
DEFAULTS = {"campsEnabled": True, "campsPerMap": 1.0, "journalsAdvanceLadder": True}


def _bible_rows():
    """[(description, journal page)] for rungs 1-5 from section 6B's table."""
    txt = open(BIBLE, encoding="utf-8").read()
    sec = txt[txt.index("### 6B."):txt.index("## 7.")]
    rows = []
    for line in sec.splitlines():
        m = re.match(r"\| \*\*(\d) · [^|]*\*\* \| (.*?) \| \*\"(.*?)\"\* \|$", line.strip())
        if m:
            rows.append((m.group(2).strip(), m.group(3).strip()))
    return rows


def static_checks():
    bad = []
    rows = _bible_rows()
    if len(rows) != 5:
        return ["cast bible 6B parsed %d rungs, expected 5 (instrument check)" % len(rows)]
    ladder = ET.parse(os.path.join(HERE, "Defs", "LoreStageTableDefs", "RUT_ScarlandsLadder.xml")).getroot()
    desc = {}
    for tgt in ladder.iter("li"):
        if tgt.findtext("field") == "description":
            for st in tgt.find("stages"):
                desc[int(st.findtext("stage"))] = st.findtext("text")
    for i, (d, _) in enumerate(rows, 1):
        if desc.get(i) != d:
            bad.append("rung %d description differs from cast bible 6B" % i)
    j = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Items", "RUT_PilgrimJournal.xml")).getroot()
    pages = [li.text for p in j.iter("pages") for li in p]
    if pages != [p for _, p in rows]:
        bad.append("journal pages differ from cast bible 6B's journal column")
    src = open(os.path.join(HERE, "Source", "PilgrimCamps.cs"), encoding="utf-8").read()
    for f in DEFAULTS:
        if '"%s"' % f not in src:
            bad.append("setting %s is not Scribed" % f)
        if not re.search(r"\b%s\b" % f, src.split("DoWindowContents")[1]):
            bad.append("setting %s has no control" % f)
    if 'Compile Include="PilgrimCamps.cs"' not in open(os.path.join(HERE, "Source", "RimMandrake.Utinni.ScarlandsLadder.csproj")).read():
        bad.append("PilgrimCamps.cs missing from the csproj")
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("ScarlandsLadder")
    suite.toggles = ["campsEnabled", "journalsAdvanceLadder"]

    def _proof(t, method, n):
        r = t.bridge_call("jawa/static_call", type=NS + "RUT_PilgrimJournals", method=method, args="current|%d" % n)
        return str((r or {}).get("result", "")) or "no result: %r" % (r,)

    def _set(t, field, value):
        t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field, value=str(value))

    @suite.chain("pilgrim_journals")
    def pilgrim_journals(t):
        with t.component("reading_walks_the_ladder", toggle="journalsAdvanceLadder"):
            txt = _proof(t, "ProofReadSequence", 6)
            if t._guard():
                if not txt.startswith("STAGES 1,2,3,4,5,5 moved T,T,T,T,T,F"):
                    raise ExpectationFailed("six reads did not walk rungs 1-5 then stop: %s" % txt)
                if "Along the Ashfall Road" not in txt and "Crater fields" not in txt:
                    raise ExpectationFailed("RUT_Scarlands description not rewritten: %s" % txt)
        with t.component("reading_off_teaches_nothing", toggle="journalsAdvanceLadder"):
            _set(t, "journalsAdvanceLadder", False)
            try:
                txt = _proof(t, "ProofReadSequence", 1)
            finally:
                _set(t, "journalsAdvanceLadder", True)
            if t._guard() and not txt.startswith("STAGES 0 moved F"):
                raise ExpectationFailed("journalsAdvanceLadder OFF but a read moved the ladder: %s" % txt)

    @suite.chain("pilgrim_camps")
    def pilgrim_camps(t):
        with t.component("camps_place", toggle="campsEnabled"):
            txt = _proof(t, "ProofCamps", 2)
            if t._guard():
                m = re.match(r"CAMPS (\d+) \| journals (\d+) corpses (\d+) fires (\d+)", txt)
                if not m or int(m.group(1)) < 1 or min(int(x) for x in m.groups()[1:]) < int(m.group(1)):
                    raise ExpectationFailed("camps did not place fire + body + journal: %s" % txt)

    # NORTHSTAR_PARTIAL_GAPS_FILL_1: the camp GenStep's order, the ladder table's ladderId/maxStage (the two rungs)
    # and the journal's stack/tradeability read back equal to the XML.
    from modcheck import shipped_defs
    shipped_defs.add_chain(suite, __file__,
                           fields_by_type={"GenStepDef": ("order",),
                                           "RimMandrake.LoreStages.RM_LoreStageTableDef": ("ladderId", "maxStage"),
                                           "ThingDef": ("label", "stackLimit", "tradeability")},
                           sanity=("RUT_PilgrimCamps", "RUT_ScarlandsLadder", "RUT_PilgrimJournal"), min_count=3)
    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
