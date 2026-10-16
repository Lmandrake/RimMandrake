# The Forge: candidates for the crescendo anole's empty slot (Phase 0 P3, Q3)

Owner ruling, by card 2026-10-15 (Q3 option A): draft two or three new Forge creatures for the small ground animal slot
that the crescendo anole (`AA_CrescendoAnole`, RM_TheForge 0.5) leaves when Alpha Animals goes. **You pick one on the
Phase 0 sheet.** None of them is ported or cast, and the Forge roster is unchanged until you pick.

All three:
- are invented, so they live in the franchise-free `RM_` tier, Forge only (one biome);
- pass the Forge's admission test (`design/Jawa/worldbuilding/biomes/the_forge.md` §4: *lives in the flash-interval,
  or in the sky*) and its bans (§6: nothing in the lava, no fur or lush register, no ordinary rain);
- take the Forge name accent (`forge_bedazzle_cast_2026-09-29.md` §0: `j`/`dh` front, back vowel, vent-closing coda);
- carry their own palette anchor, distinct from the dhokkur (rain-slick black), julmox (ash and moss green), jossur
  (scour-rust), dhuvvox (ember-fleck) and fleet flier, per your "Needs more variety" ruling;
- have a first render filed (3 facings, east master, realistic painted natural-history style, no donor pixels):
  rows in `design/RimMandrake/forge_slot_candidates_art_2026-10-15.json`, jobs `forgeslot_<name>_v1_{east,south,north}`.

Name checks (2026-10-15): `git grep -i` over `src/ design/ infrastructure/state/` finds 0 hits for each name
(probe `korrum` finds 121, so the search can see); `check_pseudo_sw_name.py` passes all three against 266 canon
entries. I dropped two earlier drafts that sat too close to existing names: `jakkur` (we have `jakkir`) and
`dhurrosh`/`dhollosh` (we have `dhurrox` and `RM_Dhollock`).

Duplicate check: I found no existing creature that hunts the dhuvvox, licks the salt crust left by the rain, or eats
the Contagion's dead ring. The nearest is a generic thin-legged scavenger in the Abyss (`RM_Lirrith`), which is why candidate C is defined by *what* it eats and *when*, not just by being a scavenger.

---

## A. Jobbosh (`RM_Jobbosh`): the dhuvvox-eater

> Where the dhuvvox run, the jobbosh follows: a forearm-long ground-runner in glazed ochre scales that waits out the
> still heat wedged deep in a cooling crack, and comes out only when the rain does. For the two hours the skirts
> glitter it eats nothing else, scooping the swarm off the wet rock faster than it can reseal, and one burst feeds it
> through the next three. The old hands read it as the dhuvvox's own warning: if the jobbosh are out, the rain is
> minutes old.

- **Role:** small predator (insectivore). The step above the dhuvvox in the food pyramid. Prey for the jossur.
- **Size:** body ~0.35, drawSize ~1.0. Forearm-long, low, quick.
- **Why it fits:** it lives entirely in the flash-interval and gives the dhuvvox clock a hunter. It is the closest of
  the three to the anole you are replacing (a small lizard-shaped animal), without the swelling. Palette: vent-sulphur
  (ochre, chalk-yellow, umber).

## B. Dhoggur (`RM_Dhoggur`): the salt-licker

> Every burst the mountain boils off leaves a skin of salt behind on the rock, and the dhoggur lives on that skin. It
> spends the heat sealed in a pumice burrow under the ash, and when the rain has flashed away it shoulders up through
> the steam on a shovel snout to rasp the fresh white crust off the stone before the next burst washes it clean. It is
> slow, squat and armoured like a kiln brick, and the jossur take more of them than of anything else that walks.

- **Role:** small grazer (it eats the mineral crust, not the moss, so it does not compete with the julmox). The jossur's
  main ground prey.
- **Size:** body ~0.45, drawSize ~1.2. Knee-high, squat, slow.
- **Why it fits:** it uses something the frozen sheet already has but nothing eats: the boiling rain flashing to steam
  on the rock. It feeds at the drying edge of the flash-interval and lives in burrows. Palette: salt-white crust over
  slate.

## C. Jurrox (`RM_Jurrox`): the ring-gleaner

> At the skirts the Contagion pushes in and dies, and the jurrox are why the ring stays fresh instead of piling up. A
> high-stepping, tong-snouted gleaner that touches the hot ash as little as it can, it works the dead red creep at a
> trot in the minutes after each burst, when the scald has softened it and killed everything still living inside. It
> eats whatever the mountain has already killed, and on the Forge that is a great deal.

- **Role:** small scavenger (carrion eater). Keeps the corpse-ring clean.
- **Size:** body ~0.4, drawSize ~1.1. Shin-high on stilt legs.
- **Why it fits:** it ties the slot to the Forge's own lore (`the_forge.md` §4, the Contagion's corpse-ring) and to the
  heat: it eats only what the mountain has already sterilised. Palette: bruise-violet and ash, oxblood only at the snout.

---

**Not done, by instruction:** no def, no roster row and no Forge roster change for any candidate. Once you pick, the
pick is ported as plain XML into `src/RimMandrake/TheForge/` and replaces the `AA_CrescendoAnole` row at 0.5.
