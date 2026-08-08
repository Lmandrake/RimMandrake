# ollama.md — installing Ollama on Windows

_Created 2026-08-08. Purpose: stand up a **local Ollama backend** on Windows for the Kolyska
LLM voice mods (RimAI Framework/Core + RimDialogue Local Server) so the "engine is god" persona
and dynamic Jawaese run offline, free, and private. See `llm_voice_preauthoring.md`._

**Evidence tags:** ✅ **CONFIRMED-FROM-SOURCE** = taken from a page actually retrieved this session
(cited). 🔶 **GENERAL KNOWLEDGE** = from prior model knowledge (cutoff May 2025); plausible but
verify against official docs.

**Update 2026-08-08 (full delivery folded in):** the Fetcher request completed — the official
**GitHub README** and two searches were retrieved and their confirmations promoted to ✅ below.
Two directives 404'd: `github.com/ollama/ollama/blob/main/docs/windows.md` and `.../docs/faq.md`
no longer exist on GitHub — **the canonical Windows docs have moved to
`https://docs.ollama.com/windows` and the FAQ to `https://docs.ollama.com/faq`** (confirmed live
in the search results). Items still resting only on general knowledge remain tagged 🔶.

---

## 1. What was retrieved (the authoritative source)

✅ **CONFIRMED-FROM-SOURCE** — official download page **https://ollama.com/download/windows**
(retrieved 2026-08-08, HTTP 200, page title "Download Ollama on Windows"). It states, verbatim:

- Two install options offered: a **PowerShell one-liner**, or a **"Download for Windows"** installer.
- The PowerShell command shown: `irm https://ollama.com/install.ps1 | iex`  ("paste this in PowerShell").
- **System requirement stated on the page: "Requires Windows 10 or later."**

✅ **CONFIRMED-FROM-SOURCE** — the official **GitHub README** (`github.com/ollama/ollama`,
retrieved 2026-08-08, HTTP 200) corroborates the Windows install line **`irm https://ollama.com/install.ps1 | iex`**
("or download manually"), and documents the REST API on **`http://localhost:11434`** with a working
`curl http://localhost:11434/api/chat` example (see §5). It also shows Python (`pip install ollama`)
and JavaScript (`npm i ollama`) client libraries, if you ever want to script against the local server.

---

## 2. Install — Option A: PowerShell one-liner (from the official page)

✅ The download page offers this exact command. Open **PowerShell** and run:

```powershell
irm https://ollama.com/install.ps1 | iex
```

🔶 Notes (general knowledge — confirm): `irm` is `Invoke-RestMethod`, `iex` is `Invoke-Expression`;
this downloads and runs Ollama's official install script. A standard user PowerShell should be
sufficient (the installer targets the current user); if it complains about execution policy you can
run PowerShell as your normal user — you generally do **not** need an admin shell for the per-user
install. Verify on the official docs before relying on this.

## 3. Install — Option B: the downloaded installer (from the official page)

✅ The page also offers a **"Download for Windows"** button, which provides the Windows installer
(🔶 historically named `OllamaSetup.exe`). Steps:

1. Click **Download for Windows** on https://ollama.com/download/windows.
2. Run the downloaded installer and follow the prompts.
3. 🔶 The installer sets Ollama up for the current user and starts the background service; a tray
   icon typically appears. (Confirm against docs.)

**System requirement (✅ from page):** Windows 10 or later.
🔶 General-knowledge specifics to confirm: 64-bit Windows; a GPU (NVIDIA/AMD) accelerates
inference but Ollama can run CPU-only; model size drives RAM/VRAM needs (a 7–8B model wants roughly
8 GB of RAM/VRAM, larger models more). These figures are approximate and should be verified.

---

## 4. Verify the install

🔶 **GENERAL KNOWLEDGE — confirm.** Open a **new** terminal (PowerShell or Command Prompt) so PATH
is refreshed, then:

```powershell
ollama --version
```

Pull and run a small model to confirm end-to-end:

```powershell
ollama run llama3.2
```

The first run downloads the model, then drops you into an interactive chat. Type `/bye` to exit.
List installed models with `ollama list`.

---

## 5. Running Ollama as a server (what the RimWorld mods need)

✅ **CONFIRMED (README + docs).** The RimAI Framework and the RimDialogue Local Server talk to
Ollama's **REST API**, which the background service exposes by default at:

```
http://localhost:11434
```

The README shows this endpoint directly (`curl http://localhost:11434/api/chat -d '{...}'`), and
the official Windows docs state that after install "Ollama will run in the background and the
`ollama` command line is available in cmd, powershell or your favorite terminal" (docs.ollama.com/windows).

- ✅ On Windows, Ollama **runs as a native background application** after install, so the API is
  usually already listening — you don't have to launch anything extra.
