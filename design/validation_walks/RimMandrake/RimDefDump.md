# RimDefDump — validation walk
subject: src/RimMandrake/RimDefDump  (packageId mandrake.rm.rimdefdump)
deps: none
list: minimal
status-hint: local research tooling (not gameplay) — dumps the post-patch def database to JSON at game load or on demand, INERT unless a marker file exists at `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt`.

## must be true
- With no marker file present, the dumper does nothing but log `"[RimMandrake.RimDefDump] inert (no dump_request.txt). To enable, create: " + marker` and is otherwise a complete no-op — no defs, no Harmony, no gameplay behaviour (`RimDefDump/Source/DefDumper.cs:140`, About.xml).
- With a marker present, it writes a capture to `DefDump/captures/<capturedUtc>/` (an ISO-ish timestamp id, `now.ToString("yyyy-MM-ddTHH-mm-ssZ")`) via a `.writing` staging dir that's cleared before use and only becomes the final dir on successful publish (`RimDefDump/Source/DefDumper.cs:99,194-198`).
- Marker contents select scope: empty or `"animals"` → `animals.json` + `manifest.json` only (fast); `"all"` → the above plus `defs/<DefType>.json` for every def type with a database (slow, large) (`RimDefDump/Source/DefDumper.cs:189`, About.xml).
- An unrecognised marker mode logs `Log.Warning` and the dump still runs (defaulting to `"animals"`), rather than crashing the load (`DefDumper.cs:189` and `:152`).
- Retention prunes old captures and logs each prune (`"pruned old capture " + ids[i]`) or, on failure, warns rather than throwing (`DefDumper.cs:308,312,319`).
- A capture id collision refuses to overwrite: `Log.Error("... capture " + captureId + " already exists; ...")` (`DefDumper.cs:258`).
- Two dev-mode debug actions exist under category `"RMDefDump"`: `"Dump defs now (all)"` and `"Dump defs now (animals)"` (`RimDefDump/Source/DefDumper.cs:62-68`), each routing to `DefDumper.RunOnDemand(mode)`.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.rimdefdump" and no XML error naming RimDefDump's About.xml   # load-time
2. [L] with no marker file present at game load, Player.log contains "[RimMandrake.RimDefDump] inert (no dump_request.txt)." and NOT "[RimMandrake.RimDefDump] starting, mode=" — proves the default-inert contract (the mod's whole safety story: "does nothing at all unless a request marker file exists")
3. [D] write the marker file with contents "animals", trigger a load (or the "Dump defs now (animals)" dev action), then confirm `DefDump/captures/<newest id>/manifest.json` and `animals.json` both exist and `manifest.json` parses as JSON — the concrete deliverable of the mod's one job
4. [D] repeat with marker contents "all" and confirm `DefDump/captures/<newest id>/defs/<DefType>.json` exists for at least one common DefType (e.g. `ThingDef.json`) — proves the "all" scope actually walks every def-type database, not just animals
5. [L] Player.log for the "all" run contains "[RimMandrake.RimDefDump] wrote " + N + " def-type files to " and does NOT contain "def type name collision" for a clean mod list — a collision line would mean two DefTypes share a filename stem and one dump silently overwrote the other (`DefDumper.cs:962,1037,1059`)
X. [S] (human pass) none — this mod produces files for another tool to read, nothing renders in-game
