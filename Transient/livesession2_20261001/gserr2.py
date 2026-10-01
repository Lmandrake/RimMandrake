L = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
ls = open(L, encoding="utf-8", errors="replace").read().splitlines()
idx = [i for i, l in enumerate(ls) if l.startswith("Error in GenStep")]
for i in idx[1:3]:
    print("----"); print("\n".join(x[:200] for x in ls[i:i+5]))
