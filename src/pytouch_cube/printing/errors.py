from enum import Enum


class Error1(Enum):
    ERROR1_NONE = 0
    ERROR1_NO_MEDIA = 0x01
    ERROR1_END_OF_MEDIA = 0x02
    ERROR1_TAPE_CUT_JAM = 0x04


class Error2(Enum):
    ERROR2_NONE = 0
    ERROR2_REPLACE_MEDIA = 0x01  # Replace the media.
    ERROR2_EXP_BUFFER_FULL = 0x02  # Expansion buffer is full.
    ERROR2_TRANS_ERROR = 0x04  # Transmission error
    ERROR2_TRANS_BUFF_FULL = 0x08  # Transmission buffer is full.
    ERROR2_COVER_OPEN = 0x10  # The cover is open


class PrinterError:
    def __init__(self, error_byte_1: int, error_byte_2: int):
        self.error1 = Error1(error_byte_1)
        self.error2 = Error2(error_byte_2)

    def __str__(self):
        if self.error1 == Error1.NO_MEDIA: return 'No media'
        if self.error1 == Error1.END_OF_MEDIA: return 'End of media'
        if self.error1 == Error1.TAPE_CUT_JAM: return 'Tape cut jam'

        if self.error2 == Error2.REPLACE_MEDIA: return 'Replace the media.'
        if self.error2 == Error2.EXP_BUFFER_FULL: return 'Expansion buffer is full'
        if self.error2 == Error2.TRANS_ERROR: return 'Transmission error'
        if self.error2 == Error2.TRANS_BUFF_FULL: return 'Transmission buffer is full'
        if self.error2 == Error2.COVER_OPEN: return 'The cover is open'

        return f'Unknown error (E1: 0x{hex(self.error1)} E2: 0x{hex(self.error2)})'
