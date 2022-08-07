
APP_SCRIPT='src/pytouch-cube/__main__.py'
ICON='pytouch3.ico'
IMG_DATA="pytouch3.png:."

VER=$(git describe)

echo "APP_VERSION = '$VER'" > src/pytouch_cube/version.py

pyinstaller \
    --add-data="$IMG_DATA" \
    --icon="$ICON" \
    --name pytouch-cube \
    --collect-all=pytouch_cube \
    "$APP_SCRIPT"