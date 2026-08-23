# weapon_tag_audit.py was reporting armed pawns as disarmed — BUILD, 2026-08-23

TWO INDEPENDENT DEFECTS, both of which made a FIXED item look still-broken.

## defect 1 — a fresh timestamp over two-day-old data
defs.sqlite lives at the DefDump ROOT and serves every capture, so it survives a
new load untouched. The audit read its TAGS from a database built 2026-08-21 and
its HEADER from the newest capture's manifest, and printed:

    dump matches the live list: 578 mods, captured 2026-08-23T07:12:04Z
    pawn kinds with EVERY weapon tag empty: 12

The capture it named says 2.

⚠️ A MODLIST FINGERPRINT CANNOT CATCH THIS. Both captures are the same 578 mods;
what changed between them was our own XML. So the check must compare CAPTURE
IDENTITY, not the mod set.

FIX: dump_projection._sqlite_describes() compares the database's
provenance.captured_utc against the capture's manifest.capturedUtc, warns once
per run, and falls back to that capture's JSON — slower, and right.

## defect 2 — the kill list subtracted twice
`if defname not in cut` removed carriers that the capture already proves survived.
The capture is ALREADY post-cut: Cherry Picker strips weaponTags at load rather
than deleting the def, so a genuinely cut weapon contributes no tag at all and can
never reach that line. Gun_Needle is on the kill list AND carries
MechanoidGunLongRange live, because it was deliberately restored — the list had not
caught up, and the list was believed over the measurement.

FIX: presence in the capture with the tag attached IS survival. Do not re-subtract
a written intent from a measured fact.

## the reading, before and after

    before:  12 pawn kinds with every weapon tag empty   (390 tags seen)
    after:    2 pawn kinds with every weapon tag empty   (401 tags seen)

The 2 are DP_ArtilleryPirate and DP_RocketPirate — declared *NoEquipTag sentinels
carrying weaponMoney 99999. Correct, not a defect.

Cleared as false positives: Mech_Pikeman, Drone_Sentry, Tribal_Archer_Fire,
BS_Crossbowman, BS_CrossbowDvergr, BS_DvergrTraditionalist, OuterRim_ImperialTrader,
VEE_Hunter, VEE_TribalHunter, VFEP_Footsoldier.

## verified independently against the capture, not taken on trust

    MechanoidGunLongRange     -> Gun_Needle
    SentryDroneGunShortRange  -> Gun_Scattergun
    WarcasketBasic            -> VFEP_WarcasketGun_Autorifle
    BS_CrossbowTag            -> VFEM_Bow_HeavyCrossbow
