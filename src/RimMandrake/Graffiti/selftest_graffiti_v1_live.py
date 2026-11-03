"""Offline proof for GRAFFITI_V1_LIVE_PROOF_1: the live proof's verdicts read the probe's real reply shapes right, every
probe method the driver calls exists in RM_GraffitiProof.cs, the raid-exit hook sits on Lord.GotoToil (the caravan exit path
never sees a hostile raider), the defs promise what the clauses expect, and the committed Graffiti DLL matches its .srchash."""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import graffiti_v1_live_proof as P  # noqa: E402

FAILS = []


def check(cond, what):
    if not cond:
        FAILS.append(what)


def wrap(s):
    """jawa/static_call answers a dict; the proof json-dumps it, so test that shape too."""
    return json.dumps({"success": True, "result": s})


def code(*a, **k):
    return P.verdict(*a, **k)[0]


# A1 spree
A1 = "READ marks 3 | factionOk 3 | ideoOk 3 | defs RM_Graffiti_Vandal,RM_Graffiti_Tag_A | state RM_GraffitiPaintingSpreeState"
for t in (A1, wrap(A1)):
    check(code("A1", t) == 0, "A1 pass shape not passed: %s" % (P.verdict("A1", t),))
check(code("A1", A1.replace("ideoOk 3", "ideoOk 2")) == 1, "A1 a mark without its ideo passed")
check(code("A1", A1.replace("factionOk 3", "factionOk 0")) == 1, "A1 marks without faction passed")
check(code("A1", A1.replace("marks 3", "marks 0").replace("Ok 3", "Ok 0")) == 1, "A1 no mark passed")
check(code("A1", "REFUSED no spree started") == 2, "A1 REFUSED not UNMEASURED")
check(code("A1", "") == 2, "A1 empty not UNMEASURED")

# A2 raid
RAID = "RAID spawned 3 | faction Rough Pigs | marksIn 0 | toil LordToil_AssaultColony"
EXIT = "EXIT mid 0 | after 3 | eligible 3 | onWall 3 | standing 3 | toil LordToil_AssaultColony->LordToil_ExitMap"
check(code("A2", wrap(EXIT), extra=wrap(RAID)) == 0, "A2 pass shape not passed: %s" % (P.verdict("A2", EXIT, extra=RAID),))
check(code("A2", EXIT.replace("mid 0", "mid 1"), extra=RAID) == 1, "A2 a tag on the way in passed")
check(code("A2", EXIT, extra=RAID.replace("marksIn 0", "marksIn 2")) == 1, "A2 marks before arrival passed")
check(code("A2", EXIT.replace("after 3 | eligible 3 | onWall 3", "after 0 | eligible 0 | onWall 0"), extra=RAID) == 1,
      "A2 no exit tag passed")
check(code("A2", EXIT.replace("onWall 3", "onWall 2"), extra=RAID) == 1, "A2 an off-wall tag passed")
check(code("A2", EXIT.replace("standing 3", "standing 0").replace("after 3 | eligible 3 | onWall 3", "after 0 | eligible 0 | onWall 0"),
           extra=RAID) == 2, "A2 a raid with nobody standing scored as a mod result")
check(code("A2", EXIT, extra="") == 2, "A2 without its RAID line not UNMEASURED")

# A3 sigil
A3 = "SIGIL ideo True | frame halo_0 | iconIsIdeo True | tinted True | wallSide 0 | cell 120,121"
check(code("A3", wrap(A3)) == 0, "A3 pass shape not passed: %s" % (P.verdict("A3", A3),))
check(code("A3", A3.replace("frame halo_0", "frame none")) == 1, "A3 no frame passed")
check(code("A3", A3.replace("tinted True", "tinted False")) == 1, "A3 untinted passed")
check(code("A3", A3.replace("iconIsIdeo True", "iconIsIdeo False")) == 1, "A3 wrong icon passed")

