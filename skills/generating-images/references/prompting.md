# Prompting an image model

## Contents

- The negation trap (the most expensive mistake)
- Length and ordering
- Keep human-facing content out
- Structure that works
- Multi-view consistency
- Worked example: a 900-word brief that failed, and its replacement

---

## The negation trap

**Image models condition on the tokens present.** A prohibition puts the
forbidden thing into the prompt, and it frequently appears in the output. This
is the single most common cause of "the model ignored my instructions".

| Instead of | Write |
|---|---|
| "NO lights, nothing glowing" | "every lamp is dark grey, cracked glass, unlit" |
| "no cables sticking out" | "all fittings terminate flush against the hull" |
| "don't make it shiny" | "matte, chalky, light-absorbing surface" |
| "no background" | "flat solid #00ff00 background" |

The rule: **describe the state you want to see, never the state you are trying
to avoid.** If a constraint cannot be phrased positively, it usually means the
constraint is about composition rather than content — put it in the structural
part of the prompt instead.

## Length and ordering

Early tokens carry more weight, and long prose gets sampled rather than
followed. Put hard constraints — canvas, size, position, background — **first**,
then the subject description.

A prompt over roughly 200 words is usually a specification that should have
been a short prompt. If it feels necessary, that is a signal the task needs
splitting into two passes, not a longer paragraph.

## Keep human-facing content out

Shell commands, rationale about why a rule exists, and pipeline notes cannot be
acted on by an image model, and they dilute what is left. Keep the *why* in a
document for humans; send the model only what it can draw.

## Structure that works

Codex's own skill recommends this scaffold, and it holds up:

```text
Use case: <slug>
Primary request: <the main subject>
Style/medium: <photo / illustration / sprite / 3D>
Composition/framing: <wide / close / top-down; placement>
Lighting/mood: <lighting + mood>
Materials/textures: <surface details>
Constraints: <what must stay true>
```

For **edits**, state invariants explicitly and repeat them every iteration:
`change only X; keep Y unchanged`. Drift across iterations is the normal
failure mode, and repetition is the cheap fix.

## Multi-view consistency

Asking for four views of one object in a single image is materially harder than
one view, and it fails for reasons unrelated to whether the rest of the
pipeline works. **Prove one view first.** Only then find out what the sheet
costs.

When you do ask for a sheet, say plainly that it is one object seen from
several sides, and that a feature visible from one side must appear on the
sides that can see it.

## Worked example

A ~900-word brief for a wrecked machine was being ignored. Its most emphatic
instruction was:

> **NO lights. NO power signatures. NOTHING glowing, anywhere.**

That is three negations stacked, so "glowing lights" was among the strongest
signals in the prompt. The replacement, positively phrased and put near the
front:

```text
Every indicator lamp, screen and light strip reads as dead: dark grey glass,
cracked lenses, empty sockets, soot. The colour of an unplugged appliance.
```

Same intent, no forbidden token, and it names concrete things to draw. The
other two changes were cutting the brief to ~150 words and removing the shell
commands and the paragraph explaining game tile footprints — neither of which
the model could act on.
