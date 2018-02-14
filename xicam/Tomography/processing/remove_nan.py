#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class RemoveNan(ProcessingPlugin):
    """
    Replace NaN values in array with a given value
    """
    tomo = InOut(description="Auto Genrated", type=np.ndarray)
    val = Input(
        description="Values to be replaced with NaN", type=float, default=0.)
    ncore = Input(description="Numner of CPU cores", type=int, default=None)


    def evaluate(self):
        self.tomo.value = tomopy.remove_nan(
            self.tomo.value, val=self.val.value, ncore=self.ncore.value)
