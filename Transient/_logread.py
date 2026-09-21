import re,sys
p=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
s=open(p,encoding="utf-8",errors="replace").read()
print("size",len(s))
print("tokens:",re.findall(r"Bridge token: (\w+)",s))
for pat in ["Resetting mods config","Recovered from incompatible","TypeLoadException","Could not find a type named RimMandrake","Config error","Could not resolve cross-reference"]:
    print(pat,"->",len(re.findall(pat,s)))
m=re.findall(r"(?i)active mods.*|mods loaded.*|Loading \d+ mods.*",s)[:3]; print(m)
print("BMT_ mentions:",len(re.findall("BMT_",s)))
print("tail:",s[-600:])
