# traps — The mod stack, RimSort and Workshop

Load order, mod managers, Steam, assemblies, and mod-list state.

**Read this one when a mod is absent, dead, or not behaving like the files say it should.**

What goes in, and what does not: `references/traps.md`.

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

### Three mods shipped the base game's own assemblies, and one shipped all of it
**Symptom:** Interaction Bubbles never drew a bubble and its shift-click settings never opened, while its toggle icon rendered fine. No exception, no log line, nothing to bisect — and a 23-minute load wasted on two dead-end hypotheses. Dubs Performance Analyzer had already printed the cause: `[Analyzer] Mod Tribal Furniture has packaged the base-game Rimworld assemblies`.
**Cause:** `Xercaine.Tribal.Furniture` (WS 3671245310) shipped **26 DLLs in `Assemblies/`, of which exactly one — `TribalFurniture.dll`, 25 KB — was the mod**; the rest were the game and Unity runtime, including a byte-identical `Assembly-CSharp.dll` (15,777,280 bytes). RimWorld loads *every* DLL in a mod's `Assemblies` folder via `Verse.ModAssemblyHandler::ReloadAll` → `System.Reflection.Assembly::LoadFrom`, which returns the **already-loaded** assembly of the same identity (Mono has no separate load contexts and dedupes by identity, mono/mono#8149). The analyzer keys its map by `Assembly` object, so the warning firing is itself proof no second copy loaded. The real costs: all of vanilla RimWorld is attributed to a furniture mod in every type→mod map (analyzer, exception attribution, Harmony patch-owner reporting), `AssemblyIsUsable` runs `GetTypes()` over a 15.7 MB image at load, and 22.7 MB downloads for a 25 KB payload.
**Fix:** sweep every active mod's resolved `contentDirs`/`Assemblies` against the DLL names in the game's `RimWorldWin64_Data/Managed`. It found three offenders: `Xercaine.Tribal.Furniture` (24 strays), `petetimessix.researchreinvented.steppingstones` (2 `UnityEngine.*`, byte-identical), and `tickleyourpawn.core` (`mscorlib.dll`, **not** byte-identical). Relocate rather than delete, with a manifest recording each file's size and byte-identity — Steam may restore them on a validation pass.
**Recurs when:** a packaged DLL whose identity is *not yet loaded* when the mod loads — Mono's dedup makes the **mod's copy win process-wide**, so byte-identical copies are inert but a non-identical `mscorlib.dll` genuinely substitutes for the game's. Suspect this when a mod's code demonstrably runs but its observations of the world are wrong, with no exception anywhere.

---

### A dead mod that the dead-mod grep cannot see
**Symptom:** `RimAI Core` was silently doing nothing while the two standing triage greps — `static constructor` and `TypeInitializationException` — were both **0**. What was actually in the log: `ReflectionTypeLoadException getting types in assembly RimAI.Core` / ``Could not resolve type with token 0100006a from typeref (expected class 'RimAI.Framework.Contracts.Result`1' in assembly 'RimAI.Framework.Contracts')``, plus three discarded defs — `Exception loading def from file … Could not find type named RimAI.Core.…CompProperties_AiServerBuffs`.
**Cause:** `RimAI.Framework.Contracts.dll` ships in the *Framework* mod, which loaded at 279 — **after** Core at 278. RimWorld loads mod assemblies in load order, so Core's typerefs could not resolve. Core's `About.xml` declares `modDependencies` on the framework and **no `loadAfter`**: `modDependency` does not imply load order, here with an assembly rather than a def.
**Fix:** put the dependency first in **both** places — RimSort `userRules.json` (User Rules; Community Rules vanish silently) *and* `ModsConfig.xml`. Add `ReflectionTypeLoadException` and `Could not resolve type with token` to the dead-mod greps: a cctor that never runs because its type never loaded produces neither standing string.
**Recurs when:** `Could not find type named X` — a third cause, after "mod absent" and "type renamed", is an assembly present but loaded too early to resolve its own references. Sweeping all 568 `About.xml` files for `modDependencies` edges pointing *later* found 8 inversions, of which exactly one logged anything; parse the XML and take the root's direct child, because a naive first-`<packageId>` regex reads a *dependency's* id as the mod's own and misses the very mod that motivated the sweep.

