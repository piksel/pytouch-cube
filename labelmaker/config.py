from dataclasses import dataclass, asdict
from typing import Callable

@dataclass
class LabelMakerConfig:
    mirror_printing: bool = False
    auto_tape_cut: bool = False

    """Warn: Only effective with laminated tape"""
    half_cut: bool = False

    """When printing multiple copies, the labels are fed after the last one is printed."""
    chain_print: bool = False

    """When printing multiple copies, the end of the last label is cut."""
    label_end_cut: bool = False

    """High resolution printing"""
    high_res_print: bool = False
    
    """No buffer clearing when printing (inverted)
    The expansion buffer of the P-touch is not cleared with the “no buffer 
    clearing when printing” command. If this command is sent when the data 
    of the first label is printed (it is specified between the “initialize”
    command and the print data), printing is possible only if a print command 
    is sent with the second or later label. However, this is possible only when 
    printing extremely small labels.
    """
    clear_buf: bool = True

    margin: int = 0


    def apply(self, fun: Callable):
        available_paras = set(fun.__code__.co_varnames)
        para_dict = {k: v for k, v in asdict(self).items() if k in available_paras}
        return fun(**para_dict)

