# BOUNDARY: who an art install speaks for, and the correction of a false keep

Code: `src/RimMandrake/Utils/art/artledger.py` (`install`, `conductor_only_authority`, `correct_keep`) and
`src/RimMandrake/Utils/art/art.py` (`install`, `correct-keep`).
The tests are in `src/RimMandrake/Utils/art/selftest_art_install_authority.py`.

## ACCEPTS

- `install` with `--owner-said`, `--by-card` or a `--per-ruling` that is not a Conductor ruling: the install is his
  keep, as before.
- `install` with `--per-ruling` set to one of the Conductor's two rulings (`CONDUCTOR_RULINGS`) and no `--owner-said`
  and no `--by-card`: the install is the Conductor's act.
- `correct_keep` with one of the Conductor's two rulings and a `--why`, naming a picture (sha, 8 or more hex digits) or
  the event id of a keep that `art install` wrote.

## DOES NOT SURVIVE

- A ledger line that is torn needs ledger repair first. A process that dies between the two writes of one install can
  leave a picture installed with no `live` event; `art.py doctor` finds it.
- Two `correct_keep` calls at the same moment on one keep both append the same event id; the ledger holds one of them.

## PROMISES

- **conductor-install-mints-no-owner-keep.** An install that cites a Conductor ruling alone writes no owner keep. The
  picture is not protected against a later install by the pipeline. The `live` event keeps the cited ruling and the
  `--why` text.
- **conductor-install-never-displaces-other-authority.** An install under a Conductor ruling alone never replaces a
  picture whose keep carries `said`, `by_card` or another `per_ruling` id.
- **correct-keep-releases-conductor-only-keep.** `correct_keep` on a keep that carries a Conductor ruling alone appends
  one release event (by the Conductor, with the ruling and the `--why`). The keep stays in the ledger. A second call
  writes nothing. `--dry-run` writes nothing.
- **correct-keep-refuses-his-keeps.** `correct_keep` refuses a keep that carries `said`, `by_card` or another
  `per_ruling` id, a keep that is not an install's, an event that is not a keep, a ruling that is not the Conductor's,
  and a blank `--why`. A refusal writes nothing.
- **correct-keep-by-event-id-releases-install-said.** `correct_keep` by event id releases an install's keep that carries
  `said` alone, when the `--why` names that install by its event id or its picture sha. By picture it still refuses.
- **art-cli-correct-keep-and-install-help.** `art.py correct-keep` prints each refusal as `REFUSED` and exits 2.
  `art.py install --help` says that `--owner-said` on an install means that the owner chose this picture and that an
  order of the owner to fix a thing goes in `--why`.
