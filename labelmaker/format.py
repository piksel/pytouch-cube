from enum import Enum


class Phase(Enum):
    RECEIVING = 0x00
    PRINTING = 0x01


class Mode(Enum):
    PTCBP = 1


class Media(Enum):
    UNKNOWN = 0x00

    LAMINATED = 0x01
    """Laminated tape, stamp tape and security tape (tape for sealing)"""

    LETTERING = 0x02
    """Instant lettering tape and iron-on transfer tape"""

    NONLAMINATED = 0x03
    """Non-laminated tape/rolls and thermal tape"""

    AV_TAPE = 0x08
    """AV Tape"""

    HG_TAPE = 0x09
    """TZ/HG Tape"""


"""
Paper   Width   Length
---- AV tape ----------
AV1789     17       89
AV1957     19       57
AV2067     20       67
---- TZ tape/HG tape --
  6 mm      6        0
  9 mm      9        0
 12 mm     12        0
 18 mm     18        0
 24 mm     24        0
 36 mm     36        0
-------+-------+------
Paper   Width   Length
"""