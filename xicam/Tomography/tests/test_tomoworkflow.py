# from xicam.core.execution.workflow import Workflow
from xicam.plugins.Workflow import Workflow, DaskWorkflow
from xicam.Tomography.processing.read_APS2BM import read_APS2BM
from xicam.Tomography.processing.remove_outlier import RemoveOutlier
from xicam.Tomography.processing.array_max import ArrayMax
from xicam.Tomography.processing.minus_log import MinusLog
from xicam.Tomography.processing.remove_stripe_fw import RemoveStripeFw
from xicam.Tomography.processing.pad import Pad
from xicam.Tomography.processing.angles import Angles
from xicam.Tomography.processing.recon import Recon
from xicam.Tomography.processing.crop import Crop
from xicam.Tomography.processing.array_divide import ArrayDivide
from xicam.Tomography.processing.circ_mask import CircMask
from xicam.Tomography.processing.write_tiff_stack import WriteTiffStack


def test_tomoworkflow():
    read = read_APS2BM()
    read.path.value = '/home/rp/data/tomography/DogaTest.hdf'
    read.sino.value = (300, 301, 1)

    outliers = RemoveOutlier()
    read.arr.connect(outliers.arr)
    outliers.dif.value = 500
    outliers.size.value = 5

    maximum = ArrayMax()
    maximum.arr.connect(outliers.corrected)
    maximum.floor.value = 1e-16

    neglog = MinusLog()
    maximum.out.connect(neglog.arr)

    stripe = RemoveStripeFw()
    neglog.out.connect(stripe.tomo)
    stripe.level.value = 8
    stripe.wname.value = 'db5'
    stripe.sigma.value = 4
    stripe.pad.value = True

    padding = Pad()
    stripe.corrected.connect(padding.arr)
    padding.axis.value = 2
    padding.npad.value = 531
    padding.mode.value = 'edge'

    # angles = Angles()
    # angles.nang.value=0
    # angles.ang1.value=90
    # angles.ang2.value=180


    gridrec = Recon()
    padding.padded.connect(gridrec.tomo)
    read.angles.connect(gridrec.theta)
    gridrec.filter_name.value = 'butterworth'
    gridrec.algorithm.value = 'gridrec'
    gridrec.center.value = 0

    crop = Crop()

    divide = ArrayDivide()

    circularmask = CircMask()

    writetiff = WriteTiffStack()

    workflow = Workflow('Tomography')
    for process in [read,
                    outliers,
                    maximum,
                    neglog,
                    stripe,
                    padding,
                    # angles,
                    gridrec,
                    # crop,
                    # divide,
                    # circularmask,
                    # writetiff
                    ]:
        workflow.addProcess(process)

    dsk = DaskWorkflow()
    result = dsk.execute(workflow)
    print(result)
