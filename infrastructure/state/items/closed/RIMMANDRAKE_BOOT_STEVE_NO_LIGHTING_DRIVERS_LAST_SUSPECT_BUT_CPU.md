# RIMMANDRAKE_BOOT_STEVE_NO_LIGHTING_DRIVERS_LAST_SUSPECT_BUT_CPU

## What the card said

<!-- answered 2026-11-21T11:28:55Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Sat Nov 21, 3:28 AM PST. SteveDesktop (the second test machine) loses the upper halves of wide CPU registers a few minutes after RimWorld starts. Last night's test you picked ran: with the hypervisor (the Windows layer that runs WSL) switched off, the fault still came, 3.5 minutes after the game started. So the hypervisor is not the cause. Two suspects remain: the ASUS/Corsair/ENE hardware-lighting drivers, or the CPU itself. A 66-hour stress soak without the game showed 0 faults, so the game is the trigger. I have not measured whether remote access survives with those drivers unloaded. (Hard to read? Type STE, Binding or Both for a rewrite.) What may I do with SteveDesktop next?
**Picked:** Unload the lighting drivers, one boot (Recommended)
**Its description:** Why: it is the only test left that separates drivers from CPU. Buys: if the fault stops, the fix is free (remove the drivers). Costs: the test lane is down about 30 minutes; case lighting and maybe fan profiles go to defaults for that boot; a small risk the machine needs your hand. Recommended: one boot answers the last open question.
**Other options:** No more tests; keep using it, results marked suspect · Stop using it for verdicts · Treat it as a bad CPU; plan a replacement

**Owed by this card** (the close names where each was done or filed): needs your hand
