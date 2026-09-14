# BACTA_TANK_CORE_1 — the Bacta Tank mod: core building, fluid, healing comp

Owner-defined at the bench, 2026-09-13 (card answers, verbatim where quoted).
HIGH PRIORITY — owner: *"Let's see if we can't slam it out all the way to
finish at high priority so we can show some wins in terms of fully finished
mods."* Standalone mod in the RimStarWars tier.

## Naming (per design/NAMING_SCHEME_PLAN.md)
- folder `src/RimStarWars/Bacta`, packageId `mandrake.rsw.bacta`
- def prefix `RSW_`, C# namespace `RimMandrake.StarWars.Bacta`

## Ruled mechanics — these are owner rulings, not suggestions

**Skeleton (card 1, option 3):** bed-derivative tank with a visible suspended
pawn, plus a custom immersion comp. NOT a sealed biosculpter-style pod. The
pawn renders inside the tank (see BACTA_PAWNINTANK_RECON_1 — owner: *"I hope
you can find the code for the visible pawn inside from the BioReactor mod
perhaps"*).

**Healing power (card 2, option 1 amended, owner verbatim):** *"as long as
medicine would aid the infections. Some infections remain in effect. Does not
heal mental brain injury, just physical injuries. Does heal organs, does not
regrow them. Healing, not regeneration. Turns penalties of battle from 'lose
pawns often' to 'pawns are out of the game if you get them back while still
alive.'"*
- Fast wound/burn healing; erases scars and permanent PHYSICAL injuries over
  immersion time.
- Organs: damaged organs heal; MISSING organs/limbs never regrow.
- Brain injuries and mental (consciousness-capacity) damage: untouched.
- Infections: helped only where medicine could treat them; untreatable kinds
  persist.
- Design intent: battle wounds stop killing pawns; they cost recovery time in
  the tank instead.
- Revival of the recently dead is BACTA_REVIVAL_MECHANIC_1, not this item.

**Fluid economy (card 3):** bacta is a TRADE-SCARCE liquid — bought/looted,
no crafting in v1. The tank consumes it per healing. Rides the ruled
LiquidDef registry (liquids framework canon 2026-09-13) as its first
showcase client; coordinate the property block with LIQUID_REGISTRY_CORE_1
rather than inventing a parallel fluid item shape.

**V1 scope (card 4): FULL KIT** — tank + fluid here; 2-1B-style medical droid
facility + bacta patches/spray in BACTA_SIDE_ITEMS_1; art in BACTA_TANK_ART_1.

## This item builds
1. Mod skeleton (About.xml with correct packageId, loadAfter our liquids mod).
2. `RSW_BactaTank` building ThingDef: 1x2 or 2x2 footprint (art decides),
   power, bed-like assignment so a downed/injured pawn can be carried in,
   linkable-facility hooks (KR pattern) left open for the droid.
3. `RSW_Bacta` fluid per the LiquidDef registry + a tradeable container item;
   trader tags so exotic/medical traders stock it.
4. `CompBactaImmersion` (C#): the ruled healing above, fluid drain, eject on
   empty/healed. Async-safe, no per-tick scans (aggregate on rare ticks).
5. Research: one project gating the build; vitals-monitor-tier prereq.
6. Mod Settings per the 2026-09-12 standing rule: per-feature toggles
   (healing comp, scar-erasure, infection gate), tunable heal-rate and fluid
   cost, defaults = shipped behavior, all-off degrades to a plain power bed.

## verify
Quicktest on the minimal+target list: wounded pawn carried in, wounds heal at
the tuned multiple; a scarred pawn's old wound erases after the tuned
immersion; a missing kidney does NOT return; a brain injury does NOT change;
fluid level drains and blocks use at zero; all settings toggles honored.
Screenshot of the visible pawn suspended in the tank (the ESB read) closes
the art acceptance alongside BACTA_TANK_ART_1.
