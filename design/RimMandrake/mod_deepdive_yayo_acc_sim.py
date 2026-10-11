"""Shooter hit factor (ShotReport.HitFactorFromShooter, before weapon/cover/size factors):
vanilla acc^d vs Yayo advShootAcc (accEf 60, baseSkill 5). Curve = ShootingAccuracyPawn
postProcessCurve (RimSage, 1.6); pre-curve value = Shooting level (healthy sight/manipulation)."""
pts=[(0,.89),(2,.93),(4,.94),(6,.95),(8,.96),(10,.97),(12,.975),(14,.98),(16,.98333),(18,.98666),(20,.99)]
def curve(x):
    for (a,va),(b,vb) in zip(pts,pts[1:]):
        if a<=x<=b: return va+(vb-va)*(x-a)/(b-a)
def yayo(a,s): return a+0.6*((s/20)*(1-a))
print("| shooter | per-tile vanilla -> Yayo | hit factor @12 tiles | @25 | @40 |")
print("|---|---|---|---|---|")
for lab,s,a in [("skill 0",0,curve(0)),("skill 5",5,curve(5)),("skill 10",10,curve(10)),("skill 15",15,curve(15)),("skill 20",20,curve(20)),("mech (no skill: offset 8; Yayo uses baseSkill 5)",5,curve(8))]:
    y=yayo(a,s)
    print("| %s | %.4f -> %.4f | %.2f -> %.2f | %.2f -> %.2f | %.2f -> %.2f |"%(lab,a,y,a**12,y**12,a**25,y**25,a**40,y**40))
