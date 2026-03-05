$ErrorActionPreference = "Stop"
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$zipPath = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

Write-Host "Downloading FFmpeg..."
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath

Write-Host "Extracting..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

$binPath = Get-ChildItem -Path $extractPath -Recurse -Filter "ffmpeg.exe" | Select-Object -ExpandProperty DirectoryName -First 1

Write-Host "FFmpeg bin found at: $binPath"
Write-Host "You should add this to your PATH or I will try to use it locally."

# Copy exe files to current dir for simplicity
Copy-Item "$binPath\*.exe" -Destination . -Force

Write-Host "Clean up..."
Remove-Item $zipPath -Force
Remove-Item $extractPath -Recurse -Force

Write-Host "Done. ffmpeg.exe is now in the current folder."
