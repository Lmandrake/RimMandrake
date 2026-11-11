# Independent pilot after three nonpasses

Fresh read-only Opus, no history/fork, neutral ext4 cwd and bounded Read/Glob/Grep: `evidence/pilot_call.json`, full original `pilot_raw.json`, exact `pilot_result.txt`.

The pilot traced run 3's clock 3 → 4 → 5 → 6. The two explicit setup ticks were measured correctly; occupied save/load contributed the uncounted final tick. It did not identify a production theft defect. This was diagnosis, not acceptance judgment.

Important additional findings acted on before another attempt: the load tick had run with pumps enabled, the round-trip comparison omitted global catch/charge/goodwill/reach fields, and source water was not checked. The script now disables pumps across the save/load interval, requires every returned theft field and all relevant source/outlet water quantities to match, measures/bounds load advance to 0–1 tick, and requires exact global clock accounting as setup ticks plus that measured load delta. The clock assertion is retained; no old result is relabeled.
