#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class Pad(ProcessingPlugin):

    arr = Input(description="Input array", type=np.ndarray)
    axis = Input(
        description="Axis along which padding will be performed", type=int)
    npad = Input(
        description="New dimension after padding", type=int, default=None)
    mode = Input(description="constant or edge", type=str, default='constant')
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)

    padded = Output(description="Padded 3D array", type=np.ndarray)

    def evalulate(self):
        self.padded.value = tomopy.pad(
            self.arr.value,
            self.axis.value,
            npad=self.npad.value,
            mode=self.mode.value,
            ncore=self.ncore.value)
