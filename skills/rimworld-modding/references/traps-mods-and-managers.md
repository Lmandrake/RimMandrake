# traps — The mod stack, RimSort and Workshop

Load order, mod managers, Steam, assemblies, and mod-list state.

**Read this one when a mod is absent, dead, or not behaving like the files say it should.**

Entry format, admission test and the append rule: `references/traps.md`.

---

### RimSort sort rules saved into Community Rules vanish silently
**Symptom:** a load-order rule was created and appeared to save; on reopening it was gone, and the load order was unchanged.
**Cause:** the rule had been added to the **Community Rules** database, whose configured source was `None`. With no backing database there is nowhere to write, and the save is discarded without an error.
**Fix:** put local rules in **User Rules**, which is the personal, always-writable layer. Community Rules is for contributing upstream, and requires a configured database source.
**Recurs when:** any RimSort setting that will not persist — check which layer received it before assuming the tool is broken.

---

### RimSort's local and workshop folder paths were swapped, so custom mods were never scanned
**Symptom:** hand-authored mods in `RimWorld/Mods/` never appeared in the mod list, no matter how correct their `About.xml` was.
**Cause:** in RimSort's settings, `local_folder` held the *Workshop* path and `workshop_folder` was empty.
**Fix:** point `local_folder` at `<RimWorld>/Mods` and `workshop_folder` at `steamapps/workshop/content/294100`.
**Recurs when:** "my new mod doesn't show up" — the mod folder and the scanned folder are two separate assumptions and only one of them is yours; verify the manager is looking where you are writing before debugging the mod.

---

### A mod shipped an assembly referencing an AssetBundle it never packaged
**Symptom:** `Unable to open archive file: …/SWCP-UnityAssets/…/SWCPshaders`, then a `NullReferenceException` in `BuildableDef.ResolveIcon` inside `LongEventHandler.ExecuteToExecuteWhenFinished` (Star Wars KotOR Resources & Materials).
**Cause:** upstream packaging omission — the bundle is absent from the Workshop upload *and* the GitHub repo. Confirmed by clean redownload, by the repo tree (no `.gitignore` excluding it), and by searching all 1,211 installed mods for any `*UnityAssets*` directory (zero matches, so no companion mod supplies it).
**Fix:** none locally; reported upstream, requesting the bundle plus a null-check that degrades to "no custom shaders". ⚠️ That issue also claims the throw "aborts the remainder of the post-load queue" — **that claim is wrong**; see `traps-diagnosis.md`.
**Recurs when:** any missing-artefact error — run clean redownload, then the upstream repo tree, then a filesystem-wide search across every installed mod, in that order; the third also rules out a companion mod being the real supplier.

---

### Subscribed to a Workshop item that Steam has removed
**Symptom:** `Created WorkshopItem for <id> but there is no folder for it`, repeated each launch.
**Cause:** the item was taken down from the Workshop. The subscription persists; the content can never download.
**Fix:** unsubscribe. Nothing else clears it.
**Recurs when:** a stable "no folder for it" line — it is an *account* state problem, not a game state problem, and no amount of verifying files will fix it.

---

### Bulk Workshop metadata: use the Steam Web API, not the item pages
**Symptom:** parallel fetches of `steamcommunity.com/sharedfiles/filedetails/` returned HTTP 429 and an audit of ~125 mod IDs stalled.
**Cause:** rate limiting on the public item pages.
**Fix:** one POST to `api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/` with `itemcount` plus `publishedfileids[0..n]` returns all of them in a single unthrottled call.
**Recurs when:** parsing that response — a substring test for `success":1` also matches `success":15` (Access Denied) and reports a failed item as a success. Capture the digits with a regex.

---

