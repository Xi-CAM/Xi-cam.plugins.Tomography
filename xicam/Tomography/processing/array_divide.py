#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import numpy as np


class ArrayDivide(ProcessingPlugin):
    """
    Divide array by a scalar
    """
    arr = Input(description="Input array", type=np.ndarray)
    div = Input(description="Divisor", type=scalar)

    out = Output(description="Array divided by the scalar", type=np.ndarray)

    def evalulate(self):
        self.out.value = np.divide(self.arr.value, self.div.value)
