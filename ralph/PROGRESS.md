# Graffiti: where the last pass got to

Pass 11 (2026-11-08). Everything is committed and pushed; game B runs the newest build (`4b3ad46` + the scrub hold, deployed at commit time).

## Weather this pass
- Game B was hung at the start: its log stopped at 20:57 mid-load of `graffiti_p10_ash_story` (a load something before this pass asked for), canary `bad_cpus=[10]`. `deploy` stopped it (forced after 90 s); `up` then worked first time. No other drops. `bad_cpus=[10]` all pass; nothing surprising needed a restart to confirm.

## Built this pass (deployed and seen live unless said)
- **Scrub graffiti order** (design 1.7, fork F7: "a scrub designator overrides"). Orders tab, drag over walls or the floor before them. `Designator_ScrubGraffiti`, `RM_ScrubGraffiti` designation (vanilla remove-paint overlay), `WorkGiver_ScrubGraffitiDesignated` (Cleaning, priority 10, uses the answer's `RM_ScrubMark` job, reaches past the Home area, `RefusesToClean` holds). Live, Ashgate: 31 marks designated over Mo's spree corridor; Lark and Fringe scrubbed 23 in 6000 ticks. Hook: `st Scrub x,z,w,h` (the designator's own drag path).
- **A scrub is a chore when ordered** (or the vanilla cleaning rounds): no "There. Gone." mote (six stacked live), and one log line per cleaner and painter a day (was one per mark, 20 from one cleanup). Grudge answers, fits, enemy marks and rescued mockery subjects still say and log in full. Live: three log lines for the whole cleanup.
- **A mark's DrawPos is its wall face** (0.75 cell on from its floor cell): designation icons, selection bracket, cleaning dust and progress bar sit on the paint (`scrub_order_designated.png`). Print only reads its altitude.
- **A wall the player had scrubbed is held clean for 10 days** against our own painters (joy, idle, replies, meaning marks, sprees too); a player's paint order overrides. `MapComponent_GraffitiSocial.HoldScrubbed/HeldClean`, saved (`rmScrubbedHold`), checked in `GraffitiJobUtility.KeptClean`. Why: the scrubbed corridor took about ten new marks in two unstaged days, and the order looked pointless. **Deployed, not yet seen live**: scrub a corridor, run `days 60000`, and check no own-colony mark lands within 2 cells of a scrubbed one.
- **Classic mode (Ideology on, "no ideoligion")**: every faction carries the player's hidden ideo (FactionIdeosTracker), so raiders' marks read as our faith and a sigil painted the hidden icon. `GraffitiJobUtility.IdeoOf` returns null there and is used for every ideo read; nobody without an ideoligion paints a tier-A sigil (an empty frame). **Built, not seen live** (needs a classic-mode quicktest; that is the stands_alone "no ideoligion" profile).
- Driver: `load` now waits for two equal mark counts before returning (the empty-first-read trap is gone).

## Seen live this pass (evidence for DONE.md; shots in the shots folder)
- `optionD_materials_playzoom.png` / `optionD_materials_close128.png`: granite, wood, steel, marble, plasteel, slate rooms in daylight (Sweep). The face paint keeps its colour over the crease on every material; brick courses show through on granite and marble; light walls are not too loud; dark walls still read. Side faces carry a vertical scrap, as designed. (The first take was black: Ashgate's local time was 8:37 pm in a dry thunderstorm. Use `kv jawa/weather_set weather=Clear lockWeather=true`, and work out local time from `jawa/time_date_at` longitude.)
- Two unstaged days on Ashgate after the cleanup (ticks 517k to 637k): 2 messages (Mo's mockery of Lark, which traces to Lark's still-standing mockery of Mo; Lark's tribute to Brick), about 6 log lines, marks 45 to 60, one vanilla break (Lark, Tortured Artist, insulting spree). **Mo does not spiral** (mood 82%). His -13.2 is a 3-day humiliation from a mockery Brick scrubbed (expires) plus -4.4 from Lark's mockery, which still stands; the player can now scrub it in one drag. Save: `graffiti_p11_ash_days`.
- Rustwall (`graffiti_p8_busy3`, then saved as `graffiti_p11_rust_memorial`):
  - `personality_psychopath_cathryn_needs.png`: Cathryn (Psychopath) after Brandt painted a mockery of her: no wall thought at all. `so Temper` reads numb, paint urge 0.
  - `personality_sensitive_kinso_needs.png`: Kinso (Volatile) "Mocked on the wall by Brandt -13" (base -8, ×1.5, × good craft); the line is at the bottom edge of the list, legible. He then scrubbed it and painted an awful mockery of Brandt back, unprompted.
  - `tribute_jealous_kinso_message.png`: Lark (Kinso's lover) painted a tribute to Brick; Kinso read it as Jealous. The message shows ("Kinso saw Lark's tribute to Brick and said nothing, loudly."); the thought is below the cut of the list.
  - `memorial_lark_grief_half.png`: Pell killed; 10,500 ticks later Lark painted a good memorial. Needs: "My friend Pell died -2", "Painted a memorial to Pell +1": exactly half. Message on screen.
  - `art_skill_crafts_ladder(_beauty).png`: one Piece at each craft, Beauty -6, -3, 0, +3, +8, +18, +30, at 40 px per cell (29 cells wide). **Not yet looked at.** Check that the overlay numbers show and the awful ones look worse.

## Do next
1. Look at `art_skill_crafts_ladder_beauty.png`. If the overlay numbers don't show, hover a cell nearer the row, or take two 64-px halves.
2. See the scrub hold live (above). Then the classic-mode quicktest: `prove_quicktest_world.py` with classic mode (or set `Find.IdeoManager.classicMode` before generating), one spree, a raid exit; check no sigils and no "Our sign" reads from raiders.
3. Clean-freak fit: `so Cast Brick/Neurotic:2/0`, `brk Brick RM_GraffitiCompulsiveCleaningBreak`, then a UI shot mid-fit.
4. Still unseen on this build: raid mark and its retake, visitors, `so Set paintingEnabled=False` then a quiet day, save and reload, making_a_mark (a Needs shot with "Left my mark" while recreation rises), a reread a day later (the trace has `rereads` lines; a thought's age is the evidence), scrawl beside tallies on a lived-in wall in daylight.
5. GPT `broaden` with these shots (required before DONE.md; pass 9's used old ones), act on one or two leads, then DONE.md.
6. Retire the old shots: move the pass-8 and earlier shots in the shots folder that the current build no longer matches into `old/`.

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with the Write or Edit tool. `g.py` is the driver; `ralph/steve.sh sync` after editing it.
- `shot` refuses a rect wider than one screen: 20 cells at 64 px, 8 at 128, 28 at 44.
- Two `so Order` calls in a row for one painter: the second replaces the first. Wait for the first (`until`).
- `so Order` without a cell can fail with "no wall": give it a known wall-face floor cell.
- The Needs tab's thought list is cut at about 17 lines and the bridge can't scroll it; a long-lived colonist's wall line may sit below the cut.
- A numb pawn (psychopath) never appears as a reader in the trace: they're skipped before reading.
- Rustwall is in a bad state (starvation, raid, two dead): good for mechanics, not for "lived-in" art shots. Ashgate is the lived-in one.
- `up` started in the background: wait for "started game b" in its log before calling the bridge.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,RimWorld.Planet}/`.
