## spec
🔑 **THERE ARE TWO DIFFERENT FACTIONS BOTH CALLED "Blackstar Company", and the
world roster names the one that cannot generate.** Measured, not inferred:

| field | `AM_EnemyPirate` (what the roster names) | `Pirate` (what B43 actually reskinned) |
|---|---|---|
| label | `pirate scavenger` | **`Blackstar Company`** |
| modName | `Ancient urban ruins` (third-party) | `Core` |
| `settlementGenerationWeight` | 🔴 **0** | **0.6** |
| `hidden` | 🔴 **True** | False |
| `settlementTexturePath` | 🔴 **absent** | `World/WorldObjects/DefaultSettlement` |
| `requiredCountAtGameStart` | 1 | 1 |

⇒ **`AM_EnemyPirate` is a HIDDEN faction with ZERO settlement weight.** It is
designed never to appear on the Configure Factions screen and never to place a
settlement. Pointing the campaign's pirate faction at it is the entire defect.
Meanwhile `BlackstarCompany.xml` correctly patched vanilla `Pirate` — that def
**already** reads `Blackstar Company`, already generates at weight 0.6, already
has settlement art, and is one of the five reskinned rows in
`WORLDGEN_FACTION_CHECKLIST.md`. **Nothing is wrong with the faction. The roster
points at the wrong def.**

FIX — repoint `faction_def` from `AM_EnemyPirate` to `Pirate` in all four places
that carry it, and nowhere else:
  `world/ASHKARR_WORLDMAP_settlements.csv`      4 rows (the `faction_def` column)
  `src/RimMandrake/Utils/ashkarr_settle.py`
  `src/RimMandrake/Utils/ashkarr_paint.py`
  `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`
⚠️ `world/*.rws` also contain the string; those are **generated worlds, not
sources** — they are re-imported from the CSV, so do not hand-edit them.
⛔ **Do NOT "fix" `AM_EnemyPirate` by patching a texture onto it.** That is the
route `BLACKSTAR_HAS_NO_SETTLEMENT_ART_1` proposed before this was understood; it
would silence the crash and leave the faction **still hidden and still
non-generating**. See that item's superseding note.

## verify
Off the dump, `Pirate.label` is `Blackstar Company` and its
`settlementGenerationWeight` is 0.6 — **already true today, no patch needed.**
Then: zero occurrences of `AM_EnemyPirate` remain in the four source files above.

## criteria
🔴 **The owner opens Configure Factions and SEES a row reading `Blackstar
          Company`, and after worldgen the planet carries Blackstar holdings he did not
          place by hand.** Neither is possible today: `hidden=True` keeps it off that
          screen and weight 0 keeps it off the map.
          ⚠️ HOW THIS LIES: the authored settlement import places 4 Blackstar holdings
          regardless, because an import writes settlements directly and never consults
          `settlementGenerationWeight`. **A planet with 4 Blackstar holdings is therefore
          NOT evidence the faction generates.** Judge it on a world where the roster import
          has NOT run, or by reading the field.
🔑        SOURCE HALF DONE — REP, 2026-08-20, on the owner's "fix it ASAP" and "go as far
          as you can yourself". **All four source files repointed to `Pirate`; zero
          occurrences of `AM_EnemyPirate` remain in any of them.** 72 CSV rows preserved,
          4 now `Pirate`/`Blackstar Company`, both python tools still compile.
          ⛔ **BUILD: do NOT redo the find-and-replace.** What is left is not source work:
            1. the LIVE world still carries the old faction — `world_settlements_import`
               must be re-run for the planet to change. **That is bridge work and CHECK
               holds the bridge.**
            2. `world/*.rws` still contain `AM_EnemyPirate` **and should** — they are
               generated worlds, re-imported from the CSV, not sources. Do not edit them.
          ✅ Precondition verified before the edit, offline: the generated world already
          contains `<def>Pirate</def>`, so the repointed import RESOLVES rather than
          refusing the whole file the way an unresolvable faction would.
