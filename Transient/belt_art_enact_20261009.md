# Art enactment 2026-10-09 (venomvine, Cistrel/Nubrith, Leachmoss)

Card decisions taken 2026-10-09 (decision taken by question card; a click is not his typed words).

## (3) Leachmoss: DONE
- leachmoss_redo_v2 job json, manifest and _artsrc render moved (not deleted) to `D:\Luke\dev\_artpipe\_withdrawn\leachmoss_redo_v2_20261009\`. Column B (31d3fe4f2827) untouched; no further Leachmoss work.

## (1) venomvine and (2) Cistrel/Nubrith: STOPPED, NO CARD PATH IN THE LEDGER
Nothing installed, nothing bypassed. The installer cannot accept a card click.
- `art.py install` over a slot holding an owner-kept sha accepts only: (a) a ruling id for an owner keep (by=owner, trust in TRUST_PROTECTS) that names the INCOMING sha, with sheet-plumbing provenance; (b) the owner-said flag carrying his typed words (hook-guarded, a card click is refused); (c) a mechanical reason is refused over a kept sha. See `src/RimMandrake/Utils/art/artledger.py` lines ~560-620.
- Protection is per sha (`artledger.protected`). The only release is `art.py purge <sha> ... --release-keep` or a `releases` ruling (artledger.py:743); both are sha-wide and need his typed words. A sha-wide release would also unprotect RM_VenomvineThicket (29ae79060e16), which he wants kept.
- Venomvine slots to change: Strangler, Weeper, Sleeper, SleeperAwake, Lure, plus the earlier Rearing/Walking/Hoard/Quench/Sworn/Shedding copies once each has a finished own render. Cistrel/Nubrith: slots RM_Cistrel_a and RM_Nubrith_a (hold 25b911d827a8), renders regen_fw_cistrel_own_v1 and regen_fw_nubrith_own_v1.
- What unblocks it, either route:
  1. One tiny review sheet (4 venomvine renders now finished + Cistrel + Nubrith) ruled keep on the own render, saved through the sheet plumbing, then `art.py ingest` and `art.py install ... --ruling <id>` per slot.
  2. One typed sentence from him in chat (e.g. that the own venomvine renders replace the thicket copy on the other venomvine plants while the thicket keeps its picture, and that Cistrel and Nubrith take their own renders); installs then use the owner-said flag per slot. Install with typed words does not release the old sha, so the thicket stays protected.
- After install: 25b911d827a8 can be retired once no slot holds it.
- Deploy: `./game` showed RUNNING at 2026-10-09, so deploy of any changed mod is owed.