### "Mods with Missing Publish Field ID" in RimSort is not an error
**Symptom:** a freshly deployed local mod appears in RimSort under the heading **Mods with Missing Publish Field ID**, with a blank Published File ID and `Source: Unknown`.
**Cause:** `About/PublishedFileId.txt` is written by Steam when a mod is *uploaded to the Workshop*. A local mod has never been uploaded, so the file correctly does not exist. RimSort groups by provenance, not by health.
**Fix:** none. Do not hand-create `PublishedFileId.txt` — a fabricated ID points the updater at someone else's Workshop item.
**Recurs when:** reading any RimSort heading — provenance categories sit in the same panel as error categories. (Here the mod being listed at all proved the local-folder scan path was finally configured right.)

---

### Disabling a mod orphaned its add-on's assembly and killed Prepatcher outright
**Symptom:** a dialog before the main menu, and `Prepatcher Error: Fatal error while reloading: System.Reflection.ReflectionTypeLoadException — Could not load type of field VSIERationalTraitDevelopment.SocialInteractionsManager_TryAssignThoughtsAfterRaid+<>c__DisplayClass1_0:__instance' (1) due to: Could not resolve type with token 0100002a at Prepatcher.Process.FreePatcher.FindAllFreePatches`.
**Cause:** Vanilla Social Interactions Expanded was disabled as a bisect step while `Stagz.VSIERationalTraitDevelopment` — a *separate* Workshop mod that hard-depends on it — stayed active. Its every type references now-absent VSIE types, so `Assembly.GetTypes()` throws. Prepatcher enumerates every active mod assembly looking for `[FreePatch]` methods and does not guard the `GetTypes()` call, so one orphaned assembly aborts the whole free-patch pass; the game then loads with **unpatched** assemblies, silently.
**Fix:** disable the orphaned add-on too. Dependency checks run in **both** directions — before disabling mod X, ask "who needs X". Scan every *active* mod's `About.xml` for the packageId (resolve the set with `rimworld_loadset.build_load_set`, never by listing folders) **and** scan DLL bytes for the assembly name (`needle = b"VanillaSocialInteractionsExpanded"`); only the byte scan catches an undeclared dependency.
**Recurs when:** any framework that reflects over the entire active assembly set — Prepatcher, Harmony `PatchAll` scanners. Restrict the byte scan to resolved `contentDirs`: `Intimacy - Friends n' Lovers` ships `Compatibility assemblies/VSIE/Assemblies/VSIECompatibility.dll`, never loaded and harmless, which a whole-folder scan reports as a second orphan.

---

### Mod-list state on disk is not authoritative while the game is running
**Symptom:** packageIds still present in `ModsConfig.xml` and mod folders still present under `294100/` after the owner had removed and unsubscribed them, reported repeatedly as "the removal didn't land". Both readings were accurate; both conclusions were wrong.
**Cause:** RimWorld holds its active mod list **in memory** while running and rewrites `ModsConfig.xml` on exit; Steam will not remove an unsubscribed mod's folder while the game has files open in it. For the whole of a live session the on-disk state reflects the load that is running, and a manager's mid-session edits can be overwritten when the game closes.
**Fix:** establish whether the game is running before making any claim. `Player.log`'s mtime versus `ModsConfig.xml`'s is the cheap tell — if the log is older than the config, a re-sort happened after the load and the running game does not match the file. Report what the timestamps imply; do not assert a state.
⛔ **Does NOT extend to RimSort.** RimSort does not save on exit — it writes only when the owner explicitly clicks Save. Editing `ModsConfig.xml` while RimSort is open is safe, and "close RimSort first" is **never** a precondition for anything. The real hazard runs the other way and is small: after an external edit RimSort's in-memory view is stale, so a later Save would write the old list back. Mitigation is one sentence — *"RimSort is open, hit Refresh"*.
**Recurs when:** any file a running process owns — config written on exit, a mod-settings file that rewrites only when its settings window closes, a live def dump describing the mod set at capture time rather than now.

---

