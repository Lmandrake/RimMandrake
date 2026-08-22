# The lightsaber armour-penetration reading — it is 0%, and the offline dump was right

**CHECK, 2026-08-22 ~08:15 PDT. 578 mods, live quicktest map.** The item asked for one
number off the in-game info card. Here it is, three times.

## The reading

Spawned each on the ground, selected it, opened `Verse.Dialog_InfoCard` through the inspect
pane's info button, and read the card the game drew:

| lightsaber | Melee damage per second | **Melee armor penetration** |
|---|---|---|
| `Force_Lightsaber_BuildYourOwn` | 43.56 | **0%** |
| `Force_Darksaber` | 61.88 | **0%** |
| `Force_Lightsaber_Crossguard` | 40.26 | **0%** |

🔑 **The card is computing, not blank** — three different DPS figures, plus market value
$2000, mass 2.00 kg, ingredients, and `Source: Star Wars : The Force - Lightsaber`. It
simply reports armour penetration as zero.

⇒ **The offline reading was correct.** `Lightsaber.dll` exporting `AdjustedArmorPenetration`,
`GetArmorPenetration` and `get_ArmorPenetrationInt` does **not** raise the number the game
displays. The item's more-likely outcome — "an ordinary-looking number that tells BUILD the
offline reading was wrong" — is not what happened.

## Two caveats, stated rather than buried
- ⚠️ **Read from the ground, not from a wielder's hand.** The item's criteria says "equip any
  lightsaber"; I did equip one on a colonist (`jawa/pawn_gear`, confirmed held), but the
  gear tab exposes no actionable info-card control through the bridge, so the equipped card
  could not be opened. If the mod's C# reads the wielder (skill, Force, psyfocus), a held
  saber could differ. **UNMEASURED**, and it is the one gap in this reading.
- ⚠️ Three sabers of fourteen. `BuildYourOwn` was deliberately not trusted alone — it is a
  craftable template and could have been a blank — which is why the Darksaber and the
  Crossguard were read too.

## What BUILD may want to know, offered not decided
`setting_physics.md` **L3** is load-bearing: *"Anything a person can wear is defeated
instantly. Personal armour is thin by necessity… There is no wearable plate that stops a
lightsaber."*

At **0% armour penetration** the engine applies the target's full armour rating against the
blow, so a stormtrooper cuirass (Sharp 1.18) or a warcasket shell reduces a lightsaber
exactly as it reduces a sword. ⇒ **L3 is doctrine, not mechanism, on this install.** Whether
that matters is BUILD's and DECIDE's call — this item only owed the number.
