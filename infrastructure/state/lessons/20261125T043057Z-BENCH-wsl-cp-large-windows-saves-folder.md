A WSL cp -a of a large Windows Saves folder (9 GB, /mnt/c to /mnt/d) fails part-way with 'Cannot allocate memory' on read and write, and leaves partial files. Back up a Saves folder with robocopy.exe under a timeout (timeout -k 10 N robocopy.exe SRC DST /E /COPY:DAT /R:2 /W:5); it copied 9.1 GB in 4 s with 0 failed, and replaced the partial files.
item: RIMMANDRAKE_SETTLE_PYRE_AFTER_PASS_REVIEW_SAVE_PENS_ART_KEPT
home: infrastructure/state/facts/tool_traps.md
