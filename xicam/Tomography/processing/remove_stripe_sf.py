#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RemoveStripeSf(ProcessingPlugin):
    """
    Normalize raw projection data using a smoothing filter approach
    """
    arr = Input(description="3D tomographic data", type=np.ndarray)
    size = Input(
        description="Size of the smoothing filter", type=int, default=5)
    ncore = Input(description="Number of CPU cores", type=int, default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)

    corrected = Output(
        description="Corrected 3D tomographic data", type=np.ndarray)

    def evaluate(self):
        self.corrected.value = tomopy.remove_stripe_sf(
            self.arr.value,
            size=self.size.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value)
