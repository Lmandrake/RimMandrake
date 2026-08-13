# vendor/ — Steam content that is not ours

**Tier rule: we did not write it and we will not edit it.** Third-party mod
source, salvaged game assemblies, and the markdown wisdom we wrote *about
operating* those mods. **No `Jawa/` vs `RimMandrake/` split** — the owner ruled
it, and the reason holds: somebody else's mod is not ours to categorise by our
reuse, and the split would only ever describe *our* interest in it.

## `vendor/wisdom/` is the exception that earns its place

The mod source is theirs. The document explaining *how to actually run
VFE-Factory*, or *which of this mod's log errors are benign*, is ours — but it is
**about their mod**, so it lives with the mod rather than in `design/`.

The test: **if the mod were uninstalled tomorrow, would this document still be
worth reading?** No → `vendor/wisdom/`. Yes → it is really a method, and belongs
in `design/RimMandrake/`.

## 🔴 Never commit third-party payloads

`mod_sources/` is ~430 MB and gitignored, and it stays that way. Same for the
salvaged assemblies. **We track that we have them and which versions — never the
bytes.** Git keeps a committed binary forever; see `observed/README.md` for what
that has already cost this repo.

## What does NOT belong here

- **Our patches against their mods** → `src/`. A patch we author is ours even
  though its target is not.
- **Candidate mods we are evaluating but have not adopted** → `research/`.
