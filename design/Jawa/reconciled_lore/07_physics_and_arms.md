# Physics and arms — the laws, and every armament ruling to date

The constitution is `worldbuilding/setting_physics.md` (L1–L18 + the
interaction matrix) — still live and canonical. This file is the compressed
map as it stands.

## The seven forms of harm

Kinetic · Thermal · Cutting-plasma · Ionic · Neural · Chemical · Gravitic.
**No form is universally best** — every one decisive somewhere, useless
somewhere else. The closed loop: blaster → beaten by ablative → beaten by
vibro → beaten by mass plate → beaten by blaster heat; shields beat plasma →
beaten by metal, mass, and anything SLOW.

Load-bearing laws, one line each: blasters ablate, supreme anti-personnel and
poor anti-material (L1); slugs punch through energy-armour — the peasant's
answer that never power-creeps (L2); a lightsaber melts, so it beats anything
wearable and stalls a vehicle (L3); shields are worn plasma that slow things
walk through — mines, rolled grenades and torpedoes are the counters, missiles
barely exist (L6/L13); armour is three unrelated technologies and beskar-class
cheats stay quest-gated (L7/L8); ship weapons are a different category of
event (L9); desert megafauna are naturally ablative, so the standard blaster
is the WRONG tool for the local wildlife (L11); the environment participates —
sand fouls, heat weaponizes, storms are ionic (L12); explosives have no hard
counter and are balanced by scarcity ALONE (L13); the Force is verbs, never
damage (L15); **everything explodes — enormous power, minimal safety** (L17),
and detonation scale tracks **energy density, not size**: a lightsaber is the
most violent thing at infantry scale, an intact recovered blade a prize, and
ion is how you take one intact.

## Ion — the campaign's signature verb

**LOCKED SPEC D1** [owner 2026-08-08]: a single-target stun gun **tiered by
target class** — strongest vs machines, strong vs droids/vehicles, weakest but
nonzero vs flesh (stacked fire downs a person alive). The tiering IS the
tactical identity; L4 reads with this tiering. Implementation
truth [measured/built 2026-08-22]: flesh rides our buildup hediff
(consciousness-cap downing); machines are reached by re-issuing the hit as
vanilla EMP (the engine whitelists stun damage defs by object identity — no
other route exists). Ion leaves the target SALVAGEABLE: the economic answer to
"why carry a zero-damage weapon" — because you want the thing afterwards.

**Ion doctrine** [owner 2026-08-29, canon.yml > weapons]: ion EMPLACEMENTS are
Imperial anti-ship technology; **personal, carryable ion is the Jawa
innovation and identity** — makeshift versions of a ship-killer, turned to
stealing droids and stunning people.

## The weapon normalization (v1 level, shipped)

`Jawa_Armoury` restretched the compressed ladder [built 2026-08-10/11, live]:
blasters 24–34, heavy 52–72, slugthrowers 18–36, lightsabers 80–120, vibro
35–52 — one-to-two-shot lethality against the unarmoured restored as physical
consequence. **The vanilla industrial firearm line stays CUT** — theme beat
balance, knowingly; v1's floor is neolithic + cheap blasters
[owner 2026-08-22]. Mech weapons alone keep industrial firearms.

## The turret doctrine [owner 2026-08-29, canon.yml > turrets]

**A turret's damage is (# squares)² × the largest similar personal weapon** —
2x2 = 16×, 3x3 = 81×, 5x5 = 625×, 7x7 = 2401×; the scale is meant to be
awesome. The official roster is 56 defs (everything else died at normalization
via Cherry Picker). Executed rulings: per-VOLLEY budgets; normalization runs
both directions; blast ordnance splits the multiplier between damage and
radius (capped r14.9, remainder into damage); fiat anchors bio 25 / tesla 20 /
gravitic 3; traps may sit ≤2× ("they cannot broadcast at range"); archotech
4×; ion anchor is the heavy ion rifle; control effects scale linear; big-burst
beams keep doctrine volley by cutting burst count; nine damage-type-indicative
renames. Generator + patch: `src/Jawa/Jawa_Armoury/Source/gen_turret_doctrine.py`.

## Detonation doctrine

**"POWER DENSITY explodes, not the fact it's a machine"** [owner 2026-08-12]:
a drained wreck cannot explode; a charged one does, scaled by what it actually
holds. `explodeOnKilled` (death), never `explodeOnDestroyed` (fires on
deconstruct). Downed is not dead — ion-captured machines never detonate, which
is the whole incentive. The full energy-density model is v2
(`explosion_energy_model.md`); droids implement it now via Droidworks
(`08_droids.md`).

## Force

Powers are **v2 entirely** (VPE out of the list); lightsabers are v1 weapons.
Any power expressible as "X damage" is mis-specified — rewrite as a verb or
drop it. Force users are problem-changers, not artillery.
