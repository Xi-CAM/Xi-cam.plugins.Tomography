from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class RAWViewer(QWidget):

    def __init__(self, header=None, *args, **kwargs):
        super(RAWViewer, self).__init__(*args, **kwargs)

        # pipeline dictionary of parameters
        # self.pipeline = OrderedDict()

        # set path as field of TomoViewer
        # self.path = paths
        # self.toolbar = toolbar

        # self._recon_path = None
        self.viewmode = QTabWidget(self)
        self.viewmode.setTabShape(QTabBar.TriangularSouth)

        # self.viewstack = QtGui.QStackedWidget(self)
        # self.viewmode = QtGui.QTabBar(self)
        # self.viewmode.addTab('Projection View')  # TODO: Add icons!
        # self.viewmode.addTab('Sinogram View')
        # self.viewmode.addTab('Flats')
        # self.viewmode.addTab('Darks')
        # self.viewmode.addTab('Slice Preview')
        # self.viewmode.addTab('3D Preview')


        # keep a timer for reconstruction
        # self.recon_start_time = 0
        # self.preview_holder = []
        # self.prange = []

        # if data is not None:
        #     self.data = data
        # elif paths is not None and len(paths):
        #     if paths.endswith('.tif') or paths.endswith('.tiff'):
        #         self.data = self.loaddata(paths, raw=True)
        #     else:
        #         self.data = self.loaddata(paths)

        self.projectionViewer = ProjectionViewer(self.data, self.toolbar, parent=self)
        self.projectionViewer.centerBox.setRange(0, self.data.shape[1])
        self.projectionViewer.stackViewer.connectImageToName(self.data.fabimage.frames)
        self.viewstack.addWidget(self.projectionViewer)

        self.sinogramViewer = StackViewer(SinogramStack.cast(self.data), parent=self)
        self.sinogramViewer.setIndex(self.sinogramViewer.data.shape[0] // 2)
        self.viewstack.addWidget(self.sinogramViewer)

        self.flatViewer = ArrayViewer(self.data.flats, flipAxes=True,  parent=self)
        self.darkViewer = ArrayViewer(self.data.darks, flipAxes=True, parent=self)
        self.viewstack.addWidget(self.flatViewer)
        self.viewstack.addWidget(self.darkViewer)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(self.viewmode)
        self.setLayout(v)

    def wireupCenterSelection(self, recon_function):
        """
        Connect the reconstruction functions parameters to the manual center selection button.
        And connect the parameters sigValueChanged to the center detection image overlay widget

        Parameters
        ----------
        recon_function : FuncionWidget
            Reconstruction function widget with a 'center' child parameter

        """
        if recon_function is not None:
            center_param = recon_function.params.child('center')
            # Uncomment this if you want convenience of having the center parameter in pipeline connected to the
            # manual center widget, but this limits the center options to a resolution of 0.5
            self.projectionViewer.sigCenterChanged.connect(
                lambda x: center_param.setValue(x)) #, blockSignal=center_param.sigValueChanged))
            self.projectionViewer.centerBox.valueChanged.connect(lambda x: center_param.setValue(x))
            self.projectionViewer.setCenterButton.clicked.connect(
                lambda: center_param.setValue(self.projectionViewer.centerBox.value()))
            center_param.sigValueChanged.connect(lambda p,v: self.projectionViewer.centerBox.setValue(v))
            center_param.sigValueChanged.connect(lambda p,v: self.projectionViewer.updateROIFromCenter(v))

    def openFlats(self):
        """
        Opens new 'flats' for dataset from path taken from user via QtGui.QFileDialog
        """

        flat_dialog = QtGui.QFileDialog(self).getOpenFileName(caption="Please select flats for this dataset: ")
        path = flat_dialog[0]

        if path:
            import fabio
            msg.showMessage('Loading flats...')
            try:
                flats = fabio.open(path)
                self.data.flats = OrderedDict()
                for frame in sorted(flats.frames):
                    self.data.flats[frame] = np.squeeze(np.copy(flats._dgroup[frame])).transpose()
                self.flatViewer.setData(self.data.flats)
                del flats
            except Exception as e:
                QtGui.QMessageBox.warning(self, 'Warning', 'Flats not loaded.')
                msg.showMessage('Unable to load flats. Check log for details.', timeout=10)
                raise e
        msg.clearMessage()

    def openDarks(self):
        """
        Opens new 'darks' for dataset from path taken from user via QtGui.QFileDialog
        """
        dark_dialog = QtGui.QFileDialog(self).getOpenFileName(caption="Please select darks for this dataset: ")
        path = dark_dialog[0]

        if path:
            import fabio
            msg.showMessage('Loading darks...', timeout=10)
            try:
                darks = fabio.open(path)
                self.data.darks = OrderedDict()
                for frame in sorted(darks.frames):
                    self.data.darks[frame] = np.squeeze(np.copy(darks._dgroup[frame])).transpose()
                self.darkViewer.setData(self.data.darks)
                del darks
            except Exception as e:
                QtGui.QMessageBox.warning(self, 'Warning', 'Darks not loaded.')
                msg.showMessage('Unable to load darks. Check log for details.', timeout=10)
                raise e
        msg.clearMessage()

    @staticmethod
    def loaddata(paths, raw=True):
        """
        Load data from a file or list of files

        Parameters
        ----------
        paths : str/list of str
            Path to files
        raw : bool
            Boolean specifiying it the file is a raw dataset with flats and darks
            (not using this now but can be used for files where flats/darks are in seperate files)

        Returns
        -------
        ProjectionStack, StackImage:
            Class with raw data from file

        """

        if raw:
            return ProjectionStack(paths)
        else:
            return StackImage(paths)


    def getsino(self, slc=None): #might need to redo the flipping and turning to get this in the right orientation
        """
        Returns the sinograms specified in slc (this and getproj can be made one function)

        Parameters
        ----------
        slc : slice, optional
            Slice object specifying the portion of the array to return

        Returns
        -------
        ndarray:
            Array of raw data

        """
        if slc is None:
            return np.ascontiguousarray(self.sinogramViewer.currentdata[:, np.newaxis, :])
        else:
            return np.ascontiguousarray(self.data.fabimage[slc])

    def getproj(self, slc=None):
        """
        Returns the projections specified in slc (this and getsino can be made one function)

        Parameters
        ----------
        slc : slice, optional
            Slice object specifying the portion of the array to return

        Returns
        -------
        ndarray:
            Array of raw data

        """
        if slc is None:
            return np.ascontiguousarray(self.projectionViewer.currentdata[np.newaxis, :, :])
        else:
            return np.ascontiguousarray(self.data.fabimage[slc])

    def getflats(self, slc=None):
        """
        Returns the flat fields specified in slc

        Parameters
        ----------
        slc : slice, optional
            Slice object specifying the portion of the array to return

        Returns
        -------
        ndarray:
            Array of flat field data

        """
        flats = np.array(self.data.flats.values())
        if slc is None:
            return np.ascontiguousarray(flats[:, self.sinogramViewer.currentIndex, :])
        else:
            return np.ascontiguousarray(flats[slc])

    def getdarks(self, slc=None):
        """
        Returns the dark fields specified in slc

        Parameters
        ----------
        slc : slice, optional
            Slice object specifying the portion of the array to return

        Returns
        -------
        ndarray:
            Array of dark field data

        """
        darks = np.array(self.data.darks.values())
        if slc is None:
            return np.ascontiguousarray(darks[:, self.sinogramViewer.currentIndex, :])
        else:
            return np.ascontiguousarray(darks[slc])

    def getheader(self):
        """Return the data's header (metadata)"""
        return self.data.header

    def addSlicePreview(self, params, recon, slice_no=None, prange=None):
        """
        Adds a slice reconstruction preview with the corresponding workflow pipeline dictionary to the previewViewer

        Parameters
        ----------
        params : dict
            Pipeline dictionary
        recon : ndarry
            Reconstructed slice
        slice_no : int, optional
            Sinogram/slice number reconstructed
        prange : dict, optional
            Dictionary of parameter being tested in TestParameterRange, and the functino it belongs to
        """
        if type(recon) == str:
            return

        if slice_no is None:
            slice_num = self.sinogramViewer.view_spinBox.value()
            self.previewViewer.addPreview(np.rot90(recon[0],1), params, slice_num)
        elif type(slice_no) is list:
            for item in range(slice_no[1]- slice_no[0]+1):
                self.previewViewer.addPreview(np.rot90(recon[item], 1), params, item+slice_no[0])
        # this block ensures that the previews are added in order if testparamrange is triggered
        elif prange:
            dummy_prange = dict(prange)
            func = dummy_prange.pop('function')
            param = dummy_prange.keys()[0]

            if len(self.prange) < 1 and recon is not None:
                self.prange = prange[param]

            # this if loop and try statement ensure no errors due to the recursion below
            if recon is not None:
                self.preview_holder.append([recon, params, slice_no])
            try:
                top_val = self.prange[0]
            except IndexError:
                pass

            # run through each recon in the preview_holder, and add them to the preview viewer if the top param in
            # prange matches the preview metadata
            for index, rec in enumerate(self.preview_holder):
                for key in rec[1].iterkeys():
                    if func in key:
                        subfunc = rec[1][key].keys()[0]
                        param_val = rec[1][key][subfunc][param]
                if top_val == param_val:
                    self.previewViewer.addPreview(np.rot90(rec[0][0], 1), rec[1], rec[2])
                    self.preview_holder.pop(index)
                    self.prange = np.delete(self.prange, 0)
                    self.addSlicePreview(params, None, slice_no, prange=prange)

        else:
            self.previewViewer.addPreview(np.rot90(recon[0],1), params, slice_no)
        self.viewstack.setCurrentWidget(self.previewViewer)
        msg.clearMessage()

    def add3DPreview(self, params, recon):
        """
        Adds a slice reconstruction preview with the corresponding workflow pipeline dictionary to the preview3DViewer

        Parameters
        ----------
        params : dict
            Pipeline dictionary
        recon : ndarry
            Reconstructed array

        """
        if type(recon) == str:
            return

        recon = np.flipud(recon)
        self.viewstack.setCurrentWidget(self.preview3DViewer)
        self.preview3DViewer.setPreview(recon, params)
        hist = self.preview3DViewer.volumeviewer.getHistogram()

        # disable auto scale
        preview_hist = self.preview3DViewer.volumeviewer.HistogramLUTWidget
        preview_hist.vb.enableAutoRange(preview_hist.vb.YAxis, False)

        max = hist[0][np.argmax(hist[1])]
        self.preview3DViewer.volumeviewer.setLevels([max, hist[0][-1]])

    def onManualCenter(self, active):
        """
        Activates the manual center portion of the ProjectionViewer.
        This is connected to the corresponding toolbar signal

        Parameters
        ----------
        active : bool
            Boolean specifying to activate or not. True activate, False deactivate

        """

        if active:
            self.viewstack.setCurrentWidget(self.projectionViewer)
            self.projectionViewer.hideMBIR()
            self.projectionViewer.showCenterDetection()

        else:
            self.projectionViewer.hideCenterDetection()

    def onMBIR(self, active):
        """
        Slot to activate MBIR slurm generation menu. Not currently in use.
        """

        if active:
            self.viewstack.setCurrentWidget(self.projectionViewer)
            self.projectionViewer.hideCenterDetection()
            self.projectionViewer.showMBIR()
        else:
            self.projectionViewer.hideMBIR()

    def onROIselection(self):
        """
        Shows a rectangular roi to select portion of data to reconstruct. (Not implemented yet)

        Parameters
        ----------
        active : bool
            Boolean specifying to activate or not. True activate, False deactivate

        """
        self.viewstack.setCurrentWidget(self.projectionViewer)
        self.projectionViewer.addROIselection()

class ProjectionViewer(QtGui.QWidget):
    """
    Class that holds a stack viewer, an ROImageOverlay and a few widgets to allow manual center detection

    Attributes
    ----------
    stackViewer : StackViewer
        widgets.StackViewer used to display the data
    data : loader.StackImage
        Image data
    imageoverlay_roi : widgets.ROIImageOverlay
        Widget used in the cor_widget for manual center detection
    selection_roi : pyqtgragh.ROI
        ROI for selecting region to reconstruct
    cor_widget : QtGui.QWidget
        Widget used in manual center detection
    setCenterButton : QtGui.QToolButton
        Button for setting center value from cor_widget to reconstruction function in pipeline
    roi_histogram : pyqtgraph.HistogramLUTWidget
        Histogram for imageoverlay
    mbir_viewer : MBIRViewer
        Menu for generating slurm files for NERSC-based MBIR jobs
    cor_box : QtGui.QStackWidget
        Widget for holding COR - related widgets
    cor_widget : QtGui.QWidget
        Widget for holding manual COR-related widgets
    auto_cor_widget : QtGui.QWidget
        Widget for holding automatic COR-related widgets

    Signals
    -------
    sigCenterChanged(float)
        emits float with new center value

    Parameters
    ----------
    data : pipeline.loader.StackImage
        Raw tomography data as a StackImage
    view_label : str
        String to show in QLabel lower right hand corner. Where the current index is displayed
    center : float
        center of rotation value
    args
        Additional arguments
    kwargs
        Additional keyword arguments
    """

    sigCenterChanged = QtCore.Signal(float)
    sigCORChanged = QtCore.Signal(bool)
    sigROIWidgetChanged = QtCore.Signal(pg.ROI)

    def __init__(self, data, toolbar=None, view_label=None, center=None, paths=None, *args, **kwargs):
        super(ProjectionViewer, self).__init__(*args, **kwargs)

        self.setMinimumHeight(200)

        self.stackViewer = StackViewer(data, view_label=view_label)
        self.toolbar = toolbar
        self.imageItem = self.stackViewer.imageItem
        self.data = self.stackViewer.data
        self.normalized = False
        self.imgoverlay_roi = ROImageOverlay(self.data, self.imageItem, [0, 0], parent=self.stackViewer.view)
        self.imageItem.sigImageChanged.connect(self.imgoverlay_roi.updateImage)
        self.stackViewer.view.addItem(self.imgoverlay_roi)
        self.roi_histogram = pg.HistogramLUTWidget(image=self.imgoverlay_roi.imageItem, parent=self.stackViewer)
        self.roi_histogram.vb.enableAutoRange(self.roi_histogram.vb.YAxis, False) #disable autoscaling for histogram
        self.mbir_viewer = MBIRViewer(self.data, path = self.parentWidget().path, parent=self)



        # roi to select region of interest
        self.selection_roi = None

        self.stackViewer.ui.gridLayout.addWidget(self.roi_histogram, 0, 3, 1, 2)
        self.stackViewer.keyPressEvent = self.keyPressEvent

        self.cor_widget = QtGui.QWidget(self)
        self.auto_cor_widget = functionwidgets.CORSelectionWidget(parent=self)
        self.cor_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.auto_cor_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.cor_widget.setMinimumHeight(50)
        self.auto_cor_widget.setMinimumHeight(50)

        self.cor_box = QtGui.QStackedWidget(self)
        self.cor_box.addWidget(self.auto_cor_widget)
        self.cor_box.addWidget(self.cor_widget)

        self.cor_button_holder = QtGui.QGroupBox(parent = self)
        h = QtGui.QHBoxLayout()
        self.manual_cor_button = QtGui.QRadioButton('Manually input center of rotation')
        self.manual_cor_button.clicked.connect(self.manualCOR)
        self.auto_cor_button = QtGui.QRadioButton('Auto-detect center of rotation')
        self.auto_cor_button.clicked.connect(self.autoCOR)
        self.auto_cor_button.setChecked(True)
        write_cor = QtGui.QPushButton('Write COR to metadata')
        write_cor.clicked.connect(self.writeCOR)
        h.addWidget(self.auto_cor_button)
        h.addWidget(self.manual_cor_button)
        h.addWidget(write_cor)
        self.cor_button_holder.setLayout(h)

        # push button for overlay widget's histogram range selection
        self.setButton = histDialogButton('Set', parent=self)
        self.setButton.connectToHistWidget(self.roi_histogram)
        self.stackViewer.ui.gridLayout.addWidget(self.setButton, 1, 3, 1, 2)

        clabel = QtGui.QLabel('Rotation Center:')
        olabel = QtGui.QLabel('Offset:')
        self.centerBox = QtGui.QDoubleSpinBox(parent=self.cor_widget) #QtGui.QLabel(parent=self.cor_widget)
        self.centerBox.setDecimals(1)
        self.setCenterButton = QtGui.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("xicam/gui/icons_45.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setCenterButton.setIcon(icon)
        self.setCenterButton.setToolTip('Set center in pipeline')
        originBox = QtGui.QLabel(parent=self.cor_widget)
        originBox.setText('x={}   y={}'.format(0, 0))
        center = center if center is not None else data.shape[1]/2.0
        self.centerBox.setValue(center) #setText(str(center))
        h1 = QtGui.QHBoxLayout()
        h1.setAlignment(QtCore.Qt.AlignLeft)
        h1.setContentsMargins(0, 0, 0, 0)
        h1.addWidget(clabel)
        h1.addWidget(self.centerBox)
        h1.addWidget(self.setCenterButton)
        h1.addWidget(olabel)
        h1.addWidget(originBox)

        # hide center button since cor updates automatically in pipeline
        self.setCenterButton.hide()

        plabel = QtGui.QLabel('Overlay Projection No:')
        plabel.setAlignment(QtCore.Qt.AlignRight)
        spinBox = QtGui.QSpinBox(parent=self.cor_widget)
        spinBox.setRange(0, data.shape[0]-1)
        slider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal, parent=self.cor_widget)
        slider.setRange(0, data.shape[0]-1)
        spinBox.setValue(data.shape[0]-1)
        slider.setValue(data.shape[0]-1)
        flipCheckBox = QtGui.QCheckBox('Flip Overlay', parent=self.cor_widget)
        flipCheckBox.setChecked(True)
        constrainYCheckBox = QtGui.QCheckBox('Constrain Y', parent=self.cor_widget)
        constrainYCheckBox.setChecked(True)
        constrainXCheckBox = QtGui.QCheckBox('Constrain X', parent=self.cor_widget)
        constrainXCheckBox.setChecked(False)
        # rotateCheckBox = QtGui.QCheckBox('Enable Rotation', parent=self.cor_widget)
        # rotateCheckBox.setChecked(False)
        self.normCheckBox = QtGui.QCheckBox('Normalize', parent=self.cor_widget)
        h2 = QtGui.QHBoxLayout()
        h2.setAlignment(QtCore.Qt.AlignLeft)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.addWidget(plabel)
        h2.addWidget(spinBox)
        h2.addWidget(flipCheckBox)
        h2.addWidget(constrainXCheckBox)
        h2.addWidget(constrainYCheckBox)
        # h2.addWidget(rotateCheckBox) # This needs to be implemented correctly
        h2.addWidget(self.normCheckBox)
        h2.addStretch(1)
        spinBox.setFixedWidth(spinBox.width())
        v2 = QtGui.QVBoxLayout(self.cor_widget)
        v2.addLayout(h1)
        v2.addLayout(h2)
        v2.addWidget(slider)

        l = QtGui.QGridLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        cor_holder = QtGui.QSplitter()
        cor_holder.setOrientation(QtCore.Qt.Vertical)
        cor_holder.addWidget(self.cor_box)
        cor_holder.addWidget(self.stackViewer)
        l.addWidget(self.cor_button_holder)
        l.addWidget(cor_holder)
        l.addWidget(self.mbir_viewer)
        self.hideMBIR()
        # self.mbir_viewer.hide()

        slider.valueChanged.connect(spinBox.setValue)
        slider.valueChanged.connect(self.stackViewer.resetImage)
        spinBox.valueChanged.connect(self.changeOverlayProj)
        flipCheckBox.stateChanged.connect(self.flipOverlayProj)
        constrainYCheckBox.stateChanged.connect(lambda v: self.imgoverlay_roi.constrainY(v))
        constrainXCheckBox.stateChanged.connect(lambda v: self.imgoverlay_roi.constrainX(v))

        # rotateCheckBox.stateChanged.connect(self.addRotateHandle)
        self.normCheckBox.stateChanged.connect(self.normalize)
        self.stackViewer.sigTimeChanged.connect(lambda: self.normalize(False))
        self.imgoverlay_roi.sigTranslated.connect(self.setCenter)
        self.imgoverlay_roi.sigTranslated.connect(lambda x, y: originBox.setText('x={}   y={}'.format(x, y)))
        self.hideCenterDetection()

        self.bounds = None
        # self.normalize(True)

    def updateCORChoice(self, boolean):
        """
        Slot to receive signal emitted when user chooses to use either automatic or manual COR detection in
        function pipeline
        """
        if self.toolbar and self.toolbar.actionCenter.isChecked():
            if boolean:
                self.cor_box.setCurrentWidget(self.auto_cor_widget)
                self.stackViewer.hide()
                self.auto_cor_button.setChecked(True)
            else:
                self.cor_box.setCurrentWidget(self.cor_widget)
                self.stackViewer.show()
                self.manual_cor_button.setChecked(True)

    def writeCOR(self):
        """
        Writes COR value acquired from user to metadata of input file
        """
        cor = QtGui.QInputDialog.getDouble(self.cor_box, 'Write COR value to file',
                                           'Write COR value to file',self.data.shape[1]/2)
        if cor[1]:
            self.data.fabimage.change_dataset_attribute('center', cor[0])


    def manualCOR(self):
        """
        Slot to receive signal when manual COR detection button is clicked in CORSelectionWidget
        """
        self.cor_box.setCurrentWidget(self.cor_widget)
        self.stackViewer.show()
        self.sigCORChanged.emit(False)

    def autoCOR(self):
        """
        Slot to receive signal when auto COR detection button is clicked in CORSelectionWidget
        """
        self.cor_box.setCurrentWidget(self.auto_cor_widget)
        self.stackViewer.hide()
        self.sigCORChanged.emit(True)



    def changeOverlayProj(self, idx):
        """
        Changes the image in the overlay. This is connected to the slider in the cor_widget
        """

        self.normCheckBox.setChecked(False)
        self.imgoverlay_roi.setCurrentImage(idx)
        self.imgoverlay_roi.updateImage()

    def setCenter(self, x, y):
        """
        Sets the center in the centerBox based on the position of the imageoverlay

        Parameters
        ----------
        x : float
            x-coordinate of overlay image in the background images coordinates
        y : float
            x-coordinate of overlay image in the background images coordinates
        """

        center = (self.data.shape[1] + x - 1)/2.0 # subtract half a pixel out of 'some' convention?
        self.centerBox.setValue(center)
        self.sigCenterChanged.emit(center)

    def hideCenterDetection(self):
        """
        Hides the center detection widget and corresponding histogram
        """
        self.normalize(False)
        self.cor_box.hide()
        self.cor_button_holder.hide()
        self.roi_histogram.hide()
        self.setButton.hide()
        self.imgoverlay_roi.setVisible(False)
        self.stackViewer.show()

    def showCenterDetection(self):
        """
        Shows the center detection widget and corresponding histogram
        """
        # self.normalize(True)
        self.cor_box.show()
        self.cor_button_holder.show()
        self.roi_histogram.show()
        self.setButton.show()
        self.imgoverlay_roi.setVisible(True)

        if self.auto_cor_button.isChecked():
            self.stackViewer.hide()
        else:
            self.stackViewer.show()

    def showMBIR(self):
        """
        Slot to receive signal and show MBIR menu when it is requested
        """

        self.mbir_viewer.show()
        self.cor_button_holder.hide()
        # self.hideCenterDetection()
        self.stackViewer.hide()

    def hideMBIR(self):
        """
        Slot to receive signal and show MBIR menu when it is requested
        """
        self.mbir_viewer.hide()
        self.stackViewer.show()


    def updateROIFromCenter(self, center):
        """
        Updates the position of the ROIImageOverlay based on the given center

        Parameters
        ----------
        center : float
            Location of center of rotation
        """

        s = self.imgoverlay_roi.pos()[0]
        self.imgoverlay_roi.translate(pg.Point((2 * center + 1 - self.data.shape[1] - s, 0))) # 1 again due to the so-called COR
                                                                                   # conventions...
    def flipOverlayProj(self, val):
        """
        Flips the image show in the ROIImageOverlay
        """

        self.imgoverlay_roi.flipCurrentImage()
        self.imgoverlay_roi.updateImage()

    def toggleRotateHandle(self, val):
        """
        Adds/ removes a handle on the ROIImageOverlay to be able to rotate the image (Rotation is not implemented
        correctly yet)

        Parameters
        ----------
        val : bool
            Boolean specifying to add or remove the handle
        """

        if val:
            self.toggleRotateHandle.handle = self.imgoverlay_roi.addRotateHandle([0, 1], [0.2, 0.2])
        else:
            self.imgoverlay_roi.removeHandle(self.toggleRotateHandle.handle)

    def addROIselection(self):
        """
        Adds/ removes a rectangular ROI to select a region of interest for reconstruction. Not implemented yet
        """
        if self.selection_roi:
            self.stackViewer.view.removeItem(self.selection_roi)

        self.selection_roi = pg.ROI([0, 0], [100, 100])
        self.stackViewer.view.addItem(self.selection_roi)
        self.selection_roi.addScaleHandle([1, 1], [0, 0])
        self.selection_roi.addScaleHandle([0, 0], [1, 1])
        self.sigROIWidgetChanged.emit(self.selection_roi)


    def normalize(self, val):
        """
        Toggles the normalization of the ROIImageOverlay.

        Parameters
        ----------
        val : bool
            Boolean specifying to normalize image
        """
        # self.roi_histogram.setLevels(0,1)
        if val and not self.normalized:
            if not hasattr(self.data, 'flats') or not hasattr(self.data, 'darks'):
                msg.showMessage('Must load flats and darks to normalize dataset', timeout=10)
                return
            flats = np.array(self.data.flats.values())
            darks = np.array(self.data.darks.values())
            self.flat = np.median(flats, axis=0).transpose()
            self.dark = np.median(darks, axis=0).transpose()

            proj = (self.imageItem.image - self.dark)/(self.flat - self.dark)
            overlay = self.imgoverlay_roi.currentImage
            if self.imgoverlay_roi.flipped:
                overlay = np.flipud(overlay)
            overlay = (overlay - self.dark)/(self.flat - self.dark)
            if self.imgoverlay_roi.flipped:
                overlay = np.flipud(overlay)
            self.imgoverlay_roi.currentImage = overlay

            self.imgoverlay_roi.updateImage(autolevels=True)
            self.stackViewer.setImage(proj, autoRange=False, autoLevels=True)
            self.stackViewer.updateImage()
            self.normalized = True
            self.roi_histogram.setLevels(-1, 1) # lazy solution, could be improved with some sampling methods
            self.roi_histogram.vb.setRange(yRange=(-1.5, 1.5))
            self.normCheckBox.setChecked(True)
        elif not val and self.normalized:
            self.stackViewer.resetImage()
            self.imgoverlay_roi.resetImage()
            min, max = self.stackViewer.quickMinMax(self.imgoverlay_roi.imageItem.image)
            self.roi_histogram.setLevels(min, max)
            self.normalized = False
            self.normCheckBox.setChecked(False)

    def keyPressEvent(self, ev):
        """
        Override QWidgets key pressed event to send the event to the ROIImageOverlay when it is pressed
        """
        super(ProjectionViewer, self).keyPressEvent(ev)
        if self.imgoverlay_roi.isVisible():
            self.imgoverlay_roi.keyPressEvent(ev)
        else:
            super(StackViewer, self.stackViewer).keyPressEvent(ev)
        ev.accept()

class StackViewer(ImageView):
    """
    PG ImageView subclass to view 3D datasets as image stacks. Removes Menu and ROI buttons from imageview and replaces
    it with a spinbox with the current frame index and a label.
    """

    def __init__(self, data=None, view_label=None, *args, **kwargs):
        super(StackViewer, self).__init__(*args, **kwargs)

        if view_label is None:
            view_label = QtGui.QLabel(self)
            view_label.setText('No: ')
        self.view_spinBox = QtGui.QSpinBox(self)
        self.view_spinBox.setKeyboardTracking(False)

        if data is not None:
            self.setData(data)

        # push button for setting the max/min values of a histogram widget
        self.setButton = histDialogButton('Set', parent=self)
        self.setButton.connectToHistWidget(self.getHistogramWidget())

        l = QtGui.QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(view_label)
        l.addWidget(self.view_spinBox)
        l.addStretch(1)
        w = QtGui.QWidget()
        w.setLayout(l)
        self.ui.gridLayout.addWidget(self.setButton, 1, 1, 1, 2)
        self.ui.gridLayout.addWidget(view_label, 2, 1, 1, 1)
        self.ui.gridLayout.addWidget(self.view_spinBox, 2, 2, 1, 1)
        self.ui.menuBtn.setParent(None)
        self.ui.roiBtn.setParent(None)

        self.sigTimeChanged.connect(self.indexChanged)
        self.view_spinBox.valueChanged.connect(self.setCurrentIndex)

        self.label = QtGui.QLabel(parent=self)
        self.ui.gridLayout.addWidget(self.label, 2, 0, 1, 1)

    def setData(self, data):
        self.data = data
        self.setImage(self.data)
        self.autoLevels()
        self.view_spinBox.setRange(0, self.data.shape[0] - 1)
        self.getImageItem().setRect(QtCore.QRect(0, 0, self.data.rawdata.shape[0], self.data.rawdata.shape[1]))

    def indexChanged(self, ind, time):
        self.view_spinBox.setValue(ind)

    def setIndex(self, ind):
        self.setCurrentIndex(ind)
        self.view_spinBox.setValue(ind)

    @property
    def currentdata(self):
        return self.data[self.data.currentframe].transpose()  # Maybe we need to transpose this

    def resetImage(self):
        self.setImage(self.data, autoRange=False)
        self.setIndex(self.currentIndex)

    def connectImageToName(self, image_names):

        self.image_names = image_names
        self.sigTimeChanged.connect(self.indexAndNameChanged)
        self.label.setText(str(self.image_names[self.currentIndex]))


    def indexAndNameChanged(self, ind, time):
        self.setCurrentIndex(ind)
        self.view_spinBox.setValue(ind)
        self.label.setText(str(self.image_names[ind]))


class ArrayViewer(StackViewer):
    """
    Subclass of StackViewer to allow for more general data inputs
    """

    def __init__(self, data=None, view_label=None, flipAxes=False, *args, **kwargs):

        super(StackViewer, self).__init__(*args, **kwargs)

        if view_label is None:
            view_label = QtGui.QLabel(self)
            view_label.setText('No: ')
        self.view_spinBox = QtGui.QSpinBox(self)
        self.view_spinBox.setKeyboardTracking(False)

        # push button for setting the max/min values of a histogram widget
        self.setButton = histDialogButton('Set', parent=self)
        self.setButton.connectToHistWidget(self.getHistogramWidget())

        l = QtGui.QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(view_label)
        l.addWidget(self.view_spinBox)
        l.addStretch(1)
        w = QtGui.QWidget()
        w.setLayout(l)
        self.ui.gridLayout.addWidget(self.setButton, 1, 1, 1, 2)
        self.ui.gridLayout.addWidget(view_label, 2, 1, 1, 1)
        self.ui.gridLayout.addWidget(self.view_spinBox, 2, 2, 1, 1)
        self.ui.menuBtn.setParent(None)
        self.ui.roiBtn.setParent(None)

        self.sigTimeChanged.connect(self.indexChanged)
        self.view_spinBox.valueChanged.connect(self.setCurrentIndex)

        self.label = QtGui.QLabel(parent=self)
        self.ui.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        if data is not None:
            self.setData(data, flipAxes=flipAxes)

    def flipAxes(self, arr):

        toReturn = np.empty((arr.shape[0], arr.shape[2], arr.shape[1]))
        for i in range(arr.shape[0]):
            toReturn[i] = arr[i].transpose()
        return toReturn

    def setData(self, data, flipAxes=False):

        if type(data) is dict or type(data).__bases__[0] is dict:
            self.keys = data.keys()
            data = np.array(data.values())
        else:
            self.keys = None

        if flipAxes: data = self.flipAxes(data)
        self.data = data
        self.setImage(self.data)
        self.autoLevels()
        self.view_spinBox.setRange(0, self.data.shape[0] - 1)
        self.getImageItem().setRect(QtCore.QRect(0, 0, self.data.shape[1], self.data.shape[2]))
        if self.keys:
            self.connectImageToName(self.keys)
