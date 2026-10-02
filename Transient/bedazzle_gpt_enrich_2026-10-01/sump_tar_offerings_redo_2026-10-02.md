# Sump tar offerings, redo (2026-10-02)

Item: `SUMP_BEDAZZLE_SITTING_1` (BENCH), turn 3 of the volley. Design pass, files only.
Rites: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6.

## 0. Brief and what changed

**His turn-2 words (ledger 2026-10-02T05:37Z):** Rite A, one thing of value thrown in the tar, *"lowers
heat, erases ownership as part of RimProperty (perhaps of something you still keep...), and lowers raid
frequency."* Rite B, *"one good thing and one hated effigy to Mob'Unloo brings about unfortunate
consequences on someone else, paid for by you."* On round 1's four: *"really poignant, but they're just
not hitting ... make it something a player on THIS map would care about."*

**Avoided, by design:** round 1's four rejected (threshold kept, pump's answer, weapon's quarrel, last
tool) and round 2's four already on the draft turn-3 card (beast turns over, pump backflow, empty stall,
grudge at table). Round 1's "pump's answer" sent the tar beast to a lottery-chosen station off-map;
offering 5 below is deliberately the opposite shape (aimed by the player, on this map, at a group that
is attacking him), and is flagged as the one to drop if he hears an echo.

🔴 **Finding: round 2 inverts Rite A.** He defined Rite A as protective: the colony pays to be hidden
(Heat down, claims wiped, fewer raids). Three of round 2's four put a Rite-A offering's consequence on
the colony itself (its pumps flood, its pen is ringed, its builds are cracked). And "grudge at table"
puts Rite B's consequence on the colony's own people, where his words say *"on someone else, paid for by
you."* This redo keeps his two shapes literally: **Rite A offerings buy protection from a Sump danger;
Rite B offerings point a Sump danger at someone else, and the colony pays in a Sump currency.**

**The rule each offering obeys:** the thing thrown in is something a Sump colony really holds and
misses (bitumen, a dig find, a vault's preserved stock, a disarmed era trap, solvent, the hide only
stillness wins); the consequence lands on a Sump stake (the tar beast, the dig lottery, the vault, the
dig traps, the skarrids). Laws kept: the offering is destroyed; nothing living or dead goes in; no
material reward; favour shows through events, told by the Narrator; nothing vanishes without a sign.

