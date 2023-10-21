from dataclasses import dataclass

from .errors import PrinterError

STATUS_REPLY = 0x00
STATUS_PRINT_DONE = 0x01
STATUS_ERROR = 0x02
STATUS_PHASE_CH = 0x06

STATUS_TYPE = [
    "Reply to status request",
    "Printing completed",
    "Error occured",
    "IF mode finished",
    "Power off",
    "Notification",
    "Phase change",
]

STATUS_BATTERY = [
    "Full",
    "Half",
    "Low",
    "Change batteries",
    "AC adapter in use"
]

STATUS_OFFSET_BATTERY = 6
STATUS_OFFSET_EXTENDED_ERROR = 7
STATUS_OFFSET_ERROR_INFO_1 = 8
STATUS_OFFSET_ERROR_INFO_2 = 9
STATUS_OFFSET_STATUS_TYPE = 18
STATUS_OFFSET_PHASE_TYPE = 19
STATUS_OFFSET_NOTIFICATION = 22


@dataclass
class Status:
    def __init__(self, raw: bytes):

        if len(raw) != 32:
            self.parse_error = "Error: status must be 32 bytes. Got " + str(len(raw))
            return

        header = raw[:8]
        if header != b'\x80\x20B0J0\x00\x00':
            self.parse_error = 'Header mismatch! Got ' + str(header)

        self.error = PrinterError(raw[STATUS_OFFSET_ERROR_INFO_1], raw[STATUS_OFFSET_ERROR_INFO_2])
        self.battery = raw[STATUS_OFFSET_BATTERY]
        self.media_width = raw[10]
        self.media_type = raw[11]
        self.media_length = raw[17]
        self.status_type = raw[STATUS_OFFSET_STATUS_TYPE]
        self.phase_type = raw[19]
        self.phase_number = raw[20:1]
        self.notif_number = raw[22]

        self.extended_error = raw[STATUS_OFFSET_EXTENDED_ERROR]

    def __str__(self):
        status = f'Status: {STATUS_TYPE[self.status_type]}'
        if self.status_type == STATUS_ERROR:
            status += f', Error: {self.error}'
        return status
