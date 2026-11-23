## spec
Design question for the Designer (Pyrelands, flamefang venom); no code is owed until the Designer rules.

By RM_FlamefangVenom's own numbers (RM_FlamefangVenomBite severityPerDamageDealt 0.02 x the venom-fangs' power 10 = 0.2
a bite; severityPerDayNotImmune +0.35; immunityPerDaySick 0.5, so immunity in 2 days; lethalSeverity 1), an untended
colonist with ordinary immunity peaks at 0.2 + 0.7 = 0.9 after ONE bite, and dies of the venom after TWO bites
(0.4 + 0.7 = 1.1) before immunity completes. If immunity gain scales with the ImmunityGainSpeed stat [guess ~85%], the one-bite peak is 0.2 + 0.7 / g,
so a colonist with g at or below 0.875 dies after one untended bite. A manhunting flamefang attacks every 99 ticks (cooldownTime 1.65 s), so two bites are
ordinary play. Measured offline: selftest_pyrelands_venom_staging.py with its 250-tick planted latch (two or three
bites): peak 1.014, deaths by the venom.

Question: is "two untended flamefang bites kill a healthy colonist; one bite nearly does" the experience the
flamefang_bite_carries_venom bar and vision intend? If yes, nothing to do. If no, the Designer names the change.

## verify
The Designer has ruled: the danger stands as intended, or a named change to RM_FlamefangVenom is filed with its test.

## criteria
- A ruling recorded on this item, either way.

## Acceptance test
none: a design ruling on the intended danger of the venom, not a defect with a known right answer.

## refs
def: HediffDef/RM_FlamefangVenom
def: DamageDef/RM_FlamefangVenomBite
file: src/RimMandrake/Pyrelands/selftest_pyrelands_venom_staging.py
