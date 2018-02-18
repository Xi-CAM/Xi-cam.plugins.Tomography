#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class Downsample(ProcessingPlugin):
    """
    Downsample along specified axis of a 3D array.
    """
    tomo = InOut(description="3D input array", type=np.ndarray)
    # recon = tomo
    level = Input(description="Downsampling level in powers of two", type=int, default=1)
    axis = Input(
        description="Axis along which downsampling will be performed",
        default=2,
        type=int)

    def evaluate(self):
        self.tomo.value = tomopy.downsample(
            self.tomo.value, level=int(self.level.value), axis=int(self.axis.value))
