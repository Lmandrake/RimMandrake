jawa/list_things returns at most limit rows (default 200), so a census that counts the 'things' rows silently stops at 200; count from perDef / countMatched, which cover every match. And after 'Regenerate Current Map' programState stays Playing, so a wait-for-Playing loop passes at once and censuses the OLD map; wait for map_info mapId to change.
home: rimbridge
