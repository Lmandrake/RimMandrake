# GPT research answer, 2026-11-22 (gpt_consult.py, Linux Codex, live web search, high effort)

Question: `/tmp/artstudy/q.md` of the study run; reproduced below the answer.

Live sources checked November 22, 2026. “Documented” on an issue means a reported observation, not a product guarantee.

1. **Windows sandbox**

`elevated` requires administrator/UAC-approved provisioning: dedicated low-privilege users, filesystem ACLs, firewall rules, and local logon-policy changes. Commands themselves run without administrator privileges. `unelevated` uses your current user’s restricted token and ACLs, avoiding that administrator provisioning; its environment-based offline controls provide weaker network isolation, and denied-read paths are unsupported. [documented: [Windows sandbox](https://developers.openai.com/codex/windows/)]

Select the implementation with `[windows] sandbox = "elevated"` or `"unelevated"`, or `-c 'windows.sandbox="unelevated"'`. Separately, top-level `sandbox_mode` or `--sandbox`/`-s` selects `read-only`, `workspace-write`, or `danger-full-access`; `-c` overrides configuration values. [documented: [configuration](https://developers.openai.com/codex/config-reference/), [CLI flags](https://developers.openai.com/codex/cli/reference/)]

`codex exec --sandbox danger-full-access …` and `sandbox_mode="danger-full-access"` disable command sandboxing; a Windows issue reports eliminating repeated UAC this way. An explicit guarantee that **all setup paths** skip UAC in `0.167.0-alpha.3.2`: **not found**. Expected CLI behavior: skips sandbox provisioning [guess ~95%]. [documented: [reported workaround](https://github.com/openai/codex/issues/31556)]

IT provisioning is documented:

```powershell
codex sandbox setup --elevated --user 'DOMAIN\alice' --codex-home 'C:\Users\alice\.codex'
```

It targets an identity and home. A once-for-all-homes guarantee or configurable shared sandbox-state directory: **not found**. [documented: [provisioning](https://developers.openai.com/codex/windows/)]

Your exact update/reset trigger matrix is **not found** as specified behavior; repeated reprovisioning/UAC is reported. [documented: [issue](https://github.com/openai/codex/issues/42213)]

Also consider `windows.sandbox="mxc"`: compatible Windows 11 systems support native isolation without administrator setup, additional accounts, or firewall rules. Explicit selection fails when unavailable. [documented: [MXC](https://developers.openai.com/codex/windows/)]

2. **Linux/WSL2**

Linux Codex inside an already-installed WSL2 uses the Linux sandbox, avoiding native Windows sandbox setup. Installing WSL itself can require administrator privileges. [documented: [WSL](https://developers.openai.com/codex/windows/wsl/)]

The **0.167.0 README** specifies bubblewrap filesystem/namespace isolation plus seccomp and `NO_NEW_PRIVS`. Landlock remains legacy; restricted filesystem policies require bubblewrap. System `bwrap` is preferred, with a bundled fallback. [documented: [versioned README](https://github.com/openai/codex/blob/rust-v0.167.0/codex-rs/linux-sandbox/README.md)]

Linux/WSL built-in image-tool invocation with ChatGPT authentication is reported. Official documentation specifically guaranteeing image generation under **Linux `codex exec`**: **not found**; validate that combination before migration. [documented: [Linux report](https://github.com/openai/codex/issues/49214)]

3. **Image usage and concurrency**

Built-in image generation counts toward general Codex usage limits; docs estimate **3–5× faster allowance consumption** than comparable turns without images. The CLI instructions describe interactive sessions and `$imagegen`; an explicit `codex exec` image-generation contract and numerical concurrent-session cap per ChatGPT account: **not found**. [documented: [image-generation docs](https://developers.openai.com/codex/image-generation/)]

Additional image-limit failures despite remaining general allowance are reported; those reports do not establish a published quota formula. [documented: [quota issue](https://github.com/openai/codex/issues/49214)]

4. **Parallel-worker authentication**

The automation guide explicitly says **do not share one `auth.json` across concurrent jobs or machines**. Preserve refreshed credentials between serialized runs. Sharing one `CODEX_HOME` therefore does not make shared-auth concurrency a documented solution. [documented: [automation auth](https://developers.openai.com/codex/auth/ci-cd-auth/)]

The “strictly single-use” premise needs qualification: an OpenAI maintainer describes a reuse grace window of roughly an hour, while acknowledging unresolved reused-token reports. [documented: [maintainer explanation](https://github.com/openai/codex/issues/10332)]

`codex login --device-auth` supports headless login with browser/code authorization. `codex login --with-api-key` reads a key from stdin. [documented: [authentication](https://developers.openai.com/codex/auth/), [login flags](https://developers.openai.com/codex/cli/reference/)]

`cli_auth_credentials_store` supports `file`, `keyring`, `auto`, and `ephemeral`. A documented refresh-race fix from changing stores: **not found**. [documented: [credential storage](https://developers.openai.com/codex/auth/)]

API keys are the documented default for automation; ChatGPT-managed automation is advanced and requires preserving refreshed state. [documented: [automation guidance](https://developers.openai.com/codex/noninteractive/)]

5. **Images API alternative**

`gpt-image-1` shut down October 23, 2026; current successors include GPT-Image-2.6 Sunburst/Flare. Edits accept up to 16 reference images; `n` supports 1–10 outputs. `input_fidelity` supports high/low on 1.5; omit it for GPT-Image-2, which always uses high fidelity. [documented: [Images reference](https://platform.openai.com/docs/api-reference/images)]

Transparent output uses `background="transparent"` with PNG/WebP. Sizes include 1024², 1536×1024 and portrait; newer models support constrained custom sizes: multiples of 16, ratio ≤3:1, edges ≤3840, 655,360–8,294,400 pixels. Alpha masks guide edits; exact preservation is not guaranteed. [documented: [image guide](https://platform.openai.com/docs/guides/image-generation)]

Billing uses text/image input and image-output tokens, rather than one universal per-image fee. Standard GPT-Image-2.6 rates per million tokens: $5 text input, $8 image input, $30 image output. [documented: [pricing](https://platform.openai.com/docs/pricing)]

The Images endpoint supplies no shell/validation agent loop; your daemon must implement cropping, resizing, validation, and retries. [guess ~99%]

Table entries are implementation forecasts:

| Option | Removes UAC prompt? | Removes refresh race? | Cost | What it cannot do |
|---|---|---|---|---|
| Windows full-access + ChatGPT [guess ~95%] | Expected | No | Plan allowance | Retain sandbox isolation |
| Unelevated + ChatGPT [guess ~95%] | Expected | No | Plan allowance | Strong elevated network isolation |
| MXC + ChatGPT [guess ~95%] | Yes, if supported | No | Plan allowance | Run on unsupported hosts |
| WSL2 + parallel ChatGPT workers [guess ~95%] | Yes | No | Plan allowance | Guarantee shared-auth reliability |
| WSL2 + serialized ChatGPT jobs [guess ~95%] | Yes | Avoids concurrent refresh | Plan allowance | Parallel agent runs |
| Images API + local processing [guess ~99%] | Yes | Yes | API tokens | Supply the agent loop automatically |
---

## The question as sent

Research question (use live web search; cite each claim with a URL to primary docs: developers.openai.com/codex, github.com/openai/codex README/docs/CHANGELOG/release notes/issues, platform.openai.com docs). Answer under 900 words. Mark each claim [documented: URL] or [guess ~N%]. If you could not find something, say "not found" — do not invent.

Context: An unattended art daemon on a Windows 11 PC calls OpenAI Codex CLI non-interactively (`codex exec`, ChatGPT-subscription sign-in, not an API key) to generate and edit PNG images with Codex's built-in image generation tool ($imagegen / image_gen tool), several workers in parallel, each with its own CODEX_HOME. Installed: Windows desktop-app codex.exe 0.167.0-alpha.3.2 with `[windows] sandbox = "elevated"` in config.toml; Linux codex-cli 0.167.0 (npm @openai/codex) inside WSL2 on the same PC. Problems seen: (a) with the Windows elevated sandbox, every NEW CODEX_HOME, every Codex auto-update that changes the command-runner build, and any re-provisioning of the machine-wide sandbox users (CodexSandboxOffline/CodexSandboxOnline, password reset) makes codex.exe re-run an elevated sandbox setup, which raises a full-screen Windows UAC consent prompt; (b) ChatGPT refresh tokens are single-use and rotate, so N CODEX_HOMEs holding copies of one auth.json fail with "refresh token was already used" when two refresh.

Questions:
1. What exactly is Codex's Windows sandbox: the "elevated" vs "unelevated"/restricted-token modes, what each needs (admin/UAC, local users, firewall rules), what config keys select them (`[windows] sandbox`, `sandbox_mode`, `--sandbox`, `-c`), and whether `--sandbox danger-full-access` or `sandbox_mode="danger-full-access"` skips the Windows sandbox setup (and thus the UAC prompt) entirely. Is there a documented way to provision the sandbox once machine-wide, or point many CODEX_HOMEs at one sandbox state?
2. Does Codex CLI on Linux (WSL2) need any Windows-side setup or prompt? What sandbox does it use (Landlock/seccomp/bubblewrap), and does the built-in image generation tool work under `codex exec` on Linux with a ChatGPT sign-in?
3. Does the built-in image generation tool under a ChatGPT plan count against the Codex usage limits, and is it documented for `codex exec`? Any documented limits on concurrent sessions per ChatGPT account?
4. Auth for many parallel non-interactive workers: is sharing one CODEX_HOME (or one auth.json) across concurrent `codex exec` processes supported or warned against (issues about concurrent refresh / "refresh token was already used")? Is there a documented headless/device-code login, a `codex login --with-api-key`, or an auth credential store option (e.g. `cli_auth_credentials_store` keyring/file) that changes this? Is there a recommended pattern for automation (API key vs ChatGPT sign-in)?
5. The API alternative: OpenAI Images API (gpt-image-1 / successors) for generate and edit with transparent background, input reference images and masks: what it supports (background=transparent, sizes, n, input_fidelity), how it is billed (per image/token), and what it cannot do compared with the Codex agent loop (which can also crop/resize/validate files with shell tools).
End with a short table: option | removes UAC prompt? | removes refresh race? | cost | what it cannot do.
