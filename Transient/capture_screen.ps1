param([string]$OutFile = "D:\Luke\dev\Rimworld\Transient\loadercap_test.png")
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type 'using System.Runtime.InteropServices;public class DPI{[DllImport("shcore.dll")] public static extern int SetProcessDpiAwareness(int v);}'
[void][DPI]::SetProcessDpiAwareness(2)
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved $OutFile"
