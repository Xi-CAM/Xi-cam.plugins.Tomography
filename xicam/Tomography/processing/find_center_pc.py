#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class FindCenterPc(ProcessingPlugin):
    """
    Find rotation axis location.

    The function exploits systematic artifacts in reconstructed images
    due to shifts in the rotation center. It uses image entropy
    as the error metric and ''Nelder-Mead'' routine (of the scipy
    optimization module) as the optimizer :cite:`Donath:06`.
    """

    proj1 = Input(description="2D projection data", type=np.ndarray)
    proj2 = Input(description="2D projection data", type=np.ndarray)
    tol = Input(description="Subpixel accuracy", type=float, default = 0.5)

    center = Output(description="Rotation axis location", type=float)

    def evaluate(self):
        self.center.value = tomopy.find_center_pc(
            self.proj1.value, self.proj2.value, tol=self.tol.value)
