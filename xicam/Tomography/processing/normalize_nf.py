#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class NormalizeNf(ProcessingPlugin):
    """
    Normalize raw 3D projection data with flats taken more than once during
    tomography. Normalization for each projection is done with the mean of the
    nearest set of flat fields (nearest flat fields).
    """

    tomo = Input(description="3D tomographic data", type=np.ndarray)
    flats = Input(description="3D flat field data", type=np.ndarray)
    darks = Input(description="3D dark field data", type=np.ndarray)
    flat_loc = Input(
        description="Indices of flat field data within tomography", type=list)
    cutoff = Input(description="Cut-off value", type=float, default=None)
    ncore = Input(
        description="Number of cores that will be assigned to jobs",
        type=int,
        default=None)
    out = Input(
        description=
        "Output array for result. If same as arr, process will be done in-place.",
        type=np.ndarray,
        default=None)

    normalized = Output(
        description="Normalized 3D tomographic data", type=np.ndarray)

    def evaluate(self):
        self.normalized.value = tomopy.normalize_nf(
            self.tomo.value,
            self.flats.value,
            self.darks.value,
            self.flat_loc.value,
            cutoff=self.cutoff.value,
            ncore=self.ncore.value,
            out=self.out.value)
