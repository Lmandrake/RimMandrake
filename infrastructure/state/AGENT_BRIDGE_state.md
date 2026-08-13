# AGENT_BRIDGE_state.md — where BRIDGE is

**Cross-session address:** ⚠️ **DEAD.** Session `891` stopped 2026-08-13 ~10:00 for
a full seat reboot. Recompute on resume, before anything else:

```bash
echo "**Cross-session address:** \`uds:/run/user/1000/cc-socks/$PPID.sock\`"
```

Identity: `infrastructure/agents/BRIDGE.md`, injected automatically. Queue: `infrastructure/state/queue/BRIDGE.md`.

---

## State of the world at handoff, 2026-08-13 ~10:00

| | |
|---|---|
| bridge | **RELEASED** |
| game | UP, owner's colony, paused |
| **left on the map** | a full gravship at **x82-167 z58-190** on a **quicktest** map, substructure patches at **100,100 / 150,150 / 168,168 / 170,170**, MetalTile at **160,160** and **170,170**, hull at **200,200** and **169,169**. Camera zoom extension left **ENABLED** (range 0-100, was 11-60) — an unexpectedly wide screenshot is this |
| ship plan | CREATE regenerated at `--center 250,250`: 31 calls, 1,053 things, **2 heatsinks held back as `footprintConflicts`** |
| mod count | **570 active** at exit. Any doc saying 573 is stale |

## Owed — first call of the next live session

`jawa/get_def GravFieldExtender` → `CompProperties_SubstructureFootprint` radius.
**30** verifies CREATE's plan; **25.9** means the owner's settings never reached the
defs, and the extender at (56,8) — 84.72 out, 0.28 of margin — breaks first.
**Until that call, "the radii applied" is INFERENCE**, and is written down as
inference deliberately. B0 itself is deployed (10:05, 17 tools, byte-verified).

## The GravshipSizeSettings file misleads three ways, all measured

| trap | detail |
|---|---|
| the UI rounds | the panel shows **26** where the stored float is **25.9**. Only the XML has the real value |
| only deltas are stored | an absent key is at DEFAULT, not zero. An almost-empty file is a mod at defaults, not unconfigured |
| the names lie twice | file is `..._GravshipSizeSettings.xml`, class inside is `GravshipSize.GravshipSettings`; scribe keys are `BG_gravEngineMaxDistance`, **not** the C# field `gravEngineMaxRadius` |

⭐ **When a config file does not exist yet, get the app to create it rather than
guessing its schema.** Hand-authoring this one would have failed silently on both
name traps; it became writable only after the owner moved a slider.
