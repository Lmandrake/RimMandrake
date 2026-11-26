# SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS

Prose: `design/RimMandrake/mod_audit/RETIREMENT_WAVE_1.md` (W3, §6) and `design/RimMandrake/relic_replacements_proposal.md`.

## spec

Put the five VWE relic precepts (Hexlink, Loccorpus, Animal Blaster, Strong Rifle, Rifle of Self) of the canonical
save on the KotOR uniques the owner approved 2026-10-14 (`RELIC_MAP` in
`src/RimMandrake/Utils/modaudit/wave1_save_preedit.py`).

## verify

A load of the canonical save logs no `Precept_Relic had null thingDef`, and no relic precept names a VWE def.

## criteria

- A1: wave-1 W5 load of the edited save logs no 'Precept_Relic had null thingDef' and the five ideoligions show the KotOR relics.

## refs

file: src/RimMandrake/Utils/modaudit/wave1_save_preedit.py
file: world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws
