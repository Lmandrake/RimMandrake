# -*- coding: utf-8 -*-
"""Emit JawaVoice_Ideology.xml from wk/ideo2.py, fanned out to four conditions."""
import io, os, sys

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines_ideology as ideo2

CONDS = ["INITIATOR_faction==PlayerColony",
         "INITIATOR_faction==PlayerTribe",
         # 🔴 CORRECTED 2026-08-21. These read `OuterRim_Jawa` / `OuterRim_JawaTribal`,
         # which are ABSENT from the live capture - measured against defs.sqlite
         # (OFFICIAL, 578 mods): both return zero rows, while `RSW_Jawa` and
         # `RSW_JawaTribal` exist as PawnKindDefs in "RimMandrake - Star Wars
         # Races". The committed output had already been moved to the live names and
         # the sibling `genxml.py` had been updated; this file was the half of the
         # rename nobody finished.
         # ⛔ Re-running it as it stood would have reverted 94 gate strings to a
         # pawnkind that does not exist. A grammar condition naming a dead kind never
         # matches, logs nothing, and the success line still reads
         # "14 defs, 47 lines -> 188 rules". The COUNT was never the thing that moved.
         "INITIATOR_kind==RSW_Jawa",
         "INITIATOR_kind==RSW_JawaTribal"]

GROUPS = [
    ("PRISONERS: acquisition, and the slow work on the will",
     ["EnslaveAttempt", "ReduceWill"]),
    ("SLAVES: inventory control, and the whisper back",
     ["Suppress", "SparkSlaveRebellion"]),
    ("CONVERSION: a sales pitch, closed or lost",
     ["ConvertIdeoAttempt", "Convert_Success", "Convert_Failure"]),
    ("COUNSEL, REASSURANCE, PREACHING: the warm end of the same instinct",
     ["Counsel_Success", "Counsel_Failure", "Reassure", "PreachHealth"]),
    ("WORK AND TRIAL: the crew driven, and a valuation dispute with an audience",
     ["WorkDrive", "Trial_Accuse", "Trial_Defend"]),
]

