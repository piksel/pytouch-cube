
$APP_SCRIPT='pytouch3.py'
$ICON='pytouch3.ico'
$IMG_DATA="pytouch3.png;."

$VER=$(git describe)
$ZIPFILE="pytouch3-win64-$VER.zip"

Write-Host -Fore Cyan "Building archive for PyTouch Cube $VER`n"
Write-Host -Fore Cyan ":: Running PyInstaller..."
pyinstaller --noconfirm --add-data=$IMG_DATA  --windowed --icon=$ICON $APP_SCRIPT

if (Test-Path dist/$ZIPFILE)
{
    Write-Host -Fore Cyan ":: Removing previous archive..."
    Remove-Item dist/$ZIPFILE
}
Push-Location dist/pytouch3
Write-Host -Fore Cyan ":: Compressing archive..."
7z a -bb0 "-x!opengl32sw.dll" "-x!qt5qml*.dll" "-xr!qwebgl.dll" "-xr!qminimal.dll" "-xr!qoffscreen.dll" ..\$ZIPFILE *
Pop-Location

Write-Host -Fore Cyan ":: Done!"
