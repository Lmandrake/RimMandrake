# Mod-list swap — CHECK owns this

The live list is
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.

🔴 **`ModsConfig.FULL.LATEST.xml` is the owner's real 583-mod list. Restore it before he
plays. Nothing here is authoritative about the game until it is copied back.**

Captured 2026-08-19 20:15, 583 active, md5 `5a9a4d3a958ad96dad442bedfc926f5c`.
Timestamped siblings are history; `LATEST` is the one to restore.

```
python3 src/RimMandrake/Utils/modlist_swap.py --status
python3 src/RimMandrake/Utils/modlist_swap.py --minimal    # swap to the test list
python3 src/RimMandrake/Utils/modlist_swap.py --restore    # put the owner's list back
```

⚠️ **RimSort and RimWorld both write this file and neither tells the other.** Do the swap
with the game DOWN and RimSort not mid-edit, and re-capture FULL if the owner has changed
his list since the timestamp above.
