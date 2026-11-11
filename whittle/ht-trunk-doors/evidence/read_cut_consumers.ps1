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
$ops = @{}
foreach ($f in [Reflection.Emit.OpCodes].GetFields('Public,Static')) {
    $op=$f.GetValue($null); $ops[[int]$op.Value -band 65535]=$op
}
$token=$assembly.GetType('RimWorld.JobDefOf',$true).GetField('CutPlantDesignated').MetadataToken
"FIELD RimWorld.JobDefOf.CutPlantDesignated TOKEN $token"
$count=0
foreach($t in $assembly.GetTypes()) {
 foreach($m in (@($t.GetMethods('Public,NonPublic,Static,Instance,DeclaredOnly')) + @($t.GetConstructors('Public,NonPublic,Static,Instance')))) {
  $body=$m.GetMethodBody();if($null -eq $body){continue};$bytes=$body.GetILAsByteArray();$i=0
  while($i -lt $bytes.Length) {
   $offset=$i;$n=[int]$bytes[$i];$i++;if($n -eq 254){$n=65024+[int]$bytes[$i];$i++};$op=$ops[$n]
   if($null -eq $op){throw "invalid opcode $n"}
   if($op.Name -eq 'ldsfld' -and [BitConverter]::ToInt32($bytes,$i) -eq $token){"READ $($t.FullName)::$($m.Name) IL_$('{0:X4}' -f $offset)";$count++}
   switch($op.OperandType.ToString()) {
    'InlineNone' {}
    {$_ -in @('ShortInlineI','ShortInlineVar','ShortInlineBrTarget')} {$i++}
    'InlineVar' {$i+=2}
    {$_ -in @('InlineI8','InlineR')} {$i+=8}
    'InlineSwitch' {$n=[BitConverter]::ToInt32($bytes,$i);$i+=4+4*$n}
    default {$i+=4}
   }
  }
 }
}
"TOTAL_READS $count"
