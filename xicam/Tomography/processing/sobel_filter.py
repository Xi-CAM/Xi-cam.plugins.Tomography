#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class SobelFilter(ProcessingPlugin):
    """
    Apply Sobel filter to 3D array along specified axis
    """
    tomo = InOut(description="Input array", type=np.ndarray)
    axis = Input(
        description="Axis along which sobel filtering is performed", type=int)
    ncore = Input(description="Number of CPU cores", type=int, default=None)

    def evaluate(self):
        self.tomo.value = tomopy.sobel_filter(
            self.tomo.value, axis=self.axis.value, ncore=self.ncore.value)
