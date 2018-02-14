#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import numpy as np


class ArrayDivide(ProcessingPlugin):
    """
    Divide array by a scalar
    """
    tomo = InOut(description="Input array", type=np.ndarray)
    div = Input(description="Divisor", type=float)

    def evaluate(self):
        self.tomo.value = np.divide(self.tomo.value, self.div.value)
