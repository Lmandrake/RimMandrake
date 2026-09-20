## the defect

A close whose evidence is entirely offline — `dotnet build`, `validate_patch`,
selftests — is a legitimate close. The defect is where the *remaining* debt goes:
into the closing commit's message, which no queue, dashboard or `rimflow next`
ever reads. The moment that session ends, nobody is looking for the live proof.

MEASURED 2026-09-20, both re-read directly:

| item | closing commit | what it said about live proof |
|---|---|---|
| `ALPHA_MECHANICS_KIT_1` | `636192203` | "Deploy + live proof + content defs are separate follow-on work." |
| `BRAINWORM_MOD_BUILD_1` | `2e7aa9cff` | "Art/deploy/live proof owed." |

🔑 **Both told the truth.** That is the point — this is not a dishonesty problem
and reopening those closures would punish the seats that were candid. The build
commit for the first (`ddd8d379f`) even shouts it: *"Builds clean; LIVE PROOF
STILL OWED."*

`MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` (closed 2026-09-19) independently names
four more closed items with the same shape — `TITANIC_CREATURES_MOD_1`,
`FLOOD_CANYON_BIOME_1`, `DROID_FDE_GOODWILL_CAP_1` and the two above. ⚠️ Those
four were not individually re-verified here; treat the count as UNCERTAIN and the
two in the table as CONFIRMED.

How `ALPHA_MECHANICS_KIT_1` surfaced at all: `ENVHAZARDS_NEVER_ACTIVATED_1` found
that `mandrake.rm.environmentalhazards` had never been in any mod list. It was
activated 2026-09-17 (`9bf9ccf4e`), six days after that close — so no live run was
possible in either direction, and all six RC comps ship inside that one mod, which
means there is no gated-vs-unaffected split to make. The mod is the gate.

## spec

The machinery already exists and was simply not reached for:

```
rimflow spawn --from <run> --for <seat> --name <ID>
```

Owed:

1. **A rule**: a close whose evidence is offline-only spawns a successor item
   carrying the live-proof debt, in the same sitting, before the close.
2. **A lint or hook**: a close-commit body containing `live proof owed`,
   `deploy owed`, `live proof still owed` or `follow-on work` with no spawned
   successor on the same ledger event is caught. WARN is probably right, not
   refuse — the honest wording is the signal, and a hook that punishes it would
   teach seats to stop writing it, which is strictly worse than the defect.

## verify

- [ ] Re-run the detection over the whole ledger: every close event whose commit
      body matches those phrases, joined against spawned successors. The count
      before the rule is the baseline.
- [ ] A deliberate offline-only close with no successor trips the lint; one with
      a successor does not.

## criteria

No debt named in a commit message is the only record of itself. A future seat
asking "what is not yet proven live?" gets the answer from `rimflow`, not from
`git log -S`.

## not owed

⛔ Reopening the closures in the table. They are built, they compile, and they
said what they had not done.
