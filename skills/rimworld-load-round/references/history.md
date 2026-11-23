# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old figures, the incident text, and the lines that are no longer
true. Each line below is a record, not a rule. The rewrite was on 2026-11-23.

## The price of a load (head, §0)

- The head once read "A cold load costs **~23–30 minutes** and there is one game shared by five seats." There are several
  games now, and the five seats are gone.
- The first minimal-list line gave the full list as "~25 minutes" and 576 mods (2026-08-20). A second copy of the
  geometry line said: `ferny.Worldbuilder` is absent, so a quicktest world comes out 119,904 tiles, not 21,872.
- The skill once said "`mandrake.inhabited` loads last". The id is `mandrake.rm.inhabited` now, and other mods follow it.
- The skill once cited `jawabench-init-line-is-lazy.md`. No such file is in the repo. The item was
  `JAWABENCH_INIT_LINE_IS_LAZY_1`.
- The skill once cited `rimbridge/references/traps.md` for the log that persists. The text is in `traps/lifecycle.md`.

## `ModsConfig.xml` and the exit (§4)

- An old line of the skill said that RimWorld rewrites the file on exit, and the next paragraph said the opposite.
- Measured 2026-08-13: at exit, `Player.log`'s last write was 10:04:55 while the config's mtime was 10:01, *older than the
  exit*. The file moved again at 16:41:39 with no game running at all.
- The parse command once used the path `.../Config/ModsConfig.xml`:
  `python3 -c "import xml.etree.ElementTree as ET;print(len(ET.parse(r'.../Config/ModsConfig.xml').getroot().find('activeMods')))"`.

## The dump marker and `refresh.py` (§5)

- The marker command was once the cmd.exe form, in a bash block:
  `echo all > "%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt"`.

## Deleted saves (§5a)

- The 26 `.rws` came back after a deletion that was already recorded as done.

## The shutdown call (§6, §9)

- The rule once read: "Whoever calls a shutdown tells CHECK BEFORE the game closes." CHECK was a seat. It is retired.

## Where findings went (§8)

- Findings once went to the per-seat queues, and surprises to the matching `traps-*.md`.

## The bare-exe incident (§10), as first written

Measured 2026-08-30. A cold load launched normally (through Steam) worked cleanly
on a 19-mod minimal list: bridge up, 301 companion tools, full mod content loaded.
Immediately after, closing that process (`Stop-Process -Force` on `RimWorldWin64`)
and relaunching by starting `RimWorldWin64.exe` directly —
`Start-Process -FilePath '...\RimWorldWin64.exe'` — produced RimWorld's own
**"Recovered from incompatible or corrupted mods errors"** dialog on the very
next launch, **three times in a row**, with the identical unchanged mod list and
unchanged mod DLLs. The actual exception (`Player.log`, `RebindAllDefOfs` →
`GenTypes.AllTypesWithAttribute`): `System.TypeLoadException: Could not resolve
type with token ... from typeref (expected class 'HarmonyLib.HarmonyPatch' in
assembly '0Harmony, Version=2.4.1.0...')` — a Harmony-assembly-version
resolution failure during the full-type reflection pass, not a content/def
problem. RimWorld's own recovery caught it and reset `ModsConfig.xml` to
Core-only (6 mods) each time.

**Isolated properly, not guessed:** reverted the two content files that had
changed between the working and failing launches (`git stash`), redeployed,
relaunched via the bare `.exe` again — **same crash**, byte-identical content
that had worked minutes earlier. This ruled out the content/def changes
entirely. The one variable that actually differed: the working launch went
through Steam; every failing relaunch used the bare executable.

**Fix, confirmed:** launch via Steam instead —
`Start-Process -FilePath '...\Steam\steam.exe' -ArgumentList '-applaunch','294100'`.
Immediate clean load: bridge up, 19 mods held, 301 tools, first try.

⇒ **Bypassing Steam's own launch path — even though the same `.exe` file runs
either way — skips whatever Steam does to mount/validate Workshop content
(`steamapps/workshop/content/294100/*`) before handing off to the game.** A
raw `.exe` launch can silently pick up a stale, partially-synced, or
inconsistently-cached copy of a Workshop mod's bundled `0Harmony.dll`,
producing exactly this class of intermittent assembly-version collision.
**Always launch (or relaunch, including a driver-initiated restart for a
def/content change) via `steam.exe -applaunch 294100`, never the bare
`RimWorldWin64.exe` path**, even though the latter looks like the more direct
and reliable route.
