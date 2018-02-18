import numpy as np
from functools import partial
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core.data import load_header, NonDBHeader
from xicam.core.execution.workflow import Workflow
from xicam.core.execution.daskexecutor import DaskExecutor
from xicam.core import msg
import distributed

from xicam.plugins import GUIPlugin, GUILayout, manager as pluginmanager
from xicam.plugins.GUIPlugin import PanelState

from xicam.gui.threads import QThreadFuture, QThreadFutureIterator
from xicam.gui.widgets.tabview import TabView
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from .widgets.RAWViewer import RAWViewer
from .widgets.tomotoolbar import TomoToolbar
from .widgets.sliceviewer import SliceViewer
from .widgets.volumeviewer import VolumeViewer

from .workflows.APS_2BM import Workflow


class TomographyPlugin(GUIPlugin):
    name = 'Tomography'
    sigLog = Signal(int, str, str, np.ndarray)
    slice = 0
    multislice = 1
    preview3d = 2
    fullrecon = 3

    def __init__(self):
        self.workflow = Workflow()

        self.headermodel = QStandardItemModel()
        # self.alignmenttabview = TabView(self.headermodel)
        self.rawtabview = TabView(self.headermodel, widgetcls=RAWViewer, field='projection')
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
            for process in self.workflow.processes:
                for name in process.inputs:
                    if name == 'path':
                        process.inputs[name].value = \
                        self.headermodel.item(self.rawtabview.currentIndex()).header.startdoc[
                            'path']
            _reconthread = QThreadFuture(self.workflow.execute, (None,),
                                         callback_slot=partial(self.showReconstruction, mode=self.slice),
                                         except_slot=self.exceptionCallback)
            _reconthread.start()
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

            numofsinograms = currentheader.meta_array('projection').shape[1]

            executor = DaskExecutor()
            client = distributed.Client()

            def chunkiterator(workflow):
                for i in range(0, int(numofsinograms), int(readprocess.chunksize.value)):
                    readprocess.sinoindex.value = i
                    yield executor.execute(workflow)

            _reconthread = QThreadFutureIterator(chunkiterator, self.workflow,
                                                 callback_slot=partial(self.showReconstruction, mode=self.fullrecon),
                                                 except_slot=self.exceptionCallback)
            _reconthread.start()
        except Exception as ex:
            msg.logError(ex)
            msg.showReady()
            msg.clearMessage()

    def exceptionCallback(self, ex):
        msg.notifyMessage("Reconstruction failed;\n see log for error")
        msg.showMessage("Reconstruction failed; see log for error")
        msg.logError(ex)
        msg.showReady()

    def showReconstruction(self, result, mode):
        if mode == self.slice:
            sliceviewer = SliceViewer()
            sliceviewer.setImage(list(result.values())[0].value.squeeze())
            self.recontabs.addTab(sliceviewer, '????')

        if mode == self.fullrecon:
            self.recontabs.widget(self.recontabs.count() - 1).appendData(list(result.values())[0].value[::4, ::4, ::4])
        msg.showReady()
