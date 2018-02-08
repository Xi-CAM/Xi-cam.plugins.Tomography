#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RetrievePhase(ProcessingPlugin):
    """
    Perform single-step phase retrieval from phase-contrast measurements :cite:`Paganin:02`
    """
    arr = Input(description="3D tomographic data", type=List)
    pixel_size = Input(
        description="Detector pixel size in cm", type=float, default=0.0001)
    dist = Input(
        description="Propagation distance of the wavefront in cm",
        type=float,
        default=50)
    energy = Input(
        description="Energy of incident wave in keV", type=float, default=20)
    alpha = Input(
        description="Regularization parameter", type=float, default=0.001)
    pad = Input(description="Self evident", type=bool, default=True)
    ncore = Input(description="Number of CPU cores", type=int, default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)

    phase = Output(
        description="Approximated 3D tomographic phase data", type=np.ndarray)

    def evalulate(self):
        self.phase.value = tomopy.retrieve_phase(
            self.arr.value,
            pixel_size=self.pixel_size.value,
            dist=self.dist.value,
            energy=self.energy.value,
            alpha=self.alpha.value,
            pad=self.pad.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value)
