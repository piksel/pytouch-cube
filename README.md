<div align="center">
<img src="https://github.com/piksel/pytouch-cube/raw/main/pytouch3.png" width="256" height="256" />
</div>


# PyTouch Cube
Qt5 Label Editor for Brother P-Touch Cube label maker.  
Forked from [this gist by @stecman](https://gist.github.com/stecman/ee1fd9a8b1b6f0fdd170ee87ba2ddafd)

# Installation note:
To install the dependencies into a virtual env run
```
python3 -m venv venv
. venv/bin/activate
```

Install the dependencies with
```
python3 -m pip install -r requirements.txt
```

and run the app with

```
python3 pytouch3.py
```

# Connecting to the device on linux

After connecting to the device it will automatically disconnect again.
On linux you can list the device by using bluetooth-ctl's paired-devices listing.
e.g.
```
[bluetooth]# paired-devices
Device EC:79:49:65:XX:XX PT-P300BTXXXX
```

You can then create an rfcom device from the bl address:
```
sudo rfcomm bind 0 EC:79:49:65:XX:XX 1
```
