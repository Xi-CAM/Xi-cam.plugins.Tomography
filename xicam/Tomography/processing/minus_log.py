#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class MinusLog(ProcessingPlugin):
    """
    Computation of the minus log of a given array
    """

    arr = Input(description="3D stack of projections", type=np.ndarray)
    ncore = Input(
        description="Number of cores that will be assigned to jobs.",
        type=int,
        default=None)
    out = Input(
        description=
        "Output array for result. If same as arr, process will be done in-place.",
        type=np.ndarray,
        default=None)

    minuslog = Output(
        description="Minus-log of the input data", type=np.ndarray)

    def evalulate(self):
        self.minuslog.value = tomopy.minus_log(
            self.arr.value, ncore=self.ncore.value, out=self.out.value)
