# JAWA_CULTURES_LEAK_TO_STRANGERS_1 — our authored cultures are in the general pool

Measured 2026-08-26 during the religion test, on a non-classic world with 45 ideoligions.

**All twelve `Jawa_Culture_*` defs are in use — and 18 ideoligions sit on them, not 12.** Six are
strangers that rolled one of our cultures and generated their own name:

```
The School            Jawa_Culture_Droid       Structure_Archist
Human Academy         Jawa_Culture_Junkers     Structure_Archist
Hominid University    Jawa_Culture_TradeMoot   Structure_Archist
Nightmare Deep        Jawa_Culture_TradeMoot   Structure_Archist
the Contract          Jawa_Culture_Blackstar   (x3 - see below)
```

⇒ A `CultureDef` is not private to the faction it was written for. Ideo generation draws from the
whole `CultureDef` database, so an unrelated outlander or pirate faction can come out **culturally
Jawa** — its leader title rolled from `Jawa_LeaderTitle_*`, its names from our name-makers.

## Why this is a decision and not a defect

On a throwaway world it is cosmetic. On the **one shipped world** it means a faction the player meets
may wear our authored flavour without being ours, which is a worldbuilding call, not a mechanism
question. ⛔ CHECK does not rule on what v1 IS.

⚠️ **And the fix has a cost.** The only lever is `CultureDef.generateOnlyFor` or equivalent gating —
narrowing it makes our cultures unavailable to the generator entirely, which is fine for the twelve
`fixedIdeo` factions (they take the culture from the def) but must be checked against anything that
relies on a Jawa culture being rollable.

## Also unexplained, flagged not diagnosed

**`the Contract` appears three times** on `Jawa_Culture_Blackstar` — three separate Ideo objects with
the same authored name, on a world with one Blackstar faction. Not investigated.

Evidence: `infrastructure/state/evidence/religion_test_2026-08-26_CHECK.md`
