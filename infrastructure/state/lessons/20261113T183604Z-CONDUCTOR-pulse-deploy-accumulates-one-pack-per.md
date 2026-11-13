pulse-deploy accumulates one pack per fetch pass (896 packs, 10 GiB): git then exceeds the timer's 80 s budget even with no tmp_pack garbage; repack -a -d it, and a stale index.lock also blocks it
home: skills/relentless/references/traps.md
