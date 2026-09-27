# The Twilight Deep — danger pass (2026-09-27 sitting)

> STATUS: RULED at the bench, 2026-09-26/27 — all seven cards answered, two of them
> redirected by owner-typed lines; §5 records the verdicts and this file is edited to
> the ruled state. Still not filed work or a frozen-sheet amendment.

Companion to `the_twilight_deep.md` (frozen sheet, waveglass amendment 2026-09-26) and
`the_twilight_deep_content_2026-09-26.md` (content drop). This file answers the owner's
2026-09-27 flag: *"we haven't detailed almost anything dangerous down here! That's a problem."*

## 0. The danger identity

The three seas already split cleanly on HOW they kill:

| sea | danger identity | the clock |
|---|---|---|
| the Grey | **mineral encasement** — the sea precipitates itself onto you; stillness is death | slow, spatial, crystalline |
| the Scald | **heat** — boiling water, steam, an exposure countdown | fast, ambient, everywhere |
| the Twilight | *(currently)* one predator and a current | — |

The Twilight cannot borrow either. Its register is the pretty ocean, the crowded one,
the one place where *"motion means life, not threat"* (frozen sheet §9). So its danger
identity is the inversion of that sentence read carefully: **in the Twilight, everything
that matters is alive, and living things have appetites, seasons and moods.** The Grey
kills you with chemistry and the Scald with physics; **the Twilight kills you with
biology** — with the abundance itself. Nothing down here is hostile the way a raid is
hostile; things are hungry, territorial, breeding, falling, or simply enormous, and the
player is standing in the middle of an ecosystem that was in motion long before the ship
came down and does not pause for it.

Three consequences that shape every entry below:

1. **The danger reads through the beauty, never against it.** Every threat below is
   also a spectacle — the thing you photograph is the thing that hurts you. A biome
   where the pretty things and the dangerous things are separate populations would be
   the Grey with better lighting; here they are the same population.
2. **Light is the currency, so light is the lever.** The player's whole economy down
   here is chasing, farming and carrying light (content drop §6.4). Danger that taxes,
   grazes, or extinguishes light bites the player where they actually live.
3. **The dark between the beams is the standing threat surface.** The sheet gave the
   dark to the predator (§5: *"the dark between is the predator's"*). This pass takes
   that line as load-bearing: the dark is not empty map, it is the place several of
   these dangers live, and the light economy is the player's answer to all of them at
   once. That is the coupling that makes the danger *Twilight-shaped*: on the dayside
   you fight the sun, in the Grey you fight the salt, down here **you hold a small
   circle of gold and things move at its edge.**

## 1. Danger roster

