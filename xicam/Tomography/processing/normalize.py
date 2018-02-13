#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class Normalize(ProcessingPlugin):
    """
    Normalize raw 3D projection data with flats and darks
    """

    arr = Input(description="3D tomographic data", type=np.ndarray)
    flats = Input(description="3D flat field data", type=np.ndarray)
    darks = Input(description="3D dark field data", type=np.ndarray)
    
    normalized = Output(
        description="Normalized 3D tomographic data", type=np.ndarray)

    def evaluate(self):
        self.normalized.value = tomopy.normalize(
            self.arr.value,
            self.flats.value,
            self.darks.value)