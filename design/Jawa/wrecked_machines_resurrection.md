<!-- status: RULED resurrection — owner, 2026-08-31: "let's resurrect that now! Fix it.
     Make it work in the new regime." Lifts the 2026-08-12 park recorded in
     src/RimMandrake/WreckedMachines/DESIGN.md and V2.md (banners there now point here).
     Canon: canon.yml wrecked_machines. Items: WRECKED_MACHINES_RESURRECTION_1 ·
     BUILDING_THEFT_HAULER_1. -->
# WreckedMachines resurrected — repair is the Jawa road to big machines

The 2026-08-12 park bought a finished, de-risked mod: three tiers
(Wrecked → Kludged → Repaired), the pilot smelter's 12 validated facings, the
`replaceTags` repair loop proven at def level, and the Research Reinvented
`SpecialResearchOpportunityDef` study mechanism verified against RR's shipped
DLL. Nothing was wasted. The new regime turns its two old liabilities into
assets:

- **RR is now the ruled substrate** (canon `research_tree.taxonomy_ruled`) —
  "study the wreck to learn to fix it" stopped being a clever integration and
  became the campaign's own progression grammar.
- **The ownership fabric exists** (`ownership_settlement_spec.md`) — a wrecked
  machine on someone's map has claims, and taking one is a TakingEvent.

## The doctrine (owner, 2026-08-31, verbatim anchors)

> "Learning the tech from the ship not to just build but to repair existing
> broken machinery to its glory is MUCH easier than building from scratch, and
> about all the Jawa can do."

**Repair-first, build-later-if-ever.** For LARGE/ADVANCED machines and turrets
the scratch-build recipe is not offered at Jawa tech reach — the route to a big
thing is: **find or take a wreck → study it (RR Analyse, ~5 sessions) →
kludge it → restore it.** Small/common machinery keeps normal build rules;
the doctrine bites only above a size/advancement line (proposal: the line is
multi-tile + Spacer-or-higher techLevel, tuned per machine in data).

> "Maybe they steal big things from colonies to have them, using powerful,
> strong droids to do so. A hauler droid that can steal buildings is a
> fantastic idea! Use that too."

**The building-theft hauler** — a heavy Droidworks chassis whose whole purpose
is uninstalling and carrying entire buildings off hostile maps. The campaign's
three new systems meet in one image: a straining droid walking a stolen
smelter down a settlement street while the perception engine decides who saw.

## What changes from the parked design

1. **Tier ladder, art pipeline, replaceTags loop: unchanged.** The one unpaid
   debt stands and is now first work: RUNTIME-verify the replaceTags build-over
   (def shape proven; in-game placement never tested; Replace Stuff's postfix
   may veto — the escape hypothesis `useHitPoints=false` is named in DESIGN.md
   §4 and needs its quicktest).
2. **Progression fields stop being provisional.** The old `⚠️ PROVISIONAL`
   costs/research now resolve against the ruled research grammar:
   restoration rows live in **THE SHIP tree** (Rekko-neutral register);
   the techprint gate is the ruled **faction-held access class**
   (`research_tree.tech_gating_ruled`) — who holds a machine's techprint is a
   faction alignment fact, and the Memory Core releases ship-original systems.
3. **Wreck placement stops being ship-only.** Wrecks are seeded by map
   authoring in three habitats: the Utinni's own deck (the v1 fiction made
   real), settlement maps via district manifests (a wrecked crane in the
   Junkers yard — steal it or claim-fee it), and wild territory maps (tar-pit
   digs and cavern floors yield wrecks — the proposals suite cross-feeds).
4. **Sacred scrap returns as a CLAN rule, not an engine rule.** v2's
   non-deconstructible wreck fought the repair loop (the Replace Stuff
   conflict). Instead: wrecks are deconstruct-forbidden by policy for
   colonists (ideology precept / restriction), not by def — the engine stays
   simple, the reverence stays real, outsiders looting YOUR wrecks stays
   possible (they don't share the faith).
5. **Parallel-def cost accepted for the pilot only.** The shipped state keeps
   VFE-Factory's building untouched; the ship-or-retexture question re-opens
   only after the pilot loop survives a live round.

## BUILDING_THEFT_HAULER_1 — the heist verb (Droidworks × ownership × visits)

- **Chassis**: a Droidworks heavy frame (the family layer's big slot); slow,
  loud, unmistakable — you do not sneak a smelter out, you WIN the right to
  walk it out (distraction, bribed gate, night lift, or open assault).
- **Mechanic**: droid-driven uninstall→minify of normally-unminifiable
  buildings (a C# gate keyed to the droid's job, not a global minify unlock —
  players without the droid still can't); carry weight scales with chassis;
  the carried building is a visible pack (art: the machine lashed to its back).
- **Fabric integration**: the taking emits one LARGE TakingEvent (a building's
  recognizability is near-maximum — a town knows its own smelter); expect the
  full perception cascade. A stolen wreck is *low* heat by comparison — towns
  guard treasure, not rubble. **The cheapest heist is stealing what the
  victim thinks is junk** — which is the entire Jawa thesis in one mechanic.
- **Failure texture**: droid downed mid-carry drops the building minified on
  the street — recoverable by EITHER side; the town re-installing its own
  smelter next visit is the world remembering.

## Sequenced work

1. **WRECKED_MACHINES_RESURRECTION_1** (FOUNDRY): un-park; quicktest the
   replaceTags runtime question (with and without Replace Stuff active);
   re-point the pilot's costs/research at the ruled grammar (Ship-tree row,
   faction-held techprint via the gating item's mechanism); wire the RR
   Analyse def and prove the study→unlock loop live; wreck-seeding hook for
   district manifests. Ships when the pilot smelter loop runs end-to-end in a
   quicktest.
2. **BUILDING_THEFT_HAULER_1** (FOUNDRY, after Droidworks family layer +
   PROPERTY_FABRIC_BUILD_1): the hauler chassis, gated minify, TakingEvent
   emission, carry/drop states.
3. **Machine roster growth** rides the treated register (`MACHINES.md`) one
   machine at a time; art cost (~8 images/machine) is the known price.
