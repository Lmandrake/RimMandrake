# RimSage / RIMCP — a searchable index of RimWorld's *own* source and Defs
## What it is, what it cannot see, and where it would fit here

**Study date:** 2026-08-19
**Upstream:** `https://github.com/realloon/RIMCP` (the repo README calls the project *RimSage*)
**Hosted service:** `https://mcp.rimsage.com/mcp` · docs `https://rimsage.com/`
**Licence:** MIT, © 2026 Vortex · **Version studied:** 1.0.1, commit `356bac8` (2026-07-31)
**Local clone:** `D:\Luke\dev\reference\RIMCP`

---

## 1. In one paragraph

RimSage is a **read-only lookup server**. You point it at two trees on your disk — a RimWorld
install and a *decompiled C# source tree you produce yourself* — and it copies the parts it
wants into its own `dist/assets/`, builds a SQLite index, and exposes six MCP tools that
search and read them. It never talks to a running game, never writes anything, and knows
nothing about mods. It answers **"how does RimWorld implement this, and what does this Def
actually resolve to"**, which is exactly the question our own tooling answers worst.

## 2. Verdict for this project

**Useful, in a narrower slot than its pitch suggests, and the narrowing is the whole story.**

✅ **What it gives us that we do not have.** We have no searchable RimWorld C# source at all.
Every claim this project makes about a vanilla class, method signature or Harmony patch target
today rests on model memory or on `strings -a -el` over an assembly. That is precisely the
habit `CLAUDE.md` forbids — *"Never guess a defName, field, or namespace"* — and RimSage is the
first tool we would have that makes obeying it cheap.

🔴 **What it cannot do, and this is disqualifying for most of our work.** RimSage imports
`Data/*/Defs/**/*.xml` and nothing else (`src/scripts/import-defs.ts:26`). **Mod folders are
never scanned.** It indexes vanilla + DLC only. Our campaign runs **579 active mods**, and
essentially every def we author, patch or argue about — `OuterRim_*`, `BTD_*`, `AB_*`,
`GarryFlowers_*` — is invisible to it. It cannot answer "what does this def inherit from" for
any def we actually ship.

⇒ **It is a vanilla-implementation reference, not a def tool for our stack.** Our existing
`DefDump` already beats it on our own defs, because that dump is the *runtime-resolved* result
of all 579 mods loading together — the thing RimSage structurally cannot compute.

## 3. Architecture

```
RimWorld install ─┐
                  ├─► import scripts ─► dist/assets/ ─► SQLite (dist/index.db) ─► 6 MCP tools
decompiled C#  ───┘                                     + ripgrep over dist/assets/Source
```

- **Runtime: Bun, not Node.** It uses `bun:sqlite`, `Bun.Glob` and `Bun.serve`; there is no
  Node fallback.
- **External `rg` (ripgrep) binary required** — `search_source` shells out to it.
- **No environment variables at all.** Every path is hardcoded relative to the repo in
  `src/utils/env.ts`. Configuration is the two CLI arguments to the import scripts, and
  nothing else.
- **Index tables:** `defs(defName, defType, label, rawPayload, mergedPayload)` keyed
  `(defName, defType)`; `csharp_index(typeName, filePath, startLine)`. Both are **dropped and
  rebuilt** on every index run.
- **No full-text search.** Def search is `LIKE %q%` on defName/label
  (`src/tools/search-defs.ts:14`). Source search is ripgrep, not the database.
- **Transports:** stdio, and a streamable HTTP server exposing `/mcp` and `/health`.

## 4. The six tools

| tool | params | returns |
|---|---|---|
| `search_source` | `query` (regex), `file_pattern?` (glob), `case_sensitive=false` | ripgrep hits with line numbers; truncated at 400 lines / 100 KB |
| `read_file` | `path`, `start_line=0`, `line_count=400` (max 2000) | file slice, plus `[TRUNCATED]` and the next `start_line` |
| `list_directory` | `path=''`, `limit=100` (max 500) | names, dirs first, dotfiles hidden |
| `get_def_details` | `defName`, `defType?`, `inheritance='merged'\|'raw'` | the Def rebuilt as XML; error text if absent |
| `search_defs` | `query`, `defType?`, `limit=20` (max 100) | `[defType] defName (label: "…")` lines |
| `read_csharp_symbol` | `typeName`, `memberName?` | code with `// File: path (Lines a-b)`; >400-line bodies collapse to signatures |

## 5. Setup, and what this machine is missing

```sh
bun install
bun run src/scripts/import-defs   /path/to/rimworld/root      # needs Version.txt present
bun run src/scripts/import-csharp /path/to/decompiled/source
bun run build            # clean && index:defs && index:csharp
bun run start            # stdio        (or: bun run start:http)
```

**Measured on this machine, 2026-08-19:**

