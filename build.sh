
APP_SCRIPT='src/pytouch_cube/__main__.py'
ICON='pytouch3.ico'
IMG_DATA="pytouch3.png:."

VER=$(git describe --all)

echo "APP_VERSION = '$VER'" > src/pytouch_cube/version.py

echo "version.py:"
cat src/pytouch_cube/version.py
echo

pyinstaller \
    --add-data="$IMG_DATA" \
    --icon="$ICON" \
    --name pytouch-cube \
    --collect-all=pytouch_cube \
    "$APP_SCRIPT"