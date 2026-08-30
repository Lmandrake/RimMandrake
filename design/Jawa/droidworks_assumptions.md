<!-- status: LIVE — the owner asked for this list verbatim, 2026-08-29:
     "Make a list of the assumptions you'd like me to check later." Check a box
     by ruling on it at the bench; each carries what changes if you rule the
     other way. -->
# Droidworks — assumptions awaiting the owner

## Platform boundaries
1. ✅ RULED YES (owner, 2026-08-29). **HAR stays as the one dependency.** "As independent as possible" read as
   independent of the DROID packs; HAR underpins 13 mostly non-droid mods in
   the load and stays regardless. If you want HAR gone too, races get
   reimplemented on raw humanlike ThingDefs — doable, roughly doubles the race
   authoring, and we lose HAR's body/needs tooling.
2. **"Retire" = remove from ModsConfig eventually, keep on disk.** Credits
   live in Droidworks' About.xml (guy762, Neronix17, JangoD'soul+Criz,
   Killathon). Private play, no redistribution — your words carried into the
   About text.
3. **Retiring ABF/Synstructs is NOT free**: KotOR Weapons and Armor + KotOR
   Resources/Materials (content we keep — the armoury uses those weapons)
   DECLARE it as a dependency. Assumed: declaration only, no hard runtime use —
   must be verified (minimal-list load without ABF, watch for errors) before
   ABF actually leaves ModsConfig. Same check for Asimov ← FSF Complex Jobs.
4. ✅ RULED CAPTURABLE (owner, 2026-08-29). **JDS Separatists become capturable on port** (spec §8.3 recommendation;
   the 2026-08-13 "never taken alive" ruling was platform-forced). Unruled —
   wave 3 assumes yes; say no and they get high energy-density detonation
   flavor instead.

## Art
5. **Yank keeps original texPath structure** so generated defs reference art
   unchanged; you regenerate freely later by overwriting files in
   `src/Jawa/Droidworks/Textures/` (same path = same def, no XML edit needed).
6. Droid Depot 1.6 art comes out of Unity AssetBundles — assumed the extracted
   PNGs are the same assets the game renders (validated only by file
   inspection until a live look).

## Numbers I picked (tune at the bench, none are canon)
7. **Detonation**: damage `50 × charge × energyDensity`, radius
   `3.9 × sqrt(scale)`; wreck threshold: no boom below 5% charge.
8. **Power cadence**: fall/day — battle 1.0 (daily top-off), astromech/labour
   0.33, protocol 0.033 (~monthly), per the design spec's prose.
9. **Reboot restores 15% power** so the droid can walk to a charger (phase 0
   has no charging building yet — the trio [nimbus/dock/socket] is next).

## Mechanics assumed viable, unproven in engine
10. A humanlike race with our non-organic flesh type **goes Downed on the
    Consciousness cap** (capacity-based downing) — the one step never observed
    live; phase-0 pilot proves it (also flagged in droid_ruling.md §5A).
11. **Food/rest suppression via HAR race settings** suffices for droids (no
    Biotech genes involved). If HAR can't fully suppress, fallback is a
    hediff/Harmony layer — small but unbudgeted.
12. **Mindless/programmable/sapient work gating** via one Harmony postfix on
    WorkTagIsDisabled (phase 1) — pattern assumed from ABF's existence proof.
13. **No Harmony at all in phase 0** — state 4 is vanilla death-with-corpse,
    state 5 is our comp on Notify_Killed, state 3 is a no-decay hediff.
    If play shows droid "death" needs interception (e.g. corpse-vs-object
    semantics), phase 0 grows the one risky Harmony unit after all.

## Loose threads
14. **82 `Asimov_EnergyNeed` strings sit in the frozen world save** with zero
    droid pawns scribed — unexplained; must be understood before Asimov leaves
    the mod list (likely harmless need-registry residue; UNCERTAIN).
15. Our 4 existing `Jawa_Droid_*` kinds (Free Droid Enclaves) ride Droid Depot
    races today; wave 2 re-points them to Droidworks races **at a save
    boundary you pick** — live campaign droids of those kinds would dangle
    otherwise.
16. Droidworks is **not yet in ModsConfig** — activation is yours at a
    start-prep pass (rimworld-start-prep rules apply; RimSort refresh trap).
17. The shop CUSTOMER layer (visitors with broken droids) still unruled as
    own-mod vs quest pack (design spec §11.3).
18. **A fifth mod holds KotOR droid plumbing**: the abstract race parent
    `guy762_KotORDroidBase` and the droid-slot equipment art
    (`droidshield_*`, `droidtech_*`, `hvyshield_*`) live in
    `guy762.KotORWeapons` (workshop 3254370945) — a mod we KEEP for the
    armoury regardless. Assumed fine to leave that art un-yanked for now;
    the def generator must read the base's fields from that mod's XML, not
    assume extraction.json has them. (Found by the art sweep, 2026-08-29.)
19. Two Droid Depot UI icons had bundle paths that differ from def texPaths
    (cultures/memes icons); extracted to the DEF paths. Assumed the def path
    is the truth (per reading-rimworld-graphics).
