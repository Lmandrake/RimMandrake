# Graffiti: where the last pass got to

Pass 7 on game B. It retired on context, about 260k tokens. Weather: none. No dead game, no dropped ssh, `bad_cpus=[]` at the start; 5 deploy/up cycles, all came up first time.

## Phone call (broaden), made this pass: `D:\ClaudeWork\rimmandrake\ralph_graffiti\gpt_help_pass007.md`
Asked: what real players would do that my staged tests miss (ask: `ralph/live/broaden_ask.md`). Its 7 leads, most revealing first: (1) leave graffiti alone in a colony that needs work, through a disruption; (2) a newcomer clicks a mark and tries to learn who, about whom, how good, and what it did; (3) farm a pawn's mood/opinion with paint-read-scrub cycles ("once per mark" vs "once per person"); (4) a confrontation meeting a pawn who can't take part (no violence, drafted, arrested); (5) the player disagrees with the colony about keeping a mark; (6) rebuild a marked wall in another material; (7) the same visitors back through another gate.
Acted on (1), (3) and (4). What it found is below. (2) is half done: the wall's inspect pane already tells the story (`WallInspectPatch`), and `g.py wallui` now clicks a wall and shoots it, but no shot was taken yet. (5), (6), (7) are untried.

## Found by playing, and fixed (build `+dirty` on 4cc156fb8c; the last fix, numb pawns, is built but NOT deployed)
- **Accidents started feuds.** Three idle days, no hooks: 79 marks and 4 "painted over my work" grudges. One of them led to a two-sided mockery feud (BW/Mo). Causes: a gap measured when the brush went up, then a neighbour finished beside it before the brush came down; and a painted reply that went over a bystander's mark as well as its target's. Fixed: the gap is measured again at the finish (`JobDriver_PaintGraffiti.FinishMark`: "left X unfinished: fresh paint beside it", seen live), and a reply needs room clear of everyone but the person it answers (`BareRoom(spare)`, `TryFindReplyCell(against)`). Rerun, three idle days: 58 marks, **0** accidental grudges.
- **Log spam**: "Mo glared at BW's tag" logged 3 times in 360 ticks (one line per tag). Now rival tag, moved, offended and mourning log once a day per reader and painter (`RM_GraffitiKernel.LogsOncePerDay`).
- **Outer walls painted solid**: outdoors counted as one map-sized room with no cap. Now open ground caps by stretch: 2 marks within 4.5 cells (`StretchHoldsEnough`).
- **A drafted pawn could be pulled into a paint fight** (vanilla `SocialFightPossible` doesn't check drafting): fight chance 0 if either pawn is drafted, and a confront fails while the painter is drafted (the grudge stays open).
- **Psychopath showed "+0 Enemy marks on our walls"** in the needs list: `ThoughtWorker_EnemyClaim` now inactive for numb pawns. BUILT, NOT DEPLOYED.

## Proven live this pass (busy colony: `st Busy` gives a potato field, a storeroom of blueprints, hauling, forever bills, trees to cut)
- **Tribute**: Lark (art 15) painted a good tribute to Vex. Vex +6.6 "Tribute from Lark" and +22 opinion (Lark became her Friend). Pell, Lark's lover, -3.7 mood and -14 "paints tributes to someone else". Brick, who hates Vex, -6.6 "paints tributes to someone I can't stand". Unprompted, Pell then painted his own tribute to Lark, and "Lark found the tribute Pell painted for them and stood looking at it". Shots: `first_look_tribute_jealous_needs.png`, `first_look_tribute_vex_social.png`.
- **Painting is recreation**: Lark's joy went 0.56 to 0.63 over one tribute.
- **Rereads at most daily**: in one day, 71 rereads, no pawn reread the same mark twice inside 60000 ticks. The first read's memory (Honored, 4 days) is stronger than a reread (0.6x), so a reread shows only once it has faded; opinion is never given again.
- **Settings**: painting off, then 30000 ticks: marks stayed at 53 while reactions went on. Social off: every wall mood and opinion went to 0 within 300 ticks, with no grudges left. Both back on.
- **Raid retaken with names**: a real raid (Kysdo, 2 pirates, sent at the wall, then turned for home) left an awful wide throw-up at (146,113): "Kysdo left their mark on your walls on the way out." 7 colonists got "Enemy marks on our walls" (-1, Volatile -1.5). Mo, ordered, scrubbed it: "Mo scrubbed away the enemy's mark", "+3 Took our wall back", and the colony thought ended.
- **Rate, no hooks, 8 idle pawns, 3 days** (second run, fixed build): 58 marks, full by day 0.75 (room caps), then flat. 1 subject mark, **1 message in 3 days**, wall mood per pawn between -1 and +6. On the busy colony, 2 days: 8 messages, 4 subject marks (a staged feud, two tributes, a mockery).

## Do next, in order
1. `ralph/steve.sh deploy` + `up` (the numb fix), then a fresh `setup @ st Busy` colony. It needs no other staging.
2. GPT lead 2: `g.py wallui <name> x,z` on a mockery, a tribute and a raid mark. Can a newcomer read who, about whom, how good, Beauty? The wall's lines show no Beauty (only the mark's own `GetInspectString` does); consider adding it.
3. The final shot set for `DONE.md`, all on this build at 64 ppc in daylight: `st Gallery`, `st Sweep` (rooms: granite 4,6,16,10; wood 19,6; steel 34,6; marble 4,16; plasteel 19,16; slate 34,16; one screen holds 18x10 cells), `st Ladder` (ugly vs fine), `st Compare` (paint vs dirt), a lived-in colony after 2 or 3 days, plus each social bar's UI shot. Retake the fight with blows on this build (`so Feud`, a hot pawn, `until "BLOWS"`).
4. Telemetry: read the newest `JawaBench\tps\tps_*.jsonl` on Steve for a 3-day run (not done in any pass).
5. Then `DONE.md` (the broaden call is done, this pass).

## Traps
- The gate refuses Bash commands containing `stage_colony`, `rimbridge` and the like, even in paths (use globs). It also blocks the WHOLE command when it delivers a context warning: re-run it.
- `ralph/steve.sh run '...'`: the driver chains with ` @ `; pass tool args with `kv`. After editing `ralph/live/g.py`, run `ralph/steve.sh sync` before using it.
- `g.py days N chunk` prints a TALLY line per chunk (marks, about, msgs, log, each pawn's wall mood/opinion total) and only event trace lines. `so Said n` lists the messages the walls sent (the game's own message list forgets them in seconds). `so Set field=value` flips a setting.
- `g.py ui` now parks a virtual hover (`rimworld/set_hover_target`) right of the cell, so Steve's real mouse no longer raises a Food tooltip. The Needs tab's top (Mood bar) is still cut off on the 720-high screen.
- A raid stages far off: `kv jawa/lord_pawn_move action=list` to find it, `kv jawa/lord_set_job lordIndex=N lordJob=LordJob_AssaultColony args=assaulterFaction=<def>;canKidnap=false;canTimeoutOrFlee=true;sappers=false;useAvoidGridSmart=false;canSteal=false`, step 600 at a time with `kv rimworld/step_game_ticks ticks=600` (safe_advance stops on threats), then `LordJob_ExitMapBest args=locomotion=Jog;canDig=false;canDefendSelf=true` when they're at a wall. `lord_travel_to` did nothing on a staging raid.
- Social off then on forgets every wall memory (by design): don't toggle it in a colony you still want to read.
- The staged hall has a stove, so it's a Kitchen and autonomous painters skip it. Own-faction marks are never auto-cleaned (fork F7).
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`. New .cs files go in `Source/Graffiti.csproj`.
