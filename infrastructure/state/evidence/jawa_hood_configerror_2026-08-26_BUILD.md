# JAWA_HOOD_NEVER_WORN_1 — criterion 3, measured offline 2026-08-26 by BUILD

`NEXT_RELOAD.md` §24 criterion 3: *"Player.log no longer carries these three lines."*
Settled without the bridge, because a log grep is not a bridge call.

```
BEFORE — the 06:35 load, infrastructure/state/logs/harvest_2026-08-26/Player.log.2026-08-26_full
  grep -c "required apparel can't be worn together"   ->  3
    Config error in Jawa_Tribal_Scavenger: ... (Apparel_WarVeil, guy762_JawaHood)
    Config error in Jawa_Tribal_Elder:     ... (Apparel_TribalHeaddress, guy762_JawaHood)
    Config error in Jawa_Tribal_Elder:     ... (Apparel_PlateArmor, guy762_Robes_jawa)

AFTER — the current load, with the Inherit="False" fix deployed at 06:5x
  grep -c "required apparel can't be worn together"   ->  0
  grep   "Config error in Jawa_"                      ->  (nothing)
```

🔑 **The same grep, over both logs.** The BEFORE reading is the positive control: the check
demonstrably fires, so the zero is a measurement rather than an absence nobody could have
observed. `PawnKindDef.ConfigErrors` runs `ApparelUtility.CanWearTogether` over every pair in
`apparelRequired` at load, so a surviving conflict would still be printing.

## ⛔ What this does NOT settle
Criteria 1 and 2 — that every pawn of all four kinds actually WEARS `guy762_Robes_jawa` and
`guy762_JawaHood`, and wears none of the three inherited pieces. Those need a spawn and
`jawa/pawn_get`, i.e. the bridge. The config error going quiet says the DEFS no longer conflict;
it does not say what the generator put on a pawn.
