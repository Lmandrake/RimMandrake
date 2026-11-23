import sys
P='src/RimMandrake/ExplosiveKnockback/Source/'
v=sys.argv[1]
E={'unheld':[('RM_KnockbackProof.cs','const int holdFrom = 1;','const int holdFrom = 55;')],
'walkoff':[('RM_KnockbackProof.cs','                                if (dd >= 55 && dd < 60 && sleeper.Spawned','                                if (dd == 40) { carrier.Position = carrier.Position + new IntVec3(3, 0, 0); }\n                                if (dd >= 55 && dd < 60 && sleeper.Spawned')],
'pit':[('RM_MapComponent_Knockback.cs','x = t.Position.x, z = t.Position.z,\n                onSuperdeep = RM_KnockbackCompat.IsSuperdeep(map, t.Position) };','x = t.Position.x, z = t.Position.z,\n                onSuperdeep = false };')]}
for f,a,b in E[v]:
    s=open(P+f,newline='').read()
    if a not in s: a=a.replace('\n','\r\n'); b=b.replace('\n','\r\n')
    assert s.count(a)==1,(f,s.count(a)); open(P+f,'w',newline='').write(s.replace(a,b))
