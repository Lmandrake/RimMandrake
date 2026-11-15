# Graffiti: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to.

Graffiti entered the pipeline on the owner's word, outside the four-mod intake rule: "Graffiti should be properly
entered into the pipeline as usual including a first touch Designer." (OWNER, item
RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED, 2026-11-15T04:53:51Z). `maturation_dispatch.json` lists
it among the advancing mods; the Dispatch step never launches the Designer.

## The mod as it stands

- **Stage now:** Stage 1, the Designer, since 2026-11-14 9:00 PM PST (`version/stage_record.json`).
- **Design Version:** none yet; it is cut at the Designer's Lock step, which Graffiti has not passed.
- **Designer:** `stage.json` reads its Lock step, status waiting_owner, parked (second_refusal, 2026-11-15T09:32Z) on
  `park_summary.md`. Accepted: Read, Argue the idea, Argue the edge, Write, Exam (64 frozen scenarios, both Readers
  matched). The coverage judge (rm-coverage-judge-1794734941) holds 22 of 24 fixes; gaps g1 (after_the_raid shares
  inv_player_orders with the spree corridor) and g18 (a wall's far side takes paint, no live control) stay open. The
  Designer can fix both at its Write step without him.
- **Waiting on:** his own word (words or a card) on RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED:
  rework, certify as it stands, waive a gap, or stop. A seat note or a --per-ruling act does not lift the park
  (`designer_stage.standing_park`).
- **Budget:** 6.94M weighted tokens of the 4M task cap spent (advisory outside a judge loop); the judge-and-rework loop
  since 2026-11-15T08:27Z has spent about 3.4M of its 8M ceiling (twice the cap).
- **Next:** on his word, the Designer (`role_launch.py`) reopens; rework sends it to the Write step for g1 and g18.
- **Open questions for him:** the park question above. His recorded answers: root plus raiders who leave threats and
  marks; agent walks first; face (B) the spree corridor; a standing raider mark makes that faction's next raid sooner
  or bigger, announced by a letter (the letter must name the wall mark as the cause:
  RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL).

## History (dated, added to only)

### 2026-11-14 9:00 PM PST, Stage 1 begins: the Designer's first touch

The owner filed the entry item at 8:53 PM PST; the first Designer run (rm-role-designer-1794718558) opened at 9:00 PM
PST. Answers to its asks came by card between 9:43 PM and 11:36 PM PST (ledger notes on the item).

### 2026-11-15 5:40 AM PST, journal started and record seeded

Written by a Conductor helper (BENCH) answering "Are all the mods being advanced right now?": Graffiti had a Designer
record but no maturation record, so `maturation.py next Graffiti` read UNMEASURED. Seeded from this journal. Nothing
was launched: the park waits on his word.
