# UI_ROOT_NEEDS_A_FRAME_HOOK_1 — ⛔ REFUSED, and this file is the reason on the record

Row 5 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`, whose criteria said this row must be *"not
built until the companion has a frame hook, or refused with that reason recorded."* **This is the
refusal.**

## Why it cannot be built the way every other tool is built
`Find.UIRoot` is **OnGUI-scoped: it throws outside an IMGUI frame.**

🔑 **And the companion's thread rule is not sufficient here, which is the whole point.**
`ctx.MainThread.InvokeAsync` puts the call on RimWorld's main thread — that is what makes every
other tool safe — but the main thread is **not the same thing as being inside a frame.** A
`[Tool]` that follows the rule correctly and touches `Find.UIRoot` still throws.

⇒ The gap is a **frame hook** the companion does not have: something running inside `OnGUI` that
a queued request can be handed to and answered from. That is new infrastructure, not a new tool.

## Status: refused, not deferred
⛔ **Do not write a UI tool "carefully" instead.** There is no careful version — the failure is
structural, and a tool that works when a window happens to be open and throws when one is not is
worse than none, because it teaches the caller to trust it.

✅ **What would reopen this:** somebody wants a UI reader badly enough to build the frame hook
first. That hook is its own item and must be proven on its own before any `Find.UIRoot` tool is
written against it.

## criteria
- [x] The reason is recorded where the next person to want a UI tool will find it.
- [ ] Reopen only behind a proven frame hook.
