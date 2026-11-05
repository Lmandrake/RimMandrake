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
EXIT = ("EXIT mid 0 | after 3 | eligible 3 | onWall 3 | exterior 3 | outsideOpen True | interiorClosed True | inside 1 | standing 4"
        " | toil LordToil_AssaultColony->LordToil_ExitMap | factionOk 3 | sinceMarks 3")
check(code("A2", wrap(EXIT), extra=wrap(RAID)) == 0, "A2 pass shape not passed: %s" % (P.verdict("A2", EXIT, extra=RAID),))
check(code("A2", EXIT.replace("mid 0", "mid 1"), extra=RAID) == 1, "A2 a tag on the way in passed")
check(code("A2", EXIT, extra=RAID.replace("marksIn 0", "marksIn 2")) == 1, "A2 marks before arrival passed")
check(code("A2", EXIT.replace("after 3 | eligible 3 | onWall 3 | exterior 3", "after 0 | eligible 0 | onWall 0 | exterior 0"), extra=RAID) == 1,
      "A2 no exit tag passed")
check(code("A2", EXIT.replace("onWall 3", "onWall 2"), extra=RAID) == 1, "A2 an off-wall tag passed")
check(code("A2", EXIT.replace("exterior 3", "exterior 2"), extra=RAID) == 1, "A2 an interior-wall tag passed")
check(code("A2", EXIT.replace(" | exterior 3", ""), extra=RAID) == 1, "A2 a reply without the exterior count passed")
check(code("A2", EXIT.replace("interiorClosed True", "interiorClosed False"), extra=RAID) == 2,
      "A2 an open (untestable) interior scored as a mod result")
check(code("A2", EXIT.replace("inside 1", "inside 0"), extra=RAID) == 2, "A2 no raider inside scored as a mod result")
check(code("A2", EXIT.replace("outsideOpen True", "outsideOpen False"), extra=RAID) == 2, "A2 an enclosed outside scored as a mod result")
check(code("A2", EXIT.replace("standing 4", "standing 0").replace("after 3 | eligible 3 | onWall 3", "after 0 | eligible 0 | onWall 0"),
           extra=RAID) == 2, "A2 a raid with nobody standing scored as a mod result")
check(code("A2", EXIT, extra="") == 2, "A2 without its RAID line not UNMEASURED")
# "in its faction's mark": the blind checker's mutant (makerFaction null / OfPlayer after MakeMark) reads factionOk 0
check(code("A2", EXIT.replace("factionOk 3", "factionOk 0"), extra=RAID) == 1, "A2 exit tags in no faction's mark passed")
check(code("A2", EXIT.replace("factionOk 3", "factionOk 2"), extra=RAID) == 1, "A2 one exit tag in the wrong faction's mark passed")
check(code("A2", EXIT.replace(" | factionOk 3 | sinceMarks 3", ""), extra=RAID) == 2, "A2 an unread maker faction not UNMEASURED")
check(code("A2", EXIT.replace(" | factionOk 3 | sinceMarks 3", " | factionUnread no fresh save"), extra=RAID) == 2,
      "A2 an unreadable save not UNMEASURED")


def save(marks, factions=(("Rough Pigs", "7"), ("Colony", None), ("Other Pigs", "9"))):
    """A minimal .rws: factions (name, loadID or None = the Scribe default 0) and marks (placedTick, makerFaction ref)."""
    fl = "".join("<li><def>Pirate</def><name>%s</name>%s</li>" % (n, "" if i is None else "<loadID>%s</loadID>" % i)
                 for n, i in factions)
    ml = "".join('<thing Class="RimMandrake.Graffiti.Filth_Mark"><def>RM_Graffiti_Tag_A</def>%s<rmMarkMakerFaction>%s'
                 '</rmMarkMakerFaction></thing>' % ("" if t is None else "<rmMarkPlacedTick>%d</rmMarkPlacedTick>" % t, f)
                 for t, f in marks)
    return ("<savegame><game><world><factionManager><allFactions>%s</allFactions></factionManager></world>"
            "<maps><li><things>%s<thing><def>Steel</def></thing></things></li></maps></game></savegame>" % (fl, ml))


