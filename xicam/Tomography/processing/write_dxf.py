#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input
import dxchange
import numpy as np


class WriteDxf(ProcessingPlugin):
    """
    Write data to a data exchange hdf5 file
    """
    recon = Input(description="Data to be saved", type=np.ndarray)
    fname = Input(
        description="File name to which the data is saved",
        type=str,
        default="/tmp/data.h5")
    axes = Input(
        description="Attribute labels for the data array axes",
        type=str,
        default="theta:y:x")
    dtype = Input(description="data-type", type=bool, default=None)
    overwrite = Input(
        description="if True, overwrites the existing file",
        type=bool,
        default=False)

    def evaluate(self):
        dxchange.write_dxf(
            self.recon.value,
            fname=self.fname.value,
            axes=self.axes.value,
            dtype=self.dtype.value,
            overwrite=self.overwrite.value)
