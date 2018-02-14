#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class NormalizeBg(ProcessingPlugin):
    """
    Normalize 3D tomgraphy data based on background intensity.

    Weight sinogram such that the left and right image boundaries
    (i.e., typically the air region around the object) are set to one
    and all intermediate values are scaled linearly.
    """

    tomo = InOut(description="3D tomographic data", type=np.ndarray)
    air = Input(
        description=
        "Number of pixels at each boundary to calculate the scaling factor",
        type=int,
        default=1)
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)

    def evaluate(self):
        self.tomo.value = tomopy.normalize_bg(
            self.tomo.value,
            air=self.air.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value)
