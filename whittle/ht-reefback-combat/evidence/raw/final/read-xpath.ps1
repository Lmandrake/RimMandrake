param([string]$InputPath)
$ErrorActionPreference='Stop'
$r=Get-Content -Raw -LiteralPath $InputPath | ConvertFrom-Json
$raw=New-Object System.Xml.XmlDocument
$raw.Load($r.raw)
$resolved=New-Object System.Xml.XmlDocument
$resolved.Load($r.resolved)
$rows=@()
foreach($xp in $r.expressions){
 try {
  $rows += @{xpath=$xp;raw_hits=$raw.SelectNodes($xp).Count;resolved_hits=$resolved.SelectNodes($xp).Count}
 } catch { $rows += @{xpath=$xp;error=$_.Exception.Message} }
}
ConvertTo-Json -Depth 6 -Compress -InputObject @($rows)
