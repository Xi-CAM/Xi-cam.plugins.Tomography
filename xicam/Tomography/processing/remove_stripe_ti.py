#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class RemoveStripeTi(ProcessingPlugin):
    """
    Remove horizontal stripes from sinogram using Titarenko's approach :cite:`Miqueles:14`.
    """
    arr = Input(description="3D tomographic data", type=np.ndarray)
    nblock = Input(description="Number of blocks", type=int, default=0)
    alpha = Input(description="Damping factor", type=float, default=1.5)
    ncore = Input(description="Number of CPU cores", type=int, default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)

    corrected = Output(
        description="Corrected 3D tomographic data", type=np.ndarray)

    def evalulate(self):
        self.corrected.value = tomopy.remove_stripe_ti(
            self.arr.value,
            nblock=self.nblock.value,
            alpha=self.alpha.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value)