HEADER = u'''<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  JawaVoice_Ideology.xml           JawaVoice \u00b7 authored 2026-08-11 \u00b7 v2 08-12
  ============================================================================

  GENERATED FILE. Do not hand edit the rules below; each authored line is
  emitted four times and the copies must agree exactly. See REGENERATING.

  THE GAP THIS FILLS
  ==================
  JawaVoice covers 189 InteractionDefs and not one of them came from Ideology.
  Every slave suppression, prisoner will-break, conversion attempt and trial
  speech was narrated in English. Those are not rare: Suppress and ReduceWill
  fire on a timer for as long as you hold anybody, so in a colony that keeps
  prisoners they are among the most frequent lines in the game.

  SCOPE: 14 defs, the ones a pawn actually SAYS to another pawn.
  The twelve Speech_* ritual defs in Interactions_Speech.xml are deliberately
  excluded: they are long third-person ceremony narration rather than dialogue,
  and a short Jawaese quip reads wrong in them.

  \u26a0\ufe0f ReduceWill EXISTS TWICE. It is an InteractionDef here and also a
  PrisonerInteractionModeDef in Ideology/Defs/PrisonerInteractionModeDefs. The
  xpaths below name InteractionDef explicitly, which is what disambiguates
  them. A /Defs/*[defName="ReduceWill"] xpath would hit both and corrupt the
  mode def.

  ============================================================================
  V2 REWRITE, 2026-08-12
  ============================================================================
  v1 scored worst of any JawaVoice file against the 639 line corpus: composite
  distance 0.272, with reduplication at 19.1% against the corpus 38.8%, and
  "nyeta" appearing in 38% of lines. v2 rebuilds every line on the shared
  lexicon documented in JawaVoice_Insults.xml and brings that to 0.171.

  Reduplication is treated as real morphology, an INTENSIFIER, exactly as in the
  insults file: nootiba nootibu = counted, and counted again. Three of the Grade
  A canon phrases work this way already (Togo togu, Taa baa, M\'um m\'aloo).

  \u26a0\ufe0f WHY THIS FILE SCORES WORSE THAN THE INSULTS AND SHOULD. Its remaining
  gap is breathy h (17.5% against 32.6%) and apostrophes (10.8% against 22.4%).
  The cause is principled rather than careless: Ideology content leans on the
  canon ceremony vocabulary, and ashuna, ibana, utinni, mambay, mombay, sabioto
  and bom\'loo happen to contain neither an h nor an apostrophe. Closing the gap
  was tested by substituting boota -> bootah, nootib -> n\'ootib and booka ->
  b\'ooka across both files; it improved this file to 0.173 and damaged the
  insults from 0.056 to 0.089, a net loss, so it was rejected. The alternative,
  forcing sand and smell imagery into counselling and conversion scenes to buy
  the h back, would trade real writing for a number. Left as is, deliberately.


  THE ENGLISH IS NOT A TRANSLATION, IT IS HOW THE JAWA TALKS
  ==========================================================
  Owner's call, 2026-08-12. Glosses were fluent English, which put a paragraph
  of subtitle under four syllables of speech. Nobody reads a paragraph floating
  over a pawn's head. They are now clipped pidgin: articles dropped, auxiliaries
  dropped, sentences short. Mean gloss 10.4 words -> 7.3; longest 17 -> 10.

      "Hands where I can see them. That is the whole of the law here."
      becomes
      "Hands where I see! That is law here."

  ⚠️ This deliberately breaks the gloss/Jawaese ratio metric, and that is
  correct. The corpus's own glosses are fluent English, so corpus gloss length
  stopped being the target. Ratio fell 2.47 -> 1.67 while every Jawaese metric
  stayed identical, which is the proof the change touched only the English.
  compose.py reports ratio but excludes it from the score. Do not pad the
  glosses back out to "fix" it.

  REGISTER
  ========
  The commercial voice from the insults, moved through different rooms. A Jawa
  threatens with PRICE, not pain: suppression is inventory control, conversion
  is a sales pitch, a trial is a valuation dispute with an audience. Counsel and
  reassurance are the warm end of the same instinct, which is that a person is
  worth keeping and most broken things can be rebuilt.

  \u26a0\ufe0f SparkSlaveRebellion IS SPOKEN BY THE SLAVE, not by a colonist. Slaves are
  members of the player faction, so the PlayerColony condition does match them.
  Those four lines are written from the slave\'s side on purpose, and reuse the
  colony\'s own manifest imagery against it.

  THE FOUR CONDITION FAN OUT
  ==========================
  47 lines authored across 14 defs, emitted as 188 rules, once per speaker
  condition (PlayerColony, PlayerTribe, RSW_Jawa, RSW_JawaTribal).
  Grammar conditions AND together and there is no OR, so four cases means four
  copies. Covering only the first would leave tribal starts and every NPC Jawa
  speaking English.

  \u26a0\ufe0f FACTION, NOT SPECIES, for the first two, so a human, Hutt or Gamorrean
  colonist also speaks Jawaese. Inherited from the existing corpus.

  REGENERATING
  ============
  Authored lines live in src/RimMandrake/Utils/jawavoice/lines_ideology.py. To change the
  writing, edit those and re run:

      python src/RimMandrake/Utils/jawavoice/genideo.py      # rewrites this file
      python src/RimMandrake/Utils/jawavoice/compose.py      # rescores it against the corpus

  Never hand edit the four copies of a rule: drift between them is invisible in
  play, because the engine simply picks a different copy.

  SAFETY
  ======
  Every op is PatchOperationConditional on the exact node, so any def falling
  out of Ideology makes that one op a silent no-op rather than a load error.
  priority=250 beats SpeakUp\'s English; Core and Ideology lines carry no
  priority, default p=1.

  All 14 xpaths confirmed to match exactly 1 node against the FULL 568 mod load
  set. Validating against the reduced set that happens to be live reports 14
  false errors, because Ideology is not active in it.

  VERIFY AFTER THE NEXT LOAD
  ==========================
    * Take a prisoner, set the interaction mode to reduce will, let it RUN.
    * Suppress a slave.
  ============================================================================
-->'''


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def op(defname, rows):
    x = '/Defs/InteractionDef[defName="%s"]/logRulesInitiator/rulesStrings' % defname
    L = ['  <Operation Class="PatchOperationConditional">',
         '    <xpath>%s</xpath>' % x,
         '    <match Class="PatchOperationAdd">',
         '      <xpath>%s</xpath>' % x,
         '      <value>']
    for jaw, gloss in rows:
        body = esc("%s (%s)" % (jaw, gloss))
        for c in CONDS:
            L.append('        <li>r_logentry(%s,priority=250)-&gt;%s</li>' % (c, body))
    L += ['      </value>', '    </match>', '  </Operation>']
    return "\n".join(L)


if __name__ == "__main__":
    out = [HEADER, "<Patch>", ""]
    for banner, defs in GROUPS:
        out.append('  <!-- =============================================================')
        out.append('       %s' % banner)
        out.append('       ============================================================= -->')
        out.append("")
        for d in defs:
            out.append(op(d, ideo2.D[d]))
            out.append("")
    out.append("</Patch>")
    dest = os.path.join(_REPO_ROOT, "src", "RimStarWars", "JawaVoice", "Patches",
                        "JawaVoice_Ideology.xml")
    io.open(dest, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    n = len(ideo2.ALL)
    print("wrote %s\n  %d defs, %d lines -> %d rules"
          % (dest, len(ideo2.D), n, n * 4))
