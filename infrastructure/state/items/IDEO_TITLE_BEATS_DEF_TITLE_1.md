## spec
CHECK, 2026-08-21, from `jawa/faction_leader_get`'s first live run: **17 factions, and the
ideoligion overrode the def on 15.**

| faction | reads | its def says |
|---|---|---|
| `Empire` | *leader* | **Emperor** |
| `OutlanderCivil` | *leader* | **High Marshal** |
| `TribeCivil` | *leader* | **War Chief** |
| `Jawa_IndigenousTribes` | *leader* | **Prime Trader** |
| `Pirate` | ⚠️ ***Ethical Dog*** — a generated string | **Captain** |

**Mechanism, verified against the 1.6 source at `RimWorld/Faction.cs:141-149`:**

```csharp
public string LeaderTitle {
  get {
    if (ideos == null || ideos.PrimaryIdeo == null || ideos.PrimaryIdeo.leaderTitleMale.NullOrEmpty())
    { ... return def.leaderTitleFemale / def.leaderTitle; }
```

⇒ **`def.leaderTitle` is reached ONLY when the primary ideo's title is empty.** An authored
FactionDef title can never beat an ideoligion that carries one — **and the def keeps reading
correct in every offline check**, which is why nothing caught it.

⛔ Fails the `leaderTitle` half of **B40 · B41 · B42 · B52**, all four of which I verified
as *shipped on disk* on 2026-08-21. They are shipped. They are also invisible.

## verify
after a regenerate without Classic ideoligion, `jawa/faction_leader_get` reports the def's
title — or the faction's own faith's title — on all seventeen, and none reads *leader* or a
generated string.

## criteria
No faction wears a title nobody authored.

## ruling
🔴 **DECIDE, 2026-08-21 — THIS IS A SYMPTOM. DO NOT FIX IT.**

The four factions reading a generic *"leader"* are being handed it by the **Classic
ideoligion**, and `CLASSIC_IDEO_ERASES_FAITHS_1` measured the disease directly:
`ideosTotal: 2`, **every one of the sixteen factions returning a null ideo name, zero memes,
zero deities.** ⇒ **none of the twelve authored faiths exists in this world at all.**

⭐ **So the titles are not a title problem.** They are the visible edge of a single
world-creation checkbox that discarded `Meckgin`, `The Rising Order`, `The Salvation`, `the
Ascendant Genome`, `the Balance`, `the Continuity Protocol`, `the Contract`, `the Covenant of
Free Wells`, `the Green Oath`, `the Reckoning of Debts`, `the Sun-Debt` and `the Weight` —
all twelve of which are correct in the deployed defs.

⛔ **Do NOT set the titles on the live faction objects.** It is available — the names were
fixed that way — and it would paint over a world that has to be rebuilt regardless. Twelve
faiths cannot be retrofitted; an Ideo is made at world creation.

⭐ **And do not fix the titles even after a clean regenerate, until they are re-measured.**
Our `fixedIdeo` blocks set `ideoName`, `ideoDescription`, `forcedMemes` and `deityPresets` —
**not** a leader title. If the generated ideo's `leaderTitleMale` comes out empty, `Faction.cs`
falls through and *"Emperor"* appears with no work at all. If a structure meme supplies one
instead, that is a different and much smaller problem. **Measure before building anything.**

### ⇒ What this actually costs, said plainly

`world/WORLDMAP_gen.rws` **is not the keeper.** It is a rehearsal that proved the pipeline
and produced one unrepeatable finding — that the ideoligion setting is as irreversible as
the faction list, and nothing on the world-creation page says so.

✅ The good news is timing: `design/Jawa/worldbuilding/WORLD_REDRAFT.md` was written last
night, and this is exactly what it exists for. It has been updated so a redraft cannot repeat
it.
