#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class MedianFilter(ProcessingPlugin):
    """
    Apply median filter to 3D array along specified axis.
    """
    tomo = InOut(description="Input array", type=np.ndarray)
    size = Input(description="The size of the filter", type=int, default=3)
    axis = Input(
        description="Axis along which median filtering is performed",
        type=int,
        default=0)
    ncore = Input(
        description="Number of cores that will be assigned to jobs.",
        type=int,
        default=None)

    def evaluate(self):
        self.tomo.value = tomopy.median_filter(
            self.tomo.value,
            size=self.size.value,
            axis=self.axis.value,
            ncore=self.ncore.value)
