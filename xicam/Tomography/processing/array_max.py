#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import numpy as np


class ArrayMax(ProcessingPlugin):
    """
    Maximum value of the array
    """
    arr = Input(description="Input array", type=np.ndarray)
    axis = Input(
        description="Axis along which search is performed",
        type=int,
        default=None)
    out = description(
        description="Alternative output array in which to place the result",
        type=np.ndarray,
        default=None)

    maxval = Output(description="Maximum value", type=scalar)

    def evalulate(self):
        self.maxval.value = np.max(
            self.arr.value, axis=self.axis.value, out=self.out.value)
