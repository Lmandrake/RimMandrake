# The Codex contract — verified facts

## Contents

- How the CLI is located (and why the path must never be hardcoded)
- Auth mode decides which capabilities exist
- The two imagegen paths
- Transparency: why chroma-key is mandatory here
- Size limits (they bite on RimWorld sprites)
- Where output actually lands
- What was checked and found clean

Everything below was established on 2026-08-12 against **codex-cli
0.147.0-alpha.6.6** by reading the installed skill and running the binary. It
is not repeated from documentation.

---

## How the CLI is located

`codex` is **not on `PATH`**. It ships inside the Codex desktop app at a
content-hash directory:

```
C:\Users\<user>\AppData\Local\OpenAI\Codex\bin\<hash>\codex.exe
```

**The hash changes on every app update**, so it is never hardcoded. The app
keeps the current value in `~/.codex/config.toml`:

```toml
CODEX_CLI_PATH = 'C:\Users\Mandrake\AppData\Local\OpenAI\Codex\bin\8e8bf206e63ac436\codex.exe'
```

`codex_image.py` resolves it in this order: `config.toml` → `PATH` →
newest `bin/*/codex.exe`. If all three miss it says so rather than guessing.

**It is a Windows binary invoked from WSL.** Any path handed to it must be a
Windows path — `codex_image.py` converts via `wslpath -w`, falling back to the
`/mnt/<drive>/` convention. Paths under `/tmp` or `~` in WSL are **not visible
to Windows**, so a working directory must live under `/mnt/c` or `/mnt/d`.

## Auth mode decides which capabilities exist

`~/.codex/auth.json` carries `auth_mode`. This install:

```json
{ "auth_mode": "chatgpt", "OPENAI_API_KEY": null, "tokens": { ... } }
```

| auth mode | built-in `image_gen` | CLI fallback `image_gen.py` | native transparency |
|---|---|---|---|
| `chatgpt` (this one) | ✅ | ❌ needs `OPENAI_API_KEY` | ❌ |
| `apikey` | ✅ | ✅ | ✅ via `gpt-image-1.5` |

**This is the single most consequential fact in this file.** A ChatGPT login
gives image generation but no API key, so every deterministic control the CLI
fallback offers — exact `--size`, exact `--out`, `--mask`, `--quality`, and
true `--background transparent` — is unavailable. Do not write instructions
that depend on them without checking `probe` first.

## The two imagegen paths

`$imagegen` is a **Codex system skill**, not a plugin — it will never appear in
`codex plugin list`. It lives at
`$CODEX_HOME/skills/.system/imagegen/` and has two modes:

- **Built-in `image_gen` tool** (default, no API key). Invoked by asking for it
  in the prompt: `Use $imagegen to ...`.
- **CLI fallback** `scripts/image_gen.py` with `generate` / `edit` /
  `generate-batch`. Requires `OPENAI_API_KEY`. **Unavailable here.**

Invocation that works:

```bash
codex exec --sandbox workspace-write --skip-git-repo-check \
  -i <windows-path-to-input.png> \
  'Use $imagegen to ... Then copy the generated image into the current working directory as out.png.'
```

`-i/--image` may repeat; order is meaningful, so describe images by index in
the prompt.

### ⚠️ `-i` is variadic and will eat your prompt

`-i, --image <FILE>...` takes **one or more** values. Without a `--`
terminator it keeps consuming positionals, so this:

```bash
codex exec -i image.png 'my prompt'        # WRONG
```

hands codex two *filenames* and no prompt. Codex then falls back to reading
the prompt from stdin, finds it empty, prints

```
Reading prompt from stdin...
No prompt provided via stdin.
```

and **exits 0 having done nothing.** A zero exit code with no output file is
the signature.

```bash
codex exec -i image.png -- 'my prompt'     # RIGHT
```

`codex_image.py` inserts the `--` whenever images are attached. Cost to find:
one silent no-op that looked like a generation failure.

**Generalises to:** a variadic option is a trap for any positional that
follows it, and the failure is silent rather than an error. When a CLI accepts
`<FILE>...`, terminate it explicitly rather than relying on the next token
looking un-filename-like.

## Transparency: why chroma-key is mandatory here

The built-in tool exposes **no transparency control**. Codex's own skill
documents the workaround: generate on a flat chroma-key background, then remove
the key locally.

Codex ships `scripts/remove_chroma_key.py` for this — **but it imports Pillow,
which is not installed in this WSL environment.** Hence
`scripts/chroma_key.py`, which does the same job on `pnglib` and the standard
library alone.

Key colour guidance from the Codex skill, confirmed sensible in testing:
default `#00ff00`; `#ff00ff` when the subject is green; avoid `#0000ff` for
blue subjects.

## Size limits — these bite on RimWorld sprites

`gpt-image-2` (the default model) constrains output size:

- max edge ≤ **3840 px**
- **both edges multiples of 16**
- long:short ratio ≤ **3:1**
- total pixels between **655,360** and **8,294,400**

⚠️ **Two consequences for this project, both verified by arithmetic:**

1. A single RimWorld facing at `512x640` is **327,680 px — below the minimum**.
   It cannot be generated at native size. Generate larger, then downscale with
   `pnglib.resize_rgba` (which premultiplies alpha, so no dark halo).
2. The existing smelter sheet is `1416x1416`. **1416 is not a multiple of 16**
   (1416/16 = 88.5), so it is not a legal output size either.

Sizes that are legal and useful: `1024x1024`, `1536x1024`, `1024x1536`,
`2048x2048`, `2048x1152`.

## Where output actually lands

Built-in mode saves under `$CODEX_HOME/generated_images/<session-uuid>/`, and
the tool takes **no destination argument**. The agent must be *told* to copy
the file to the working directory, and it may not comply.

`codex_image.py` therefore verifies the destination exists and, if not,
snapshots `generated_images/` before and after the run and harvests whatever
appeared. In the 2026-08-12 probe the agent did copy the file correctly, so the
harvest path is a safety net rather than the normal route.

## What was checked and found clean

Recorded so nobody re-checks it:

- `codex plugin list` — **no imagegen plugin**, and correctly so; it is a
  system skill. Do not go looking for it there again.
- `OPENAI_API_KEY` — absent from both the WSL and Windows environments, and
  null in `auth.json`. Three places checked.
- Pillow and numpy — **absent** from the WSL Python. `pnglib` is the answer,
  not a `pip install`.
