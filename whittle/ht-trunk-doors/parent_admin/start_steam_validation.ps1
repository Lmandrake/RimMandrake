$ErrorActionPreference = 'Stop'
$steam = Get-Process steam | Select-Object -First 1
if (-not $steam -or -not $steam.Path) { throw 'Existing Steam client is required' }
$contentLog = Join-Path (Split-Path $steam.Path) 'logs/content_log.txt'
if (-not (Test-Path -LiteralPath $contentLog)) { throw 'Steam content log is absent' }
$before = Get-Item -LiteralPath $contentLog
$receipt = @{
    appid = 294100
    uri = 'steam://validate/294100'
    requestedUtc = [DateTime]::UtcNow.ToString('o')
    contentLog = $contentLog
    priorBytes = $before.Length
    priorModifiedUtc = $before.LastWriteTimeUtc.ToString('o')
    result = 'request only; completion requires a new validation log record'
}
Start-Process -FilePath $receipt.uri
$receipt | ConvertTo-Json -Depth 4