- To run/serve it manually in a terminal: `ollama serve`.
- Quick check that the API is up (browser or curl): visiting `http://localhost:11434` should
  return `Ollama is running`.

**Wiring to the mods** (from `llm_voice_preauthoring.md`):
- **RimAI Framework** — in Mod Options, set the provider **base URL** to `http://localhost:11434`
  (or its OpenAI-compatible endpoint — confirm the exact path the mod's Ollama template expects),
  leave the API key blank for local, pick your model, run its Test + Save.
- **RimDialogue Local Server** — set `OllamaUrl` to `http://localhost:11434` in its
  `appsettings` and select the model; the server needs **.NET 9** installed alongside.

---

## 6. Useful environment variables (✅ Windows procedure confirmed)

✅ **The Windows procedure is confirmed** by the official docs (docs.ollama.com/windows and
docs.ollama.com/faq, per the delivered search): "On Windows, Ollama inherits your user and system
environment variables. First **Quit Ollama** by clicking it in the task bar. Start **Settings**
(Windows 11) or **Control Panel** (Windows 10) and search for *environment variables*. Click
**Edit environment variables for your account**. Edit or create a variable for `OLLAMA_HOST`,
`OLLAMA_MODELS`, etc. Click OK/Apply, then start Ollama again." Restarting Ollama is required for
changes to take effect.

- ✅ `OLLAMA_HOST` — the bind address Ollama listens on. Default is local-only; set it to
  `0.0.0.0:11434` to accept connections from other machines on your LAN (e.g. if RimWorld runs on a
  different PC than Ollama). Security caveat: exposes the API to your network.
- ✅ `OLLAMA_MODELS` — directory where models are stored. The docs explicitly describe this as the
  way to "change where Ollama stores the downloaded models instead of using your home directory" —
  point it at another drive if models are large. (🔶 The home-directory default is historically
  `%USERPROFILE%\.ollama\models`; the exact path wasn't in the retrieved text — verify in-app.)
- ✅ Other real variables (confirmed to exist by the env-var reference results): `OLLAMA_KEEP_ALIVE`
  (how long a model stays loaded in memory) and `OLLAMA_KV_CACHE_TYPE` (KV-cache quantization). 🔶
  `OLLAMA_ORIGINS` (allowed CORS origins) is commonly cited but wasn't in the retrieved snippets.
  Note: the results flag that `OLLAMA_FLASH_ATTENTION` became a **three-state override (since Oct
  2025)**, no longer a simple on/off — mentioned only so you don't rely on stale on/off guidance.

---

## 7. Model choice for the Jawaese / persona use-case

🔶 **RECOMMENDATION (not established fact).** Per `llm_voice_preauthoring.md` §B.4, small models
may not reliably hold the `Jawaese. (English gloss)` shape or the machine-spirit tone. Start by
testing a mid-size instruct model (e.g. an 8B-class model like `llama3.1`/`llama3.2`, or a
`qwen2.5`/`mistral` instruct variant) against the B.1 prompt; step up in size if the gloss shape
or persona discipline slips. Pick the largest model your RAM/VRAM runs at playable latency.

---

## 8. Sources

Retrieved via Fetcher request `2026-08-08_ollama_windows_install.txt` (4 of 6 directives worked):

- ✅ **Official download page — "Download Ollama on Windows"**, https://ollama.com/download/windows
  (HTTP 200) — source of the PowerShell one-liner, the "Download for Windows" installer, and the
  "Requires Windows 10 or later" requirement.
- ✅ **Official GitHub README**, https://github.com/ollama/ollama (HTTP 200) — corroborates the
  Windows install line, the `http://localhost:11434` REST API + `/api/chat` example, and the
  Python/JS client libraries.
- ✅ **Search: Ollama Windows install requirements** — surfaced the current canonical docs
  **https://docs.ollama.com/windows** ("Ollama runs as a native Windows application, including
  NVIDIA and AMD Radeon GPU support… runs in the background") and the hardware page
  https://docs.ollama.com/gpu.
- ✅ **Search: OLLAMA_HOST / OLLAMA_MODELS env vars** — surfaced **https://docs.ollama.com/faq** and
  https://docs.ollama.com/windows, source of the confirmed Windows env-var procedure and the
  `OLLAMA_MODELS` model-relocation behavior in §6.
- ✗ **404 (moved):** `github.com/ollama/ollama/blob/main/docs/windows.md` and `.../docs/faq.md` no
  longer exist — docs relocated to `docs.ollama.com/windows` and `docs.ollama.com/faq`. Fetch those
  two URLs next time deeper detail is needed (e.g. exact default model path, full env-var list).

_Remaining 🔶 items are from general model knowledge (cutoff May 2025); everything tagged ✅ is
verified against a page retrieved 2026-08-08._
