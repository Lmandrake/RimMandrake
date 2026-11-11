$ErrorActionPreference = 'Stop'
$rows=@()
foreach($base in @(8,20,7)) {
 $health=[single]([single]$base * [single]0.6)
 $bodyProduct=[single]([single]40 * $health)
 $brainProduct=[single]([single]10 * $health)
 $heartProduct=[single]([single]15 * $health)
 $rows+=@{baseHealthScale=$base;stageFactor=[double][single]0.6;
  healthScale=[double]$health;bodyProduct=[double]$bodyProduct;
  bodyCeiling=[Math]::Ceiling($bodyProduct);brainCeiling=[Math]::Ceiling($brainProduct);
  heartCeiling=[Math]::Ceiling($heartProduct)}
}
ConvertTo-Json -Depth 4 -InputObject @($rows)
