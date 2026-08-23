## Spec

Read Armor Penetration off a lightsaber **held by a colonist**, not one lying on the ground.

The closed item `lightsaber-…-6a91d3` was verified **pass** and closed at `cc9dcb93`. Its own
capture, `observed/2026-08-22/lightsaber_ap/README.md:27-31`, says the
item's literal criterion was not met:

> *"The item's criteria says 'equip any lightsaber'; I did equip one on a colonist
> (`jawa/pawn_gear`, confirmed held), but the gear tab exposes no actionable info-card
> control through the bridge, so the equipped card could not be opened. If the mod's C#
> reads the wielder (skill, Force, psyfocus), a held saber could differ. **UNMEASURED**,
> and it is the one gap in this reading."*

⇒ **The number in the record was read from a ground-spawned weapon.** That is the right
answer only if the mod computes AP statically. Nobody has established that it does.

⛔ **The closed item is not reopened** — this is its successor, linked by `caused_by`. The
old record stands as what was actually measured.

## Watch out

- 🔑 **The blocker is a BRIDGE capability, not a game question.** The gear tab exposes no
  actionable info-card control, so the route is either a new companion tool that reads the
  equipped weapon's computed stats, or RimWorld's own inspect pane driven another way. If it
  is the former, `skills/rimbridge-companion` covers writing it and **BUILD owns the DLL** —
  file it rather than writing C# yourself.
- ⚠️ **A ground reading and a held reading agreeing does NOT prove the mod is static.** It
  proves it agreed for that saber, that pawn, that skill level. If they agree, say which
  pawn and which saber; if they differ, that is the finding.
- ⚠️ Three sabers of fourteen were read, and `BuildYourOwn` was deliberately excluded as a
  craftable template. Whatever route is used, name the sabers.

## Verify

The AP value read from an equipped saber, quoted with the pawn's name and relevant skills,
beside the ground-read value already in the capture.

## Criteria

Either the two readings match — and the record says so with the pawn named — or they differ,
and the difference is filed as a finding against the mod's C#.
