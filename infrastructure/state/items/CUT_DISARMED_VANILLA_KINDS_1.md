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

---

## ruling — DECIDE, 2026-08-21, on the owner's words

🔴 **OWNER, 2026-08-21:** *"Please do what it takes to restore Pikeman and Sentry. We
should not be turning off Mech weaponry, that was a mistake to correct."*

That is a ruling about the **cut**, not about the tag index — so the repair is at the
cut, not in `WeaponTags_Renormalise.xml`. Restoring the weapon restores the pool with
zero patch ops and gives the mech back *its own* gun rather than a human rifle.

### In scope — three kinds, two mechanisms

| kind | mechanism | why this one |
|---|---|---|
| `Mech_Pikeman` | **UN-CUT `Gun_Needle`** (Core) — delete its `<li>` from the Cherry Picker list | Owner's ruling verbatim. Appending `Gun` would arm a mechanoid with an industrial rifle; that is not restoring mech weaponry, it is disguising the hole |
| `Drone_Sentry` | **UN-CUT `Gun_Scattergun`** (Odyssey) — same | Same ruling. `weaponMoney 9999~9999` resolved to this weapon until we cut it |
| `Tribal_Archer_Fire`, `Tribal_Hunter_Fire` | **APPEND `NeolithicRanged`** beside the dead `NeolithicRangedFlame` in the hand-authored block of `WeaponTags_Renormalise.xml` | ⛔ `Flamebow` **stays cut.** The owner ruled on *mech* weaponry; a neolithic fire-bow is not that, and its cut reads deliberate. These kinds become plain archers — armed, not on fire. The mechanism is the one `THREE_ANCIENT_KINDS_ARMED_1` already proved |

⚠️ **The two un-cuts are edits to a LIVE game config**
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`,
1,349 `<li>`, all three weapons present and confirmed today). Config files never wait on
the game — but **Cherry Picker's in-game UI writes this file**, so an edit made while the
game is up can be clobbered when its window is next saved. Sequence it accordingly and
re-read after, and refresh `deployed/config/v1_freeze/` to match.
🔑 The tag pool only re-forms on a **load**. Nothing here is visible without one.

### Out of scope, and each for its own reason — do not reopen these

- ⛔ `DP_ArtilleryPirate` · `DP_RocketPirate` · `VFEP_Footsoldier` — bucket 2 by cause,
  bucket 1 by **intent**. Their mods equip them by another route and arming them breaks it.
  **Intent overrides cause.** Unchanged from `FIFTEEN_TAGLESS_KINDS_RULING_1`.
- ⛔ `VEE_Hunter` · `VEE_TribalHunter` · `BS_Crossbowman` · `BS_CrossbowDvergr` ·
  `BS_DvergrTraditionalist` · `AncientMallGuards` (PKM) — **mod kinds, not base game.** The
  ruling's discriminator was *does this kind ever spawn HERE*, and that discriminator was
  never disproved — only the CAUSE beneath it was. It still rules them out.
- ⛔ The seven out-of-scope-by-reachability kinds stay out. Nothing here reopens them.

🔑 **The correction that outlives this item.** `FIFTEEN_TAGLESS_KINDS_RULING_1` was right
about *which kinds matter* and wrong about *why they were tagless*. It said our cut was not
the cause; the cut was the cause for 11 of 14. The discriminator survives, the premise does
not, and `weapon_tag_audit.py`'s `emptied by the cut: 0` was a structural artefact of
reading a dump where Cherry Picker neuters rather than deletes — **183 of 183 cut weapons
present-and-neutered, zero deleted.** Any future attribution question must go to the mod's
SOURCE XML, never to the dump.
