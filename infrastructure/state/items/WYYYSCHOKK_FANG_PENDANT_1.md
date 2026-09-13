# WYYYSCHOKK_FANG_PENDANT_1 — tribal bravery pendant: social weight with the hunting tribes, trade good everywhere

Filed by BENCH, 2026-09-13, owner's direct spec (verbatim): *"add this
awesome concept to the game for the Wildsteam/Blackstar/Deep Tribe factions,
as they all have a concept of respected hunting: Wyyyschokk fangs on a tribal
pendant showing the bravery of the person. These should have social
consequences for being worn by implying the person is quite brave (with
those factions), and be a trade good elsewhere on planet regardless."*
Reference image: a rough-corded tribal pendant of dark fangs (owner-supplied,
2026-09-13 — cord-wrapped fang cluster, red-tipped dark teeth on twine).

## spec

1. **The fang** — `RSW_WyyyschokkFang` (RimStarWars tier): butcher/hunt
   product on the Wyyyschokk race (a few per corpse; VERIFY the wyyyschokk's
   def home — SWBestiary or donor — and add butcherProducts there or by
   patch). Stackable, small marketValue on its own.
2. **The pendant** — `RSW_Apparel_FangPendant`: neckwear-layer apparel
   (VERIFY an open apparel layer/bodyPartGroup that does not fight existing
   neck slots in the 599-list — collision here is silent), crafted at a
   crafting spot/tailor bench from fangs + a textile cord; low work, tribal
   tech level. Art per the reference image and the art lawset (this is an
   ITEM sprite — flat, outlined, reads at inventory size).
3. **Social consequence (the mechanic)** — observers from the three hunting
   tribes regard the wearer as brave:
   - Faction targets: the campaign's Wildsteam, Blackstar, and Deep Tribe
     factions — 🔴 VERIFY their FactionDef defNames from the live defs/dump;
     the owner's names are display names, never guess defNames.
   - Mechanism options for FOUNDRY (pick at build, note the choice): (a) a
     Harmony-free `ThoughtWorker_ObserverFactionApparel` C# thought — social
     thought on observers whose faction is listed, keyed to the worn pendant
     (cleanest, mirrors vanilla royal-apparel expectation machinery);
     (b) ideoligion precept route — REJECTED here: precept budget is
     FactionDef-fixed (rimworld-ideoligion skill: named precepts are design
     register, not mechanism).
   - Effect shape: +opinion of wearer from those factions' pawns (magnitude
     tunable in Mod Settings), and a small trade/negotiation goodwill flavor
     with those factions is optional v2 — keep v1 to opinion thoughts.
   - The implication is BRAVERY: name the thought accordingly ("wears the
     fang of the great weaver" style); flavor text cites the hunt.
4. **Trade good everywhere** — pendant carries real marketValue + tradeTags
   so every trader/settlement buys it regardless of faction (the Bazaar's
   worldTag weighting can later make hunting-tribe settlements pay MORE —
   note the seam, build nothing Bazaar-side here).
5. **Home**: RSW tier mod (SWBestiary or a small `RimStarWars: TrophyCraft`)
   for fang+pendant+thought; RUT patch wires the three campaign factions in
   (faction lists are campaign data). Mod Settings: toggle the social system,
   defaults ON.

## verify

Quicktest: butcher a wyyyschokk → fangs; craft pendant; spawn observers of a
listed faction and an unlisted one — opinion delta appears only for listed;
pendant sells to a vanilla trader. Selftest-able parts (def resolution,
thought registration) wired into run_selftests where the mod pattern allows.

## Watch out

- Neck-slot apparel collisions across 599 mods are silent — live-verify the
  pendant coexists with common neckwear.
- Never invent the faction defNames or the wyyyschokk defName — read them
  (RimSage/dump/mod XML) and record them in this file before coding.
- Thought stacking: cap one instance per observer (no per-pendant stacking).
