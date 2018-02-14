#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class NormalizeRoi(ProcessingPlugin):
    """
    Normalize raw projection data using an average of a selected window
    on projection images.
    """
    tomo = InOut(description="3D tomographic data", type=np.ndarray)
    roi = Input(
        description=
        "[top-left, top-right, bottom-left, bottom-right] pixel coordinates",
        type=list,
        default=[0, 0, 10, 10])
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)

    def evaluate(self):
        self.tomo.value = tomopy.normalize_roi(
            self.arr.value, roi=self.roi.value, ncore=self.ncore.value)
