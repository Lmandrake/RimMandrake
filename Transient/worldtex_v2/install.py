"""Install the v2 world textures through the art ledger, in place of the placeholders (same paths the defs name).
usage: python3 Transient/worldtex_v2/install.py [--dry-run]"""
import subprocess,sys,os
OWN="What's next on the world? Let's get it looking great again. Right now it's barely recognizable."
D=os.path.dirname(os.path.abspath(__file__))
MAP={"RM_Stillsand":("RimMandrake/Stillsand","RM_Stillsand"),"RUT_Umbra":("RimUtinni/UtinniPatches","RUT_Umbra"),
"RM_LongShade":("RimMandrake/LongShade","RM_LongShade"),"RM_TheRot":("RimMandrake/TheRot","RM_TheRot"),
"RM_Wasteland":("RimMandrake/Wasteland","RM_Wasteland"),"RM_NightsideIce":("RimMandrake/NightsideIce","RM_SleepingIce"),
"RM_Abyss":("RimMandrake/Abyss","RM_Abyss"),"RM_BlueDesert":("RimMandrake/BlueDesert","RM_BlueDesert"),
"RM_FloodedCanyon":("RimMandrake/CrackedLands","RM_CrackedLands"),"RM_LeaningScrub":("RimMandrake/LeaningScrub","RM_LeaningScrub"),
"RM_TwilightSea":("RimMandrake/TerminalBiomes","RM_TwilightSea"),"RM_Cauldron":("RimMandrake/Cauldron","RM_Cauldron"),
"RM_GreySea":("RimMandrake/TerminalBiomes","RM_GreySea"),"RM_TheScald":("RimMandrake/TerminalBiomes","RM_Scald"),
"RM_RustCathedral":("RimMandrake/RustCathedral","RM_RustCathedral"),"RM_Greentide":("RimMandrake/Greentide","RM_Greentide"),
"RM_WeepingStones":("RimMandrake/WeepingStones","RM_WeepingStones"),"RM_Pyrelands":("RimMandrake/Pyrelands","RM_Pyrelands"),
"RM_Contagion":("RimMandrake/Contagion","RM_Contagion"),"RM_Webwork":("RimMandrake/Webwork","RM_Webwork"),
"RM_GelatinousSlime":("RimMandrake/GelatinousSlime","RM_Slime"),"RM_Miasma":("RimMandrake/Miasma","RM_Miasma"),
"RM_Warscar":("RimMandrake/Scarlands","RM_Warscar"),"RM_TheChill":("RimMandrake/TerminalBiomes","RM_Chill"),
"RM_TheForge":("RimMandrake/TheForge","RM_Forge"),"RM_FeverWood":("RimMandrake/FeverWood","RM_FeverWood"),
"RM_TheSump":("RimMandrake/TheSump","RM_Sump")}
bad=0
for dn,(mod,name) in MAP.items():
    rel=f"World/Biomes/{name}.png"; assert os.path.exists(f"src/{mod}/Textures/{rel}"), (dn, mod, rel)
    x=subprocess.run(["python3","src/RimMandrake/Utils/art/art.py","install",mod,rel,"--file",os.path.relpath(os.path.join(D,"tex",dn+".png")),"--owner-said",OWN]+sys.argv[1:],capture_output=True,text=True)
    out=(x.stdout+x.stderr).strip().splitlines(); bad+=x.returncode!=0
    print(x.returncode, mod, rel, (out[-1] if out else "")[:120])
print("failures",bad)
