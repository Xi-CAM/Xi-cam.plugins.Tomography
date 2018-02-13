#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import dxchange
import numpy as np


class WriteNpy(ProcessingPlugin):
    """
    Write data to a binary file in NumPy ``.npy`` format
    """
    data = Input(description="Data to be written", type=np.ndarray)
    fname = Input(description="filename", type=str, default='/tmp/data.npy')
    overwrite = Input(description="True or False", type=bool, default=False)
    dtype = Input(description="Self-descriptive", default=None)

    def evaluate(self):
        dxchange.write_npy(
            self.data.value,
            fname=self.fname.value,
            dtype=self.dtype.value,
            overwrite=self.overwrite.value)
