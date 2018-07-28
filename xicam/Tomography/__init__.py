import numpy as np
from functools import partial
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core.data import load_header, NonDBHeader
from xicam.core.execution.workflow import Workflow
from xicam.core.execution.daskexecutor import DaskExecutor
from xicam.core.execution.localexecutor import LocalExecutor
from xicam.core import msg
import distributed
import dask.threaded


from xicam.plugins import GUIPlugin, GUILayout, manager as pluginmanager
from xicam.plugins.GUIPlugin import PanelState

from xicam.gui.threads import QThreadFuture, QThreadFutureIterator, Invoker, InvokeEvent
from xicam.gui.widgets.tabview import TabView
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from .widgets.RAWViewer import RAWViewer
from .widgets.tomotoolbar import TomoToolbar
from .widgets.sliceviewer import SliceViewer
from .widgets.volumeviewer import VolumeViewer

from .workflows.APS_2BM import TomoWorkflow


class TomographyPlugin(GUIPlugin):
    name = 'Tomography'
    sigLog = Signal(int, str, str, np.ndarray)
    slice = 0
    multislice = 1
    preview3d = 2
    fullrecon = 3

    def __init__(self):
        self.workflow = TomoWorkflow()

        self.headermodel = QStandardItemModel()
        # self.alignmenttabview = TabView(self.headermodel)
        self.rawtabview = TabView(self.headermodel, widgetcls=RAWViewer, field='primary')
        self.recontabs = QTabWidget()

        self.workfloweditor = WorkflowEditor(self.workflow)
        self.workfloweditor.setHidden(True)

        self.tomotoolbar = TomoToolbar()
        self.tomotoolbar.sigSliceReconstruction.connect(self.sliceReconstruct)
        self.tomotoolbar.sigFullReconstruction.connect(self.fullReconstruction)

        self.stages = {
            'Alignment': GUILayout(QLabel('Alignment'), right=self.workfloweditor, top=self.tomotoolbar),
            'Preprocess': GUILayout(self.rawtabview, right=self.workfloweditor, top=self.tomotoolbar),
            'Reconstruct': GUILayout(self.recontabs, top=self.tomotoolbar, right=self.workfloweditor),
        }
        super(TomographyPlugin, self).__init__()

    def appendHeader(self, header: NonDBHeader, **kwargs):
        item = QStandardItem(header.startdoc.get('sample_name', '????'))
        item.header = header
        self.headermodel.appendRow(item)
        self.headermodel.dataChanged.emit(QModelIndex(), QModelIndex())

    def sliceReconstruct(self):
        currentitem = self.headermodel.item(self.rawtabview.currentIndex())
        if not currentitem: msg.showMessage('Error: You must open files before reconstructing.')
        try:
            msg.showBusy()
            msg.showMessage('Running slice reconstruction...', level=msg.INFO)
            path = self.headermodel.item(self.rawtabview.currentIndex()).header.startdoc['path']
            self.workflow.execute(None, path=path, threadkey='slicereconstruct',
                                  callback_slot=partial(self.showReconstruction, mode=self.slice),
                                  except_slot=self.exceptionCallback)
        except Exception as ex:
            msg.logError(ex)
            msg.showReady()
            msg.clearMessage()

    def fullReconstruction(self):
        volumeviewer = VolumeViewer()
        self.recontabs.addTab(volumeviewer, '????')

        currentitem = self.headermodel.item(self.rawtabview.currentIndex())
        if not currentitem: msg.showMessage('Error: You must open files before reconstructing.')
        try:
            msg.showBusy()
            msg.showMessage('Running slice reconstruction...', level=msg.INFO)
            currentheader = self.headermodel.item(self.rawtabview.currentIndex()).header
            readprocess = self.workflow.processes[0]  # hopefully! TODO: require a readprocess first
            readprocess.path.value = currentheader.startdoc['path']
            numofsinograms = currentheader.meta_array('primary').shape[1]
            readprocess.chunksize.value = 10

            executor = DaskExecutor()
            client = distributed.Client("tcp://localhost:8786", n_workers=3, threads_per_worker=1)
            #client = distributed.Client(n_workers=3, threads_per_worker=1)

            from distributed import Queue

            readprocess.sinoindex.value = list(range(0, int(numofsinograms), int(readprocess.chunksize.value)))

            #print(readprocess.sinoindex.value)

            self.sliceviewer = SliceViewer()
            self.recontabs.addTab(self.sliceviewer, '????')
            qApp.processEvents()
            #executor.execute(self.workflow, callback=self.callback, client=client)

            def chunkiterator(workflow):
                def callback(data):
                    print("CALLING DATA")
                    yield data

                executor.execute(workflow, callback=self.callback, client=client)

            _reconthread = QThreadFuture(chunkiterator)

            #_reconthread = QThreadFutureIterator(chunkiterator, self.workflow,
            #                                     callback_slot=partial(self.showReconstruction, mode=self.fullrecon),
            #                                     except_slot=self.exceptionCallback)
            _reconthread.start()


            """            
            def chunkiterator(workflow):
                for i in range(0, int(numofsinograms), int(readprocess.chunksize.value)):
                    print("processing:", i)
                    readprocess.sinoindex.value = i
                    yield executor.execute(workflow, client)
                    #yield workflow.execute(None)

            _reconthread = QThreadFutureIterator(chunkiterator, self.workflow,
                                                 callback_slot=partial(self.showReconstruction, mode=self.fullrecon),
                                                 except_slot=self.exceptionCallback)
            _reconthread.start()
            """

        except Exception as ex:
            msg.logError(ex)
            msg.showReady()
            msg.clearMessage()

    _invoker = Invoker()

    def fn(self, result):
        self.sliceviewer.setImage(result)

    def callback(self, result):

        def fn(_invoker, slice_viewer, my_result):
            def my_fn():
                slice_viewer.setImage(my_result)
            QCoreApplication.postEvent(_invoker, InvokeEvent(my_fn))

        fn(self._invoker, self.sliceviewer, result)

    def exceptionCallback(self, ex):
        msg.notifyMessage("Reconstruction failed;\n see log for error")
        msg.showMessage("Reconstruction failed; see log for error")
        msg.logError(ex)
        msg.showReady()

    def showReconstruction(self, result, mode):
        print('result:', result)

        if mode == self.slice:
            sliceviewer = SliceViewer()
            sliceviewer.setImage(list(result.values())[0].value.squeeze())
            self.recontabs.addTab(sliceviewer, '????')

        if mode == self.fullrecon:
            self.recontabs.widget(self.recontabs.count() - 1).appendData(result)
        msg.showReady()
