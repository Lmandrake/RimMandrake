# caravan/static/seal fixes 20261009

- HalfExtractedCore tradeability Sellable->All (caravan sells it to player; needs Buyable)
- ProofHarvest accepts ; as well as | (static_call splits on |); Webwork validation.py uses ;
- VAULT_SEAL_PLUG_1 existed with criteria; verify-notes added
