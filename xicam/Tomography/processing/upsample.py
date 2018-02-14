#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class Upsample(ProcessingPlugin):
    """
    Upsample along specified axis of a 3D array
    """
    tomo = InOut(description="3D input array", type=np.ndarray)
    level = Input(
        description="Upsampling level in powers of two", type=int, default=1)
    axis = Input(
        description="Axis along which upsampling will be performed",
        type=int,
        default=2)

    def evaluate(self):
        self.tomo.value = tomopy.upsample(
            self.tomo.value, level=self.level.value, axis=self.axis.value)
