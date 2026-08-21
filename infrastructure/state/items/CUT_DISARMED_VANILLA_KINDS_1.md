## spec
Filed by BUILD out of `WEAPON_TAGS_MATCH_NOTHING_1`. Full evidence:
`infrastructure/state/observed/build/WEAPON_TAGS_MATCH_NOTHING_1_offline.txt`.

🔴 **`FIFTEEN_TAGLESS_KINDS_RULING_1`'s premise is wrong. The cut IS the cause, for 14 of
the 15** — and BUILD gave DECIDE that wrong premise, so this is BUILD's error to report,
not DECIDE's to have caught.

**Why the instrument lied.** `weapon_tag_audit.py` printed `emptied by the cut: 0` and
that zero was **structurally guaranteed, never a measurement**. Cherry Picker does not
DELETE a cut weapon — it **neuters it in place**: the ThingDef stays in the dump carrying
`weaponTags: []` and MarketValue 0. Measured: **183 of 183** cut weapons are
present-and-neutered, zero deleted. A neutered weapon therefore contributes no tag to a
dump-built index, so a tag whose every carrier was cut **never enters the index at all**
and cannot be counted as emptied. The filter could only ever fire on a tag that still had
a live carrier — which by definition is not empty.
⇒ **Attribution needs the mod's SOURCE XML**, which still carries the tag the neutered def
used to have. Done that way: **11 of the 14 dead tags lost every carrier to our cut.**

⭐ **THE PART THAT IS BIGGER THAN FIFTEEN KINDS.** Three of those carriers are base game:

| weapon | from | sole carrier of | ⇒ every one of these spawns bare-handed |
|---|---|---|---|
| `Gun_Needle` | **Core** | `MechanoidGunLongRange` | `Mech_Pikeman` |
| `Gun_Scattergun` | **Odyssey** | `SentryDroneGunShortRange` | `Drone_Sentry` |
| `Flamebow` | **Biotech** | `NeolithicRangedFlame` | `Tribal_Archer_Fire`, `Tribal_Hunter_Fire` |

⚠️ **`Mech_Pikeman` and `Drone_Sentry` were filed as "built-in weapons, deliberate
upstream". That is wrong.** Vanilla mechs and drones equip from the tag pool like anything
else — `Mech_Pikeman` carries `weaponTags [MechanoidGunLongRange]` and
`weaponMoney 9999~9999`, which resolved to `Gun_Needle` until we cut it. They are ours.
🔑 `MECHANOIDS_STAY_ON_1` keeps the Mechanoid faction, so this is live content.

**THE RULING NEEDED, and it is scope again, not mechanism.** The ruling's own
discriminator — *does this kind ever spawn HERE* — was sound and is untouched; only the
CAUSE it rested on was wrong. So the question is narrower than "repair other mods' kinds":
⇒ **do we re-arm the kinds OUR cut disarmed, where the kind is base game and does reach
this planet?** The candidates are the three rows above, and the mechanism is the one
`THREE_ANCIENT_KINDS_ARMED_1` already proved — more ops in the hand-authored block of
`WeaponTags_Renormalise.xml` appending a live tag beside the dead one.
⛔ Do not rule "fix all 14": `DP_ArtilleryPirate`, `DP_RocketPirate` and `VFEP_Footsoldier`
are bucket 2 by cause but bucket 1 by intent — their mods equip them by another route, and
arming them would break that. Intent overrides cause.
⛔ The seven out-of-scope-by-reachability kinds stay out; nothing here reopens them.

## verify
- DECIDE names which of the cut-disarmed kinds are in scope and what tag each receives.
- Whatever is ruled in scope is patched, and `weapon_tag_audit.py` under a FRESH dump
  reports a tagless list containing only the kinds DECIDE declared out of scope, by name.
- ⚠️ The audit refuses to report unless the dump's mod set matches `ModsConfig.xml`.

## criteria
DECIDE's, and it is a written ruling. No artefact is owed by this item itself.

## notes
The instrument is corrected in place: `weapon_tag_audit.py` no longer prints the false
line, prints the neutered count instead, and carries the mechanism as a comment in
`audit()`. ⚠️ That correction was still uncommitted in a file another seat was mid-edit
when this was filed — confirm it landed before trusting the tool's output.