# A4 going over
A4 = "OVER placed True | firstGone True | marksAtCell 1 | def RM_Graffiti_ThrowUp_A | rivalFaction True"
check(code("A4", wrap(A4)) == 0, "A4 pass shape not passed: %s" % (P.verdict("A4", A4),))
check(code("A4", A4.replace("marksAtCell 1", "marksAtCell 2")) == 1, "A4 two marks on one cell passed")
check(code("A4", A4.replace("def RM_Graffiti_ThrowUp_A", "def RM_Graffiti_Tag_A")) == 1, "A4 the first mark surviving passed")

# A5 thought
A5 = "THOUGHT makerHostile True | worker True | mood True | viewerOn True"
check(code("A5", wrap(A5)) == 0, "A5 pass shape not passed")
check(code("A5", A5.replace("mood True", "mood False")) == 1, "A5 no mood thought passed")
check(code("A5", A5.replace("worker True", "worker False")) == 1, "A5 worker inactive passed")

# A6 scrub
CLEAN = ("CLEAN unforcedOwn False | unforcedDevotional False | unforcedControl True | forcedOwn True | forcedDevotional True"
         " | ordered True")
DONE = "DONE ownGone True | devotionalGone True | job none"
check(code("A6", wrap(CLEAN), extra=wrap(DONE)) == 0, "A6 pass shape not passed: %s" % (P.verdict("A6", CLEAN, extra=DONE),))
check(code("A6", CLEAN.replace("unforcedOwn False", "unforcedOwn True"), extra=DONE) == 1, "A6 own mark auto-cleanable passed")
check(code("A6", CLEAN.replace("unforcedDevotional False", "unforcedDevotional True"), extra=DONE) == 1,
      "A6 devotional auto-cleanable passed")
check(code("A6", CLEAN.replace("unforcedControl True", "unforcedControl False"), extra=DONE) == 1,
      "A6 a control that nothing could clean passed (the protection would be blind)")
check(code("A6", CLEAN, extra=DONE.replace("devotionalGone True", "devotionalGone False")) == 1, "A6 forced clean left a mark passed")
check(code("A6", CLEAN, extra="") == 2, "A6 without DONE not UNMEASURED")

# A7 designator
A7 = "READ painted 3 | matched 3 | of 3 | pending 0 | got RM_Graffiti_CrossOut,RM_Graffiti_Glyph_Collectivist,RM_Graffiti_Paste_Flyer | job none"
check(code("A7", wrap(A7)) == 0, "A7 pass shape not passed")
check(code("A7", A7.replace("matched 3", "matched 2")) == 1, "A7 a pool pick in place of the chosen mark passed")
check(code("A7", A7.replace("painted 3", "painted 1").replace("pending 0", "pending 2")) == 1, "A7 unpainted passed")

