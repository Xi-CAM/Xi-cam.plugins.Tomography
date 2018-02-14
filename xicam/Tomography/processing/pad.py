#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class Pad(ProcessingPlugin):
    tomo = InOut(description="Input array", type=np.ndarray)
    axis = Input(
        description="Axis along which padding will be performed", type=int)
    npad = Input(
        description="New dimension after padding", type=int, default=None)
    mode = Input(description="constant or edge", type=str, default='constant')
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)

    def evaluate(self):
        self.tomo.value = tomopy.pad(
            self.tomo.value,
            self.axis.value,
            npad=self.npad.value,
            mode=self.mode.value,
            ncore=self.ncore.value)
