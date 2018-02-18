from xicam.plugins import ProcessingPlugin, Input, Output
import dxchange
import numpy as np


class read_APS2BM(ProcessingPlugin):
    """
    Remove high intensity bright spots from a N-dimensional array by chunking
    along the specified dimension, and performing (N-1)-dimensional median
    filtering along the other dimensions.
    """
    path = Input(description="Path to file", type=str)
    chunksize = Input(description="Number of sinograms to read simultaneously", type=int, default=1)
    sinoindex = Input(description="Index of (first) sinogram to read", type=int)

    tomo = Output(
        description=
        " Output array for result. If same as arr, process will be done in-place",
        type=np.ndarray)
    flats = Output(description="Array data for flat fields", type=np.ndarray)
    darks = Output(description="Array data for dark fields", type=np.ndarray)
    angles = Output(description="Tomogram angles", type=np.ndarray)

    def evaluate(self):
        self.tomo.value, self.flats.value, self.darks.value, self.angles.value = dxchange.read_aps_2bm(self.path.value,
                                                                                                       None,
                                                                                                       (
                                                                                                           self.sinoindex.value,
                                                                                                           int(
                                                                                                               self.sinoindex.value) + int(
                                                                                                               self.chunksize.value),
                                                                                                           1))
