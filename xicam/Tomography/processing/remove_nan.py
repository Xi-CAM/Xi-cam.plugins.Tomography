#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RemoveNan(ProcessingPlugin):
    """
    Replace NaN values in array with a given value
    """
    arr = Input(description="Auto Genrated", type=np.ndarray)
    val = Input(
        description="Values to be replaced with NaN", type=float, default=0.)
    ncore = Input(description="Numner of CPU cores", type=int, default=None)

    out = Output(description="Corrected array", type=np.ndarray)

    def evalulate(self):
        self.out.value = tomopy.remove_nan(
            self.arr.value, val=self.val.value, ncore=self.ncore.value)
