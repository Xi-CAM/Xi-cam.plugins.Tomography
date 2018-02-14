#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class RemoveOutlier(ProcessingPlugin):
    """
    Remove high intensity bright spots from a N-dimensional array by chunking
    along the specified dimension, and performing (N-1)-dimensional median
    filtering along the other dimensions.
    """
    tomo = InOut(description="Input array", type=np.ndarray)
    dif = Input(
        description=
        "Expected difference value between outlier value and the median value of the array",
        type=float)
    size = Input(description="Size of the median filter", type=int, default=3)
    axis = Input(description="Axis along which to chunk", type=int, default=0)
    ncore = Input(description="Number of CPU cores", type=int, default=None)


    def evaluate(self):
        tomopy.remove_outlier(
            self.tomo.value,
            self.dif.value,
            size=self.size.value,
            axis=self.axis.value,
            ncore=self.ncore.value,
            out=self.tomo.value)
