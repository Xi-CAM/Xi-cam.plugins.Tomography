#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class Downsample(ProcessingPlugin):
    """
    Downsample along specified axis of a 3D array.
    """
    arr = Input(description="3D input array", type=np.ndarray)
    level = Input(description="Downsampling level in powers of two", type=int)
    axis = Input(
        description="Axis along which downsampling will be performed",
        type=int)

    downsample = Output(
        description="Downsampled 3D array in float32", type=np.ndarray)

    def evalulate(self):
        self.downsample.value = tomopy.downsample(
            self.arr.value, level=self.level.value, axis=self.axis.value)
