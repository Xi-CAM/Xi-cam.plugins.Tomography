#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class FindCenterVo(ProcessingPlugin):
    """
    Find rotation axis location using Nghia Vo's method. :cite:`Vo:14`.
    """

    tomo = Input(description="3D tomographic data", type=np.ndarray)
    ind = Input(
        description="Index of the slice to be used for reconstruction",
        type=int,
        default=None)
    smin = Input(description="Coarse search radius", type=int, default=-50)
    smax = Input(description="Coarse search radius", type=int, default=50)
    srad = Input(description="Fine search radius", type=float, default=6)
    step = Input(description="Step of fine searching", type=float, default=0.5)
    ratio = Input(
        description=
        "he ratio between the FOV of the camera and the size of object. It's used to generate the mask",
        type=float,
        default=0.5)
    drop = Input(
        description="Drop lines around vertical center of the mask",
        type=int,
        default=20)

    center = Output(description="Rotation axis location", type=float)

    def evaluate(self):
        self.center.value = tomopy.find_center_vo(
            self.tomo.value,
            ind=self.ind.value,
            smin=self.smin.value,
            smax=self.smax.value,
            srad=self.srad.value,
            step=self.step.value,
            ratio=self.ratio.value,
            drop=self.drop.value)
