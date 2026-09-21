param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Destination
)

Add-Type -AssemblyName System.Drawing

$workspace = [IO.Path]::GetFullPath((Get-Location).Path)
$destinationFull = [IO.Path]::GetFullPath($Destination)
if (-not $destinationFull.StartsWith($workspace + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Destination must be inside the current workspace: $destinationFull"
}

$sourceBitmap = [System.Drawing.Bitmap]::new($Source)
$outputBitmap = [System.Drawing.Bitmap]::new(
    $sourceBitmap.Width,
    $sourceBitmap.Height,
    [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
)

$rect = [System.Drawing.Rectangle]::new(0, 0, $sourceBitmap.Width, $sourceBitmap.Height)
$sourceData = $null
$outputData = $null

try {
    $sourceData = $sourceBitmap.LockBits(
        $rect,
        [System.Drawing.Imaging.ImageLockMode]::ReadOnly,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    )
    $outputData = $outputBitmap.LockBits(
        $rect,
        [System.Drawing.Imaging.ImageLockMode]::WriteOnly,
        [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    )

    $byteCount = [Math]::Abs($sourceData.Stride) * $sourceBitmap.Height
    $sourcePixels = [byte[]]::new($byteCount)
    $outputPixels = [byte[]]::new($byteCount)
    [Runtime.InteropServices.Marshal]::Copy($sourceData.Scan0, $sourcePixels, 0, $byteCount)

    for ($i = 0; $i -lt $byteCount; $i += 4) {
        $alpha = [int]$sourcePixels[$i + 3]

        if ($alpha -le 24) {
            # Fully key-colored background; the small cutoff removes near-invisible fringe noise.
            $outputPixels[$i] = 0
            $outputPixels[$i + 1] = 255
            $outputPixels[$i + 2] = 0
            $outputPixels[$i + 3] = 255
            continue
        }

        # Alpha-composite subject pixels over #00ff00.
        $blue = [int](($sourcePixels[$i] * $alpha + 127) / 255)
        $green = [int](($sourcePixels[$i + 1] * $alpha + 255 * (255 - $alpha) + 127) / 255)
        $red = [int](($sourcePixels[$i + 2] * $alpha + 127) / 255)

        # Reserve exact #00ff00 exclusively for the background key.
        if ($red -eq 0 -and $green -eq 255 -and $blue -eq 0) {
            $red = 1
        }

        $outputPixels[$i] = [byte]$blue
        $outputPixels[$i + 1] = [byte]$green
        $outputPixels[$i + 2] = [byte]$red
        $outputPixels[$i + 3] = 255
    }

    [Runtime.InteropServices.Marshal]::Copy($outputPixels, 0, $outputData.Scan0, $byteCount)
}
finally {
    if ($null -ne $sourceData) { $sourceBitmap.UnlockBits($sourceData) }
    if ($null -ne $outputData) { $outputBitmap.UnlockBits($outputData) }
}

try {
    if (Test-Path -LiteralPath $destinationFull) {
        Remove-Item -LiteralPath $destinationFull -Force
    }
    $outputBitmap.Save($destinationFull, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $outputBitmap.Dispose()
    $sourceBitmap.Dispose()
}

Get-Item -LiteralPath $destinationFull | Select-Object FullName, Length, LastWriteTime