# A8 log
LOADED = wrap("LOADED graffiti True | ideology True | thought True | raidHook True")
clean_log = "RimWorld 1.6.4630 rev123\nLoading mods\n[RimMandrake] Graffiti settings loaded\n"
check(P.log_verdict(clean_log, LOADED)[0] == 0, "A8 clean log not passed: %s" % (P.log_verdict(clean_log, LOADED),))
bad = clean_log + "Config error in RM_Graffiti_Tag_A: graphicData is null\n"
check(P.log_verdict(bad, LOADED)[0] == 1, "A8 a Graffiti config error passed")
xref = clean_log + "Could not resolve cross-reference to Verse.ThoughtDef named RM_Graffiti_ViewedHostileMark\n"
check(P.log_verdict(xref, LOADED)[0] == 1, "A8 a cross-reference error passed")
fileonly = clean_log + "Exception loading def from file ThingDefs_Graffiti.xml: System.FormatException\n"
check(P.log_verdict(fileonly, LOADED)[0] == 1, "A8 an error naming only a Graffiti XML file passed")
multi = clean_log + "Exception in Verse.DefDatabase: NullReferenceException\n  at RimMandrake.Graffiti.Filth_Mark.Print ()\n"
check(P.log_verdict(multi, LOADED)[0] == 1, "A8 an exception whose Graffiti frame is on the next line passed")
adjacent = "RimWorld 1.6\nConfig error in SomeoneElse_Thing: bad\n[RimMandrake] Graffiti settings loaded\n"
check(P.log_verdict(adjacent, LOADED)[0] == 0, "A8 another mod's error blamed on the Graffiti record after it")
other = clean_log + "Config error in SomeoneElse_Thing: bad\nLoading textures\nLoading sounds\nLoading language\n"
check(P.log_verdict(other, LOADED)[0] == 0, "A8 another mod's error blamed on Graffiti")
check(P.log_verdict(clean_log, wrap("REFUSED no current map"))[0] == 2, "A8 without Graffiti loaded not UNMEASURED")
check(P.log_verdict(clean_log, LOADED.replace("ideology True", "ideology False"))[0] == 2, "A8 a DLC-less load not UNMEASURED")
check(P.log_verdict(clean_log, LOADED.replace("raidHook True", "raidHook False"))[0] == 1, "A8 a missing raid hook passed")
check(P.log_verdict("", LOADED)[0] == 2, "A8 empty log passed")

quoted = RAID.replace("Rough Pigs", 'The "Red" Pigs \\ back')
check(P.field(quoted, "marksIn") == "0" and code("A2", EXIT, extra=wrap(quoted)) == 0, "A2 a quoted faction name broke the RAID read")
check(P.field(wrap(A4), "rivalFaction") == "True", "the last field of a wrapped reply kept the JSON tail")
typed = clean_log + "Could not find a type named RimMandrake.Graffiti.Missing\n"
check(P.log_verdict(typed, LOADED)[0] == 1, "A8 'Could not find a type named' passed")

check(P.log_verdict(clean_log, LOADED.replace("graffiti True", "graffiti False"))[0] == 2, "A8 with Graffiti not loaded passed")
deep = clean_log + "Exception in Verse.DefDatabase: NullReferenceException\n" + "  at Some.Frame ()\n" * 60 + "  at RimMandrake.Graffiti.X ()\n"
check(P.log_verdict(deep, LOADED)[0] == 1, "A8 a Graffiti frame deep in a long stack trace passed")

unity = clean_log + "Exception ticking: NullReferenceException\nVerse.TickManager:DoSingleTick ()\nRimMandrake.Graffiti.RaidExitTaggerMod:Postfix (Verse.AI.Group.Lord,Verse.AI.Group.LordToil,bool)\n"
check(P.log_verdict(unity, LOADED)[0] == 1, "A8 an exception owned by an unindented Unity frame passed")

# the bridge reply is unwrapped, so a non-ASCII faction name never ends a field early
uni = P._reply({"success": True, "result": RAID.replace("Rough Pigs", "P\u00edgs \u00c6therfolk")})
check(P.field(uni, "marksIn") == "0" and code("A2", EXIT, extra=uni) == 0, "A2 a non-ASCII faction name broke the RAID read: %r" % uni)
check(P._reply("x") == "x" and "\\u" not in P._reply({"other": "\u00ed"}), "_reply escaped non-ASCII text")

# every probe method the driver calls exists, public static string X(string)
src = open(os.path.join(HERE, "Source", "RM_GraffitiProof.cs"), encoding="utf-8").read()
driver = open(os.path.join(HERE, "graffiti_v1_live_proof.py"), encoding="utf-8").read()
called = set(re.findall(r'call\("(\w+)"', driver))
called |= set(re.findall(r'_until\(rb, call, "(\w+)"', driver)) | {"Sigil", "GoingOver", "HostileThought"}
check({"SpreeRead", "CleanDone", "DesignateRead"} <= called, "the method scan is blind to the _until reads: %s" % sorted(called))
for m in sorted(called):
    check(re.search(r"public static string %s\(string args\)" % m, src), "probe method %s missing from RM_GraffitiProof.cs" % m)
