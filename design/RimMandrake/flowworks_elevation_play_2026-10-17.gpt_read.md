# Outside read (GPT) for flowworks_elevation_play_2026-10-17.md — verbatim, evidence not authority

Model gpt-6.1-sol via `src/RimMandrake/Utils/gpt_consult.py`, job `consult-20261017-101015-3458550`, 2026-10-17. Given the
play/rules/coherence lens and two files (`relative_depth_climb_design_2026-10-12.md`, `flowworks_pits_unified_model_2026-10-02.md`),
with no recommendation from us. Dispositions: §7 of the main file.

---

**Ship 0.5 m increments with an 8 m player-digging cap: 16 notches, plus undug ground.** Keep natural beds deeper. There is no uniquely correct maximum from play alone; 8 m is a useful first boundary because it permits the owner’s 4/7 m basin and substantial reservoirs. Beyond that, storage keeps increasing while most movement and containment decisions repeat.

The important distinction is **depth resolution, maximum excavation, and maximum supported natural depth**. They need not share one limit.

1. **The natural breaks are abilities and infrastructure, not round-number depths.**

| Depth or delta | New player value / rule threshold |
|---|---|
| 0.5 m | Smallest meaningful excavation and water-capacity increment: **1,000 L per cell**. |
| 1 m sheer step | Contains ordinary small creatures; humans climb slowly. |
| 1.5 m sheer step | Contains ordinary humans; maximum single-cell ramp span. |
| 2 m sheer step | Contains large creatures; current pit/spike threshold. |
| 2.5 m sheer step | Contains ordinary huge creatures with K=4. **Last baseline containment threshold.** |
| 4–8 m absolute depth | Reservoirs, terraces, nested containment and substantial drained landscapes. Access planning becomes the main choice. |
| 20 m | Dramatic natural lakebeds; little additional standard containment value. |
| 50–125 m | Extreme landscape support. Primarily spectacle and capacity, unless new mechanics justify it. |

Modifiers can shift individual creatures’ thresholds. Absolute depth never substitutes for the relevant **edge delta**.

Do not refine below 0.5 m: extra clicks buy little movement gameplay. Water already uses litres, so finer water accounting does not require finer excavation.

The proposed 4/7 m basin holds **152,000 L** when filled to surrounding ground level: 128,000 L at uniform 4 m, plus 24,000 L in the central sump. Its inner 3 m cliff contains baseline huge creatures; its outer 4 m cliff requires access infrastructure. Those are understandable choices.

2. **Four delightful stories are worth supporting.**

- **The desert reserve:** dig a broad 4 m basin with a 7 m sump. Falling water exposes useful terraces while the sump preserves the final supply. The extra digging adds measurable drought endurance.
- **The reclaimed lake:** drain a 20 m lake and walk livestock down its gradual shore. Establish grazing on suitable sediment. Nobody becomes trapped merely because the floor is far below original ground.
- **The animal sorting yard:** use 1 m drops for small animals, 1.5 m for humans, and 2.5 m for huge creatures. Shared ramps turn containment into circulation when opened.
- **The working quarry-prison:** a shallow service terrace surrounds deeper cells. Wardens, haulers and rescue teams share deliberate access routes; damage to one ladder creates an immediate emergency.

**Five failures need explicit cheap rules.**

- **Death marches and endless failed jobs.** A doctor accepts a rescue in a 20 m hole, then repeatedly fails to arrive. **Fix:** job availability must use the same pawn-specific route permissions as walking, including the return journey when carrying someone. Animals must also reject voluntary cliff descents. Recheck before the final excavation removes an exit.
- **Permanent, unattackable terrain walls.** A continuous trench defeats every grounded raid forever. **Fix:** organised attackers need one fallback assault-access action. Suggested tuning: erect a destructible ladder from a reachable lip in **10 seconds + 1 second/metre**. Apply it to relevant humanlike and mech assaults; animals may retreat.
- **Remote services and instant extraction.** “Adjacent warden” becomes free tending, feeding and rescue through 20 m of air. **Fix:** retain lip capture/conversion, but require a usable service ladder. Feeding, tending and hauling require floor access. A carried pawn uses the ladder at a slower rate; never teleports.
- **One-cell terrain edits teleport giants.** Breaking the W×W condition currently permits walking out, potentially across a 125 m wall. **Fix:** width grants a local bracing crossing only between supporting banks within the creature’s width. It cannot waive every cliff in the pocket. This tightens the older width ruling.
- **Invulnerable firing pits and environmental execution chambers.** Adjacent-only shooting can protect a pawn from distant retaliation while fire or gas bypasses the same boundary. **Fix:** apply shooting restrictions symmetrically. Keep ordinary fire/gas behaviour; add no depth multiplier, gas reservoir or depth immunity. Burning oil still harms occupants normally.

