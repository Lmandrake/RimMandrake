# Backlog: the big questions (2026-10-09)

The small ruling-blocked items were auto-decided and built with PROVISIONAL defaults (log:
`Transient/belt_autodecide_log_20261009g.md`). These are the ones that are genuinely yours: each one
changes what the player experiences, and the answers point in different directions. Each card is a draft
in plain words; the item it came from is in brackets at the end, for whoever enacts the answer.

---

## 1. The tiny living bolt in the Rust Cathedral: how does it get onto walls?

You described it as "a little button that flits around on walls and other surfaces". The game has no
creature that can stand inside a wall cell, so it has to be faked one of two ways.

- **It hops along beside walls and is drawn on the wall face.** It stays a real animal (can be hunted, tamed,
  counted). Costs: on open ground with no walls nearby it just looks like a tiny floor critter.
- **It is scenery that lives on walls, not an animal.** Looks right everywhere, jumps wall to wall. Costs: it
  can't be hunted or tamed and leaves the creature roster.
- **Real wall-walking.** Costs: the engine can only do this by letting every flyer, raiders included, pass
  through every wall. Not recommended.

**Recommendation: hop beside walls, drawn on the face.** It keeps the creature a creature, and it is one
small behaviour plus a drawing offset. *(RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1)*

---

## 2. Cracked Lands: who is the rival salvage crew when Star Wars is switched off?

After a flood recedes, a rival crew turns up to work the salvage beside yours. In the campaign they are
Jawas. In the franchise-free mod they need to be somebody.

- **An existing outlander or pirate-style faction, sent as visitors.** Nothing new to make or explain.
  Costs: they look like any other caravan, so the moment has no identity of its own.
- **A new small scavenger faction of ours.** A crew with its own look and name, reusable in other biomes.
  Costs: a faction, pawn kinds and art to make; a bigger build.
- **Drop the crew from the free mod; Jawas only in the campaign.** Cheapest. Costs: the free mod loses the
  event entirely, which goes against "the free mod must look the same, just without Star Wars".

**Recommendation: a new small scavenger faction.** The free mod is meant to stand on its own, and a salvage
crew is reusable wherever floods leave wreckage. *(CRACKEDLANDS_SALVAGE_CLAIM_CREW_1, Q1)*

---

## 3. Cracked Lands: when the rival crew talks to you, what are they offering?

- **A split of the salvage.** You agree, they take a share and leave peacefully. Simple and readable.
- **A toll.** You pay them silver or goods and they leave all of it to you.
- **A trade.** They open a normal trade window and swap for what they've already picked up.

Whichever you pick, they race you for the salvage if you refuse, and steal once relations collapse (already
ruled). How often they come is being set to a chance per flood as a provisional default.

**Recommendation: a split of the salvage.** It is the only one of the three that is about the salvage itself,
which is what the whole event is about. *(CRACKEDLANDS_SALVAGE_CLAIM_CREW_1, Q2)*

---

## 4. Cracked Lands: what does a talus clasp "prying cracks wider" actually do?

The talus clasp is a pale plant that roots against fossil-bearing rock.

- **Slowly turns the rock next to it into a fossil seam or rubble.** The plant visibly changes the cliff over
  time and gives you a reason to leave it alone. Costs: it changes map terrain, so it needs a setting and a limit.
- **More yield when you mine next to it.** You learn to mine where clasps grow. Costs: invisible until you mine.
- **Flavour only, in the description.** Nothing to build. Costs: the plant does nothing you'd notice.

