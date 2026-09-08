param([int]$Count = 45, [int]$IntervalSec = 40)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$dir = "D:\Luke\dev\Rimworld\Transient\loadercaps"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
for ($i = 1; $i -le $Count; $i++) {
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
    $f = Join-Path $dir ("cap_{0:d3}.png" -f $i)
    $bmp.Save($f, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Start-Sleep -Seconds $IntervalSec
}
Write-Output "capture loop done: $Count frames"