check(P.PROBE == "RimMandrake.Graffiti.RM_GraffitiProof" and "namespace RimMandrake.Graffiti" in src
      and "public static class RM_GraffitiProof" in src, "PROBE type name does not match the C# class")
csproj = open(os.path.join(HERE, "Source", "Graffiti.csproj"), encoding="utf-8").read()
check('Compile Include="RM_GraffitiProof.cs"' in csproj, "RM_GraffitiProof.cs is not compiled")

# the raid-exit hook sits where a hostile raid actually goes
tagger = open(os.path.join(HERE, "Source", "RaidExitTagger.cs"), encoding="utf-8").read()
check("nameof(Lord.GotoToil)" in tagger, "RaidExitTagger does not patch Lord.GotoToil")
check(not re.search(r"AccessTools\.Method\(typeof\(CaravanExitMapUtility\)", tagger),
      "RaidExitTagger patches the caravan exit path again (a hostile raider never reaches it)")

# the defs promise what the clauses expect
defs, thoughts = {}, {}
for fn in os.listdir(os.path.join(HERE, "Defs")):
    root = ET.parse(os.path.join(HERE, "Defs", fn)).getroot()
    for d in root.findall("ThingDef"):
        ext = d.find("modExtensions/li[@Class='RimMandrake.Graffiti.ModExtension_Graffiti']")
        if d.findtext("defName") and ext is not None:
            defs[d.findtext("defName")] = ext
    for d in root.findall("ThoughtDef"):
        thoughts[d.findtext("defName")] = d.findtext("workerClass")
check(thoughts.get("RM_Graffiti_ViewedHostileMark") == "RimMandrake.Graffiti.ThoughtWorker_ViewedGraffitiMark",
      "RM_Graffiti_ViewedHostileMark missing or on the wrong worker: %r" % thoughts.get("RM_Graffiti_ViewedHostileMark"))
raid = [n for n, e in defs.items() if e.findtext("raidExitEligible") == "true"]
check(len(raid) > 0, "no raidExitEligible mark at all (the def reader is blind)")
for n in raid:
    check(defs[n].findtext("onViewHostileMaker") == "RM_Graffiti_ViewedHostileMark", "%s leaves no hostile-maker reaction" % n)
for n in ("RM_Graffiti_Tag_A", "RM_Graffiti_ThrowUp_A"):
    check(n in raid, "%s is not a raid-exit mark (A4/A5 use it)" % n)
sig = defs.get("RM_Graffiti_IdeoSigil")
check(sig is not None and sig.findtext("sigilTierA") == "true" and sig.findtext("category") == "Devotional",
      "RM_Graffiti_IdeoSigil is not a tier-A Devotional sigil")
frame = sig.findtext("sigilFrameTexPath") if sig is not None else ""
check(frame and frame.endswith("/halo_0") and os.path.isfile(os.path.join(HERE, "Textures", frame + ".png")),
      "the sigil's halo frame %r has no texture" % frame)
free = [n for n, e in defs.items() if e.findtext("designatorEligible") == "true" and not e.findtext("minArtistic")
        and e.find("requiresAnyMeme") is None and not e.findtext("requiresHostileToFactionDef")]
check(len(free) >= 3, "fewer than 3 ungated designator marks for A7: %s" % free)

# the committed DLL is the one its sources stamp
r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/dll_source_stamp.py"), "check"],
                   cwd=REPO, capture_output=True, text=True, timeout=300)
check("MATCH src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll" in r.stdout.splitlines(),
      "Graffiti DLL is not MATCH in dll_source_stamp: " + (r.stdout + r.stderr)[-400:])

if FAILS:
    print("FAIL selftest_graffiti_v1_live:\n  " + "\n  ".join(FAILS))
    sys.exit(1)
print("PASS selftest_graffiti_v1_live")
