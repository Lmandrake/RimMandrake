import collections
L = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
ls = open(L, encoding="utf-8", errors="replace").read().splitlines()
c = collections.Counter()
for i, l in enumerate(ls):
    if l.startswith("Error in GenStep"):
        fr = next((x.strip() for x in ls[i+1:i+6] if x.strip().startswith("at ")), "?")
        c[fr[:110]] += 1
print(len(ls)); [print(v, k) for k, v in c.items()]
