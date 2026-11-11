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
$selected = @{
 'Verse.Thing'=@('.ctor'); 'Verse.ThingWithComps'=@('.ctor');
 'Verse.Def'=@('.ctor'); 'Verse.ThingDef'=@('.ctor');
 'Verse.RaceProperties'=@('.ctor'); 'RimWorld.LifeStageDef'=@('.ctor');
 'Verse.LifeStageAge'=@('.ctor'); 'Verse.DefModExtension'=@('.ctor');
 'Verse.Pawn'=@('.ctor'); 'Verse.Pawn_AgeTracker'=@('.ctor');
}

foreach ($typeName in $selected.Keys | Sort-Object) {
 $t=$assembly.GetType($typeName,$true)
 $methods=@($t.GetMethods('Public,NonPublic,Static,Instance,DeclaredOnly')) + @($t.GetConstructors('Public,NonPublic,Static,Instance'))
 foreach($m in $methods | Where-Object {$selected[$typeName] -contains $_.Name}) {
  "METHOD $typeName::$($m.Name) TOKEN $($m.MetadataToken)"
  $body=$m.GetMethodBody(); if($null -eq $body){continue}; $bytes=$body.GetILAsByteArray(); $i=0
  while($i -lt $bytes.Length) {
   $offset=$i; $n=[int]$bytes[$i]; $i++; if($n -eq 254){$n=65024+[int]$bytes[$i];$i++}; $op=$ops[[int]$n]; if($null -eq $op){throw "Unknown opcode $n at $offset"}; $arg=''
   switch ($op.OperandType.ToString()) {
    'InlineNone' {}
    'ShortInlineI' {$arg=[string][sbyte]::Parse($bytes[$i].ToString('X2'),'HexNumber');$i++}
    'ShortInlineVar' {$arg=[string]$bytes[$i];$i++}
    'InlineVar' {$arg=[string][BitConverter]::ToUInt16($bytes,$i);$i+=2}
    'ShortInlineR' {$arg=[string][BitConverter]::ToSingle($bytes,$i);$i+=4}
    'InlineR' {$arg=[string][BitConverter]::ToDouble($bytes,$i);$i+=8}
    'InlineI' {$arg=[string][BitConverter]::ToInt32($bytes,$i);$i+=4}
    'InlineI8' {$arg=[string][BitConverter]::ToInt64($bytes,$i);$i+=8}
    'ShortInlineBrTarget' {$d=[sbyte]::Parse($bytes[$i].ToString('X2'),'HexNumber');$i++;$arg='IL_{0:X4}' -f ($i+$d)}
    'InlineBrTarget' {$d=[BitConverter]::ToInt32($bytes,$i);$i+=4;$arg='IL_{0:X4}' -f ($i+$d)}
    'InlineSwitch' {$count=[BitConverter]::ToInt32($bytes,$i);$i+=4;$end=$i+4*$count;$targets=@();for($j=0;$j -lt $count;$j++){$targets+=('IL_{0:X4}' -f ($end+[BitConverter]::ToInt32($bytes,$i)));$i+=4};$arg=$targets -join ','}
    default {$token=[BitConverter]::ToInt32($bytes,$i);$i+=4;try {if($op.OperandType.ToString() -eq 'InlineString'){$arg='"'+$m.Module.ResolveString($token)+'"'}else{$member=$m.Module.ResolveMember($token);$arg=$member.DeclaringType.FullName+'::'+$member.ToString()}}catch{$arg='TOKEN '+$token+' RESOLUTION: '+$_.Exception.Message}}
   }
   'IL_{0:X4}: {1} {2}' -f $offset,$op.Name,$arg
  }
 }
 if($typeName -in @('Verse.XmlInheritance','RimWorld.WildAnimalSpawner')) {'AVAILABLE XML METHODS'; $methods | ForEach-Object {$_.ToString()}}
}
