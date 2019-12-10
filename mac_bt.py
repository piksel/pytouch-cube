from pprint import pprint

import ctypes
import ctypes.util
import objc
import AppKit

iokit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('IOKit'))
cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))

kIOMasterPortDefault = ctypes.c_void_p.in_dll(iokit, "kIOMasterPortDefault")
kCFAllocatorDefault = ctypes.c_void_p.in_dll(cf, "kCFAllocatorDefault")

kCFStringEncodingMacRoman = 0
iokit.IORegistryEntryCreateCFProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
iokit.IORegistryEntryCreateCFProperty.restype = ctypes.c_void_p

cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32]
cf.CFStringCreateWithCString.restype = ctypes.c_void_p

cf.CFDataGetLength.argtypes = [ctypes.c_void_p]
cf.CFDataGetLength.restype = ctypes.c_int



try:
    # mac os 10.5 loads frameworks using bridgesupport metadata
    '''
        __bundle__ = objc.initFrameworkWrapper("IOBluetoothUI",
            frameworkIdentifier="com.apple.IOBluetoothUI",
            frameworkPath=objc.pathForFramework(
                "/System/Library/Frameworks/IOBluetoothUI.framework"),
            globals=globals())

    '''
    IOBluetoothUI = objc.ObjCLazyModule("IOBluetoothUI",
            frameworkIdentifier="com.apple.IOBluetoothUI",
            frameworkPath=objc.pathForFramework(
                "/System/Library/Frameworks/IOBluetoothUI.framework"),
            metadict=globals())

    IOBluetooth = objc.ObjCLazyModule("IOBluetooth",
                        frameworkIdentifier="com.apple.IOBluetooth",
                        frameworkPath=objc.pathForFramework(
                            "/System/Library/Frameworks/IOBluetooth.framework"
                        ),
                        metadict=globals())

    IOKit = objc.ObjCLazyModule("IOKit",
                                frameworkIdentifier="com.apple.IOKit",
                                frameworkPath=objc.pathForFramework(
                                    "/System/Library/Frameworks/IOKit.framework"
                                ),
                                metadict=globals())

except (AttributeError, ValueError) as x:
    pprint(x)

del objc

def formatdevaddr(addr):
    """
    Returns address of a device in usual form e.g. "00:00:00:00:00:00"
    - addr: address as returned by device.getAddressString() on an
      IOBluetoothDevice
    """
    # make uppercase cos PyS60 & Linux seem to always return uppercase
    # addresses
    # can safely encode to ascii cos BT addresses are only in hex (pyobjc
    # returns all strings in unicode)
    return addr.replace("-", ":").encode('ascii').upper()

def _getdevicetuple(iobtdevice):
    """
    Returns an (addr, name, COD) device tuple from a IOBluetoothDevice object.
    """
    addr = formatdevaddr(iobtdevice.getAddressString())
    name = iobtdevice.getName()
    cod = iobtdevice.getClassOfDevice()
    return (addr, name, cod)

def selectdevice():
    gui = IOBluetoothUI.IOBluetoothDeviceSelectorController.deviceSelector()

    SERIAL_SERVICE = 0x1101

    # try to bring GUI to foreground by setting it as floating panel
    # (if this is called from pyobjc app, it would automatically be in foreground)
    try:
        gui.window().setFloatingPanel_(True)
    except:
        pass

    # only allow devices with Serial service
    uuid = IOBluetooth.IOBluetoothSDPUUID.uuid16_(SERIAL_SERVICE)
    gui.addAllowedUUID_(uuid)

    # show the window and wait for user's selection
    response = gui.runModal()   # problems here if transferring a lot of data??
    if response == AppKit.NSRunStoppedResponse:
        results = gui.getResults()

        if len(results) > 0:  # should always be > 0, but check anyway
            devinfo = _getdevicetuple(results[0])

            # sometimes the baseband connection stays open which causes
            # problems with connections w so close it here, see if this fixes
            # it
            dev = results[0]
            if dev is not None:

                name = dev.getName()
                disp_name = dev.getDisplayName()
                dev_class = [dev.getDeviceClassMajor(), dev.getDeviceClassMinor()]

                print('Name:', name)
                print('DispName:', disp_name)
                print('DeviceClass', 'Major:', dev_class[0], 'Minor:', dev_class[1])


            pprint(devinfo)
            dev = IOBluetooth.IOBluetoothDevice.withAddressString_(devinfo[0])

            if dev is not None and dev.isConnected():
                dev.closeConnection()

            return devinfo

    # user cancelled selection
    return None

class CFRange(ctypes.Structure):
    _fields_ = [("location", ctypes.c_int), ("length", ctypes.c_int)]

def get_bytes_property(device_type, property):
    """
    Search the given device for the specified string property

    @param device_type Type of Device
    @param property String to search for
    @return Python string containing the value, or None if not found.
    """


    key = cf.CFStringCreateWithCString(
            kCFAllocatorDefault,
            property.encode("mac_roman"),
            kCFStringEncodingMacRoman)

    CFContainer = iokit.IORegistryEntryCreateCFProperty(
            device_type,
            key,
            kCFAllocatorDefault,
            0)
    output = None
    print(type(CFContainer))

    if CFContainer:

        cf_range = CFRange()
        cf_range.location = 0

        print(cf_range.length)
        cf_range.length = cf.CFDataGetLength(CFContainer)

        cf.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        cf.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_uint8)

        output = list(range(cf_range.length))

        out_ptr = cf.CFDataGetBytePtr(CFContainer)
        # 0, cf.CFDataGetLength(CFContainer))
        for i in range(0, cf_range.length):
            output[i] = out_ptr[i]

        print(out_ptr)
        print(cf_range.length)
        print(output)


        #cf.CFDataGetBytes(CFContainer, cf_range, out_ptr)

        #output = cf.CFStringGetCStringPtr(CFContainer, 0)
        #if output is not None:
        #    output = output.decode('mac_roman')
        #cf.CFRelease(CFContainer)
    return output