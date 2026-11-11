param([string]$GameDir)
$ErrorActionPreference = 'Stop'
$managed = Join-Path $GameDir 'RimWorldWin64_Data/Managed'
[AppDomain]::CurrentDomain.add_ReflectionOnlyAssemblyResolve({param($s,$e)
    $name = ([Reflection.AssemblyName]$e.Name).Name + '.dll'
    $path = Join-Path $managed $name
    if (Test-Path $path) { return [Reflection.Assembly]::ReflectionOnlyLoadFrom($path) }
    return [Reflection.Assembly]::ReflectionOnlyLoad($e.Name)
})
$assembly = [Reflection.Assembly]::ReflectionOnlyLoadFrom((Join-Path $managed 'Assembly-CSharp.dll'))
foreach($name in @('RimWorld.PawnGenOption','Verse.PawnGenOption','RimWorld.PawnGroupMakerUtility','RimWorld.IncidentWorker_ManhunterPack')) {
 $t=$assembly.GetType($name,$false)
 if($null -eq $t){"ABSENT $name";continue}
 "TYPE $name"
 $t.GetMethods('Public,NonPublic,Static,Instance,DeclaredOnly') | ForEach-Object {$_.ToString()}
}
