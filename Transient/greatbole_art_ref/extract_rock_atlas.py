import UnityPy

path = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\resources.assets"
env = UnityPy.load(path)

found = []
for obj in env.objects:
    if obj.type.name == "Texture2D":
        try:
            d = obj.read()
        except Exception:
            continue
        name = getattr(d, "m_Name", "")
        if "rock_atlas" in name.lower():
            found.append((name, d))

print("candidates:", [n for n, _ in found])

for name, d in found:
    out = "%s.png" % name
    d.image.save(out)
    print("saved", out, d.image.size)
