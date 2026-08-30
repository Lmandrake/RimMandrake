# The campaign — Flight of the Utinni

**RimWorld 1.6 + Odyssey, all DLC enabled** (Anomaly's *storyline content at
zero* — its creatures and abilities remain a reskin library [owner 2026-08-13]).
A **single-player build for the owner's own play** — never design for
release-robustness or other players' mod lists. There is **no worldgen in any
version**: players-of-this-save receive one hand-made frozen world as a savegame
[owner 2026-08-15/18].

## Premise

A Jawa scavenger clan on the desert world **Ash'karr** breaks into the oldest
hulk in a Hutt discard yard — a Rakatan vessel, dead since before the Cartel
had a name for the sand — and wakes it by pressing a Jawa-patterned mind into
its empty ancient core. The ship was the **Kolyska**, "Cradle", one of the
initiator vessels that terraformed this world; the clan paints **The Utinni**
on its flank and the machine has never once answered to it. The campaign opens
the moment the stolen ship sets down and the hatch opens: the ship is home, the
Hutts are furious, the Empire watches from orbit, and the flight hardware is
missing. **Getting it off the ground is the campaign.**

Feel: Firefly / Battlestar Galactica / Oregon-Trail-in-space / a scientific
expedition crossing an unexplored world.

## The loop

Land → choose objectives → temporary camp → explore → gather → improve the ship
→ enemy pressure rises → **decide what to leave behind** → launch → repeat. The
permanent colony lives aboard; planetary camps are disposable. Small crew
(~3–8). No tile is self-sufficient (the four-axis terrain schema, `02_world.md`)
— the slices only add up if you keep moving, *which is the campaign*.

## The pillars

1. **Anti-exponential.** The gravship + its onboard industry are the ONLY
   sanctioned scalable trees. Everything else is a fixed identity, a finite or
   quest-gated reward, or flavor — never a parallel ladder. This is why
   psycasting, gene-shopping, the mechanitor ladder, fluid ideology and royal
   permits are forbidden as *player* systems.
2. **No arms race (§19.5).** Enemy danger is qualitative capability — smarter
   AI, coherent tactics, distinct rosters — never stat inflation.
3. **The 7-question test** gates every mod/subsystem/reward: parallel ladder?
   removes a limitation or imposes a dependency? scales indefinitely? weakens
   crew composition? bypasses fuel/space/risk/time/mood/scarcity? reducible to
   one authored exception? makes the ship more or less necessary?
4. **Mod count is not the constraint — the capability ceiling is.** A large
   cosmetic/flavor library is endorsed; only ceiling-raisers get scrutiny.
   Curation is by Cherry Picker surface-trimming, not uninstalling.

## The three pressures that force motion

- **The Empire** — the singular escalating military pursuer, orbital-first. Its
  detection timer forces exit from any open-sky tile **in under one growing
  season** [owner 2026-08-06]. Dark/covered tiles PAUSE the orbital clock and
  substitute their own dangers and scarcities [owner 2026-08-05].
- **The Hutt ledger** — economic/criminal pressure; they want the ship back and
  they want paying, which is very Hutt. Strongly negative but recoverable.
- **Ta'Baa's clock** — the theological pressure to move (`05_the_clan.md`).

## v1 start (ruled and built)

- **Delivery is a SAVEGAME**, committed to the repo; the scenario def
  `Flight of the Utinni` exists so the engine embeds its ScenParts + pawns into
  one save [owner 2026-08-14/18/19]. The freeze IS a savegame: map ported →
  factions/ideoligions correct at initiation → save; nothing short of that is
  "the frozen world" [owner 2026-08-22].
- **Fixed pawns, fixed ship, fixed map.** Six founders (xenotype `MandrakeJawa`,
  all male, robe+hood): **Nekko Vok** (Captain, 47, the succession clock),
  **Tobb Nkik** (Keeper of the Articles), **Griz Utinn** (the Hands, droid-theft
  arc), **Yeku** (First-Hatched, the only real gun, love-gate candidate),
  **Sekki Vosh** (the Long Pot — sixth founder, ruled in for food), **Wim
  Ateeka** (Twice-Kin — the love-gate's living precedent). Full specs:
  `worldbuilding/SCENARIO_SPEC.md`. The start is HARD and stays hard
  [owner 2026-08-15].
- **The ikee** (`AA_Eyeling` reskinned): the clan's walking eye, bonded to
  Yeku, findable in the wild. *The Utinni is named for the find, the ikee for
  the looking.*
- **Flight capability is v1; flight HARDWARE ships unbuilt** — no thruster,
  tank or console. Mobility is earned mid-game (~8 cells, Steel 370, Comp 7
  when reached). Do not "fix" this [ruled 2026-08-14].
- **Strangers stay enabled** — a wanderer is not a free colonist, it is a
  SITUATION the clan's doctrine answers (enslave; love-gate if Jawa)
  [owner 2026-08-22].

## Victory [owner 2026-08-30]

v1 is OPEN-ENDED: the arcs provide climaxes, nothing rolls credits. The
pressure systems (pursuit cadence, the pride-crisis) give the late game its
shape; authored endings (the god-map roads) are v2.

## Fuel is life

**Many paths to fuel, or the ship starves** [owner 2026-08-15]: helixien gas
(volcanic/deep-desert tiles), propane lakes (the deep night), tar pits (the
Pyrelands margin). They differ in ACCESS COST, never in viability; no quest or
faction may ever gate the last remaining path. Redundancy is the requirement.

## Names of record [owner 2026-08-15]

| thing | name |
|---|---|
| planet | **Ash'karr** — "The Sundered" |
| scenario | **Flight of the Utinni** |
| ship | **The Utinni** (born *Kolyska*, "Cradle") |
| burning savanna | **The Pyrelands** |
| the one mega-structure | **The Rust Cathedral** |
| the precursors | **Rakata** (endonym) / **the Forsaken, the Forgotten** (exonym) |

"The Sundered" must appear in player-facing text at least once (it does, in the
opening narration). `Ash'karr`'s apostrophe is the character most likely to be
silently stripped — check it everywhere a name is written.
