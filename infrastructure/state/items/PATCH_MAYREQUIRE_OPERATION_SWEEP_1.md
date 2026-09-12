# PATCH_MAYREQUIRE_OPERATION_SWEEP_1 — repo-wide sweep for inert MayRequire on patch Operations

Filed 2026-09-12 (FOUNDRY, descended from RUST_CATHEDRAL_MECHANICS_1): while
building §4 of that item's kit, `MayRequire` on a patch `<Operation>` was
found to be ignored by the engine, forcing an xpath-based gate instead of
the attribute. Filed to check whether other patches in this repo rely on
the same broken assumption.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — swept, 0 defects found, closing

**Mechanism confirmed via RimSage against real engine source** (refines the
filing note's framing): the fault line is the XML TAG, not nesting depth.
`ModContentPack.LoadPatches` (`Verse/ModContentPack.cs:357-385`) and
`DirectXmlToObject.ObjectFromXml<T>` never read `MayRequire` on an
`<Operation>` element, at any depth. The ONLY place `MayRequire`/
`MayRequireAnyOf` is actually evaluated is `DirectXmlToObject.
ListFromXml<T>`, used for `List<PatchOperation>` fields (e.g.
`PatchOperationSequence.operations`'s `<li Class="PatchOperation...">`
children) — checked against `ModLister.AllModsActiveNoSuffix`/
`AnyModActiveNoSuffix` and honored at any nesting depth *when written on a
`<li>`, never on a bare `<Operation>` tag*.

**Swept**: 153 `MayRequire` occurrences across every `Patches/` folder under
`src/RimMandrake/`, `src/RimUtinni/`, `src/RimStarWars/` — 133 on
`<Operation>` tags (all top-level in every file checked, all effectively
harmless since each one's xpath already fails safely when the gated mod is
absent — not because the engine honors the attribute, but because the
xpath finds nothing) and 20 on `<li Class="PatchOperation...">` list items
(genuinely gated by the real mechanism, all correct). **Zero occurrences of
the actual dangerous pattern** (`MayRequire` on `<match>`/`<nomatch>`/
`<success>`/`<failure>` conditional-result tags, or an `<Operation>`
mistakenly substituted for an `<li>` inside an `operations` list) were
found anywhere in this repo's shipped patches.

## spec
Grep every `Patches/` folder under `src/RimMandrake/`, `src/RimUtinni/`,
`src/RimStarWars/` for `MayRequire`, classify each hit as engine-honored
(a `<li Class="PatchOperation...">` inside a list field) or inert (any
`<Operation>` tag, regardless of nesting), and fix any inert occurrence
that is actually relied upon (i.e. would misbehave with the gated mod
absent) rather than merely inert-but-harmless.

## verify
Every `MayRequire` occurrence in the repo is accounted for as one of: (a)
correctly on a `<li>` list item, (b) on an `<Operation>` tag but harmless
because its own xpath already fails safely without the gated mod, or (c)
fixed. This pass found the full set is (a) or (b) — zero were relying on
the broken attribute to actually prevent a bad edit.

## criteria
No patch file in this repo silently misbehaves (patches something that
doesn't exist, or errors) when a `MayRequire`-named mod is absent, due to
the `MayRequire`-on-`<Operation>` anti-pattern. Met — swept clean, closing.
