#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import numpy as np


class ArrayMax(ProcessingPlugin):
    """
    Maximum value of the array
    """
    arr = Input(description="Input array", type=np.ndarray)
    floor = Input(
        description="Floor value for comparison",
        type=int,
        default=0)
    out = Output(
        description="Alternative output array in which to place the result",
        type=np.ndarray)

    def evaluate(self):
        self.out.value = np.maximum(self.arr.value, self.out.value)
