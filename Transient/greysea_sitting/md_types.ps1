$p = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2111424996\1.6\Assemblies\MapDesigner.dll'
$a = [Reflection.Assembly]::LoadFile($p)
try { $ts = $a.GetTypes() } catch [Reflection.ReflectionTypeLoadException] { $ts = $_.Exception.Types | ? { $_ } }
foreach ($t in $ts) { try { foreach ($m in $t.GetMethods([Reflection.BindingFlags]'Public,Static,DeclaredOnly')) { "$($t.FullName)::$($m.Name)" } } catch {} ; try { foreach ($f in $t.GetFields([Reflection.BindingFlags]'Public,NonPublic,Static,DeclaredOnly')) { "$($t.FullName).$($f.Name) [field]" } } catch {} }
