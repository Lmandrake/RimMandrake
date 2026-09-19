# XML_PATCH_VALIDATION_SWEEP_1 — static-validate all authored XML against the live 589-mod dump

## spec

Answer the owner's question ("how are we gonna validate all that XML") for the static
half of the problem: does every authored patch/def actually match and resolve against
the mod list the game will really build. (The runtime half — Config errors a load
actually logs — is the separate, already-filed `LOAD_CONFIG_ERROR_SWEEP_1`.)

Ran `skills/rimworld-modding/scripts/validate_patch.py` across every authored XML file —
`src/RimMandrake/`, `src/RimStarWars/`, `src/RimUtinni/`, and the still-unmigrated
`src/SPLIT_Phase3/Jawa_Patches/` — against a FRESH live def dump
(`.../DefDump/captures/2026-09-04T02-23-44Z`, fingerprint `e86680d6d5c586ba`, confirmed to
match the live 589-mod `ModsConfig.xml` via `refresh.py --fingerprint` before use) and
the three real `--defs` scan roots (Workshop content, `RimWorld/Mods`, `RimWorld/Data`).

**616 files scanned. Raw result: 65 errors across 17 files, 13,409 warnings.**

## What the 65 errors actually were

Every single one was investigated against real source (mod XML on disk, not guessed —
this project's hard rule) before being called anything. None were guessed-and-fixed.

**32 errors — validator false positives, no code defect, nothing to fix:**
- **9 errors, `RSW_VFEP_Warcasket_Hazard`** (`Warcasket_HazardRetune.xml`) and
  **2 errors, `RSW_DW_Race_OuterRim_MuckrakerDroid`** (`MuckrakerChassis_TheftHauler.xml`):
  one is a documented dump blind spot (the def's XML element is the C# class name
  `VFEPirates.WarcasketDef`, not `ThingDef` — the dump has no file for that type at
  all, and the source file's own header already says so); the other guards content
  from `mandrake.rsw.droidworks`, which exists in our source tree but is **not currently
  deployed/active** (only `mandrake.rsw.msedroidfix` is) — a correct, safe no-op.
- **~21 errors across 9 files under `Absorbed_KotorCore/`**: every one of these
  "missing" `texPath`s (`Things/Pawn/Animal/Iguana/Dessicated_Iguana`,
  `Things/Mote/Smoke`, `Things/Projectile/Needle`, `Things/Building/Linked/*`, etc.) is
  a genuine, currently-used **vanilla** RimWorld texPath. Vanilla ships its art packed
  inside Unity asset bundles under `Data/Core|Biotech|Anomaly|Odyssey` — there is no
  loose `Textures/` folder to scan at all — so a directory-scanning validator can never
  resolve a vanilla texPath from any `--defs` root. The donor mod (`guy762.mm.kotorcore`)
  is reusing vanilla art exactly as vanilla's own defs do; this is not a defect in the
  absorption. **`validate_patch.py` itself has a structural blind spot here** — worth a
  follow-up so this whole class stops showing up as false ERRORs on every future run.

**28 errors — `PatchOperationConditional`-guarded references to content in mods that
are not currently active.** Verified individually against each named mod's real
installed XML (not guessed): `JDSCIS_CIS_Faction` (Separatist Droid Army mod, inactive),
`Titan` (the `titans.fl` Titan race mod, inactive — NOT the same as `XylTitan`, which
IS active and correctly patched elsewhere in the same file), `guy762_KotORFaction_Civilians`
(`guy762.KotORFactions`, inactive), `guy762_brifle_rohlan`/`guy762_brifle_sith` (`guy762.KotORWeapons`,
inactive — confirmed the defNames are real in that mod's current XML), and
`Bullet_ArchotechChargeBlasterHeavy` (`rpgwanderer.opturret`'s Archotech Blaster
Turret, inactive — and our own `Absorbed_OPTurret.xml` already says it retired and
re-baked this as `RSW_Bullet_ArchotechChargeBlasterHeavy`, so `Armoury_RangedDamage.xml`'s
reference to the old external name is likely vestigial too; not touched, flagged for
whoever next opens that file). All correct, guarded, safe as-is.

**5 errors — FIXED, genuine dead patch blocks, removed** (`fa437162`… see commit
`7fdf3a48`): `CAEvilSacrilegHunters` and `CAFriendlyMechanoid` in
`src/RimUtinni/FactionSlate/Patches/OnlyOurFactions.xml`. Verified against Caravan
Adventures' own current 1.6 `FactionDefs.xml`: both defNames were removed from the mod
going into 1.6, permanently (not a version fluke) — the surviving faction,
`CASacrilegHunters`, is already patched separately and untouched. Both blocks were
already-harmless Conditional-guarded no-ops (this was known since
`JAWA_FACTION_SLATE_LOAD_ORDER_1`, 2026-08-29) — this just drops the two that can never
fire again under any current build of that mod, and updates the About.xml note that
had flagged them.

**6 errors — genuine, unfixed, needs the art pipeline, not a path fix:**
`RSW_Karrask`, `RSW_KarraskShedRaw`, `RSW_KarraskPlate` (our own original creature,
`src/RimStarWars/Livestock/Defs/`) reference `texPath`s with **no PNG anywhere in the
repo** under any `Textures/` tree (confirmed — only unrelated mockup art exists at
`src/RimStarWars/Livestock/art/mockups/karrask_opt2.png`/`karrask_opt3.png`, not under
a Textures folder). This creature will render as a pink placeholder until art is
generated via the `generating-rimworld-sprites` skill. **Not attempted here** — art
generation is a separate, iterative pipeline, out of scope for a code-review pass.

## Config-error baseline (the sibling live-load check), re-confirmed same session

Game is UP on the full 589-mod list and its current `Player.log` shows exactly 31
`Config error in` / 5 cross-reference lines, matching `LOAD_CONFIG_ERROR_SWEEP_1`'s
frozen baseline byte-for-byte (same 16 unique sources, same counts) — no drift, no new
defects since that baseline was frozen 2026-09-03. That item's actual fix work (the 19
third-party issues) is still open and still explicitly low-priority; nothing here
changes that call.

## verify

- `validate_patch.py` run recorded above; findings individually source-verified, not
  guessed (two dedicated investigation passes against real Workshop mod XML).
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"` on both edited files
  after the fix — both well-formed.
- Re-ran `validate_patch.py` on `OnlyOurFactions.xml` alone post-fix: 0 errors (was 20).

## criteria

1. Every claimed defect is backed by a read of real source, not a guess — done for all
   10 distinct broken-defName root causes and all ~9 texPath root causes.
2. The 5 genuinely-dead patch entries are removed; nothing else in the 65 was touched
   without individual verification that touching it was safe.
3. **Recommended follow-up, not done here** (flagging, not fixing, per scope):
   - `validate_patch.py` needs a fix for the vanilla-packed-asset texPath blind spot —
     it currently reports a false ERROR for any def reusing vanilla art by texPath, and
     this session found 21 of them in one absorbed-content file alone. Also flagged
     separately this session (different review pass): a `MayRequire`-only guard is
     never recognized (false "unguarded" WARN, and a legitimate mod-absent case reports
     as a hard ERROR instead of a no-op), and `check_dict_keyed_fields()` — the check
     for this project's own headline `<li>`-in-dict-field defect — only runs on the
     `<Patch>` code path, not on `<Defs>` files. All three belong to a future
     `skills/` curation pass (skill scripts are edited in dedicated fresh-context
     sessions per CLAUDE.md, not ad hoc mid-sweep).
   - `Armoury_RangedDamage.xml`'s `Bullet_ArchotechChargeBlasterHeavy` reference is
     likely vestigial now that `Absorbed_OPTurret.xml` re-baked it under our own name —
     worth a look next time that file is open.
   - `RSW_Karrask` art (3 defs) needs generating.