---

### RimSort's "ignore" dismisses a WARNING, not your sort rules
**Symptom:** the owner clicks *ignore* on RimSort's "no Publisher ID" complaint about locally-authored mods, several times a session, and reasonably fears the dismissal is also discarding the User Rules that pin those same mods' load order. A mod that will not stay where it was put makes the fear look confirmed.
**Cause:** they are **two separate databases under `AppData\Local\RimSort\dbs\`, both keyed by `packageId`, and neither reads the other.** `ignore.json` is self-described as *"Mods to ignore when checking for missing properties (identified by packageid)"* — pure warning suppression. `userRules.json` holds the sort rules. Dismissing a warning cannot touch a rule.
**Fix:** read RimSort's own log rather than reasoning about the UI. `AppData\Local\RimSort\Logs\RimSort.log` prints the count on every start:
```
read_rules_db: Checking Rules DB at: ...\dbs\userRules.json
read_rules_db: DB exists!
read_rules_db: Loaded 13 additional rules
```
**Count the rules in the file and check the number matches.** 2026-08-13: 7 existing + 6 added = the 13 it logged, so every rule loaded. Two independent confirmations agreed — the log count, and `ignore.json`'s mtime (17:24) being *later* than `userRules.json`'s (17:19) with the rules still intact.
⚠️ **On the field itself — why it is absent and why never to fabricate one — see "Mods with Missing Publish Field ID in RimSort is not an error" above.** This entry is only about whether *dismissing* the warning costs you anything. It does not.
**Generalises to:** any tool where a dismissal dialog and a behaviour store are different files. **The dialog is not the state.** Before believing a UI action had a side effect, find the file it writes and diff it — and prefer a log line that *counts* what was loaded over any inference from the interface.

### A reskin whose donor ships art LOOSE fails silently if it loads first
**Symptom:** an art-replacement mod is deployed, enabled, correctly named, throws nothing, and is simply invisible in game — the original art still draws.
**Cause:** when both donor and reskin ship textures **loose** (not in an AssetBundle), nothing arbitrates but **load order** — last writer wins. Placed before its donor, the reskin loads, is overwritten, and RimWorld logs **nothing at all**, because no error occurred. Where the donor serves from an **AssetBundle**, loose beats bundle regardless and order is irrelevant.
**Fix:** for every reskin, establish which way the donor ships its art, and pin `loadAfter` in `userRules.json` — not just a hand-placement in `ModsConfig.xml`, which the next Sort discards. 🔴 **Do NOT add `loadBottom` to a reskin.** ❌ The reason given here until 2026-08-20 — *"`loadBottom` outranks `loadAfter`"* — was **wrong**, and so was this skill's opposite claim that it is *"only a hint"*. Read out of RimSort's source: `loadBottom` is tier membership, and the four-tier sort **silently drops any `loadAfter`/`loadBefore` edge crossing a tier boundary**. For a bottom-tier reskin the `loadAfter` edge is discarded but the mod still lands after a normal-tier donor, so the rule is **redundant rather than defeated** — and the genuinely broken pairing is `loadBottom` + `loadBefore`. Either way: write `loadAfter`, leave `loadBottom` off. Owner of this fact: `skills/rimworld-start-prep/SKILL.md`.
**Verify positionally, never by assumption:** read both indices out of `<activeMods>` and assert `reskin_idx > donor_idx`. Also assert the **donor is active at all** — a reskin whose donor is disabled fails the same invisible way.
**Generalises to:** every last-writer-wins resource with no conflict detection — texture overrides, loose XML patches on the same node, two mods writing the same def. **The absence of an error is not evidence of success**, and these are exactly the failures a clean log will never show you.

### A delete in a Steam-synced folder is undone by the next launch
**Symptom:** 27 savegames and 178 screenshots were deleted on the owner's order, `Saves/` verified **empty** immediately afterwards, and the loss was recorded as **irreversible**. Six hours later the game launched and **26 `.rws` totalling 701 MB were back, with their ORIGINAL mtimes** — `New Arrivals2.rws` at 43,738,239 bytes, mtime 09:46, byte-identical in size to the pre-delete record. The `Saves/` directory mtime was the launch time.
**Cause:** **Steam Cloud.** RimWorld's `AppData\LocalLow\Ludeon Studios\...` tree is cloud-synced, so a local delete is a local *divergence*, not a deletion. On the next launch Steam reconciles and re-materialises every file the cloud still holds. The immediate post-`rm` check is what makes this convincing: `Saves/` genuinely was empty, so the delete "succeeded" by every check available at the time.
**Fix:** **Verify a deletion AFTER the owning application has next started, not immediately after the `rm`.** To make it stick, Steam Cloud must be disabled for the title first (Properties → General → Steam Cloud), and only then delete. Also check `du -sh` and the file count, not just that a `ls` looks empty.
🔴 **Never report a deletion as "irreversible" from a post-`rm` check alone.** That claim was propagated into a queue and told other seats their measurements were the only surviving record and not to file bugs when a savegame tool found nothing — both wrong, and both would have cost someone a hunt.
**Generalises to:** every cloud-mirrored tree — Steam Cloud, OneDrive-redirected `Documents`, Dropbox, iCloud Drive. **The filesystem is not the authority when something else holds a replica.** The same shape covers a mod folder Steam restores on a validate pass, and it is why "the file is gone" and "the data is gone" are different claims.

### A def deployed AFTER launch is invisible to the running game, and looks perfectly deployed on disk
**Symptom:** a fix is committed, deployed to the Steam `Mods` tree, and confirmed present — repo copy and game copy identical, right bytes, right path. It then fails to appear in the running game, and the failure is indistinguishable from the bug it was meant to fix. 2026-08-14: the ground hulk's `minSpacing 85 -> 0` fix would have been tested on the process that still held `minSpacing 85`, and a no-show would have been recorded as a **third** consecutive failure of a def that was already correct.
**Cause:** **RimWorld reads defs exactly once, at startup.** Deploying to disk changes what the *next* launch will load and nothing about the process already running. Every ordinary check — mtime, diff, `ls` — inspects the disk, which is right, rather than the process, which is stale.
**Fix:** compare the deploy time against the process start time before trusting any live test.
```bash
tasklist.exe | grep -i rimworld            # then read StartTime for the PID
find "<Steam>/steamapps/common/RimWorld/Mods" -newermt "<process StartTime>" -type f
```
**Any file that returns is invisible to the running game.** ⚠️ **The bridge cannot answer this for you** — `jawa/get_def` returns the def that was *loaded* and does not expose most fields (`minSpacing` came back `extra: null`), so a successful read is not proof the def is current. **The mtime is the evidence.**
🔴 **For a map-generation def, the bar is higher still: a cold load is necessary but not sufficient — the map must be GENERATED after it.** A `GenStepDef` or `terrainPatchMaker` runs at map-gen only, so loading a save made by the old process shows the old result forever.
**Generalises to:** every long-lived process that reads configuration once — and to the general shape *"I verified the artifact, not the consumer"*. When a fix is deployed while the thing under test is already running, **the disk is not the system under test.** Ask what time the consumer last read it, and treat a post-launch deploy as a scheduled change, not a live one.

**The three-command check** *(moved from `SKILL.md` §6b, 2026-08-14; the rule
stayed there, this is the recipe)*:

```bash
# the process start time IS the def-read time -- RimWorld reads defs once, at launch
powershell.exe -NoProfile -Command "Get-Process RimWorldWin64 | Select Id,StartTime"
find "<game>/Mods" -newermt "<that StartTime>"        # anything listed is NOT loaded
md5sum <repo copy> <deployed copy>                   # differ => the game has the other one
```

**Two measured cases, both reported as done, both false:**

* A `GenStepDef` fixed and deployed at 01:33:48 against a process started 01:03:26.
  The map showed the OLD behaviour and read as a third failure of the fix.
* A DLL verified with `strings -a -el` in the repo — md5 `b7730027` — while the game
  held a different build, `82b48e53`, dated before the launch. "Verified in the
  binary" and "verified in the game" are different claims.
