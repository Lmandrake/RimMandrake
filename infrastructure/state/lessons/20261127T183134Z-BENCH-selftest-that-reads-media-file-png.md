A selftest that reads a media file (png, ogg...) must read the git index blob when the working file is absent: helper clones are slim (no media on disk), and a bare os.path.exists check reads FAIL, which code_review_status turns into a false DIRTY. Pattern: git cat-file blob :<path> (selftest_world_sea_lists.py glass_png).
item: RIMMANDRAKE_REVIEW_WORLD_SEA_LISTS_FRESH_READER_OWED
home: skills/rimworld-modding
