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

PyBluez 0.23 in Version is incompatible with setuptools >=58.0.0
Downgrade setuptools first with
```
python3 -m pip install setuptools==57.0.0
```

Then install the dependencies with
```
python3 -m pip install -r requirements.txt
```

and run the app with

```
python3 pytouch.py
```



