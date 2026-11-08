# Graffiti: where the last pass got to

Pass 12 (2026-11-08). Everything is committed and pushed. Game B runs the newest build (weathering, deployed and seen live).

## Weather this pass
- No drops, no dead game, no ssh failures. `bad_cpus=[10]` all pass; nothing surprising needed a restart to confirm. Six deploy/up cycles, each about 25 s.

## Built and seen live this pass
- **Skill shows on the wall.** The craft ladder at 64 px showed masterwork looking like normal work. Good+ pieces now stand off the wall on a dark 3D block in the paint's own darkest shade (deeper with craft), and masterwork and legendary carry white shine glints on their letters' top edges (`RM_GraffitiKernel.CraftDepth`, `ShinePoints`, `MarkPoint`; `Filth_Mark.PrintSkill`). The block needs a render queue one under the paint: an altitude bump alone drew it over the letters. Shots: `art_skill_ladder_*`.
- **The scrub hold covers the whole dragged stretch.** Live: the 2.9-cell ring round each scrubbed mark left gaps, and a tag and a mockery landed in them within a day. Now the bounding rect of the drag, 3 cells wider, is held for 10 days (`HoldStretch`, saved as `rmHeldStretches`/`rmHeldSince`). Live: nothing was painted inside it for 6 days (`scrub_hold_lived_in_corridor_day18.png`).
- **A mockery off the wall eases its subject at once** (GPT lead 4). Scrubbed, crossed out, painted over, weathered or its wall gone: the subject's "Mocked on the wall by X" goes to stage 1, "(gone now)", -4 base instead of -8, a day at most (`Notify_MockeryGone`, hooked in `Filth_Mark.Destroy` and the cross-out). Live: "Lark's humiliation over Karen's mockery eases: it's off the wall" when Lark painted back over it.
- **Paint weathers** (from GPT lead 2, the long run). Five and a half unattended days (`graffiti_p12_ash_long`): marks reached 67 by day 11 and nobody painted again for 3.5 days. Every joy giver answered null because every wall was at its cap, and nothing but the player or an answer ever removed our own marks. Now each mark has a life (`WeatherDays`: indoors about 44 days, outdoors half that, posters half again, stencils x1.3, scrawls x0.8, better craft longer, +-25% by id). It fades over the last 40%, as more wall shows through, thinner paint and lower Beauty, and then it's gone with a trace line. A `permanent` flag is saved and never weathers, left for Luminous Pigments. Live, from day 16: three outdoor marks wore away in 1.5 days, and Karen painted four new ones, a mockery among them, in the gaps. One message in 1.5 days.
- **Classic-mode hook** `so Classic on|off` (sets `Find.IdeoManager.classicMode`): built and deployed, **not yet used**.
- Ledger lines now show each wall memory's age (`(age N)`), which is the evidence for rereads at most daily. The bridge's `jawa/pawn_need` memory list is capped and drops ours.

## Seen live this pass (no code change needed)
- Painting switched off (`so Set paintingEnabled=False`): 19,000 ticks, no new marks, no paint replies; a scrub of a mockery still happened (cleaning, not painting).
- Save and reload: 60 marks identical (def, craft, Beauty, maker, subject, room) and every pawn's wall mood and opinion totals equal.
- Long run (`graffiti_p12_ash_long`, ticks 637k to 961k): 11 messages in 5.5 days, all in a burst around one Karen–Lark mockery feud (mockery, reply over it, confronts, cross-out, a tribute). Wall mood per pawn stayed between about +6 and -10, with no one spiralling. Karen confronted Lark at 954353 with BLOWS (chance 0.36), but I don't see a message for it in `Said`. Check whether the fight message goes through `Tell`.
- Performance (game B's `JawaBench/tps` record): 0.57 ms per tick average while fast-forwarding, worst 12.7 ms; all map components 0.003 ms per tick.
- GPT lead 3 (insult read through a bedroom wall): not possible. A reader must share the mark's room and have line of sight to the floor before it (`GraffitiSocial` ~L305). Lead 5 (Beauty exploit): ten excellent pieces raise an 8x8 room's average Beauty by about 1.25, far less than one sculpture.

## GPT broaden (pass 12): asked, got, acted on
Asked with six current shots (`ralph/live/broaden_ask_pass12.md`). Answer: `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gpt_help_pass012.md`. Acted on: lead 2 (a long ignored run, which found the dead equilibrium, now fixed by weathering) and lead 4 (cleaning a mockery should visibly help its subject, fixed). Checked by code: leads 3 and 5. Not tried: lead 1 (a newcomer working back from "Mocked on the wall by X" to the mark: try `wallui` on the wall, and the thought's tooltip), lead 6 (an emergency mid-answer: draft or restrict, then release), lead 7 (people change while the paint stays).

## Do next (then DONE.md: the broaden requirement is met this pass)
1. Look at a mark mid-fade at play zoom and 128 px (load `graffiti_p12_ash_day18`; find a mark whose inspect says "fading"). If it reads as faint new paint rather than worn paint, weather it differently (patchier, not just thinner).
2. Unseen on this build: raid tag and retake (`kv jawa/fire_raid points=120 arrivalMode=EdgeWalkIn ...`, wait until they reach the east wall, then `kv jawa/lord_set_job lordIndex=N lordJob=LordJob_ExitMapBest args=locomotion=Jog;canDig=false;canDefendSelf=true`), visitors (`so Order <painter>/RM_Graffiti_FactionInsult/<faction>/x,z` on the outer wall, then `kv jawa/fire_incident incidentDef=TraderCaravanArrival faction=OutlanderCivil forced=true`, `gw` before and after), the clean-freak fit (Mo is Very Neurotic: `brk Mo RM_GraffitiCompulsiveCleaningBreak`, then a `ui` shot mid-fit), classic mode (`so Classic on`, `st Spree 1`, a day; Count shows no new IdeoSigil or Glyph, and the Ledger shows no "Our sign").
3. making_a_mark: `setjoy 0.4 <names>` then `painting making_mark 30000` (it now waits for joy to rise before the mid shot; I never looked at the second set).
4. Rereads at most daily: `so Ledger`, where a mark seen for days has a memory with age under 60000.
5. Lead 1 (newcomer finds the mockery): one `wallui` shot of the wall carrying it.
6. DONE.md with verdicts on every north-star line.

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with the Write or Edit tool. `g.py` is the driver; `ralph/steve.sh sync` after editing it.
- `shot` refuses a rect wider than one screen: 20 cells at 64 px, 8 at 128.
- Local time: `kv jawa/time_date_at` gives no hour; compute it as ((ticksAbs + longitude/360*60000) % 60000)/2500. Ashgate is at longitude -17.9, Rustwall at -23.1. `kv jawa/weather_set weather=Clear lockWeather=true` after every load.
- Ashgate runs low on food: stock it with `kv rimworld/spawn_thing defName=MealSurvivalPack x=120 z=131 stackCount=10` (x 120..125) before long runs.
- `ui` shots raise a Food tooltip unless a cell is passed (it parks the hover on the map).
- The Needs tab list is cut at about 17 lines and the bridge can't scroll it.
- `days` shows only the last trace lines of each chunk; `so Said 30` lists every message with its tick.
- Saves on game B: `graffiti_p12_ash_long` (day 16, before weathering), `graffiti_p12_ash_weather`, `graffiti_p12_ash_day18` (newest, with weathering), `graffiti_p11_rust_memorial` (Rustwall).
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,RimWorld.Planet}/`.
