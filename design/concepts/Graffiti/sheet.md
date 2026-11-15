# Graffiti: a colony's walls become a record of its people

## his words
- 2026-08-30: "Add a queue item to assess the graffiti mod and expand it to include sacred graffiti, socially infuriating graffiti or amusing graffiti, or even beautiful graffiti."
- 2026-08-31: "Fully flesh out the graffiti mod now for tremendous application in the Jawa game. Jawas love graffiti. All the various kinds. Go for it!"
- 2026-09-09: "It should be a mod more aligned to punk style graffiti such as is seen in urban settlements, as well as ideoligion-inspired sigils taken from the Rimworld ideoligions as they exist in the game."
- 2026-11-07: "And did you test the social implications of the mod? It's more than just art display."
- 2026-11-07: "Please ensure that a person's art skill goes into the art's effect. A poor artist will paint such a bad graffiti mark that it is ugly, harms a room's beauty, and gives mood debuffs. But a highly skilled artist is actually making art. It is beautiful, improves a room and people's moods. And this combines with slanderous art: it can actually make you really angry as well as improve your mood from the beauty of it. Emotions are complicated."
- 2026-11-07: "Sociopaths wouldn't feel any mood change or care, while sensitive types might get extra mood debuffs or buffs as results. Clean freaks might get extra debuffs and have a mood break that makes them compulsively clean graffitti marks."
- 2026-11-14, the root: "(1) mostly, but it should also include Raiders that oppress with left-behind threats and marks for future attacks." OWNER:1794721657820999692
- 2026-11-14, the face: "It's not easy for me to understand this decision, but I'd say B." OWNER:1794728091811038301
- 2026-11-14, by card: a raider's standing mark -> "Sooner or bigger raid". OWNER:1794728164229812842

## does
- [leaf:mark_appears] A painting spree leaves marks on the wall, never an empty wall with a clean job log
- [leaf:reads_at_play_zoom] Every face-on mark reads at play zoom as made on purpose
- [leaf:sits_on_wall] A mark sits on its wall's front face and climbs onto the top, never floating over the floor; an edge-on wall takes no paint
- [leaf:marks_various] One colony holds visibly different kinds of mark, not recolours
- [leaf:ideo_sigil] A colonist of an ideoligion paints a sigil with that ideoligion's own icon, tinted, in a frame
- [leaf:punk_register] The set reads as urban punk graffiti, with no real-world signage
- [leaf:ugliness_visible] An ugly scrawl looks worse than a tally: stat and picture agree
- [leaf:art_skill] The painter's art skill sets beauty and mood both ways; a skilled slander angers and pleases at once
- [leaf:own_fun] Making a mark is recreation and gives its maker a small buff
- [leaf:rereads_daily] The same mark moves mood at most daily and opinion once
- [leaf:mockery] A mockery names someone and changes how people regard its painter
- [leaf:tribute_memorial] A tribute warms, a rival is jealous, a memorial eases its grieving painter
- [leaf:answer_wall] Pawns answer the wall: a scrub, cross-out, reply or confrontation the player sees finish
- [leaf:scrub_protection] Cleaners leave devotional and the colony's own marks unless ordered
- [leaf:player_orders] The player orders a chosen mark on a chosen cell and gets exactly it
- [leaf:raid_mark_troubles] A leaving raid tags the outer walls and troubles the colony until the wall is scrubbed
- [leaf:going_over] An enemy paints over a colonist's tag, which is gone
- [leaf:raider_pressure] While a raider faction's mark stands, a letter names it and points at the mark, and its next raid comes sooner or larger; the last mark gone lifts it. OWNER:1794728164229812842, owed
- [leaf:visitors] A visiting trader reads an insult to its faction once per visit, never recharged
- [leaf:fights_reasons] A fight has people and a reason, and never breaks a pawn's restrictions
- [leaf:temperament] Psychopaths feel nothing, sensitive pawns feel more both ways, clean freaks take more and can break into cleaning marks
- [leaf:stands_alone_settings] Works without any ideoligion, survives a reload, stops when each of its settings says stop: 8 today, 11 with the raider pressure's switch, mode and size
- [leaf:stories_not_tax] In an ordinary colony over weeks, occasional stories, never a mood tax or a message stream
- [leaf:walk_lived_in] A lived-in colony walked again after a reload: a spree, recreation tagging, a raid and a trader, in both orders, tell the same story
- [leaf:paint_dies_with_wall] Paint dies with its wall
- [leaf:weathering_bounds_marks] Paint weathers: it fades over the last 40 percent of its life, sooner outdoors
- [floor:mod_settings] Superb Mod Settings: every behaviour has its switch, and the raider pressure gets one with its tuning
- [advisory] Mood sizes, weather days and the pressure factor are tuning; scenes check sign and shape

## does not
- [leaf:no_english] No legible real-world English or a third-party author's tag in any mark
- [leaf:not_dirt] No mark that reads as vanilla dirt at play zoom
- [floor:worldgen] No worldgen of any kind
- [floor:multiplayer] No multiplayer support

## waived

## open

## delegated
- The raider pressure letter names the faction and points at its standing mark, so the push is traceable to the wall; the last mark of that faction scrubbed or weathered lifts it; sooner versus larger and the size are Mod Settings with shipped defaults. Undo by saying so.
- The ideoligion sigil, going-over, scrub protection, player orders, wall loss and weathering are built capabilities kept as leaves under the nearest validated line; none adds a bar to the north star.
- Breach bias toward a colonist-painted warning glyph stays built and is covered by its switch check only; it has no line of its own.
- Showcases after his flagship: the social wall, then the raid and its pressure, then the devout wall, chosen by most new capability each.

## pruning
- mark_appears: yes, it already failed silently once
- reads_at_play_zoom: yes, his 2026-09-16 ruling
- sits_on_wall: yes, a floating decal reads broken
- marks_various: yes, his all the various kinds
- ideo_sigil: yes, his ideoligion-inspired sigils
- punk_register: yes, his punk style and no Earth signage
- no_english: yes, it shipped once with a donor tag
- not_dirt: yes, a mess is not a message
- ugliness_visible: yes, stat and picture must agree
- art_skill: yes, his 2026-11-07 words
- own_fun: no alone, a small buff
- rereads_daily: no alone, but stacking reads becomes a tax
- mockery: yes, more than art display
- tribute_memorial: yes, more than art display
- answer_wall: yes, a wall nobody answers is a decal
- scrub_protection: no alone, but wiping sigils breaks devotion
- player_orders: no alone, a player tool
- raid_mark_troubles: yes, in the validated north star
- going_over: no alone, it is how a raid claims a wall
- raider_pressure: yes, his root clause and his card
- visitors: no alone, but a recharging trader drains goodwill
- fights_reasons: yes, violence from nothing reads broken
- temperament: yes, his 2026-11-07 words
- stands_alone_settings: yes, the settings floor
- stories_not_tax: yes, a tax is the failure he most fears
- paint_dies_with_wall: no alone, ruled by card
- weathering_bounds_marks: no alone, but it bounds raid marks and pressure
- walk_lived_in: yes, the walk is the mod in play