good = save([(1000, "Faction_7"), (1050, "Faction_7"), (1100, "Faction_7"), (500, "Faction_9"), (1200, "Faction_0")])
check(P.exit_faction_marks(good, "Rough Pigs", 1000) == (3, 4, None), "save read: %r" % (P.exit_faction_marks(good, "Rough Pigs", 1000),))
check(P.exit_faction_marks(good, "Colony", 1000)[:2] == (1, 4), "save read: a loadID-0 faction (Scribe default, omitted) not matched")
check(P.exit_faction_marks(save([(1000, "null")] * 3), "Rough Pigs", 1000)[:2] == (0, 3), "save read: null makerFaction counted")
check(P.exit_faction_marks(save([(1000, "Faction_0")] * 3), "Rough Pigs", 1000)[:2] == (0, 3), "save read: player makerFaction counted")
check(P.exit_faction_marks(save([(999, "Faction_7")]), "Rough Pigs", 1000)[:2] == (0, 0), "save read: a mark older than the raid counted")
check(P.exit_faction_marks(save([(None, "Faction_7")]), "Rough Pigs", 1000)[:2] == (0, 0), "save read: a mark without placedTick counted")
check(P.exit_faction_marks(save([], factions=(("Rough Pigs", "7"), ("Rough Pigs", "8"))), "Rough Pigs", 0)[0] is None,
      "save read: an ambiguous faction name was guessed")
check(P.exit_faction_marks(good, "Nobody", 0)[0] is None, "save read: an absent faction not refused")
check(P.exit_faction_marks("<savegame><game>", "Rough Pigs", 0)[0] is None, "save read: a truncated save not refused")
check(P.exit_faction_marks("<savegame/>", "Rough Pigs", 0)[0] is None, "save read: a save without factions not refused")


# run("A2") end to end on a fake bridge: the EXIT line gains factionOk from the save it writes, so a raid-path makerFaction
# mutant (the save's marks in no faction / the player's) goes red, and a missing save is UNMEASURED
import shutil  # noqa: E402
import tempfile  # noqa: E402


class FakeBridge:
    def __init__(self, saves, save_text):
        self.saves, self.save_text, self.calls = saves, save_text, []

    def call(self, tool, params=None):
        self.calls.append(tool)
        if tool == "jawa/static_call":
            m = params["method"]
            return {"success": True, "result": RAID if m == "RaidStart" else EXIT.split(" | factionOk")[0], "ticksGame": 1000}
        if tool == "rimworld/save_game" and self.save_text is not None:
            with open(os.path.join(self.saves, params["saveName"] + ".rws"), "w", encoding="utf-8") as fh:
                fh.write(self.save_text + " " * 1200)
        return {"success": True}


class FakeR:
    def __init__(self, d):
        self.d = d

    def _player_log_candidates(self):
        yield os.path.join(self.d, "Player.log")


tmp = tempfile.mkdtemp(prefix="graffiti_a2_")
try:
    os.makedirs(os.path.join(tmp, "Saves"))
    _sleep, P.time.sleep = P.time.sleep, (lambda s: None)
    for text, want, what in ((good, 0, "a raid whose exit tags carry its faction"),
                             (save([(1000, "null")] * 3), 1, "the makerFaction=null mutant"),
                             (save([(1000, "Faction_0")] * 3), 1, "the makerFaction=OfPlayer mutant"),
                             (None, 2, "no save written")):
        fb = FakeBridge(os.path.join(tmp, "Saves"), text)
        got = P.run("A2", fb, FakeR(tmp))
        check(got[0] == want, "run A2 on %s: %r (want %d)" % (what, got, want))
        check("rimworld/save_game" in fb.calls, "run A2 never saved the game to read the tags' faction")
        check(not os.path.exists(os.path.join(tmp, "Saves", P.SAVE_NAME + ".rws")), "run A2 left its proof save behind")
    P.time.sleep = _sleep
finally:
    shutil.rmtree(tmp, ignore_errors=True)

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
# deliberately conservative: another mod's error right before a Graffiti line FAILS (a look at the named line settles it)
check(P.log_verdict(adjacent, LOADED)[0] == 1, "A8 the error window no longer reaches the next lines")
fullnode = ('RimWorld 1.6.4633\nXML error: Could not find parent node named "FilthBsae" for node "ThingDef".\n'
            'Full node: <ThingDef ParentName="FilthBsae"><defName>RM_Graffiti_Tag_A</defName></ThingDef>\n')
check(P.log_verdict(fullnode, LOADED)[0] == 1, "A8 an XML error whose Graffiti def is on its Full node line passed")
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

