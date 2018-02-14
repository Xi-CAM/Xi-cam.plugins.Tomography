#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class Recon(ProcessingPlugin):
    """
    Reconstruct object from projection data.
    """
    tomo = Input(description="Input array", type=np.ndarray)
    angles = Input(description="Projection angles in radians", type=np.ndarray)
    center = Input(
        description="Location of rotation axis", type=np.ndarray, default=None)

    sinogram_order = Input(
        description="Determins whether data is a stack of sinograms",
        type=bool,
        default=False)

    algorithm = Input(
        description="[art, bart, fbp, gridrec, etc.]", type=str, default=None)
    init_recon = Input(
        description="Initial guess of the reconstruction",
        type=np.ndarray,
        default=None)
    ncore = Input(description="Number of CPU cores", type=int, default=None)
    nchunk = Input(
        description="Chunk size for each core", type=int, default=None)

    num_gridx = Input(
        description="Number of pixels along X in Reconstructed data",
        type=int,
        default=None)
    num_gridy = Input(
        description="Number of pixels along y in Reconstructed data",
        type=int,
        default=None)
    filter_name = Input(
        description="Name of the filter for analytic reconstruction",
        type=str,
        default='none')
    filter_par = Input(
        description="Filter parameters", type=np.ndarray, default=None)

    num_iter = Input(
        description="Number of algorithm iterations", type=int, default=None)

    num_block = Input(
        description="Number of data blocks for intermediate updating",
        type=int,
        default=None)

    ind_block = Input(
        description="Order of projections to be used",
        type=np.ndarray,
        default=None)

    reg_par = Input(
        description="Regularization parameter for smoothing",
        type=float,
        default=None)

    recon = Output(
        description="Reconstructed 3D array", type=np.ndarray)

    def evaluate(self):
        if self.algorithm.value == 'gridrec':
            kwargs = {
                'num_gridx': self.num_gridx.value,
                'num_gridy': self.num_gridy.value,
                'filter_name': self.filter_name.value,
                'filter_par': self.filter_par.value,
            }
        else:  # TODO: Not sure which are applicable to other algorithms yet
            kwargs = {
                'num_iter': self.num_iter.value,
                'num_block': self.num_block.value,
                'ind_block': self.ind_block.value,
                'reg_par': self.reg_par.value
            }

        # remove unset kwargs
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        self.recon.value = tomopy.recon(
            self.tomo.value,
            self.angles.value,
            center=self.center.value,
            sinogram_order=self.sinogram_order.value,
            algorithm=self.algorithm.value,
            init_recon=self.init_recon.value,
            ncore=self.ncore.value,
            nchunk=self.nchunk.value,
            **kwargs)