### Three mods shipped the base game's own assemblies, and one shipped all of it
**Symptom:** Interaction Bubbles never drew a bubble and its shift-click settings never opened, while its toggle icon rendered fine. No exception, no log line, nothing to bisect — and a 23-minute load wasted on two dead-end hypotheses. Dubs Performance Analyzer had already printed the cause: `[Analyzer] Mod Tribal Furniture has packaged the base-game Rimworld assemblies`.
**Cause:** `Xercaine.Tribal.Furniture` (WS 3671245310) shipped **26 DLLs in `Assemblies/`, of which exactly one — `TribalFurniture.dll`, 25 KB — was the mod**; the rest were the game and Unity runtime, including a byte-identical `Assembly-CSharp.dll` (15,777,280 bytes). RimWorld loads *every* DLL in a mod's `Assemblies` folder via `Verse.ModAssemblyHandler::ReloadAll` → `System.Reflection.Assembly::LoadFrom`, which returns the **already-loaded** assembly of the same identity (Mono has no separate load contexts and dedupes by identity, mono/mono#8149). The analyzer keys its map by `Assembly` object, so the warning firing is itself proof no second copy loaded. The real costs: all of vanilla RimWorld is attributed to a furniture mod in every type→mod map (analyzer, exception attribution, Harmony patch-owner reporting), `AssemblyIsUsable` runs `GetTypes()` over a 15.7 MB image at load, and 22.7 MB downloads for a 25 KB payload.
**Fix:** sweep every active mod's resolved `contentDirs`/`Assemblies` against the DLL names in the game's `RimWorldWin64_Data/Managed`. It found three offenders: `Xercaine.Tribal.Furniture` (24 strays), `petetimessix.researchreinvented.steppingstones` (2 `UnityEngine.*`, byte-identical), and `tickleyourpawn.core` (`mscorlib.dll`, **not** byte-identical). Relocate rather than delete, with a manifest recording each file's size and byte-identity — Steam may restore them on a validation pass.
**Recurs when:** a packaged DLL whose identity is *not yet loaded* when the mod loads — Mono's dedup makes the **mod's copy win process-wide**, so byte-identical copies are inert but a non-identical `mscorlib.dll` genuinely substitutes for the game's. Suspect this when a mod's code demonstrably runs but its observations of the world are wrong, with no exception anywhere.

---

### 38. A dead mod that the dead-mod grep cannot see
**Symptom:** `RimAI Core` was silently doing nothing while the two standing triage greps — `static constructor` and `TypeInitializationException` — were both **0**. What was actually in the log: `ReflectionTypeLoadException getting types in assembly RimAI.Core` / ``Could not resolve type with token 0100006a from typeref (expected class 'RimAI.Framework.Contracts.Result`1' in assembly 'RimAI.Framework.Contracts')``, plus three discarded defs — `Exception loading def from file … Could not find type named RimAI.Core.…CompProperties_AiServerBuffs`.
**Cause:** `RimAI.Framework.Contracts.dll` ships in the *Framework* mod, which loaded at 279 — **after** Core at 278. RimWorld loads mod assemblies in load order, so Core's typerefs could not resolve. Core's `About.xml` declares `modDependencies` on the framework and **no `loadAfter`**: `modDependency` does not imply load order, here with an assembly rather than a def.
**Fix:** put the dependency first in **both** places — RimSort `userRules.json` (User Rules; Community Rules vanish silently) *and* `ModsConfig.xml`. Add `ReflectionTypeLoadException` and `Could not resolve type with token` to the dead-mod greps: a cctor that never runs because its type never loaded produces neither standing string.
**Recurs when:** `Could not find type named X` — a third cause, after "mod absent" and "type renamed", is an assembly present but loaded too early to resolve its own references. Sweeping all 568 `About.xml` files for `modDependencies` edges pointing *later* found 8 inversions, of which exactly one logged anything; parse the XML and take the root's direct child, because a naive first-`<packageId>` regex reads a *dependency's* id as the mod's own and misses the very mod that motivated the sweep.

---
