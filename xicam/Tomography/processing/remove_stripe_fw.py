#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np
from tomopy.prep import stripe


class RemoveStripeFw(ProcessingPlugin):
    """
    Remove horizontal stripes from sinogram using the Fourier-Wavelet (FW) based method :cite:`Munch:09`.
    """
    tomo = InOut(description="3D tomographic data", type=np.ndarray)
    level = Input(
        description="Number of discrete wavelet transform levels",
        type=int,
        default=None)
    wname = Input(description="haar, db5, sym5 etc", type=str, default='db5')
    sigma = Input(
        description="Damping parameter in Fourier space",
        type=float,
        default=2)
    pad = Input(
        description=
        "If True, extend the size of the sinogram by padding with zeros",
        type=bool,
        default=True)
    # ncore = Input(description="Number of CPU cores", type=int, default=None)
    # nchunk = Input(
    #     description="Chunk size for each core", type=int, default=None)


    def evaluate(self):
        if self.level.value is None:
            size = np.max(self.tomo.value.shape)
            self.level.value = int(np.ceil(np.log2(size)))

        stripe._remove_stripe_fw(
            self.tomo.value,
            level=self.level.value,
            wname=self.wname.value,
            sigma=self.sigma.value,
            pad=self.pad.value,
            # ncore=self.ncore.value,
            # nchunk=self.nchunk.value
        )
