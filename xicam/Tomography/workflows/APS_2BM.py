from xicam.core.execution.workflow import Workflow
from xicam.core.execution.daskexecutor import DaskExecutor
# from xicam.plugins.Workflow import Workflow, DaskWorkflow
from xicam.Tomography.processing.read_APS2BM import read_APS2BM
from xicam.Tomography.processing.normalize import Normalize
from xicam.Tomography.processing.remove_outlier import RemoveOutlier
from xicam.Tomography.processing.array_max import ArrayMax
from xicam.Tomography.processing.minus_log import MinusLog
from xicam.Tomography.processing.retrieve_phase import RetrievePhase
from xicam.Tomography.processing.remove_stripe_fw import RemoveStripeFw
from xicam.Tomography.processing.pad import Pad
from xicam.Tomography.processing.angles import Angles
from xicam.Tomography.processing.recon import Recon
from xicam.Tomography.processing.crop import Crop
from xicam.Tomography.processing.array_divide import ArrayDivide
from xicam.Tomography.processing.circ_mask import CircMask
from xicam.Tomography.processing.write_tiff_stack import WriteTiffStack
import tomopy
import numpy as np


class Workflow(Workflow):
    def __init__(self):
        super(Workflow, self).__init__('APS-2BM')
        read = read_APS2BM()
        read.path.value = '/home/rp/data/tomography/DogaTest.hdf'
        read.sino.value = (1050, 1051)

        norm = Normalize()
        # read.tomo.connect(norm.tomo)
        # read.flats.connect(norm.flats)
        # read.dark.connect(norm.darks)

        outliers = RemoveOutlier()
        # norm.normalized.connect(outliers.arr)
        outliers.dif.value = 500
        outliers.size.value = 5

        # maximum = ArrayMax()
        # outliers.corrected.connect(maximum.arr)
        # maximum.floor.value = 1e-16

        # neglog = MinusLog()
        # maximum.out.connect(neglog.arr)

        # phase = RetrievePhase()
        # maximum.out.connect(phase.arr)
        # phase.pixel_size.value=6.5e-5
        # phase.dist.value=3
        # phase.energy.value=27

        stripe = RemoveStripeFw()
        # outliers.corrected.connect(stripe.tomo)
        stripe.level.value = 8
        stripe.wname.value = 'db5'
        stripe.sigma.value = 4
        stripe.pad.value = True

        padding = Pad()
        # stripe.corrected.connect(padding.arr)
        padding.axis.value = 2
        padding.npad.value = 448
        padding.mode.value = 'edge'

        # angles = Angles()
        # angles.nang.value=0
        # angles.ang1.value=90
        # angles.ang2.value=180


        gridrec = Recon()
        # padding.padded.connect(gridrec.tomo)
        # read.angles.connect(gridrec.theta)
        gridrec.filter_name.value = 'butterworth'
        gridrec.algorithm.value = 'gridrec'
        gridrec.center.value = np.array([1295 + 448])  # 1295
        gridrec.filter_par.value = np.array([0.2, 2])
        # gridrec.sinogram_order.value = True

        crop = Crop()
        # gridrec.reconstructed.connect(crop.arr)
        crop.p11.value = 448
        crop.p22.value = 448
        crop.p12.value = 448
        crop.p21.value = 448
        crop.axis.value = 0

        divide = ArrayDivide()

        circularmask = CircMask()
        # crop.croppedarr.connect(circularmask.arr)
        circularmask.val.value = 0
        circularmask.axis.value = 0
        circularmask.ratio.value = 1

        writetiff = WriteTiffStack()

        for process in [read,
                        norm,
                        outliers,
                        # maximum,
                        # neglog,
                        # phase,
                        stripe,
                        padding,
                        # angles,
                        gridrec,
                        crop,
                        # divide,
                        circularmask,
                        # writetiff
                        ]:
            self.addProcess(process)

        self.autoConnectAll()
