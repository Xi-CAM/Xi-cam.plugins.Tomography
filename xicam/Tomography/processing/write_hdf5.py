#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input
import dxchange
import numpy as np


class WriteHdf5(ProcessingPlugin):
    """
    Write data to hdf5 file in a specific group
    """
    data = Input(description="Array data to be saved", type=np.ndarray)
    fname = Input(
        description="File name to which the data is saved",
        type=str,
        default='/tmp/data.h5')
    gname = Input(
        description="Path to the group inside hdf5 file",
        type=str,
        default='exchange')
    dname = Input(
        description="Name for dataset inside hdf5 file",
        type=str,
        default='data')
    dtype = Input(description="data-type", default=None)
    overwrite = Input(
        description="if True, overwrites the existing file",
        type=bool,
        default=False)
    appendaxis = Input(
        description="Axis where data is to be appended to",
        type=int,
        default=None)
    maxsize = Input(
        description=
        "Maximum size that the dataset can be resized to along the given axis",
        type=int,
        default=None)

    def evaluate(self):
        dxchange.write_hdf5(
            self.data.value,
            fname=self.fname.value,
            gname=self.gname.value,
            dname=self.dname.value,
            dtype=self.dtype.value,
            overwrite=self.overwrite.value,
            appendaxis=self.appendaxis.value,
            maxsize=self.maxsize.value)
