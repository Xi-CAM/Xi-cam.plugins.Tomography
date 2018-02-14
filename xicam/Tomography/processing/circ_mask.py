#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class CircMask(ProcessingPlugin):
    """
    Apply circular mask to a 3D array.
    """

    recon = InOut(description="Arbitrary 3D array", type=np.ndarray)
    axis = Input(
        description="Axis along which mask will be performed", type=int)
    ratio = Input(
        description=
        "Ratio of the mask's diameter in pixels to the smallest edge size along given axis. ",
        default=1.0,
        type=int)
    val = Input(
        description="Value for the masked region", default=0., type=int)

    def evaluate(self):
        self.recon.value = tomopy.circ_mask(
            self.recon.value,
            self.axis.value,
            ratio=self.ratio.value,
            val=self.val.value)
