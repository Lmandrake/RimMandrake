import re,sys
L="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
t=open(L,errors="ignore").read()
cen=re.findall(r"\[(RimMandrake[^\]]*)\] Harmony: patched (\d+), missing (\d+)",t)
print("census lines:",len(cen)); [print(" ",c) for c in cen]
print("Harmony patch failed:",len(re.findall(r"Harmony patch failed",t)))
print("missing>0:",len(re.findall(r"Harmony: patched \d+, missing [1-9]",t)))
print("Patch operation failed:",len(re.findall(r"Patch operation .* failed",t)), "(baseline 38)")
print("xref:",len(re.findall(r"Could not resolve cross-reference",t)))
print("Exceptions:",len(re.findall(r"Exception",t)))
print("needs downloadUrl:",len(re.findall(r"needs to have <downloadUrl>",t)))
