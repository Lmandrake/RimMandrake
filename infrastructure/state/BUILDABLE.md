# BUILDABLE.md — what the stack can and cannot give us

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


BUILD publishes here. **One line per fact**, written when a limit or a capability is
learned that DECIDE would otherwise have to ask about: what a def type supports, what
a mod already gives us, what the engine refuses.

**Replace a superseded line. Never append a correction under it** — a stale line above
its own correction still gets read first.

Every line carries the date and how it was measured. A fact with no measurement behind
it does not belong here.

---

## What the stack already gives us

- **Lightsabers are LIVE and plentiful — 14 `ThingDef`s.** `Force_Lightsaber_Custom`
  (plain), `_Dual`, `_Curved`, `_Crossguard`, `_Shoto`, `_Inquisitor`,
  `_BuildYourOwn`, `_UniqueObi`, `_UniqueAnakin`, `Force_Ezra_BlasterLightsaber`,
  plus throw/whip/projectile defs. Mod `lee.theforce.lightsaber`, active.
  *Measured 2026-08-15 against the def dump refreshed at that load.* ⚠️ Absence from
  a screenshot is not absence from the build — that inference nearly became a
  "missing weapon" item.
- **All 8 authored Jawa `FactionDef`s load.** `Jawa_IndigenousTribes` (label "Jawa
  Trade Moot"), `Jawa_HuttCartel`, `Jawa_Junkers`, `Jawa_DeepwaterCompact`,
  `Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_AscendantHelix`,
  `Jawa_FreeDroidEnclaves`. *Live via `jawa/get_def`, 8/8, 2026-08-15.*

## What the engine refuses, and what that costs

- **Only `Jawa_IndigenousTribes` carries `requiredCountAtGameStart`.** The other
  seven are `canMakeRandomly` with no required count, so they default to **0** at the
  Configure Factions screen and a world generated without hand-ticking them contains
  none of them. **Worldgen happens once.** *Measured on disk 2026-08-15; filed as
  `seven-factions-have-no-required-count-9c4e17`.*
- **A `PatchOperationFindMod` that FAILS proves the mod is PRESENT.** An absent mod
  returns **true** and logs nothing, so the failure can only mean an inner op broke.
  `<mods>` matches the About.xml `<name>`; `<activeMods>` lists the `packageId`.
  *2026-08-15, cost one wrong diagnosis and two seats' time.*
- **Patches run on RAW XML, before `ParentName` inheritance.** A def that only
  *inherits* a container has no such node to patch, so an add-if-missing `<nomatch>`
  aimed at that container fails — and `PatchOperationSequence` stops at the first
  failure, silently killing every op after it. **Any generator that decides what to
  patch by reading a RESOLVED def dump will emit this bug.** *2026-08-15.*
- **Nothing on the 155-tool bridge can order an attack.** `jawa/order_pawn` issues a
  GOTO even with a `targetId`; drafted pawns hold at `Wait_Combat`; spawned hostiles
  have no lord and idle. Blocks every combat test. *2026-08-15,
  `bridge-cannot-order-a-melee-attack-3f8c21`.*

## Deploy targets that are not `Mods/`

- **`Xenotypes/*.xtp` and `Ideos/*.rid` are deploy targets.** They live under
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`,
  nothing syncs them from the repo, and `deploy_custom_mods.py` does not cover them.
  A `.xtp` **bakes at world creation** and a stale one drops renamed genes **silently
  in play**. *2026-08-15: `MandrakeJawa.xtp` had been correct in the repo since
  `c57f347` and stale in the game for a day, dropping four genes.*
- **An offline validator cannot catch a stale `.xtp`.** It validates the file you
  point it at; the game reads a different copy. Check the deployed one.
- 🔴 **An offline validator answers "is this file self-consistent", never "is the file
  the game reads correct".** `validate_save_artifact.py` returned **36/36 resolve** on
  `MandrakeJawa.xtp` twice — once on a file the running engine was contradicting, once
  on a freshly deployed one it had not yet read. Same output, opposite meanings. A
  deploy is **FIX DEPLOYED, UNVERIFIED** until a startup log shows zero
  `Could not load reference to`. *2026-08-15.*
