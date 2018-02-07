#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class CircMask(ProcessingPlugin):
    """
    Apply circular mask to a 3D array.
    """

    arr = Input(description="Arbitrary 3D array", type=np.ndarray)
    axis = Input(
        description="Axis along which mask will be performed", type=int)
    ratio = Input(
        description=
        "Ratio of the mask's diameter in pixels to the smallest edge size along given axis. ",
        type=int)
    val = Input(description="Value for the masked region", type=int)
    circ_mask = Output(description="Masked array", type=np.ndarray)

    def evalulate(self):
        self.circ_mask.value = tomopy.circ_mask(
            self.arr.value,
            axis=self.axis.value,
            ratio=self.ratio.value,
            val=self.val.value)
