## spec
🔴 **OWNER, 2026-08-21:** *"Please do what it takes to restore Pikeman and Sentry. We
should not be turning off Mech weaponry, that was a mistake to correct."*
Ruled in `CUT_DISARMED_VANILLA_KINDS_1`; read it for why the repair is at the CUT and not
in `WeaponTags_Renormalise.xml`.

**Delete exactly two `<li>` entries from the live Cherry Picker list:**

```
C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml
```

| remove | from | restores the sole carrier of | which re-arms |
|---|---|---|---|
| `Gun_Needle` | Core | `MechanoidGunLongRange` | `Mech_Pikeman` (`weaponMoney 9999~9999`) |
| `Gun_Scattergun` | Odyssey | `SentryDroneGunShortRange` | `Drone_Sentry` |

⛔ **Remove nothing else.** `Flamebow` is in the same file and **stays cut** — ruled.
Measured 2026-08-21: the file holds **1,349** `<li>` and all three defNames are present
exactly once each. After the edit it must hold **1,347**.

⚠️ **Cherry Picker's in-game UI writes this file**, so an edit made while the game is up
can be clobbered when that window is next saved. The game is UP. Either do it in the
shutdown window, or do it now and **re-read the file afterwards** to confirm both lines
are still gone. Config files themselves never wait on the game (`CLAUDE.md`).
✅ Afterwards refresh `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` to
match, or the freeze copy becomes the stale one.

## verify
- `grep -c "<li>"` on the live file reads **1347**.
- `grep -c` for `Gun_Needle` and for `Gun_Scattergun` each read **0**; `Flamebow` reads **1**.
- On the NEXT dump taken against a matching mod list, `Gun_Needle` and `Gun_Scattergun`
  carry non-empty `weaponTags` and non-zero `MarketValue` (both currently read `[]` and 0 —
  that is the neutering signature, and it disappearing is the proof).
- `weapon_tag_audit.py` no longer lists `Mech_Pikeman` or `Drone_Sentry` as tagless.
  ⚠️ It refuses to report unless the dump's mod set matches `ModsConfig.xml`, and the
  current dump is one mod stale in BOTH directions (see `queue/HUMAN.md`, 08:19) — re-take
  it on the next load rather than trusting a matching count.

## criteria
CHECK, on the next load: spawn a `Mech_Pikeman` and a `Drone_Sentry` and confirm each
holds a weapon. 🔑 The tag pool only re-forms on a load; nothing here is visible without one.
