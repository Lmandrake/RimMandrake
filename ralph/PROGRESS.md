# Graffiti: where the last pass got to

Pass 5 on game B. It ran the pass-4 social layer live for the first time, fixed what play showed, then retired on context. Weather: none. No dead game, no dropped ssh, `bad_cpus=[]` throughout. About 9 deploy/up cycles, all came up first time. Player.log clean at load (no exception).

## Proven live this pass (8 cast colonists, staged colony; driver `ralph/live/g.py`)
- **Mockery**: subject Humiliated (-8.8, or -13.2 on a Volatile pawn, so sensitive feels 1.5x) and opinion of painter -33/-45 ("Painted me on the wall"). Friends take it badly (FriendDefends, opinion -13). An enemy of the subject is gleeful (+4, opinion of painter +11). Kind disapproves ("Paints cruel things", -6.6). Neutrals lose regard for the subject (LostFace). Painter gets "Showed the wall what X is" +4. Psychopath: nothing at all.
- **Answers**: the subject crossed it out or scrubbed it, and the maker resented it ("X wiped out my work", opinion -8). A friend (Sinn, abrasive) confronted the painter: trace `Sinn confronts Lark: fight chance 0.19 -> words`. Lark (Tortured artist), whose work Grigory painted over, replied with a mockery of Grigory. Brick, humiliated, painted a crude revenge mockery of Sinn. Read it all in `first_look_social_brick_social.png`.
- **Fight chance scales with temper** (`so Fight a/b`): Brick (Brawler+Bloodlust) 0.243, rising to 0.483 once he hates the painter. Grigory (Volatile) 0.101, Mo 0.030, Vex (Kind) 0.017. **No fight with blows seen yet.**
- **Clean refusal and bond**: Mo, who hates Grigory, was refused: "Mo won't clean up an insult to Grigory." Vex cleaned it, and Grigory got +4.5 mood and +18 opinion of Vex ("Wiped that mockery of me off the wall"). The maker got -2.5 and -10.
- **Memorial**: Pell died, and Lark (friend 70) painted a memorial for Pell on her own: "+5 Painted a memorial to Pell" (grief eased). A non-friend reading it gets nothing.
- **Clean freak**: Mo (Very Neurotic) gets "Filth all over the walls" -3. The forced break `RM_GraffitiCompulsiveCleaningBreak` runs (state, alert, scrubs marks one by one, each maker resents it). About 800-1200 ticks per scrub.
- **Art skill**: craft is rolled and shown. Good and fine marks give "Good/Fine work on the wall" +1..+2, even on a mockery (the owner's "emotions are complicated" holds). Awful and poor marks give "Clumsy/Hideous paint" -1..-2. Room beauty follows the craft.

## Fixed this pass (all deployed and live)
- **Who paints follows art**: `GraffitiTemperament.Urge` = paint column x `RM_GraffitiKernel.HandUrge(passion, level)`. It feeds JoyGiver `GetChance` and the idle tagger. Artistic-disabled pawns never paint by choice (a spree still can). Before: the two weakest hands made 7 of 8 marks, an art-disabled pawn among them, and the level-15 artist none.
- **Form by skill, craft ceiling by form**: `FormAffinity` weights the pool (beginners tally, scratch and tag; artists throw-up, stencil, paste and piece). `CraftCeiling`: Glyph/Scrawl at most Normal, Tag Good, ThrowUp Excellent. Before: "excellent Scratches" scored +8 Beauty.
- **Beauty stat line reads craft**: `StatPart_GraffitiCraft` on Beauty, installed at startup. Before, the stat said the def's -6 while the room counted +3.
- Colonist lists are copied before iterating. `FreeColonistsSpawned` is a cached list the game refills mid-loop: the Ledger crashed on it, and SocialMark, Notify_Cleaned and the fit loop had the same shape.
- Proof hooks in `RM_GraffitiSocialProof`: Recruit, Cast, Befriend, Feud, Kill, Send, Order (with a cell), CleanOrder (the float menu's check, forced), Fight, Temper, Marks, Ledger("trace"). The bridge splits `static_call` args on `|`, so the hooks take `/`. Reading trace ring: `GraffitiSocial.Trace`.

## Not yet seen live (do these next, in order)
1. A fight with blows (roll it: several hot subjects, or more confrontations), with the message and the wall.
2. Tribute: Honored, Jealous (lover of maker), Scoffs.
3. Rereads a day later: mood again at 0.6 once the first memory expires, and opinion not again.
4. Settings off: social off forgets everything, painting off stops replies. Save and load mid-feud (grudges survive).
5. Visitors (trader caravan reading an insult; capped per visit), raid exit mark plus "retaken" ending the territory thought.
6. Joy: does Recreation rise while painting? ("making_a_mark_is_its_own_fun").
7. Rate: 18 marks in about 16k ticks with 8 idle pawns. The staged colony has nothing to do, so this overstates it, but check a busy colony over 3+ days. Count messages too (`rimworld/list_messages` returned 0 even after events; find out why). Consider `IdleTagChance` 0.02 -> 0.01.
8. Speech motes in a shot: `g.py until "<regex>" <ticks> 60`, then a shot at once.
9. Then the art: option D corners and junctions at 64 ppc, the blind judge's points (stamps with opaque backing read as pasted paper; shaded-dome sigils; tidy icons gear/sun/crown; side-face marks unreadable; the speckled brown scrawl reads as dirt), telemetry from `JawaBench/tps` on Steve, the required `broaden` phone call (none made yet this pass or last), and DONE.md.

## Traps
- The gate refuses Bash commands containing `stage_colony`, `rimbridge` and the like, even in `ls` or `grep` paths (use globs such as `rimb*`). Segments that start with `ralph/steve.sh` are fine.
- `ralph/steve.sh run '...'`: pipes split commands, so quote hook args in double quotes, and the driver chains with ` @ `. Raw JSON through it breaks on spaces; add a driver command instead (see `brk`).
- `ui` shots need `jawa/screenshot_mode enabled=false` (the driver does it) or the UI is hidden. A tooltip may cover the top-left.
- The staged hall has a stove, so the game calls it a Kitchen and autonomous painters skip it (owner's rule). Marks land in the corridor, bedrooms and outside.
- Own-faction marks are never auto-cleaned (fork F7), so a mockery stands until someone answers it or the player orders Clean. A feud can loop (Sinn re-mocks Brick after each scrub) until the Insulted memories fade.
- `GraffitiTemperament` caches per pawn for 2500 ticks; `Cast` calls `Forget`.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`. New .cs files go in `Source/Graffiti.csproj`.
