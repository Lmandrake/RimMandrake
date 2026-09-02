# Retire ALL remaining third-party Star Wars donor mods

Owner, 2026-09-01: *"file this as a ticket to track to get rid of them all so
we don't forget. And I bet we can get rid of Mlie and TSDA very quickly if we
put our mind to it. And we should."*

Umbrella tracker — each wave retires like WEAPONS_DONOR_RETIREMENT_1 did:
absorb what the campaign uses, gate what references it, retire, cold-load
verify. 🔴 Its incident lesson binds every wave: **check the WHOLE active mod
list for dependents before switching anything off** — the wave's own scope is
not "everything that could break."

## The census (MEASURED against ModsConfig.FULL.LATEST.xml, 593 active, 2026-09-01)

| wave | mods | state |
|---|---|---|
| **1 — quick wins (owner-directed)** | `mlie.starwarsanimalcollection` · `m3.continued.jangodsoul.starwars.tsda` | not started. ⚠️ Before cutting Mlie: retexture-prefix animals may be on the planet and in the fauna cast (`defname-denylist-misses-retextures`); census the cast CSV + planet first |
| **2 — KotOR/droid cluster (the bottleneck)** | `guy762.mm.kotorcore` · `guy762.kotordroids` · `btd.gbp.shippack.kotor.vge` | kotorcore blocked on kotordroids' dependency; DROID_DONOR_PATCH_GATE_1 is 9/10 sites done, Site 1 waits on the Droidworks `Need_Power` port landing on KotORDroids |
| **3 — OuterRim family** | `neronix17.outerrim.core` · `.droiddepot` · `.furnitureanddecor` · `.galacticempire` · `.rebelalliance` + `leutiankane.mines2patchouterrim` | not started. galacticempire is the known interloper (`galactic-empire-is-reskinned-vanilla`); droiddepot ties into the droid system |
| **4 — singles** | `lee.theforce.lightsaber` · `starwars.themedsounds` | not started; sounds pack likely trivial, lightsaber needs a Force-content ruling first |

Weapon donors are NOT here — 5 of 6 already retired under
WEAPONS_DONOR_RETIREMENT_1; its last pack (kotorcore) is wave 2's.

## criteria
- [ ] Wave 1: Mlie + TSDA retired, full-list cold load clean, campaign fauna
      cast shows zero rows lost to the cut (assert coverage, not absence of
      errors).
- [ ] Wave 2: kotordroids' kotorcore dependency worked down (Need_Power port
      + whatever else a dependents sweep finds); kotorcore retired; then
      kotordroids/shippack per droid-system progress.
- [ ] Wave 3: OuterRim absorption items filed per mod before any retirement.
- [ ] Wave 4: both singles ruled and actioned.
- [ ] `ModsConfig.FULL.LATEST.xml` carries zero third-party SW packageIds;
      every survivor is `mandrake.*`.
