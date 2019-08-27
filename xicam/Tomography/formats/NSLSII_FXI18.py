from xicam.plugins.datahandlerplugin import DataHandlerPlugin, start_doc, descriptor_doc, event_doc, stop_doc, \
    embedded_local_event_doc

import os
import dxchange
import uuid
import re
import functools
from pathlib import Path
import h5py
import numpy as np


class NSLSII_FXI18(DataHandlerPlugin):
    """
    A data handler for NSLS-II's FXI18 beamline
    """
    name = 'NSLSII_FXI18'

    DEFAULT_EXTENTIONS = ['.hdf', '.h5']

    descriptor_keys = []

    def __init__(self, path):
        super(NSLSII_FXI18, self).__init__()
        self.path = path

    def __call__(self, arr='img_tomo', slc=None, **kwargs):
        h5 = h5py.File(self.path, 'r')
        if arr == 'sino':
            return np.squeeze(h5['img_tomo'][:][slc])
        else:
            return np.squeeze(h5[arr][slc])

    # TODO add a validator

    @classmethod
    def reduce_paths(cls, paths):
        return paths[0]

    @classmethod
    def getEventDocs(cls, path, descriptor_uid):
        with h5py.File(path, 'r') as h5:
            angles = np.deg2rad(h5['angle'])

        for proj_index in range(cls.num_projections(path)):
            yield embedded_local_event_doc(descriptor_uid, 'projection', cls, (path,),
                                           resource_kwargs=dict(arr='img_tomo', slc=proj_index),
                                           metadata={'angle': angles[proj_index]})

        for sino_index in range(cls.num_sinograms(path)):
            yield embedded_local_event_doc(descriptor_uid, 'sinogram', cls, (path,),
                                           resource_kwargs=dict(arr='sino', slc=sino_index))

        for flat_index in range(cls.num_flats(path)):
            yield embedded_local_event_doc(descriptor_uid, 'flat', cls, (path,),
                                           resource_kwargs=dict(arr='img_bkg', slc=flat_index))

        for dark_index in range(cls.num_darks(path)):
            yield embedded_local_event_doc(descriptor_uid, 'dark', cls, (path,),
                                           resource_kwargs=dict(arr='img_dark', slc=dark_index))

    @classmethod
    def num_projections(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['img_tomo'].shape[0]

    @classmethod
    def num_sinograms(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['img_tomo'].shape[1]

    @classmethod
    def num_flats(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['img_bkg'].shape[0]

    @classmethod
    def num_darks(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['img_dark'].shape[0]

    @classmethod
    def getStartDoc(cls, path, start_uid):
        return start_doc(start_uid=start_uid, metadata={'path': path})

    @classmethod
    def getDescriptorDocs(cls, paths, start_uid, descriptor_uid):
        yield descriptor_doc(start_uid, descriptor_uid)

    @classmethod
    def title(cls, path):
        return Path(path).resolve().stem