| prerequisite | status |
|---|---|
| `rg` (ripgrep) | ✅ present |
| `bun` | 🔴 **not installed**, neither in WSL nor on Windows |
| `node` / `npm` | 🔴 not installed either (irrelevant here — Bun is mandatory) |
| RimWorld install with `Version.txt` | ✅ `C:\Program Files (x86)\Steam\steamapps\common\RimWorld`, version `1.6.4871 rev590` |
| decompiled C# source tree | ✅ **already exists** — see §7 |
| `ilspycmd` (to regenerate it) | ✅ `C:\Users\Mandrake\.dotnet\tools\ilspycmd.exe`, v8.2.0.7535 |

⭐ **The hosted endpoint needs none of this.** `https://mcp.rimsage.com/mcp` requires no Bun,
no import, no index — it is one line of MCP config. That is the zero-cost way to try it, and
it is what the prompt in `research/Jawa/Claude Code Prompt — Integrate RimSage.md` proposes.
⚠️ But the repo never states that the hosted service runs this code, at what commit, or
against which game version. Treat hosted answers as *unversioned*.

## 6. Traps worth knowing before trusting an answer

- 🔴 **List merge is CONCAT.** `def-resolver.ts:69` concatenates parent and child lists. That
  is **not** RimWorld's behaviour in every case, so a `merged` view can differ from what the
  game actually loads. `Inherit="false"` replaces wholesale (`:73`).
- 🔴 **Vanilla + DLC only.** No Patches, no Languages, no About, and **no mods** — only
  `Data/*/Defs/**`.
- **Abstract bases vanish.** A Def with no `defName` is silently dropped at index time
  (`src/scripts/index-defs.ts:71`), so `get_def_details` can never return one — even though
  those are exactly the nodes an inheritance question is about.
- **The C# type index is a single-line regex** over `class|struct|interface|enum`
  (`index-csharp.ts:16`); generics and multi-line declarations can be missed. Method
  extraction is brace-counting that assumes comment-free decompiled source.
- **`read_csharp_symbol` bypasses the path sandbox** (`read-csharp-symbol.ts:35`) — it joins
  the DB-stored path directly. Every other tool is sandboxed to `dist/assets`.
- **XML entities are not decoded** (`processEntities: false`, `xml-utils.ts:6`).
- **A stale index is indistinguishable from a fresh one** — no schema version, no check that
  the C# tree matches the game build.
- **The HTTP transport has no auth, no rate limit, no CORS config** (`src/http.ts:7`). Fine on
  loopback; do not expose it.

## 7. 🔴 The decompiled tree already exists — and it is in Temp

Self-hosting needs a decompiled `Assembly-CSharp` source tree (the README notes this is
permitted under the RimWorld EULA). **We have one already:**

```
C:\Users\Mandrake\AppData\Local\Temp\rwdec
```

9,217 `.cs` files, 44 MB, dated 2026-08-15. `AC.csproj` declares
`<AssemblyName>Assembly-CSharp</AssemblyName>`. It holds `Verse\` (1,747 files, including
`Verse\ThingDef.cs` and `Verse\Map.cs`) and `RimWorld\` (5,913 files). This is the genuine
full decompilation, not a sample.

🔴 **It is under `%TEMP%`.** A reboot or any cleanup wipes it, and nothing in this project
records that it exists or how it was made. That is the same class of exposure as the
cherrypick decisions were: a real asset on one disk with nothing pointing at it. Two honest
options — copy it somewhere durable (it is 44 MB of *derived* data, so **not** into git), or
write down the one command that regenerates it. `ilspycmd.exe` v8.2.0.7535 is installed at
`C:\Users\Mandrake\.dotnet\tools\ilspycmd.exe`, so regeneration is cheap and provenance
beats bulk.

⚠️ Unverified: whether that tree matches the current `Assembly-CSharp.dll` (DLL dated
2026-06-30, tree 2026-08-15 — likely current, but nothing checks it).

**For contrast, what is NOT usable:** Ludeon's shipped `RimWorld\Source` folder holds only 43
`.cs` reference examples, 488 KB. And the 6,280 `.cs` under
`D:\Luke\dev\Rimworld\vendor\mod_sources` are *mod* sources, not the game.

## 8. Recommendation

1. **Try the hosted endpoint first**, at project scope. Zero prerequisites, one config line,
   and it answers the question we are worst at: *what does vanilla actually do*.
2. **Do not use it for our own defs.** Our `DefDump` is the authority there and RimSage
   cannot see our mods at all. Any guidance we write must say so, or someone will ask it about
   an `OuterRim_` def and believe the "not found".
3. **Self-hosting is a real project**, not a config change: install Bun, produce a decompiled
   source tree, and re-index whenever the game updates. Worth it only if the hosted service
   proves unreliable or lags 1.6.
4. **Never let a `merged` Def view settle an inheritance argument on its own** — the concat
   semantics differ from the engine. Check against the live `DefDump`, which is the loaded
   truth.

---

**Related:** `research\RimMandrake\reference\autorim_mcp_live_bridge.md` (the runtime-truth
counterpart) · `skills\rimbridge\SKILL.md` (our own live bridge) ·
`research\Jawa\Claude Code Prompt — Integrate RimSage.md` (the owner's integration brief)