fmt = clean_log + "XML format error: duplicate list item in RM_Graffiti_Tag_A\n"
check(P.log_verdict(fmt, LOADED)[0] == 1, "A8 an XML format error passed")
harm = (clean_log + "Exception ticking: NullReferenceException\n(wrapper dynamic-method) MonoMod.Utils.DynamicMethodDefinition:"
        "Verse.Log.Error_Patch1 (string)\nRimMandrake.Graffiti.Filth_Mark:Print (Verse.SectionLayer)\n")
check(P.log_verdict(harm, LOADED)[0] == 1, "A8 a Harmony wrapper frame split the record and passed")

notdef = clean_log + "Type ThingDeff is not a Def type or could not be found, in file ThingDefs_Graffiti.xml.\n"
check(P.log_verdict(notdef, LOADED)[0] == 1, "A8 a rejected Graffiti def root passed")

ref = clean_log + "Could not execute post-long-event action. Exception: System.NullReferenceException\n[Ref 12345678]\n  at RimMandrake.Graffiti.Startup.Initialize ()\n"
check(P.log_verdict(ref, LOADED)[0] == 1, "A8 a [Ref] marker split the record and passed")
orphan = clean_log + "Something odd\nRimMandrake.Graffiti.Filth_Mark:Print (Verse.SectionLayer)\n"
check(P.log_verdict(orphan, LOADED)[0] == 1, "A8 a bare Graffiti stack frame passed")

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

# every clause's static_call carries as many '|'-separated args as its probe method takes, by the bridge's OWN rule
# (JawaBenchCompanionProbeTools.cs StaticCall: "" is ZERO args, else args.Split('|'), matched on GetParameters().Length);
# the args="" mutant of run() made every live line A1-A8 exit 2 ("No public static SpreeStart with 0 params")
bridge_src = open(os.path.join(REPO, "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionProbeTools.cs"),
                  encoding="utf-8").read()
check("string.IsNullOrEmpty(args) ? new string[0] : args.Split('|')" in bridge_src
      and "m.GetParameters().Length == raw.Length" in bridge_src,
      "jawa/static_call's arity rule changed: re-derive the emulation below from JawaBenchCompanionProbeTools.cs")
arity = {m: (0 if not ps.strip() else ps.count(",") + 1)
         for m, ps in re.findall(r"public static string (\w+)\(([^)]*)\)", src)}
check(len(arity) >= 13 and arity.get("SpreeStart") == 1, "probe signature scan is blind: %r" % arity)


class ArityBridge:
    """Answers jawa/static_call exactly as the real bridge would on arity; any other tool succeeds."""

    def __init__(self):
        self.static, self.refused = [], []

    def call(self, tool, params=None):
        if tool != "jawa/static_call":
            return {"success": True}
        m, a = params["method"], params.get("args", "")
        raw = [] if not a else a.split("|")
        self.static.append(m)
        if params.get("type") != P.PROBE or arity.get(m) != len(raw):
            self.refused.append((m, a))
            return {"success": False, "message": "No public static %s with %d params." % (m, len(raw))}
        return {"success": True, "result": "REFUSED offline arity bridge (no game)", "ticksGame": 1}


_sleep2, P.time.sleep = P.time.sleep, (lambda s: None)
try:
    for clause in P.CLAUSES:
        ab = ArityBridge()
        try:
            P.run(clause, ab, FakeR(tmp))
        except Exception as ex:  # a probe reply this bridge cannot shape may end the run; the calls made still count
            check(ab.static, "run %s raised before any static_call: %r" % (clause, ex))
        check(ab.static, "run %s made no jawa/static_call (the arity scan is blind to it)" % clause)
        check(not ab.refused, "run %s: the bridge would refuse %r (arg count != probe parameter count)" % (clause, ab.refused))
finally:
    P.time.sleep = _sleep2

# the committed DLL is the one its sources stamp
r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/dll_source_stamp.py"), "check"],
                   cwd=REPO, capture_output=True, text=True, timeout=300)
check("MATCH src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll" in r.stdout.splitlines(),
      "Graffiti DLL is not MATCH in dll_source_stamp: " + (r.stdout + r.stderr)[-400:])

if FAILS:
    print("FAIL selftest_graffiti_v1_live:\n  " + "\n  ".join(FAILS))
    sys.exit(1)
print("PASS selftest_graffiti_v1_live")
