verify_clone.py on two NVMe drives is latency-bound, not CPU-bound (one shard ~55 MB/s per side, CPU 13%, queue 0.6): 6 parallel shards by top folder reached 225 GB in ~65 min, still too slow for the owner. Budget hours for a whole-disk hash verify or sample it; shard by size, not by folder (Users held most of the bytes).
home: D:\ClaudeWork\rimmandrake\steve_diag\nvme_replacement.md