**Recommendation: slowly turns rock into a fossil seam.** It is the one you can see happen, and fossil seams
already exist on this map. (This plant's art also still has to go to a review sheet before it ships.)
*(CRACKEDLANDS_THREE_HEIGHT_FLORA_1, Q1)*

---

## 5. Ozzik now has five found rites; the register's cap is four

Two Ozzik rites were picked by card on the same day (the Open Boast in the Warscar, the Ceded Room in the
Greentide), which takes him to five. Nothing has been cut.

- **Allow five for Ozzik.** Both rites get built. Costs: he has one more rite than any other god.
- **Cut the Ceded Room.** Costs: the Greentide loses its rite.
- **Cut the Open Boast.** Costs: the Warscar has no Ozzik rite, which was the reason it was put there.
- **Move one of them to another god.** Costs: the rite has to be re-themed.

**Recommendation: allow five.** Both were chosen deliberately and each sits in a different biome; the cap is
a guideline for balance, not a mechanic. *(WARSCAR_OPEN_BOAST_RITE_1, GREENTIDE_CEDED_ROOM_RITE_1)*

---

## 6. The FeverWood ant hive's third chamber, the kept guard: build it now or wait?

The ruling said to build the guard creature last, and to decide after playing a hive that already reacts
(notice, alarm, rally, hunt) whether it's still needed. The reacting hive is built.

- **Build it now.** A new larger creature stationed where corridors narrow, answering the hive's alarm.
  Costs: a new creature and its art, before anyone has played the hive.
- **Wait until you have played a reacting hive.** Costs: the hive stays at two of three chambers until then.
- **Drop the guard.** The reaction is the depth you chose as primary.

**Recommendation: wait until you've played it.** That was your own sequencing, and the guard costs a new
creature. *(FEVERWOOD_HIVE_GUARD_CHAMBER_1)*

---

## 7. The owner-quote guard can't see what you type mid-turn

The safety check that refuses invented owner quotes only reads messages from the start of a turn. When
you type something while an agent is working, and the agent quotes you, the check refuses it as forged.

- **Teach the check to read mid-turn messages too.** Your words work whenever you type them. Costs: a change
  to an authorization guard, which is yours to approve.
- **Leave it; agents record such words as "said mid-turn, not quotable".** Nothing changes. Costs: what you
  type mid-turn can't authorize anything until you repeat it.

**Recommendation: teach it to read mid-turn messages.** The guard exists to stop invented quotes, not to
ignore real ones. *(OWNER_SAID_GUARD_MIDTURN_BLIND_1)*

---

## 8. Titans: how does a titan get through a wall or a giant plant in its way?

Your ruling says a titan smashes through anything built rather than going round. Right now it only damages
what it brushes while already walking, so a fully walled-off lane stops it forever. (The Large Pawns mod's own
wall-breaking is switched off, as you ruled.)

- **It walks up to the nearest thing in its way and strikes it until it falls, then carries on.** Only things
  the crush rules allow are ever struck; it's a visible "approaches and smashes" moment. Costs: a new behaviour,
  about a half-day of work plus tuning.
- **Switch Large Pawns' wall-breaking back on for titans only, filtered through our crush rules.** Reuses a
  working behaviour. Costs: titans stop smashing whenever Large Pawns isn't installed.
- **Let titans path straight into breakable things and shove until they break.** Smallest change. Costs: smaller
  titans can stand against a wall for a long time before it gives.

**Recommendation: walk up and strike.** It works with or without Large Pawns and matches what you described.
*(TITAN_BREAKTHROUGH_CLEARING_1)*

---

## 9. The FeverWood ant hive on open ground: what makes it feel like a hive?

On rock the hive is now dug out properly. On open ground, though, a "dug" hive is just roofed floor with no
walls, so it reads as patches of roof you can walk into from any side.

- **Only put hives where there's rock.** Every hive is a real cave. Costs: fewer maps get one.
- **Raise natural rock walls around open-ground hives.** Looks like a cave anywhere. Costs: changes the map's
  ground around the hive.
- **A new hive-resin wall built by the ants.** Most flavourful. Costs: a new wall and its art.
- **Leave it open and call them "burrow mouths".** No work. Costs: the dungeon feel stays weak.

**Recommendation: rock sites first, rock walls when no rock site exists.** Both reuse ordinary rock, need no new
art, and every hive can only be entered through its tunnel. *(ANT_HIVE_REAL_GEOMETRY_1)*

---

## Engineering calls FOUNDRY is making itself (not for you; listed so nothing is hidden)

- **Very large canal networks (over 6,000 cells) don't pass liquid between their chunks.** FOUNDRY will raise
  the cap behind the existing setting after one in-game timing on a big network. Nobody has built one that size
  yet. *(FLOW_ORDER_EXTERNAL_INPUT_1 part 2)*
- **Some Warscar proofs set the state they claim to observe.** FOUNDRY will rewrite them one per sitting so they
  set only the input and watch the real ticks, starting with the floor-arming proof.
  *(WARSCAR_VALIDATION_FIDELITY_1 part d)*
