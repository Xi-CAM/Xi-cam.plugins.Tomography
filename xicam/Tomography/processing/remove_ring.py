#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RemoveRing(ProcessingPlugin):
    """
    Remove ring artifacts from images in the reconstructed domain.
    Descriptions of parameters need to be more clear for sure.
    """
    arr = Input(description="Array of reconstruction data", type=np.ndarray)
    center_x = Input(
        description="abscissa location of center of rotation",
        type=float,
        default=None)
    center_y = Input(
        description="ordinate location of center of rotation",
        type=float,
        default=None)
    thresh = Input(
        description="maximum value of an offset due to a ring artifact",
        type=float,
        default=300.)
    thresh_max = Input(
        description="max value for portion of image to filter",
        type=float,
        default=300.)
    thresh_min = Input(
        description="min value for portion of image to filer",
        type=float,
        default=-100.)
    theta_min = Input(
        description=
        "minimum angle in degrees (int) to be considered ring artifact",
        type=int,
        default=30)
    rwidth = Input(
        description="Maximum width of the rings to be filtered in pixels",
        type=int,
        default=30)
    int_mode = Input(description="WARP or REFLECT", type=str, default='WARP')
    ncore = Input(description="Number or CPU cores", type=int, default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)
    out = Input(
        description=
        "Output array for result. If same as arr, process will be done in-place",
        type=np.ndarray,
        default=None)

    corrected = Output(
        description="Corrected reconstruction data", type=np.ndarray)

    def evalulate(self):
        self.corrected.value = tomopy.remove_ring(
            self.arr.value,
            center_x=self.center_x.value,
            center_y=self.center_y.value,
            thresh=self.thresh.value,
            thresh_max=self.thresh_max.value,
            thresh_min=self.thresh_min.value,
            theta_min=self.theta_min.value,
            rwidth=self.rwidth.value,
            int_mode=self.int_mode.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value,
            out=self.out.value)
