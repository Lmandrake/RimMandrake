# Oracle experiment spike — thin client + ONE god-letter consumer, proven end to end

Filed thin (no spec/verify/criteria) — FOUNDRY decided the shape below and
proceeded per CHARTER. Spec: `design/RimMandrake/llm_ingame_wiring_spec.md`.
Cast: `design/RimMandrake/nine_voices_cast_bible.md`.

## spec
Build the smallest real slice of the Oracle architecture (spec §1): a thin
OpenAI-compatible chat-completions client, the register-lint Validator, and
ONE consumer (Ohm, per the cast bible — the spec's own validation example
already used him). Ships as `mandrake.rm.oracle` (`src/RimMandrake/Oracle/`),
a plain RimMandrake-tier mod with no Harmony and no def patches — pure new
GameComponent + client behind two verification hooks. Per §4/§5: mock-endpoint
gate first, cloud key after the owner sees it work.

**Scope decision:** the "then cloud key" half of the item title needs
credentials only the owner has. This spike proves the MECHANISM end to end
against a real HTTP round trip (a local mock server) and stops there — the
cloud trial and the v1 posture ruling (dormant vs consumer-live) are the
owner's next move once he has this to look at, per §5.2's own wording
("the v1 posture is ruled after he sees it work").

## verify
1. **Offline selftest (no network)** — `OracleValidator.TryValidateOhm`
   against 5 canned strings: clean fragment (pass), a self-unification tell
   (reject), Ohm naming Zizzik (reject, his own taboo), empty (reject),
   over the 600-char cap (reject). **5/5 correct**, run live via
   `jawa/oracle_selftest` on the minimal+Oracle test list.
2. **Mock-endpoint quicktest** — a local Python stub
   (`http.server`, marker string `MOCKMARKER-9f3a1c`) serving
   `/v1/chat/completions`. Configured via a new `jawa/oracle_configure` bridge
   tool (baseUrl `http://127.0.0.1:8843/v1`, blank key — the one case
   `OracleGameComponent` allows no key), fired via `jawa/oracle_test_ohm_letter`.
   **`rimworld/list_letters` read back the delivered letter's raw `text`
   field: it IS the mock server's exact string, marker included** — the
   fire-and-forget async HTTP call ran for real, the validator accepted it,
   and it was delivered live, not the fallback. Zero "falling back" log lines
   (every fallback path in `OracleGameComponent` logs one; their total
   absence is itself proof the success path ran, since the branches are
   exhaustive).
3. **Live cloud trial** — NOT DONE. Needs an API key in Mod Settings, which
   is the owner's to supply. Everything up to this point is proven; this step
   and the v1 posture decision are next, and are his call.

## criteria
- [x] Thin OpenAI-compatible client, hand-rolled JSON (see notes — a real
      JSON library would have shipped a DLL RimWorld's own Mono BCL doesn't
      carry and thrown at runtime despite compiling clean).
- [x] ONE consumer (Ohm) end to end: persona block + law → HTTP call →
      register lint → letter, with a fallback on every failure path.
- [x] Offline selftest: 5/5.
- [x] Mock-endpoint quicktest: delivered letter's text is the mock server's
      exact marker string, read back via `rimworld/list_letters`.
- [ ] Cloud key trial — owner's to run.
- [ ] v1 posture (dormant-ship vs consumer-live) — owner's ruling, per spec §5.2.

## notes

### Debug actions from a mod's own assembly did not surface through the bridge
`[DebugAction]` methods (the spec's own §4 verification-hook mechanism) built
correctly and would work for a human with Dev Mode open in the real game, but
`rimworld/list_debug_action_roots`, `list_debug_action_children` and
`search_debug_actions` all returned empty/zero for `RimMandrake.Oracle` — AND
for the pre-existing, already-verified `RimMandrake.Inhabited` category, which
rules out an Oracle-specific defect. Not chased (would mean digging into
RimBridgeServer's own debug-action tree-walker); worked around by adding two
`[Tool]` methods (`jawa/oracle_selftest`, `jawa/oracle_configure`,
`jawa/oracle_test_ohm_letter`, all `#if JAWA_GM_TOOLS` gated except selftest)
to the JawaBench companion instead, referencing `RimMandrakeOracle.dll`
directly the same way it already references Harmony's — the mod loader has it
loaded well before RimBridgeServer attaches. Worth filing as a rimbridge trap
if anyone hits it again; skipped here to stay in scope.

### JSON: hand-rolled, not a library, and that was a real near-miss
First pass used `System.Web.Extensions`' `JavaScriptSerializer` — compiled
clean via the `Microsoft.NETFramework.ReferenceAssemblies` NuGet package.
`System.Web.Extensions.dll` is **not** in RimWorld's own trimmed Mono
`Managed/` folder (checked by directory listing before shipping, not assumed)
— a reference-assemblies package supplies compile-time facades with no IL
bodies, so this would have thrown `FileNotFoundException` on first use at
runtime despite a green build. Rewrote `OracleHttpClient` to hand-roll the
narrow JSON it actually needs (two strings in, one string out) against
`System.Net.Http.dll`, which **is** confirmed present in `Managed/`.

### Live game state
`ModsConfig.xml` restored to the owner's 593-mod Route B list (see
`FOW_ROUTE_B_INTEGRATION_1`); `mandrake.rm.oracle` is deployed
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Oracle\`) but
**not** in that active list — it is opt-in, off by default (`enabled=false`
kill switch), and adding it to the owner's real list is a separate decision
from proving the mechanism. `JawaBench.BridgeTools.dll` was rebuilt `--gm` and
redeployed with the three new tools; a plain (non-`--gm`) rebuild before any
future non-GM session would drop `jawa/oracle_configure` and
`jawa/oracle_test_ohm_letter` along with `fire_incident`/`send_letter` — that
is the existing, intentional gate, not a regression.
