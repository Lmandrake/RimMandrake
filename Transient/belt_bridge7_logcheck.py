import re, sys
L = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
txt = open(L, encoding="utf-8", errors="replace").read()
lines = txt.splitlines()
print("lines", len(lines))
def hits(pred, label, show=6):
    h = [l for l in lines if pred(l)]
    print("%-58s %d" % (label, len(h)))
    for l in h[:show]: print("    ", l[:260])
    return h
hits(lambda l: "Bridge token:" in l, "Bridge token (expected 1)", 1)
hits(lambda l: "Recovered from incompatible or corrupted mods" in l or "Caught exception while loading play data" in l, "dead-load strings (expect 0)")
hits(lambda l: "Failed to find any textures" in l or "Could not load Texture" in l or "Could not find texture" in l, "ALL texture-missing lines (info)", 40)
fold = ("RimStarWars/SWBestiary/", "RimStarWars/Shokk/", "RimUtinni/UtinniPatches/", "Megathrips", "swanimals/Dalgo", "swanimals/Iriaz", "Nuna")
hits(lambda l: ("texture" in l.lower() or "Failed to find" in l) and any(f in l for f in fold), "F3: texture errors on fold paths (expect 0)")
hits(lambda l: "ArtFold" in l and ("rror" in l or "Failed" in l), "ArtFold patch errors (expect 0)")
hits(lambda l: "artoverride" in l.lower(), "artoverride mentions (expect 0)")
hits(lambda l: "Could not resolve cross-reference" in l, "cross-reference errors (info)", 20)
leather = ("RM_ToxinSealant", "RM_RoyalRind", "RM_GreatboleGrubSpines", "RSW_TelluroxShell")
hits(lambda l: any(x in l for x in leather) and ("rror" in l or "exture" in l), "leather texPath fix errors (expect 0)")
hits(lambda l: any(x in l for x in ("Zersium", "AlloyForge", "AlloyDurasteel", "PlasteelAlloying")) and ("rror" in l or "Exception" in l), "zersium/alloy forge errors (expect 0)")
rem = ("RM_RotWeakChitin", "RM_RotMediumChitin", "RSW_WeakChitin", "RSW_FragileChitin", "RSW_MediumChitin", "RSW_ToxiChitin",
       "RSW_GrayChitin", "RSW_CrystalChitin", "RUT_Hardwood", "ChunkSlagPlasteel_GT", "RUT_TibannaGas", "Silooth")
hits(lambda l: any(x in l for x in rem) and ("rror" in l or "Could not" in l or "xception" in l), "removed-def / silooth errors (expect 0)")
hits(lambda l: "JawaRules" in l and ("rror" in l or "xception" in l), "JawaRules errors (expect 0)")
hits(lambda l: l.startswith("Config error"), "Config errors (info)", 40)
