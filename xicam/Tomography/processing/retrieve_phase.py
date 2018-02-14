#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
from tomopy.prep.phase import _retrieve_phase, _calc_pad, _reciprocal_grid, _paganin_filter_factor
import numpy as np


class RetrievePhase(ProcessingPlugin):
    """
    Perform single-step phase retrieval from phase-contrast measurements :cite:`Paganin:02`
    """
    tomo = InOut(description="3D tomographic data", type=np.ndarray)
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

    def evaluate(self):
        # New dimensions and pad value after padding.
        py, pz, val = _calc_pad(self.tomo.value, self.pixel_size.value, self.dist.value, self.energy.value,
                                self.pad.value)

        # Compute the reciprocal grid.
        dx, dy, dz = self.tomo.value.shape
        w2 = _reciprocal_grid(self.pixel_size.value, dy + 2 * py, dz + 2 * pz)

        # Filter in Fourier space.
        phase_filter = np.fft.fftshift(
            _paganin_filter_factor(self.energy.value, self.dist.value, self.alpha.value, w2))

        prj = np.full((dy + 2 * py, dz + 2 * pz), val, dtype='float32')
        _retrieve_phase(self.tomo.value,
                        phase_filter,
                        py,
                        pz,
                        prj,
                        self.pad.value)
