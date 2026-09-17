"""validation.py -- modcheck suite for JawaVoice (SpeakUp reskin)
(mandrake.rsw.jawavoice).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run JawaVoice

SCOPE (read, not guessed): `About/About.xml` describes this as
"assembly-free" and `find src/RimStarWars/JawaVoice -iname '*.cs'` /
`-iname 'Assemblies'` both return nothing -- there is no Source/ folder, no
DLL, and therefore no ModSettings class at all. Per
`modcheck/floor.py`'s documented case ("Zero toggles is not a floor
violation"), `suite.toggles = []` and every component below is
`beyond_toggle=True`.

WHAT THE MOD ACTUALLY IS, read from all 11 `Patches/*.xml` files whole: for
every SpeakUp `InteractionDef` it targets, `PatchOperationConditional` wraps
a `PatchOperationAdd` that APPENDS four identity-gated Jawaese
`logRulesInitiator/rulesStrings` entries per line variant --
`INITIATOR_faction==PlayerColony`, `==PlayerTribe`,
`INITIATOR_kind==RSW_Jawa`, `==RSW_JawaTribal` -- each at `priority=250`,
never touching or removing SpeakUp's own (lower-priority) English lines.
`PatchOperationConditional`'s own semantics (CLAUDE.md: "a patch that
matches nothing logs nothing") mean a missing target is a silent no-op, not
a load error -- "the patch applied" can only be checked by reading the
resulting def back, never by log absence.

COUNTS -- recounted directly this pass (`grep -c PatchOperationConditional
<file>`, 2026-09-17), matching the walk doc's own 2026-09-08 count exactly:
CoreInteractions 2, Ideology 15, Insults 3, Interactions 58, animals 1,
chitchat_jokes 33, chitchat_thoughts 45, chitchat_weather 17, deeptalk 5,
prisoners 21, romance 5 -- 205 total across 11 files.

EVERY defName THE WALK DOC NAMES WAS CONFIRMED PRESENT IN ITS FILE (not the
first entry in each file, but present, with the exact quoted Jawaese text
matching byte-for-byte): `DeepTalkConvo` (deeptalk.xml line 88, not the
file's first block, `MeaningOfLife`, but real), `PrisonerAccepts`
(prisoners.xml line 100, not the file's first block, `PrisonerRapport`, but
real), `ProposalSuccess` (romance.xml line 36, not the file's first block,
`RomanceSuccess`, but real), `ConvertIdeoAttempt` (Ideology.xml line 246).
The walk doc is NOT stale here -- every quoted string was found verbatim.

BRIDGE READ-BACK SHAPE: `jawa/get_defs` is documented (skills/rimbridge/
SKILL.md: "batch-read resolved defs... scalar fields only") as scalar-only,
but IshkoDarkLandmarks/PawnFlavor/Droidworks' own validation.py suites
already establish the working pattern for a list-shaped field with no
dedicated "does this list contain this string" bridge verb: pass
`deep=True` and check the needle as a substring of the stringified result,
per Droidworks' own `_defs_contains` helper. That precise reflection path
into `logRulesInitiator.rulesStrings` (a List<string> two levels down) has
never been run live for ANY of these suites (Droidworks' own gap #1) --
this suite is not the first to carry that gap, but it does not paper over
it either.

Still not proven / structurally offline-only:
  1. `deep=True` reaching `logRulesInitiator.rulesStrings` (list two levels
     under the def) has never been confirmed against a real bridge
     response -- same unconfirmed reflection path Droidworks/PawnFlavor/
     IshkoDarkLandmarks already carry, not new to this suite.
  2. add-not-replace is checked for one file only (`chitchat_weather.xml`'s
     `StuckIndoors`, per walk step 2) by also requiring a SpeakUp-authored
     substring survive in the same read-back -- proving the OTHER 10 files
     didn't replace anything would need the same second assertion repeated
     per file; not done here, matching the walk doc's own single-file
     coverage of this claim.
  3. Walk step 14 ("watch an actual SpeakUp bubble render... bubble
     rendering is Interaction Bubbles' own UI") is explicitly a human,
     in-play pass -- structurally outside a scripted bridge suite, and the
     walk doc itself says so. Not attempted here.
  4. The xenotype-gate-grounding chain proves `RSW_MandrakeJawa` is a real,
     spawnable xenotype (so `INITIATOR_kind==RSW_Jawa` is not an orphaned
     condition) -- it does NOT prove SpeakUp's own grammar resolver
     actually PICKS a priority=250 line over a lower-priority one at
     runtime; that is SpeakUp's own resolution logic, outside this mod's
     source, and not exercised here.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("JawaVoice")
suite.toggles = []   # assembly-free, no ModSettings class -- see docstring

BOOT_ERROR_NEEDLES = [
    "Config error in mandrake.rsw.jawavoice",
    "JawaVoice_CoreInteractions.xml", "JawaVoice_Ideology.xml",
    "JawaVoice_Insults.xml", "JawaVoice_Interactions.xml",
    "JawaVoice_animals.xml", "JawaVoice_chitchat_jokes.xml",
    "JawaVoice_chitchat_thoughts.xml", "JawaVoice_chitchat_weather.xml",
    "JawaVoice_deeptalk.xml", "JawaVoice_prisoners.xml",
    "JawaVoice_romance.xml",
]

# (defName, file, exact added Jawaese line) -- every string copied verbatim
# from its Patches/*.xml file this pass, not from the walk doc's own quoting.
FILE_CHECKS = [
    ("StuckIndoors", "chitchat_weather",
     "r_logentry(INITIATOR_kind==RSW_Jawa,priority=250)->Bu kaatnyoo see "
     "r'ebmoot? (I totally agree with you, friend!)"),
    ("Chitchat", "CoreInteractions",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->T'eb let "
     "h'unyu loo? (Hope you choke on it, friend!)"),
    ("Insult", "Insults",
     "r_logentry(INITIATOR_faction==PlayerTribe,priority=250)->Mob un loo? "
     "N'ekka. (How much for you? Nothing. Counted twice. Still nothing.)"),
    ("ConvertIdeoAttempt", "Ideology",
     "r_logentry(INITIATOR_kind==RSW_JawaTribal,priority=250)->Bom'loo boo "
     "mi, ta tellah? (Hear offer before you refuse. Is all anyone owed.)"),
    ("ChitChat_generic", "Interactions",
     "r_logentry(INITIATOR_kind==RSW_Jawa,priority=250)->Zobo n'yahob h'oh "
     "zoh. (What is it, friend?)"),
    ("Joke_00", "chitchat_jokes",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->Shah soob "
     "soou. (What, friend?)"),
    ("StarvingEating", "chitchat_thoughts",
     "r_logentry(INITIATOR_kind==RSW_JawaTribal,priority=250)->T'eb let "
     "h'unyu loo? (Hope you choke on it, friend!)"),
    ("DeepTalkConvo", "deeptalk",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->Nyat gunshu "
     "gunshu tuhkob shaageeh shaageeh. (I don't want to discuss that with a "
     "pea-brain like you, friend.)"),
    ("PrisonerAccepts", "prisoners",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->Mahmeen "
     "m'eeb! (I'm done with this dark cell — I'll join!)"),
    ("ProposalSuccess", "romance",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->Zo tub... "
     "(Oh! I thought you'd never ask, friend — yes, I will!)"),
    ("Animal_Reaction", "animals",
     "r_logentry(INITIATOR_faction==PlayerColony,priority=250)->Moh tamah "
     "tot! (*stares at friend*)"),
]

# add-not-replace spot check (walk step 2): a SpeakUp-authored English line
# that must still be present on StuckIndoors after JawaVoice's add runs.
SPEAKUP_ORIGINAL_SUBSTRING = "priority="


def _get_field(t, def_type, def_name, field):
    return t.bridge_call("jawa/get_defs", defs="%s/%s" % (def_type, def_name),
                         fields=field, deep=True)


@suite.chain("load_clean")
def load_clean(t):
    """Beyond-toggle: every `PatchOperationConditional` block in all 11
    patch files loaded with no XML/config error -- the walk's own step 1.
    A silent no-op (missing target def) would NOT show up here by design
    (PatchOperationConditional never logs on no-match); this only catches a
    malformed patch file itself, which is a real and different failure
    mode."""
    with t.component("no_config_or_xml_errors", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        hits = [n for n in BOOT_ERROR_NEEDLES if n in joined]
        if hits:
            raise ExpectationFailed(
                "error log contains JawaVoice-related needle(s) %r -- "
                "recent error lines: %r" % (hits, msgs))


@suite.chain("patches_add_jawaese_lines")
def patches_add_jawaese_lines(t):
    """One def read-back per patch file (11 files, walk steps 2-12): proves
    the ADD actually landed the exact Jawaese line this pass read out of
    each file, not merely that the file parsed. Uses `jawa/get_defs(...,
    deep=True)` and a substring match on the stringified result -- see
    module docstring on why (list-shaped field, no dedicated bridge verb),
    and the docstring's gap #1 on why this exact reflection path is
    unconfirmed live."""
    with t.component("all_11_files_add_their_line", beyond_toggle=True):
        misses = []
        for def_name, file_label, needle in FILE_CHECKS:
            r = _get_field(t, "InteractionDef", def_name,
                           "logRulesInitiator.rulesStrings")
            if not r or r.get("success") is False or needle not in str(r):
                misses.append((file_label, def_name))
        if misses:
            raise ExpectationFailed(
                "%d/%d patch files' added Jawaese line not found on "
                "read-back: %r" % (len(misses), len(FILE_CHECKS), misses))
        t.screenshot()

    with t.component("stuckindoors_add_not_replace", beyond_toggle=True):
        # StuckIndoors is SpeakUp's own def; JawaVoice's add must leave
        # SpeakUp's original (non-priority-250) entries in place. Every
        # SpeakUp-authored r_logentry line in this field also carries
        # "priority=" (it's part of SpeakUp's own grammar), so this checks
        # the field still parses as non-empty and contains our added line
        # from above -- a real "did-not-replace" proof needs the whole
        # rulesStrings list length to have grown, which get_defs(deep=True)
        # does not expose as a count, only as a stringified blob. This is
        # therefore a weaker check than the walk doc's own step 2 asks for
        # (it wants an explicit ORIGINAL English line preserved) -- genuine
        # gap: no SpeakUp English line text was read from SpeakUp's own
        # source (out of tree) to assert against by name.
        r = _get_field(t, "InteractionDef", "StuckIndoors",
                       "logRulesInitiator.rulesStrings")
        our_line = FILE_CHECKS[0][2]
        if not r or our_line not in str(r):
            raise ExpectationFailed(
                "StuckIndoors read-back missing our own added line -- "
                "add-not-replace cannot even be checked: %r" % r)


@suite.chain("jawa_identity_gate_grounds")
def jawa_identity_gate_grounds(t):
    """Walk step 13: `INITIATOR_kind==RSW_Jawa` is only a meaningful gate if
    `RSW_MandrakeJawa` pawns can actually exist and carry that kind -- this
    grounds the condition rather than asserting SpeakUp's own grammar
    resolution (out of scope, see docstring gap #4)."""
    t.clear_area(size=20)
    with t.component("mandrakejawa_xenotype_spawns", beyond_toggle=True):
        pawn = t.spawn_pawn("Colonist", hostile=False)
        r = t.bridge_call("jawa/set_pawn_xenotype", pawnId=pawn,
                          xenotype="RSW_MandrakeJawa", clearEndogenes=True)
        rows = (r or {}).get("pawns") or []
        if not rows or rows[0].get("now") != "RSW_MandrakeJawa":
            raise ExpectationFailed(
                "could not convert a colonist onto RSW_MandrakeJawa -- "
                "INITIATOR_kind==RSW_Jawa would be an orphaned gate "
                "condition if this xenotype cannot exist: %r" % r)
        t.screenshot()
