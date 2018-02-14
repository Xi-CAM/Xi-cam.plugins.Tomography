#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class MinusLog(ProcessingPlugin):
    """
    Computation of the minus log of a given array
    """

    tomo = InOut(description="3D stack of projections", type=np.ndarray)
    ncore = Input(
        description="Number of cores that will be assigned to jobs.",
        type=int,
        default=None)
    out = Input(
        description=
        "Output array for result. If same as arr, process will be done in-place.",
        type=np.ndarray,
        default=None)

    def evaluate(self):
        self.tomo.value = tomopy.minus_log(
            self.tomo.value, ncore=self.ncore.value, out=self.out.value)