Also, fall damage must depend on **metres dropped**, never `drop / MaxDepth`. Changing a setting must not make the same 2 m fall safer.

3. **Movement, imprisonment and environment should remain separate rules.**

Keep the ruled cardinal delta limits. Diagonals must not bypass blocked cardinal corners. Nobody voluntarily walks down a non-traversable drop.

Ramps and stairs should share one rule: **one cell bridges at most 1.5 m**, in either direction, at walking speed for everyone. A 7 m descent needs at least five such transitions. No ramp grants access across unrelated walls.

Ladders bridge their actual endpoint delta, at any depth. Suggested starting speed: **one second/metre**, doubled while carrying a pawn. Lowered ladders retain prison-door permissions; during prison breaks, prisoners must be able to use or attack the access fitting. Raised ladders close access.

Water movement uses **water above the local floor**, not excavation depth. Suggested initial bands, with `H` as pawn height:

- `h ≤ 0.3H`: shallow wading, **1.5× travel time**.
- `0.3H < h ≤ 0.6H`: deep wading, **3×**.
- `h > 0.6H`: swimming required for voluntary travel.
- Drowning begins when the airway is submerged: approximately `h ≥ H` standing, `h ≥ 0.2H` downed.

These are tuning values. The essential correction is that **one litre in a 7 m pit cannot drown its occupant**. Swimmers also need an exit; swimming does not grant wall climbing.

A real prison needs a prisoner bed, a structurally bounded human enclosure, and controlled exits. A ramp reaching the surface defeats containment unless an ordinary prison barrier closes it. Determine the room structurally; determine each occupant’s escape ability separately. A human prison need not contain a giant.

**Deeper prisons should add capacity and access burden, not recruitment bonuses or automatic security ratings.** The threshold matters; another 5 m should not magically reduce resistance. Forbid prison designation without a service route, or explicitly accept starvation oubliettes as a separate outcome.

Open pits remain outdoors: no automatic roof, cave darkness or insulation. Keep the ruled strong outdoor-temperature coupling and cruelty thought, but do not multiply exposure by depth. Roofs, lamps and heating use ordinary rules. A 20 m hole is not automatically cooler, darker or roofable for free.

4. **Vegetation needs substrate, moisture and time—not a depth timer.**

Replace universal fertility zero with exposed substrate. Suggested starting fertility:

| Substrate | Fertility |
|---|---:|
| Rock / sterile desert sand | 0 |
| Gravel | 0.1 |
| Exposed soil | 0.3 |
| Natural fertile lake sediment | 0.7 |

Draining reveals existing sediment; excavation does not manufacture it. Digging deeper can remove the fertile layer.

After **10 growing days** exposed, eligible cells can begin sparse biome-appropriate grass and shrub colonisation if temperature, moisture and light permit. Use ordinary growth thereafter. Defer automatic trees; crops still require sowing and their normal fertility requirements.

Dry desert sand stays barren indefinitely. Wetting rock does not turn it into farmland. Fertility does not rise merely because time passes.

This makes lake reclamation valuable without creating a “dig anywhere for free soil” exploit.

5. **Ship the 8 m tier first; defer new depth systems.**

It delivers the requested geometry, every baseline containment threshold, and useful storage. Support existing deeper natural floors with identical movement and access rules. Defer player excavation beyond 8 m until actual stories justify it; defer groundwater, collapse, depth-based shade, gas pooling and special underground agriculture.

Three existing rules need explicit reconciliation:

- **“Pit = exactly 2 m” is obsolete.** A sheer 1.5 m drop contains humans; a gradual 20 m bowl does not.
- **“Spikes only at maximum depth” becomes unstable when the cap changes.** Recommend a fixed **2 m minimum**, on designated pit-floor cells. This requires revising that ruling.
- **Absolute-depth adjacent-only shooting breaks drained landscapes:** two pawns on a broad, flat 20 m lakebed cannot have an ordinary firefight. Narrow that exception to actual confining pit boundaries, which requires an owner-approved amendment.

The cap is easy to change later. Shipping contradictory meanings of “pit” will be much harder to undo.