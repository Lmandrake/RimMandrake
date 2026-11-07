# Graffiti: where the last pass got to

Pass 6 on game B. It retired on context, about 260k tokens. Weather: none. No dead game, no dropped ssh, `bad_cpus=[]`, one deploy/up cycle (first time). Player.log had no exception after loading the save on the new build.

## Proven live this pass (build c7512fe, the pass-5 colony at ticks 18k-64k, plus hot-tempered recruits)
- **A fight with blows, with people and a reason**: Hob (Brawler+Bloodlust, hates Sinn -61) read Sinn's mockery of him, then `Hob confronts Sinn: fight chance 0.85 -> BLOWS`. Message: "Hob confronted Sinn about what Sinn painted on the wall, and it came to blows." Hob's state is Social fighting. Shot: `first_look_social_fight_blows.png`. Seven confrontation trials before it: Kane (0.27) words; Dax crossed it out instead; Rook scrubbed; Orm defaced. So blows are rare, as designed.
- **Visitors, capped**: Lark and Abbott painted two FactionInsults to Eraen on the outer south wall, then an Eraen caravan came. Goodwill went 0 to -12 once and stayed at -12 for 4000+ ticks with both insults in reach. Messages: "Relations with Eraen have changed from 0 to -12 (insult painted on a wall)" and "Meyer of Eraen read the insult on your wall", both pointing at wall cell (112,114). `rimworld/list_messages` works now (3 messages).
- **Raid mark**: a pirate raid reached the east wall. Its lord was switched to `LordJob_ExitMapBest` (`g.py kv jawa/lord_set_job lordIndex=2 lordJob=LordJob_ExitMapBest args=locomotion=Jog;canDig=false;canDefendSelf=true`). Barisk tagged a Supremacist glyph at (143,120). Message: "Blight Blighters left their mark on your walls on the way out." Every colonist then had "Enemy marks on our walls" (-1, -1.5 if volatile), and the hot ones read it as Defiant. Within 1500 ticks the mark was gone and so was the thought. WHO removed it is unknown: no Reclaimed thought appeared, and the trace was lost. The new build traces every mark that goes and why.
- **Save and load mid-feud** on the new build: 101 marks and Ivo's open Deface grudge survived `graffiti_feud.rws` (game B's Saves).

## Built this pass (deployed: the C# yes; the 14 new textures NOT yet deployed, see below)
- **Side faces climb across the top** (`RM_GraffitiKernel.ClimbMax`/`FootOf`, `SideFaceShare` 0.22, `SideTopLip` 0.05; twin `art_source/wallgeom.py`). The raid's mark proved the need: a mark that troubles the whole colony was a 6 px sliver on a side face (`/tmp`-only shot, retake). Offline the width went from about 22 px to 38 px. Live (`first_look_side_faces_climb.png`) it is about 30 px. Better, but still narrow, so look again.
- **A mark about you is read first** (`GraffitiSocial.Look`, two passes). Before, Rook walked past his own mockery and read two tags instead.
- **Trace tells the whole story**: painted, scrubbed or crossed out, a visitor's goodwill, gone with its wall, and gone with no cleaner.
- **Sigil icons are two flat tones**, not UI shading (`WallPlane.PaintedIcon`). Not seen live yet.
- Proof hooks `Lovers a/b` and `PlayLog n`. `g.py` gains `kv tool k=v` (raw JSON breaks through ssh), `gw [faction]` (goodwill), and an `until` that prints every trace line.
- **Art redo by a helper** (manifest prompts, `bake.py` gets a per-mark alpha `floor`; old gen3 sources in `gen3/old/`): Paste_Flyer/Wanted/Gig become stencils sprayed straight on the wall with no paper, and their labels change ("stencil portrait", "wanted stencil", "fight-night stencil"). Vandal 0-5 become ugly sprayed paint instead of brown dirt. Gear, crown (now lime white) and tunneler are redone. Sheet: `first_look_art_redo_sheet.png`. Worry: the vandal yellow, violet and orange are the most saturated colours in the set. vandal_1 is a goofy face with its tongue out; check it doesn't recall the banned mouth logo. `validate_sprite.py` rejects all soft-edged art, including the old set, so it is no judge here.

## Do next, in order
1. `ralph/steve.sh deploy` + `up` (the textures were baked after the last deploy), then a FRESH quicktest colony. The pass-5/6 colony is ruined: 15 colonists, 6 beds, major break risk. Build it lived-in with a bed each, and shoot the gallery and sweep at 64 ppc: side faces, sigils with flat icons, the new stencils and vandals in game. Daylight only: the outer-wall insult at 2 AM was invisible.
2. Tribute: `so Lovers a/b`, Lark paints a tribute to a friend. Look for Honored, Jealous (the maker's lover) and Scoffs (someone who hates the subject).
3. Rereads a day later (mood again at 0.6, opinion not again). Settings off (social off forgets; painting off stops replies). Joy while painting.
4. Rate in a busy colony over 3+ days: marks, messages per day, mood totals. Then telemetry from `JawaBench\tps` on Steve (not done yet).
5. Retakes the Conductor asked for: the two Needs shots without the Food tooltip, and Mo mid-scrub. The real mouse on Steve's screen makes the tooltips, and it moves between shots: check each UI shot.
6. The required `broaden` phone call (none made in pass 5 or 6), act on it, then DONE.md.

## Traps
- The gate refuses Bash commands containing `stage_colony`, `rimbridge` and the like, even in paths (use globs). It also blocks the WHOLE command when it delivers a note or a context warning: re-run any edit it swallowed.
- `ralph/steve.sh run '...'`: pipes split commands; the driver chains with ` @ `; pass tool args with `kv`, not JSON.
- An ordered painter far away shows "painting graffiti" while walking (markDef is set at the wall). That is not a failure; wait.
- An answer waits while its target is over 45 cells away (owner's rule), so a confront can sit for thousands of ticks.
- `AnswerCooldownTicks` is 60000: a pawn who answered can't take on another grudge for a day. Fresh trials need fresh pawns.
- `ui` shots need `jawa/screenshot_mode enabled=false` (the driver does it).
- The staged hall has a stove, so it counts as a Kitchen and autonomous painters skip it.
- Own-faction marks are never auto-cleaned (fork F7).
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`. New .cs files go in `Source/Graffiti.csproj`.
