# PyTouch Cube

Forked from [this gist by @stecman](https://gist.github.com/stecman/ee1fd9a8b1b6f0fdd170ee87ba2ddafd)

## Controlling the Brother P-Touch Cube label maker from a computer

The Brother PTP300BT label maker is intended to be controlled using the official Brother P-Touch Design & Print iOS/Android app. The app has arbitrary limits on what you can print (1 text object and up to 3 preset icons), so I thought it would be a fun challenge to reverse engineer the protocol to print whatever I wanted.

Python code at the bottom if you want to skip the fine details.

## Process

Intitially I had a quick peek at the Android APK to see if there was any useful information inside. The code that handles the communication with the printer in *Print&Design* turned out to be a native library, but the app clearly prepares a bitmap image and passes it to this native library for printing. Bitmaps are definitely something we can work with.

Next I used the bluetooth sniffing capability of stock Android to capture a few label prints from the official app. Inspecting these packet captures in Wireshark, it was apparent that all of the communication used bluetooth's serial port profile (SPP). Interestingly, the the printer shows up as "Fujitsu" in packet captures, and since Brother has a lot of label maker products I figured there was a good chance they were using some existing label maker hardware and firmware with a bluetooth to serial adapter bolted on.

After a little Googling, this hunch paid off - a bunch of developer documentation for some of Brother's higher-end/business label maker products matched up with the bytes being sent over the bluetooth serial connection. Mainly:

- [PT-9500PC Command Reference: CBP-RASTER Mode (PTCBP Mode) Volume](http://etc.nkadesign.com/uploads/Printers/95CRRASE.pdf)

At first I found similarities in a manual for Brother's ESC/P protocol, which has the same command format, initialisation command and 32 byte status format, but the P-Touch Cube doesn't appear to support this (based on trying the ESC/P commands on the device).

## Serial protocol

From Brother's developer docs for a different device, the packet captures could be broken down as:

```
// 64 bytes of 0x0 (to clear print buffer?)
...

// Initialize/reset settings registers
1B 40

// Enter raster mode (aka. PTCBP)
1B 69 61 01

// Set media and quality (most importantly, the number of 128px lines to expect)
// Found docs for this last by searching for the first three bytes (command)
// See http://www.undocprint.org/formats/page_description_languages/brother_p-touch
1B 69 7A C4 01 0C 00 08 01 00 00 00 00

// Set expanded mode bits (print chaining: off)
1B 69 4B 08

// Set mode bits (mirror print: no, auto tape cut: no)
1B 69 4D 00

// Set margin (feed) size
1B 69 64 1C 00

// Set compression mode: TIFF (packbits)
4D 02

// Transfer n1 + n2*256 bytes of raster data
// The official app transfers one line of data at a time (16 bytes = 128 pixels)
47 n1 n2 [data]
...

// Print and feed
1A
```

## Image data

Image data is sent to the printer as a 1-bit-per-pixel bitmap. The Brother app sends a 128 pixel wide image (regardless of tape width), oriented as lines across the print head. For a horizontal label (printing along the length of tape), the input image needs to be rotated by 90 degrees before sending.

Once in the correct orientation, image data needs to be mirrored horizontally (with the settings above at least). It looks like the command `1B 69 4D` can be used to enable mirroring by the printer, but I haven't tested this.

The outer edges of a 12mm label do not appear to be printable (print head too narrow?). The outer 30 pixels of each side (length-wise) are not printed. I haven't tested with narrower labels.

## Python code

The code here is what I had at the point I got this working - it's a bit hacked together. It prints images, but the status messages printed aren't complete and the main script needs some tidying up. The printer sometimes goes to an error state after printing (haven't figured out why yet), which can be cleared by pressing the power button once.

This needs a few modules installed to run:

```
pyserial
pypng
packbits
```

Then it can be used as:

```sh
# Existing image formated to spec above
./labelmaker.py monochrome-128px-wide-image.png

# Using imagemagick to get a usable input image from any horizontal oriented image
# -resize 128x can be used instead of -crop 128x as needed
# -rotate 90 can be removed if the image is portrait already
convert inputimage.png -monochrome -gravity center -crop 128x -rotate 90 -flop out.png
```

I was working on Linux, so the serial device is currently hard-coded as `/dev/rfcomm0`. On OSX, a `/dev/tty.*` device will show up once the printer is paired.

To pair the printer with my Linux machine, I used:

```sh
# Pair device
$ bluetoothctl
> scan on
... (turn printer on and wait for it to show up: PT-P300BT8894)
> pair [address]

# Setup serial port
$ sudo modprobe rfcomm
$ sudo rfcomm bind rfcomm0 [address of printer]
```
