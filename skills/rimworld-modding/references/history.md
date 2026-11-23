# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old figures and the lines that are no longer true. Git holds the
rest. Each line below is a record, not a rule. The rewrite was on 2026-11-23.

## Sources of truth (§1b)

- The table of three sources was added on 2026-08-19, with the `rimsage` MCP server. The stack then had 579 mods.
- Before `rimsage`, the only route to a vanilla signature was `strings -a -el` over an assembly. Root `CLAUDE.md` then said
  "never guess a defName, field, or namespace".
- The dump was once at `…\LocalLow\…\DefDump\defs\*.json`. A capture is now a folder under `DefDump\captures\`.
- The decompiled tree was once at `D:\Luke\dev\reference\rimworld-decompiled`. That folder does not exist now. §1b once
  said in one paragraph that no local tree exists and that one exists at `D:\ClaudeWork\rimmandrake\decomp\rw16`.
- The RimDefDump mod was once at `mods/dev/RimDefDump`. Two scripts were cited as `Utils/animal_inventory.py` and
  `Utils/animal_live_diff.py`; both are under `src/RimMandrake/`.
- §1b once said that RimBridge has no `list_defs`/`get_def`. `jawa/get_def` and `jawa/get_defs` exist now.

## The load (§2)

- §2 once gave a cold load as **23–30 minutes** past ~500 mods. The load-round skill holds the measured times.
- §2 once said that `jawa/get_defs` is scalar-only, with no word of `deep=true` for a nested read.

## The tier ladder (§3)

- The example once said that the shield of `Apparel_ShieldBelt` is "entirely" two stats and that a grep with zero hits moves
  the job to tier c. Core's `Apparel_Belts.xml` carries `<li Class="CompProperties_Shield" />`.

## The rule leads (§4, §5b)

- On 2026-08-14 and later, the paragraphs of §4 and §5b moved to `patch-operations.md`, `traps-xml-and-defs.md` and
  `load-order.md`. A leftover first line of each stayed in `SKILL.md`, cut in mid-sentence. The rewrite gave each a whole rule.

## The validator (§5)

- §5 once gave `python3 scripts/validate_patch.py` with three `C:/` roots:
  `C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data`,
  `C:/Program Files (x86)/Steam/steamapps/workshop/content/294100` and
  `C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods`. WSL `python3` cannot read them.
- §5 once ended "Silence is success." A patch that matches nothing is also silent.

## Load order (§5b)

- §5b once said that `ParentName` resolves only against `Abstract="True"` defs. Core's `Stun` damage def has a `Name=` and is
  not abstract. §5b also cited a def that was discarded whole; in the 1.6 source, a def with an unfound parent loads alone.

- §5b once called the recursion of a self-referencing research project unconditional. `FinishProject` recurses only into a
  prerequisite that is not finished.

## C# (§8)

- §8 once said that biome-kit mechanics get feature-gated so that they can be enabled in a different biome without the whole
  kit. The owner's card of 2026-11-21 replaced that.
- §8 once said that a `GameComponent` with the wrong constructor fails silently. 1.6 logs one line.
- §8 once gave this build command:
  `/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build 'D:\Luke\dev\Rimworld\src\...\Foo.csproj' -c Release` (forward-slash binary,
  Windows-style project path). `D:\Luke\dev\Rimworld` does not exist now.
- The reference project was `mods/dev/RimDefDump/Source/RimDefDump.csproj`.

## Lessons (§9)

- §9 once told each agent to append a trap to a topic file, and gave the cost of all five files as ~25k tokens (and again, ~25k, beside `whats_new.py`). The five files
  and `traps.md` held 143,835 bytes on 2026-11-23.
- §9 once said to edit the copy in the user's project, re-package, and say that the edit is **delivered**. In this repo, an edit
  of `skills/<name>/` is the installed text.
