#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np


class GaussianFilter(ProcessingPlugin):
    """
    Apply Gaussian filter to 3D array along specified axis.
    TODO: Make simga to an optional sequence
    """
    tomo = InOut(description="Input array", type=np.ndarray)
    sigma = Input(
        description="Standard deviation for Gaussian kernel",
        type=float,
        default=3)
    order = Input(
        description="Order of the filter along each axis",
        type=tuple,
        default=0)
    axis = Input(
        description="Axis along which median filtering is performed",
        type=int,
        default=0)
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)

    def evaluate(self):
        self.tomo.value = tomopy.gaussian_filter(
            self.tomo.value,
            sigma=self.sigma.value,
            order=self.order.value,
            axis=self.axis.value,
            ncore=self.ncore.value)