Eight entries — D3, the lamp-lure, was CUT at the sitting (light-as-lure belongs to the
dark-floored Grey and Scald, not the lighted Twilight; the ruling is in its slot and §5).
All names invented (`RM_` tier per Q11a); *suulk*, *vaulisk*, *undersurge*,
*gloamline* and *murrowisp* were collision-checked against `src/` and `design/` 2026-09-27
(one hit was a base64 substring in a review sheet's embedded PNG, not a name) — re-check
any renamed form before authoring, per the content drop's own convention. Every entry
obeys the six hard bans, keeps the waveglass a sky, and threatens no Compact hostility.

### D1 — Veil-fall pane strike: the sky sheds

**(a) Fiction.** The waveglass sheds — that is already canon, and the retirement of
`RM_MoldMatRoof` ruled the floor's share of it: *"a big panel that occasionally floats
down and can be harvested."* Most veil-fall is flakes and litter. Once in a while the lid
lets go of a **whole pane** — a sheet of living glass the size of a room, turning slowly
down through the gold, beautiful the entire way, and then it lands. The Compact's word for
being under one is not recorded, because the people it happened to did not come back up.

**(b) In play.** A letter fires and a **shadow marker** appears on the floor — a soft
dark patch that grows over ~15 seconds as the pane descends (the player watches the thing
arrive: the danger IS the spectacle). Anything in the footprint when it lands takes crush
damage — pawns, animals, plants, lamps, buildings. Then the landed pane is the reward:
**`RM_VeilPane`**, a large harvestable thing (the ruled event + item), plus everything it
smothered. The decision it forces: the pane is worth going to, and the strike zone is
random — so a colony strung out along a chained lamp field is exposed in proportion to
how much ground its lights hold. Haul crews race the weloon, which eat it.

**(c) Engine.** An `IncidentDef` + the vanilla skyfaller shape (meteorite idiom: descent
graphic, shadow, impact damage — the content drop already flags the custom-skyfaller
route as read-from-`Data/Core` before authoring). The landed pane is a building-like
thing with a work-to-harvest. **No new C#** beyond the skyfaller subclass if the stock
one can't carry the size; flag: probably a small subclass for the outsize footprint.

**(d) Interactions.** Panes shed thickest near a **closing skylight** (D5's drift gives
the strike a weather-vane: the well that is dying rains first — a legible tell and one
more reason to read the ceiling). A pane landing on a channel is carried by the current
(§2.2's item-drift) until it grounds on a bank — free delivery, if you can read the
river. A pane can crush a claim-buoy, a bank stake, a lamp, a cage's tether. The whale
sequence's beat-4 rain is this danger's little sibling and shares its art language.

**(e) BENCH position.** Build it early — it is the cheapest marquee danger in the set,
it is the ruled pane-event anyway, and it teaches "the sky is alive" better than prose.

### D2 — The suulk: the lamp-grazer

**(a) Fiction.** In a sea where light is food, shelter and speech, something grazes
light. The **suulk** is a soft, slow, night-coloured thing — a drifting fold of dark
tissue, almost invisible, lovely when a beam catches it — that feeds on luminous
symbionts. Wild, it grazes hoolimbre bladders and waelune, and the sea shrugs; the
colonies are older than appetite. Then a diver plants a noothelm row, hangs lamp-bladder
strings, cultures a sun-sphere — and has built the richest grazing meadow in the sea.

**(b) In play.** A suulk (or two — never a swarm) drifts in from the map edge on a
several-day cadence and beelines for the **brightest player-owned glower**, dims it as it
feeds (radius shrinking over minutes — visible), and destroys it if left. It is nearly
harmless to pawns (a shove, a slime) and slow: the danger is never to life, it is to the
**light economy** — the standing constraint that the useful lamp count stays SMALL means
losing two lamps is losing a district. Decisions forced: guard the lights, kill it (it is
big, slow and killable — but killing the pretty thing is the biome asking what kind of
resident you are), or **decoy it** — a sacrificial cheap lamp at the map edge, which the
Compact's own practice teaches (a lit stake standing alone outside the bottom-houses,
inspect string says why).

**(c) Engine.** One race + a **light-targeting JobGiver** (new C#, small): find highest
`glowRadius` thing owned by player, path, channel "feed" job that decrements the glow
(the breathing-radius ticker from content drop §6.2 already makes radius writable). The
same targeting brain is D4's lure-in-reverse — **build it once as `RM_JobGiver_SeekGlow`,
shared** — and it is the natural base for the light-attraction the owner redirected to
the Grey and the Scald (§5, C2).

**(d) Interactions.** Eats cultivated lights (noothelm, hoolimbre strings, waelune kept
as pets — a real loss the children's animal makes cruel in exactly the right way);
and it grazes the **sun-sphere** too, slowly and loudly — RULED (§5, C4): the dearest
lamp needs a guard, not an exemption.
Ignores the skylights (it cannot graze the sky) and the Compact's lamps (their stakes are
suulk-scarred and tended — texture, and ban 4 kept: the Compact never suffers for the
player's sake). During lid-dark (D9) suulk activity doubles: the dark brings the grazers.

**(e) BENCH position.** The signature danger of the set — it attacks the thing this
biome made the player love — and cheap once `RM_JobGiver_SeekGlow` exists. Build second.

### D3 — CUT: light does not call the sea here

The drawn-dark proposal (player lamps attract prey, predators follow the prey into the
lamplight) was put to the owner and cut for the Twilight. Owner, typed, 2026-09-26:
*"Actually attacking light makes more sense in the Grey and Scald (dark on the bottom)
than it does on the beautiful lighted Twilight floor with lots of lighted everything."*
⇒ On a floor already full of living light, one more lamp is no signal; light-as-lure is
a **dark-floor** mechanic. Redirected, not dead: the Grey and the Scald get the
attraction mechanism when their danger passes come up, and `RM_JobGiver_SeekGlow`
(D2/D4) is its natural shared base. The Twilight's standing pressures are the famine
(D5), the grazer (D2) and the liar (D4) instead.

### D4 — The vaulisk: counterfeit gold

**(a) Fiction.** The Twilight's light grammar is honest: gold is home and harvest,
blue-white is moving, green is growing (content drop §6.1). The **vaulisk** is the one
liar. An ambush thing of the dark between, it hangs a **gold lure** — a false bladder,
indistinguishable at range from a hoolimbre lamp — and waits. The sea's whole language
has exactly one counterfeiter, and every Compact child is taught the tell before they
are taught to swim a net: *a lamp with no piip around it is not a lamp.*

**(b) In play.** Spawns rarely, in the dark between shafts, disguised as a lit
lamp-bladder plant. Small wild fauna drift to its glow (the lure feeds itself). A pawn sent to harvest "that hoolimbre we didn't plant" gets an
ambush: fast strike, drag two cells toward the dark, then it must be fought or driven
off — dangerous to one pawn, not a base threat. The tell is real and learnable: no piip
sparks, no breathing pulse (its glow is steady; every living lamp in the biome
breathes — §6.2's ticker becomes a gameplay read), and thessmoss dead in a ring around
it. Decisions: check before you harvest; light your approach; or farm the vaulisk
itself — killed, its lure organ is a small trophy glower, the one lamp that never
breathes, which the Compact will not have in their houses.

**(c) Engine.** One race + a **disguise state** (new C#, small): spawns as a plant-like
dormant thing carrying the false glower; swaps to pawn on proximity/harvest-job start.
The reveal-swap is the one novel mechanism; the lure reuses `RM_JobGiver_SeekGlow`'s
attraction in reverse (a glow that pulls). Trophy item is XML.

**(d) Interactions.** Teaches D2's system by inverting it; the breathing-glow
ticker (already owed) becomes diegetic information; gives the dark between the beams a
second resident beside the loohn so "the dark is the predator's" scales past one
species; and during lid-dark (D9) a floor full of scattered lights is suddenly a floor
where any of them might be lying.

**(e) RULED (§5, C3).** In — one per map at most, the tell always readable: the biome
earns one liar exactly because everything else is honest, and it must never become
common enough to make the colour grammar untrustworthy.

### D5 — The light famine: the beams walk away

**(a) Fiction.** The skylights drift over **about a week** (owner ruling, superseding
the sheet's years-scale). That is not scenery — it is the biome's landlord. The well
your kelp reaches for, the gold your farm was priced by, the water your nets stand in:
in a week it can be somewhere else, and the dark that arrives where it stood is not
empty. Ban 5 was always a danger ruling wearing a real-estate hat.

**(b) In play.** The standing clock every other danger stands on. A shaft closing over
a player's ground is a slow, fully legible catastrophe: the rim dims over a day or two
(the pale new-growth ring above thickens — a sky-read), the pallu thin out, the kelp
stand starts dying, the fishing water fades, and then the cells go dark — and dark
cells are the loohn's ground and D2/D4's habitat. The early game is CHASING the light
(the brief's own line): pack the field, move the chained cages, follow the gold. The
mid-game answer is the bank works (immobile, current-fed, light-independent wealth) and
the late-game answer is growing your own (sun-spheres) — at which point D2
re-prices that answer. The famine is never a raid and never sudden; it is rent.

**(c) Engine.** Extends the already-owed skylight-drift `MapComponent` (content drop
§6.3): shorten the timer to ~a week, add the rim-dimming warning stage and a letter.
Add **predator dark-gating** (small C#): the loohn's hunting-ground preference reads
unlit cells, so closure hands territory to it mechanically, not just in prose.
Everything else is already owed by the content drop.

**(d) Interactions.** Prices the skylight-rights economy (a right expires with the
shaft — ruled); feeds D1 (panes shed at closing wells); hands the loohn its dark frontier;
makes the chained/walkable cage fields the designed answer (mobile farming exists
BECAUSE the light moves); and the gardener event (whale sequence) firing a drift is the
one place a danger has a face.

**(e) BENCH position.** Not new work — a re-parameterisation of owed work plus one
small gating comp — but it must be named as a DANGER in the sheet's register, because
it is the one that shapes a whole playthrough.

### D6 — The undersurge: the river in flood

**(a) Fiction.** The dry rivers breathe. Some days — after a bloom above the lid, after
the gardener passes, for reasons the well-keeper charts and does not explain — the
heavy water comes down harder: the channels run wide, the current climbs the banks past
the stake-line, and for a day the richest ground in the sea belongs to the river again.
The Compact's stakes are set where they are because of the surge, not the calm.

**(b) In play.** A weather-scale event (a day or so): current strength up, and the push
zone **widens one to two cells past the stake-line onto the inner bank** — exactly the
strip where the murrgrave is thickest, the silt is sown, and the bank works stand. The
tells precede it by hours: every sennefan snaps to alignment, the murrol vanish
upstream, veil-fall litter on the bed visibly accelerates, the stake lamps swing (an
effecter). Decisions forced: pull harvest crews off the banks, finish the half-built
bank-works job or abandon the site, and — the sharp one — anything STORED on the inner
bank starts to drift. The bank works themselves (buildings) hold; the people and stock
around them do not. The richest ground being one step from the killer is the ruled
coupling; the undersurge is that coupling given a tide, so the step MOVES.

**(c) Engine.** Extends the owed current `MapComponent` (content drop §2.2): a
strength/width multiplier driven by a `GameCondition` `RM_Undersurge`; the widened zone
is derived from the stored flow grid, no second grid. Tells are effecters + a letter.
**No new system** — a parameter storm on the one movement system already owed, which is
why it belongs in `TWILIGHT_CHANNEL_CURRENT_1`'s scope, not a new item.

**(d) Interactions.** This is the bank-works coupling extended, per the brief: the
anchor prize is immobile, so the danger comes to IT. Feeds D7 (surge days are how
colonists end up at the sink); interacts with cages (a cage chained over the bed is
untouched — the surge is the cage's advert); the Compact's cast reads it coming (the
net-widow's one warning, the well-keeper's chart) so talking to the houses has survival
value.

**(e) BENCH position.** Fold into `TWILIGHT_CHANNEL_CURRENT_1` as a required phase-2
bar, not a separate mechanism — the current without its flood is a lesser danger and a
lesser reason the stake-line exists.

### D7 — The sink: where the river takes you

**(a) Fiction.** Every channel ends somewhere lower. The sink is a basin at the low end
— dark, far from any well, floored in everything the river ever took: litter, panes,
shells, stakes, and the sea's patient scavengers. A pawn carried the whole way arrives
alive, cold, half-buried in silt, in the dark — in the loohn's parish, at the end of
the map from home.

**(b) In play.** This is the ruled open question folded in as danger design. Carried to
the sink, a pawn takes **`RM_Hediff_Sunk`** — downed-adjacent: consciousness and moving
crushed, a slow severity ramp (silt, cold, exhaustion), death in a day or two if
unrecovered. The rescue is the set piece the mechanism was always pointing at: an
expedition into the biome's worst ground — the dark between (the loohn's and D4's
habitat), possibly during the surge that caused it (D6), into the liar's country. Getting
your colonist back is a story every single time, and the Mod Setting ladder makes it
harsher for those who want it: default *recoverable*; harsher *recoverable-but-injured*
(permanent lung/frostbite-analog scarring); harshest *lost* (the pawn is gone, a
death-letter in the river's register).

**(c) Engine.** The sink basin is placed by the owed channel genstep (flow grid already
knows its low end). The hediff + drop-at-sink is small C# inside the current
`MapComponent`'s existing "where does the carry end" question — it was always going to
need an answer; this is the answer. Rescue is vanilla (`JobDriver_Rescue`, with the
content drop's noted verify on moving targets — at the sink the target has stopped).

**(d) Interactions.** Terminates D6's carries; sited in D5's dark (a sink is definitionally
far from the wells — high ground gets the light, low ground gets the river); the picked
wreck and the Compact's ford-stones both read as the sink's history; and the net-widow's
whole characterisation is this mechanism with a face.

**(e) RULED (§5, C1).** Recoverable by default, with the harsher Mod Setting ladder —
the Grey's encasement precedent (recoverable, dangerous object-state) matched.

### D8 — The laden deck: the sky lands on your ship

**RULED at the sitting — ship danger is IN, and the owner replaced the slow-fouling
draft with a sharper mechanism.** Owner, typed, 2026-09-26: *"Yes. The grey sea should
crystallize the hull, freeze doors shut. twilight drops sky panes on the ship that need
to be cleared off."* ⇒ Each sea claims a parked hull in its own register: the Grey
encases (crystallising hull, doors frozen shut — owed to the Grey's pass), and the
Twilight **buries the deck in veil-fall**.

**(a) Fiction.** The ship sits under a shedding sky. Panes settle on the hull the way
they settle on the floor — and a deck under veil-fall is the most beautiful thing that
can happen to a spacecraft, translucent blue-green sheets catching the beams, right up
until the day you need to leave. The ship is the only way back. The sky knows where it
is parked.

**(b) In play.** While the ship sits on the floor, veil-fall accumulates on it — D1's
pane events and the ordinary shed land on the hull's footprint as visible pane things;
the spectacle IS the gauge. **Launch requires a cleared deck**: a clearing job per pane,
each yielding the harvestable pane material (the sea pays you for evicting it). ⛔ Never
a stranding: panes DELAY departure behind a job the colony can always do; they never
disable the engine and never fire during an emergency launch already in progress — the
never-strand guarantee stays a binding bar on the item.

**(c) Engine.** Simpler than the fouling draft: no severity float, no hull-art staging.
Panes are things landing on ship-footprint cells (D1's skyfaller, unmodified); a
launch-gate check counts panes on the footprint; the clearing job is near-vanilla
(haul/deconstruct-shaped). Mod Settings: accumulation rate, off.

**(d) Interactions.** Rides D1 wholesale — floor and deck are ONE pane system; a long
stay reads on the hull at a glance; heavy shed before lid-dark (D9) loads the deck at
the worst time; the picked wreck acquires its second reading — a ship nobody cleared,
generations on; and the Grey's crystallisation twin makes ship-claiming a cross-sea
grammar: every sea touches your ship in its own voice.

**(e) BENCH position.** Better than the draft in every direction: cheaper (a launch
gate inside D1's system, no new comp), prettier, and coupled to work already owed.

### D9 — Lid-dark: the day the sky goes out

**RULED (§5, C7): lid-dark has no timer — it falls when the gardener's passes align.**

**(a) Fiction.** The sky goes out because something vast is overhead: the gardener
working a long seam of the lid, the waveglass thickening behind it after a heavy shed
— and for a day the gold does not come down. No
beams. No moving patches. The whole sea runs on its own small lights, which is the
Twilight remembering what every other biome on this planet already knows about the
dark. The Compact bars no doors and lights every lamp, and the children are kept in.

**(b) In play.** A rare weather (the content drop's lighting-only set, one step past
`RM_TwilightOvercast`): every skylight at ~0 for ~a day. Fishing in the shafts stops
(the water is dark), kelp pauses, and the map's entire economy of visibility inverts
onto the player's handful of lamps, while D2's grazers and D4's liar work a floor where
scattered gold lights can no longer be assumed honest. Not damaging in itself; it is the amplifier weather
that makes the biome's whole danger grammar play at once. The morning after, the beams
return — moved (a drift check fires), because the lid healed differently than it was.

**(c) Engine.** One `WeatherDef`, triggered from the gardener-passes incident (a
fraction of passes escalate to lid-dark — ruled cadence, no commonality-table timer) +
the skylight ticker already reading current weather (content drop §7.1 built exactly
this hook for `RM_TwilightSilt`). The drift-on-exit is one call into D5's component.
**No new C#.**

**(d) Interactions.** The showcase of the set: D2 doubled, D4 at its most credible, D5
advanced a step at dawn — and the beauty holds, because a floor lit only by living
light is the content drop's §6.1 rule made total. It now deepens the gardener event
instead of running beside it: the whale-shadow hour is the preview, lid-dark is the
feature, and both wear the same face.

**(e) BENCH position.** Ship it with the weather set — it is nearly free and it is the
single best demonstration that the Twilight's danger comes through its beauty.

## 2. Interaction map

One table, existing system × danger, so a builder can see the mesh and a reviewer can
see nothing double-spends:

| existing system | which dangers touch it | how |
|---|---|---|
| **skylight drift (~a week)** | D1, D5, D9 | closing wells shed panes; drift IS the famine; lid-dark fires a drift at dawn |
| **chained cage fields / walkable lights** | D2, D5 | grazers eat them; mobility is the designed answer to the famine |
| **cultivated light (noothelm / hoolimbre / sun-sphere)** | D2, D4 | the suulk's meadow; the thing the vaulisk counterfeits |
| **bank works + river current (ONE piece, ruled)** | D6, D7 | the surge brings the river to the immobile prize; the sink is where a mistake on the bank ends |
| **veil-fall / shed panes** | D1, D6, D8, D9 | the pane event is a strike; litter accelerating on the bed is the surge's tell; panes bury the parked deck; heavy shed precedes lid-dark |
| **the clinging layer** | D4 | no-piip-around-it is the vaulisk's tell |
| **whale sequence (frenzy hour)** | D5, D9 | gardener passes can fire a drift, and lid-dark itself fires from the passes (ruled) |
| **the loohn (the ONE existing predator)** | D5, D7, D9 | never buffed, never multiplied — every entry makes the EXISTING predator matter more by handing it dark ground |
| **ship-only access (RM_SeaDiveHatch)** | D8 | the only entry allowed to touch the ship, behind a never-strand bar |
| **Compact houses / cast** | D2, D4, D6 | decoy stakes, the taught tell, the surge warning — the Compact is the danger's TEACHER, never its source (ban 4 intact) |

What is deliberately NOT in the roster: no new apex predator (the loohn stays the one
true predator; D2/D4 are a grazer and an ambusher, below it), no hostile faction or
raid-analog of any kind, no toxin/plague axis (the Scald and Miasma own body-clock
danger), no encasement or burial (the Grey's), and nothing that touches or reaches the
waveglass — every danger arrives FROM the sky or the floor, never at it.

## 3. The river-sink question, folded in

Discharged inside D7: the sink is designed as a **recoverable "sunk" state at the
channel's low basin** — a dark-country rescue set piece rather than a coin-flip death —
with a three-step Mod Setting ladder (recoverable / recoverable-with-scarring / lost).
RULED at the sitting (§5, C1): recoverable default, with the ladder. Everything D7 needs
lands inside `TWILIGHT_CHANNEL_CURRENT_1`'s existing scope (the carry always needed an
end state; this is the end state).

## 4. Engine summary — what owes new C#

| danger | new C# | size | shared with |
|---|---|---|---|
| D1 pane strike | skyfaller subclass only if stock can't carry the footprint | tiny–none | whale-rain beat 4 art language |
| D2 suulk | **`RM_JobGiver_SeekGlow`** (find/path/feed on brightest glower) | small | D4 — build once; the Grey/Scald attraction later |
| D3 (cut) | — the attraction mechanism is redirected to the Grey and Scald | — | future Grey/Scald danger passes |
| D4 vaulisk | disguise→pawn reveal swap | small | trophy item is XML |
| D5 light famine | predator dark-gating comp; drift re-parameterised to ~a week | small | drift component already owed (§6.3) |
| D6 undersurge | none beyond the owed current component — a condition-driven multiplier on it | — | `TWILIGHT_CHANNEL_CURRENT_1` |
| D7 sink | `RM_Hediff_Sunk` + carry-terminus in the current component | small | same item |
| D8 laden deck | launch-gate pane count + clearing job; panes ride D1's skyfaller | tiny–small | D1 — one pane system |
| D9 lid-dark | none (1 WeatherDef + existing hooks) | — | weather set (§7.1) |

Net-new C# systems: **two** (`RM_JobGiver_SeekGlow`, the vaulisk reveal); the deck's
launch gate is a check inside D1's pane system, and everything else rides components
the content drop already owes. Items filed from the sitting:
`TWILIGHT_DANGER_LIGHTWEB_1` (D2+D4 — one glow-brain, two faces),
`TWILIGHT_PANE_STRIKE_1` (D1+D8 — floor and deck are one pane system), and
`GREYSEA_SHIP_CRYSTALLISATION_1` (the Grey's half of the typed C5 ruling); D5/D6/D7/D9
fold as bars into the light-economy, channel-current and weather work already owed.

## 5. Rulings — 2026-09-26 sitting, all seven cards answered

Recorded on `TWILIGHTSEA_FLOOR_PASS_1`. C2 and C5 are owner-TYPED (quote-eligible);
the other five are decisions taken by question card — our wording, clicked, never to
be passed as `--owner-said`.

- **C1 — the sink:** recoverable default, with the harsher Mod Setting ladder (card).
- **C2 — light calling the sea: CUT for the Twilight.** Owner typed: *"Actually
  attacking light makes more sense in the Grey and Scald (dark on the bottom) than it
  does on the beautiful lighted Twilight floor with lots of lighted everything."*
  The attraction mechanic is redirected to the dark-floored seas (D3's slot records it).
- **C3 — the liar:** in — one vaulisk per map at most, the tell always readable (card).
- **C4 — the suulk's diet:** the sun-sphere too, slowly and loudly (card).
- **C5 — the ship: danger touches it, redesigned.** Owner typed: *"Yes. The grey sea
  should crystallize the hull, freeze doors shut. twilight drops sky panes on the ship
  that need to be cleared off."* ⇒ D8 is the laden deck; the Grey's pass owes hull
  crystallisation and frozen doors (`GREYSEA_SHIP_CRYSTALLISATION_1`).
- **C6 — the pane:** it can kill outright; the ~15 s shadow warning is the fairness (card).
- **C7 — lid-dark:** tied to the gardener — no timer; the sky goes out because
  something vast is overhead (card).

---

*Nothing above amends the frozen sheet until its sitting; the sheet's danger register
(§9's "motion means life") gets the one-line addendum there, on his word.*