**What exists (searched before proposing, all under `src/`):** the tar beast's wake path
(`RUT_BeastBulge`, `CompWakeUpDormant`, `RM_CompBeastWakeRelay`; body owed by `SUMP_TAR_BEAST_BUILD_1`,
which also owes the dig and pumping wake causes); the dig lottery (`RM_CompWorkedLottery`,
`RUT_DigStratumTable`: traps weighted above era remains by ban 1, `trapWeightMultiplierPerStratum` 1.3,
an armed trap runs a fuse, `TryDisarmPendingTrap` is a high-skill check, failure detonates through
`GenExplosion`, success yields nothing); the tar vault (`RM_Comp_TarVaultSeal`: stops rot, extraction
needs solvent or the item comes up as `RUT_TarRuinedGoods`); RimProperty
(`GameComponent_PropertyLedger`: `TryGetRecords`/`RecordClaim` only, decay computed lazily from age in
`ClaimDecay.cs`); the solvents (`RUT_WeakTarSolvent` from `RUT_ThrummelSeepwax`, the only homegrown
thing that lets go of tar); skarrids (`RM_Skarrid`, still ambusher at the glass-reach margins, prized
hide `RM_SkarridHide`); bitumen and korveth pitch (`RUT_Bitumen`, `RM_KorvethPitch`, *"half the Sump's
economy"*). Derricks and pumps exist only in the sheet (`the_sump.md` §7b), not as buildings, so no
offering below depends on one.

**Shared machinery (all six):** one `RitualOutcomeEffectWorker` per rite in `mandrake.rut.rites`
(new C#, as every Salvation rite is). It reads the offered Thing's def or category and dispatches to
that offering's effect, so an offering is a row in a small table, not a new ritual. The value floor and
each effect's duration are Mod Settings numbers.

## 1. Give Back the Pitch (Rite A)

- **Throw in:** a stack of bitumen or korveth pitch worth at least the rite's value floor. The colony's
  own product, the thing it pumps, renders and sells.
- **What happens:** for one season (15 days, a setting), every tar bulge on this map sleeps through the
  colony's industry: building within 20 cells, digging and pumping no longer wake it. **An explosion
  still does**, and the Narrator says so. The mice keep detouring around the bulge, so the danger stays
  visible; only its temper changes.
- **Why a Sump player cares:** the bulge is the one thing that makes good land unusable. It sits on the
  flat glass the colony wants for walkways, moats and a second shaft. A season of quiet is a building
  season: the colony gets its moat poured or its shaft sunk next to the giant, and then the lull ends
  and everything it built is sitting next to a beast that will wake on the next spade. The pay-off and
  the trap are the same act. It is also the sheet's own line, *"everyone at the derricks knows which
  ponds you don't pump deep"*, made a bargain: give back what you took and it lets you take more.
- **Mechanism:** a `GameConditionDef` `RM_TarLull` on the map (shows its days left), and a Harmony
  prefix on the bulge's wake path (`CompWakeUpDormant` activation via `RM_CompBeastWakeRelay`) that
  refuses construction, dig and pump causes while the condition runs and lets an explosion through.
  New C#, small. Rides `SUMP_TAR_BEAST_BUILD_1`, which adds the dig and pump wake causes it suppresses.
- **Readable signs:** the pitch sinking slow; a letter, *"The tar has eaten. It will sleep through your
  work until [date]."*; the condition in the map's list; at the end, a ring of filth around the bulge
  for a day, the sheet's rising bubble.
- **Build cost:** S (after the beast item).

## 2. The Fuse the Tar Drinks (Rite A)

- **Throw in:** one find the dig shafts brought up (a sunken machine, a sealed casing, an era relic,
  once the finds roster ships real ThingDefs; today's placeholder chunks are excluded by a value floor).
  The tar's own prize, given back unopened or unsold.
- **What happens:** the next three era traps the colony's shafts roll on this map arm as usual, the
  click is heard, and then the fuse goes out: the tar has drunk it. The trap resolves as a harmless
  sprung lump. Ban 1 is untouched (traps are still rolled first and as often; they just do not go off).
- **Why a Sump player cares:** *"every dig is treasure or a click."* Digging is the Sump's core play, and
  the click is its worst moment: a fuse, a high-skill disarm, a detonation in the shaft. Three safe
  clicks let a colony dig deep without its best crafter on standby, or push a shaft past the depth it
  was afraid of. The price is a real find, and the next three digs may bring up something worse.
- **Mechanism:** a `MapComponent` counter set by the outcome. A Harmony postfix where
  `RM_CompWorkedLottery` arms a trap row: while the counter is above zero, resolve it as disarmed
  (the existing `TrapDisarmResult.Disarmed` path), decrement, play the click and a hiss. New C#, small.
- **Readable signs:** the click, then a hiss and a puff of tar from the shaft; a Narrator line naming
  which of the three it was; the counter shown on the dig shaft's inspect pane.
- **Build cost:** S.

## 3. The Vault Forgets (Rite A)

- **Throw in:** one thing of value, any (the rite's normal price).
- **What happens:** every foreign claim on everything sealed in the colony's tar vaults is wiped: old
  owners, battle-loot origins, rival purchases. What the tar keeps is the colony's. This is his
  *"erases ownership ... perhaps of something you still keep"* read on this map: the thing you still
  keep is what you keep **in the tar**.
- **The Sump half of it (proposed, optional):** while sealed in a vault a claim does not decay either.
  The tar keeps everything perfectly, intentions included, so a stolen masterwork hidden in tar stays
  just as hot as the day it went in. A colony that hides loot in its vault is storing evidence; the
  Sinking is the one thing that clears it. Without this half, the offering is still answer A to card
  Q2 ("which kept thing is cleansed"): the vault's contents.
- **Why a Sump player cares:** the vault is the Sump's larder and safe, and the only place a Jawa
  colony can sit on stolen goods out of sight. It turns the vault from storage into a laundering
  ritual: steal, seal, throw, and the stolen goods come out clean (with a solvent, as always).
- **Mechanism:** the new ledger call Rite A already owes (`GameComponent_PropertyLedger`: clear the
  records of other claimants on a Thing), run over each Thing held by every `RM_Comp_TarVaultSeal`
  building on the map. The optional half is a check in `ClaimDecay` that does not advance a claim's age
  while its Thing sits in a sealed vault (a stored "sealed since" tick on the record). New C#, small to
  medium. Answers card Q2 in one stroke.
- **Readable signs:** a letter listing each cleansed item and whose claim was wiped; vault inspect text
  reads *"no other claim"* on each item.
- **Build cost:** S (M with the frozen-decay half).

## 4. The Kept Intention (Rite B)

- **Throw in:** the good thing is **a disarmed era trap** the colony's diggers won (this needs a small
  new item: a successful disarm today yields nothing; it would yield the trap as a valuable, heavy
  thing). The effigy names a faction, as ruled.
- **What happens:** the next time that faction raids, sieges or drops onto a map the colony holds,
  the tar's kept trap goes off under their gathering point a few hours after they arrive: an era
  explosion where they stage, telegraphed by a click the colonists can hear. The sheet's line,
  *"the tar preserves everything, including intentions"*, pointed at someone.
- **Paid for by you:** the trap was a prize (sale value, and the obvious thing to re-arm as your own
  defence once traps are placeable); and the explosion is on **your** map, so a raid that stages near
  your walls takes your walls with it.
- **Why a Sump player cares:** the click is the thing every Sump digger dreads; this is the colony
  learning to aim it. It makes the most frightening find on the map into its strongest curse.
- **Mechanism:** the outcome writes (faction, explosion def) into a `WorldComponent`. A Harmony postfix
  on `LordMaker.MakeNewLord` catches that faction's next hostile lord on a player map, reads its staging
  cell, and schedules `GenExplosion.DoExplosion` with the trap's own parameters after a delay, with a
  click sound and a ring mote at the cell for the last hour. New C# (medium) plus the disarm-yield item.
  If the ruled "arrive tarred" curse is also cast on that faction, both apply; they do not stack on one
  effigy.
- **Readable signs:** the effigy and trap sinking together; on arrival, the Narrator: *"Something under
  their camp has been waiting a long time"*; the ring mote; the click; the crater.
- **Build cost:** M.

## 5. Wake It Under Their Camp (Rite B)

- **Throw in:** the good thing is the colony's whole store of tar solvent (all of it, at least the value
  floor). The effigy names a faction.
- **What happens:** the next time that faction sieges or raids this map and builds anything (a siege
  camp, sandbags, a mortar), the nearest tar bulge wakes and goes for **their** buildings, not the
  densest cluster (which is the ruled default, and is usually yours). It eats their camp, then sinks at
  a new address, as ruled. Off-map, nothing happens.
- **Paid for by you:** twice. The solvent is gone, so every colonist the woken beast's trail tars stays
  tarred until the thrummels can be raided again for seepwax. And the beast is awake on **your** map:
  its trail lays tar across your ground on the way, a building in its path still goes, and where it
  sinks may be closer to home than where it rose.
- **Why a Sump player cares:** the tar beast is the giant he ruled the full station-eater for, and
  nobody fights it. This is the one way a colony can make it work for them, and it costs the one
  substance that undoes the tar. Not round 1's "pump's answer": the player aims it, on this map, at a
  group already attacking him, and pays with his own ground.
- **Mechanism:** a `WorldComponent` flag (faction). When that faction's lord on this map spawns a
  building, the outcome wakes the nearest `RUT_BeastBulge` through its existing wake call and sets the
  tar beast's target to that lord's buildings (one field on the beast's job, which
  `SUMP_TAR_BEAST_BUILD_1` writes anyway). If the map has no bulge, the curse waits for one. New C#,
  medium; depends on the beast item.
- **Readable signs:** the effigy sinking; when they build, the mice break and run *away from their
  camp*; the bulge's bubble; the Narrator names the camp it is heading for; the tar trail and the mounds
  where their buildings stood.
- **Build cost:** M (after the beast).

## 6. The Margin Rises (Rite B)

- **Throw in:** the good thing is skarrid hide (`RM_SkarridHide`, *"the prize for beating it at its own
  game of stillness"*), at the value floor. The effigy names a faction.
- **What happens:** the next group of that faction to cross this map (raid, caravan, visitors) finds
  skarrids rising along their path: a handful of still ambushers already half-sunk at the glass-reach
  margins they will walk past, seams opening as the column comes by. Skarrids take lone stragglers and
  never chase far off the black (their own description).
- **Paid for by you:** the skarrids stay. They are wild animals on your map after the visitors have
  gone, lying in the same margins your haulers and dig crews use, and they will take a lone colonist as
  readily as a lone raider. The colony traded its prize hide for more of the thing that wins it.
- **Why a Sump player cares:** skarrids are the Sump's quiet killer of lone pawns, and the margins are
  where the colony works. It makes the map's own ambusher a weapon, and the colony has to live with it.
- **Mechanism:** the outcome writes the faction to a `WorldComponent`; an `IncidentWorker` fires when
  that faction's next lord enters the map, computes its route edge, and spawns `RM_Skarrid` on margin
  cells (tar-adjacent, within N cells of the route), using the existing skarrid ambush behaviour. No
  faction-targeted AI: they take whoever comes nearest. New C#, small to medium.
- **Readable signs:** the mice abandon the route an hour ahead; skarrid bulges are visible on the
  margins (they are a "bulge slightly too small", so a watchful player sees them); the Narrator names the
  group.
- **Build cost:** S to M.

## 7. Draft question card

Header `Tar offers` (10 characters). Multi-select. Above the card in chat, BENCH explains in full: the
two rites as he ruled them, that each offering is one specific thing thrown into the tar that decides
what the rite does on this map, and that none of these come back.

*You asked for offerings a player on THIS map would care about. Rite A (one thing of value) hides you;
these A offerings hide you from the Sump itself. Rite B (a good thing and an effigy) hurts someone else,
paid by you; these B offerings aim the Sump's own dangers. Which should exist?*

| Option | Text (≤25 words) |
|---|---|
| **Give back the pitch** *(Rite A, recommended)* | Throw in a stack of your tar pitch: for a season the sleeping tar beast ignores your building and digging, though explosions still wake it. |
| **The vault forgets** *(Rite A)* | Throw in anything valuable: every old owner's claim on what you keep sealed in your tar vaults is wiped clean. Steal, seal, throw. |
| **The kept intention** *(Rite B)* | Throw in a disarmed ancient trap with a faction's effigy: it explodes under their next camp on your map, which may be near your walls. |
| **Wake it under them** *(Rite B)* | Throw in all your tar solvent with a faction's effigy: their next siege wakes the tar beast against their camp, tarring your ground on the way. |

Not on the card, kept here for the next round: **The fuse the tar drinks** (three safe dig traps; strong
and cheap, held back because the finds it costs are still placeholder chunks) and **The margin rises**
(skarrids along their route; good, but the weakest of the six on "someone else": the colony ends up
living with the curse longest).
