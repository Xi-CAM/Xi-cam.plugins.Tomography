#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RemoveOutlier(ProcessingPlugin):
    """
    Remove high intensity bright spots from a N-dimensional array by chunking
    along the specified dimension, and performing (N-1)-dimensional median
    filtering along the other dimensions.
    """
    arr = Input(description="Input array", type=np.ndarray)
    dif = Input(
        description=
        "Expected difference value between outlier value and the median value of the array",
        type=float)
    size = Input(description="Size of the median filter", type=int, default=3)
    axis = Input(description="Axis along which to chunk", type=int, default=0)
    ncore = Input(description="Number of CPU cores", type=int, default=None)
    out = Input(
        description=
        " Output array for result. If same as arr, process will be done in-place",
        type=np.ndarray,
        default=None)

    corrected = Output(description="Corrected array", type=np.ndarray)

    def evaluate(self):
        self.corrected.value = tomopy.remove_outlier(
            self.arr.value,
            self.dif.value,
            size=self.size.value,
            axis=self.axis.value,
            ncore=self.ncore.value,
            out=self.out.value)