🔴        **ROOT CAUSE FOUND — BUILD, 2026-08-20, after REP's source fix. The diagnosis
          above is RIGHT and INCOMPLETE, and the missing half is why the repoint alone will
          not produce a Blackstar Company.**

          **1. Vanilla `Pirate` is never generated either, and it is not our doing.**
          `FactionGenerator.InitializeFactions` skips a def entirely when ANY other def
          declares `replacesFaction` at it with `requiredCountAtGameStart > 0`:
            `if (!ordered.Any(x => x.requiredCountAtGameStart > 0 && x.replacesFaction == facDef) && ...)`
          **Biotech's `PirateWaster` declares `replacesFaction: Pirate`, req 1.** So while
          Biotech is active — and it always is here — vanilla `Pirate` is displaced at
          worldgen no matter what label, weight or count we patch onto it. The faction the
          campaign reskinned is a faction the engine never creates.

          **2. It cannot arrive later.** `requiredCountAtGameStart` is read in exactly one
          place, reached only from `WorldGenStep_Factions`. **There is no load-time top-up**
          — the only one is `BackCompatibility.cs`, a hardcoded list of five vanilla
          factions (Empire, HoraxCult, Entities, TradersGuild, Salvagers). ⚠️ This
          CORRECTS a claim our own `RebelAlliance_Suppress.xml` and `Jawa_Patches/About/
          About.xml` both made; both are fixed, and the fact is in `BUILDABLE.md`.

          **3. Measured, not inferred, in the 08:36 autosave of the live world:**
            `<def>Pirate</def>` **0** · `<def>PirateWaster</def>` **0** ·
            `<def>AM_EnemyPirate</def>` **1** (hidden, which is why a non-hidden faction
            listing does not show it)
          ⚠️ **REP's precondition check was sound but aimed at a different artifact.**
          `world/WORLDMAP_gen.rws` DOES contain `<def>Pirate</def>` — but the world that is
          LOADED is not that file. Check the world you are importing into.

          🔴 **CONSEQUENCE FOR THE NEXT RE-IMPORT, and it is worse than the bug it fixes:**
          this item's own spec says the importer *"refuses the WHOLE import if any faction
          is unresolvable"*. The CSV now points 4 rows at `Pirate`, which is **not in the
          live world** — so a re-import could fail **all 72 rows** where it previously
          skipped 4. **Do not run it until the faction exists.**

          ✅ **THE FIX IS TO CREATE THE FACTION, NOT TO CONFIGURE IT.**
          `FactionGenerator.CreateFactionAndAddToManager(FactionDef)` is public and is
          exactly what `BackCompatibility` calls for its five. No bridge tool exposes it.
          ⇒ BUILD is adding `jawa/faction_create`. Until it deploys, the four Blackstar
          rows cannot land in this world by any route.
          ⚠️ **And decide which def before creating one:** `Pirate` carries our reskin and
          the right label, but Biotech will keep displacing it in any FUTURE worldgen, so
          creating it here fixes this world and not the next one. Whether to also patch
          `PirateWaster.replacesFaction` away is DECIDE's — filed as
          `PIRATE_REPLACED_BY_BIOTECH_1` in `queue/DECIDE.md`.

📌        MEASURED IN THE SAVED WORLD — REP, 2026-08-20 at shutdown. `b3af026` concluded
          Biotech's `PirateWaster` (`replacesFaction = Pirate`, confirmed in the dump)
          makes `InitializeFactions` skip `Pirate`, and that the roster therefore has no
          vessel. **In `world/WORLDMAP_gen.rws` that did not happen.** Parsed the faction
          objects directly — 22 of them, each a `<def>`/`<name>` pair:
            `<def>Pirate</def>` `<name>Blackstar Company</name>` `<loadID>10</loadID>`
          ⇒ **Blackstar is ALIVE in that world, on `Pirate`, already carrying the right
          name** — so the repoint lands on a faction that exists, and Blackstar is NOT one
          of the ten wearing dice-picked names (the ten are confirmed: `Jawa_Junkers` reads
          *Liliya's Stars*, `Jawa_HuttCartel` reads *Thiinum*).
          ⚠️ **`AM_EnemyPirate` is ALSO in that world**, as *The Scimitar Lions*. So the
          four settlements were NOT skipped for want of a faction, and that half of the
          earlier diagnosis is wrong — the cause is still open.
          🔴 **SCOPE, and it is the whole caveat:** this is the world **on disk**. BUILD
          measured the **live** world over the bridge and counted 16 factions, not 22.
          **They may be different worlds.** Nothing here contradicts a live reading; one
          `jawa/list_factions` against the live game settles which world is which, and
          until then neither number should be quoted as "the" faction count.

## notes
**from:** OWNER, 2026-08-20, verbatim: *"We really need to figure out why Blackstar, of all
the factions, does not generate. That's not acceptable and we should fix it ASAP
so it stops being a carried item. It's a fully specced faction, it's time it acted
like it."* Diagnosed by REP the same hour off the **fresh 578-mod dump**.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

doing
