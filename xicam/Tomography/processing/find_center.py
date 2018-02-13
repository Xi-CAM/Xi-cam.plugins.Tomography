#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class FindCenter(ProcessingPlugin):
    """
    Find rotation axis location.

    The function exploits systematic artifacts in reconstructed images
    due to shifts in the rotation center. It uses image entropy
    as the error metric and ''Nelder-Mead'' routine (of the scipy
    optimization module) as the optimizer :cite:`Donath:06`.
    """

    tomo = Input(description="3D tomographic data", type=np.ndarray)
    theta = Input(description="Projection angles in radian", type=np.ndarray)
    ind = Input(
        description="Index of the slice to be used for reconstruction",
        default=None,
        type=int)
    init = Input(
        description="Initial guess for the center", default=None, type=float)
    tol = Input(
        description="Desired sub-pixel accuracy", default=0.5, type=float)
    mask = Input(
        description="If True, apply a circular mask", default=True, type=bool)
    ratio = Input(
        description=
        "The ratio of the radius of the circular mask to the edge of the reconstructed image",
        default=1.,
        type=float)
    sinogram_order = Input(
        type=bool,
        default=False,
        description=
        "Determins whether data is a stack of sinograms (True, y-axis first axis) or a stack of radiographs (False, theta first axis)."
    )

    center = Output(description="Rotation axis location", type=float)

    def evaluate(self):
        self.center.value = tomopy.find_center(
            self.tomo.value,
            self.theta.value,
            ind=self.ind.value,
            init=self.init.value,
            tol=self.tol.value,
            mask=self.mask.value,
            ratio=self.ratio.value,
            sinogram_order=self.sinogram_order.value)
