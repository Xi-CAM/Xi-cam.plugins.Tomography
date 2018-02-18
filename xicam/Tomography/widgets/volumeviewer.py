import os
import numpy as np
import pyqtgraph as pg
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *
from vispy import scene
from vispy.color import Colormap


class VolumeViewer(QWidget):
    sigImageChanged = Signal()

    def __init__(self, data=None):
        super(VolumeViewer, self).__init__()

        self.levels = [0, 1]

        ly = QHBoxLayout()
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(0)

        self.volumeRenderWidget = VolumeRenderWidget(data)
        ly.addWidget(self.volumeRenderWidget.native)

        self.HistogramLUTWidget = None
        self.HistogramLUTWidget = pg.HistogramLUTWidget(image=self, parent=self)
        self.HistogramLUTWidget.setMaximumWidth(self.HistogramLUTWidget.minimumWidth() + 15)  # Keep static width
        self.HistogramLUTWidget.setMinimumWidth(self.HistogramLUTWidget.minimumWidth() + 15)

        v = QVBoxLayout()
        v.addWidget(self.HistogramLUTWidget)

        # ly.addWidget(self.HistogramLUTWidget)

        self.setButton = histDialogButton('Set', parent=self)
        self.setButton.setMaximumWidth(self.HistogramLUTWidget.minimumWidth() + 15)
        self.setButton.setMinimumWidth(self.HistogramLUTWidget.minimumWidth() + 15)
        self.setButton.connectToHistWidget(self.HistogramLUTWidget)
        v.addWidget(self.setButton)
        ly.addLayout(v)

        # self.xregion = SliceWidget(parent=self)
        # self.yregion = SliceWidget(parent=self)
        # self.zregion = SliceWidget(parent=self)
        # self.xregion.item.region.setRegion([0, 1000])
        # self.yregion.item.region.setRegion([0, 1000])
        # self.zregion.item.region.setRegion([0, 1000])
        # self.xregion.sigSliceChanged.connect(self.setVolume) #change to setVolume
        # self.yregion.sigSliceChanged.connect(self.setVolume)
        # self.zregion.sigSliceChanged.connect(self.setVolume)
        # ly.addWidget(self.xregion)
        # ly.addWidget(self.yregion)
        # ly.addWidget(self.zregion)

        self.setLayout(ly)

        self.volumeRenderWidget.setData(data=data)

    def appendData(self, data):
        self.volumeRenderWidget.appendData(data)
        self.sigImageChanged.emit()

    def setData(self, data):
        self.volumeRenderWidget.setData(data)
        self.sigImageChanged.emit()

    @property
    def data(self):
        return self.volumeRenderWidget.data

    def moveGradientTick(self, idx, pos):
        tick = self.HistogramLUTWidget.item.gradient.listTicks()[idx][0]
        tick.setPos(pos, 0)
        tick.view().tickMoved(tick, QPoint(pos * self.HistogramLUTWidget.item.gradient.length, 0))
        tick.sigMoving.emit(tick)
        tick.sigMoved.emit(tick)
        tick.view().tickMoveFinished(tick)

    def setLevels(self, levels, update=True):
        self.levels = levels
        self.setLookupTable()
        if self.HistogramLUTWidget: self.HistogramLUTWidget.region.setRegion(levels)
        if update:
            self.volumeRenderWidget.update()

    def setLookupTable(self, lut=None, update=True):
        try:
            table = self.HistogramLUTWidget.item.gradient.colorMap().color / 256.
            pos = self.HistogramLUTWidget.item.gradient.colorMap().pos
            # table=np.clip(table*(self.levels[1]-self.levels[0])+self.levels[0],0.,1.)
            table[:, 3] = pos
            table = np.vstack([np.array([[0, 0, 0, 0]]), table, np.array([[1, 1, 1, 1]])])
            pos = np.hstack([[0], pos * (self.levels[1] - self.levels[0]) + self.levels[0], [1]])
            self.volumeRenderWidget.volume.cmap = Colormap(table, controls=pos)
        except AttributeError as ex:
            print(ex)

    def getHistogram(self, bins='auto', step='auto', targetImageSize=100, targetHistogramSize=500, **kwds):
        """Returns x and y arrays containing the histogram values for the current image.
        For an explanation of the return format, see numpy.histogram().

        The *step* argument causes pixels to be skipped when computing the histogram to save time.
        If *step* is 'auto', then a step is chosen such that the analyzed data has
        dimensions roughly *targetImageSize* for each axis.

        The *bins* argument and any extra keyword arguments are passed to
        np.histogram(). If *bins* is 'auto', then a bin number is automatically
        chosen based on the image characteristics:

        * Integer images will have approximately *targetHistogramSize* bins,
          with each bin having an integer width.
        * All other types will have *targetHistogramSize* bins.

        This method is also used when automatically computing levels.
        """
        if self.data is None:
            return None, None
        if step == 'auto':
            step = (int(np.ceil(float(self.data.shape[0]) / targetImageSize)),
                    int(np.ceil(float(self.data.shape[1]) / targetImageSize)))
        if np.isscalar(step):
            step = (step, step)
        stepData = self.data[::step[0], ::step[1]]

        if bins == 'auto':
            if stepData.dtype.kind in "ui":
                mn = stepData.min()
                mx = stepData.max()
                step = np.ceil((mx - mn) / 500.)
                bins = np.arange(mn, mx + 1.01 * step, step, dtype=np.int)
                if len(bins) == 0:
                    bins = [mn, mx]
            else:
                bins = 500

        kwds['bins'] = bins
        hist = np.histogram(stepData, **kwds)

        return hist[1][:-1], hist[0]

        # @volumeRenderWidget.connect
        # def on_frame(self,event):
        #     self.volumeRenderWidget.cam1.auto_roll

        # def writevideo(self,fps=25):
        #     writer = imageio.save('foo.mp4', fps=25)
        #     self.volumeRenderWidget.events.draw.connect(lambda e: writer.append_data(self.render()))
        #     self.volumeRenderWidget.events.close.connect(lambda e: writer.close())


class VolumeVisual(scene.visuals.Volume):
    def set_data(self, vol, clim=None):
        """ Set the volume data.

        Parameters
        ----------
        vol : ndarray
            The 3D volume.
        clim : tuple | None
            Colormap limits to use. None will use the min and max values.
        """
        # Check volume
        if not isinstance(vol, np.ndarray):
            return
            raise ValueError('Volume visual needs a numpy array.')
        if not ((vol.ndim == 3) or (vol.ndim == 4 and vol.shape[-1] <= 4)):
            return
            raise ValueError('Volume visual needs a 3D image.')

        # Handle clim
        if clim is not None:
            clim = np.array(clim, float)
            if not (clim.ndim == 1 and clim.size == 2):
                raise ValueError('clim must be a 2-element array-like')
            self._clim = tuple(clim)
        self._clim = vol.min(), vol.max()  # NOTE: THIS IS MODIFIED BY RP TO RESET MIN/MAX EACH TIME

        # Apply clim
        vol = np.array(vol, dtype='float32', copy=True)
        vol -= self._clim[0]
        vol *= 1. / (self._clim[1] - self._clim[0])

        # Apply to texture
        self._tex.set_data(vol)  # will be efficient if vol is same shape
        self._program['u_shape'] = vol.shape[2], vol.shape[1], vol.shape[0]
        self._vol_shape = vol.shape[:3]

        shape = vol.shape[:3]
        if self._vol_shape != shape:
            self._vol_shape = shape
            self._need_vertex_update = True
        self._vol_shape = shape

        # # Create vertices?
        # if self._index_buffer is None:
        #     self._create_vertex_data()


class SliceWidget(pg.HistogramLUTWidget):
    sigSliceChanged = Signal()

    def __init__(self, *args, **kwargs):
        super(SliceWidget, self).__init__(*args, **kwargs)
        self.item.paint = lambda *x: None
        self.item.vb.deleteLater()
        self.item.gradient.gradRect.hide()
        self.item.gradient.allowAdd = False
        self.setMinimumWidth(70)
        self.setMaximumWidth(70)
        self.item.sigLookupTableChanged.connect(self.ticksChanged)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(70, 200)

    def ticksChanged(self, LUT):
        self.sigSliceChanged.emit()
        # tuple(sorted(LUT.gradient.ticks.values()))

    def getSlice(self):
        bounds = sorted(self.item.gradient.ticks.values())
        bounds = (bounds[0] * self.item.region.getRegion()[1], bounds[1] * self.item.region.getRegion()[1])
        return slice(*bounds)


class VolumeRenderWidget(scene.SceneCanvas):
    def __init__(self, data=None, size=(800, 600), show=False):
        super(VolumeRenderWidget, self).__init__(keys='interactive', size=size, show=show)

        # Prepare canvas
        self.measure_fps()

        self.unfreeze()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.central_widget.add_view()

        self.data = None
        if data: self.setData(data)

        # Create three cameras (Fly, Turntable and Arcball)
        fov = 60.
        self.cam1 = scene.cameras.FlyCamera(parent=self.view.scene, fov=fov, name='Fly')
        self.cam2 = scene.cameras.TurntableCamera(parent=self.view.scene, fov=fov, name='Turntable')
        self.cam3 = scene.cameras.ArcballCamera(parent=self.view.scene, fov=fov, name='Arcball')
        self.view.camera = self.cam2  # Select turntable at first

        # Set whether we are emulating a 3D texture
        emulate_texture = False
        self.volume = VolumeVisual(np.zeros((1, 1, 1)), parent=self.view.scene, emulate_texture=emulate_texture)
        self.volume.method = 'translucent'

    def setData(self, data):
        if data is None: return
        data = np.nan_to_num(data)
        self.data = data

        # Create the volume visuals
        if self.volume is not None:
            self.volume.set_data(data)
            self.volume._create_vertex_data()  # TODO: Try using this instead of slicing array?

            # Translate the volume into the center of the view (axes are in strange order for unkown )
            scale = 3 * (2.0 / self.data.shape[1],)
            translate = list(map(lambda x: -scale[0] * x / 2, reversed(data.shape)))
            self.volume.transform = scene.STTransform(translate=translate, scale=scale)
        self.update()

    def appendData(self, data):
        print('dataappended:', data, data.min(), data.max())
        if self.data is not None:
            print('vol1:', self.data.shape, 'vol2:', data.shape)
            data = np.vstack([self.data, data])
        self.setData(data)

    # Implement key presses
    def on_key_press(self, event):
        if event.text == '1':
            cam_toggle = {self.cam1: self.cam2, self.cam2: self.cam3, self.cam3: self.cam1}
            self.view.camera = cam_toggle.get(self.view.camera, self.cam2)
            print(self.view.camera.name + ' camera')
        elif event.text == '2':
            pass
        elif event.text == '3':
            pass
        elif event.text == '4':
            pass
        elif event.text == '0':
            self.cam1.set_range()
            self.cam3.set_range()
        elif event.text != '' and event.text in '[]':
            s = -0.025 if event.text == '[' else 0.025
            self.volume.threshold += s
            th = self.volume.threshold
            print("Isosurface threshold: %0.3f" % th)


class histDialogButton(QPushButton):
    """
    Button to connect to a pyqtgraph.HistogramLUTWidget. Sets the maximum and minimum hist value based on
    values provided by user from popup dialog
    """

    def __init__(self, label, *args, **kwargs):
        super(histDialogButton, self).__init__(label, *args, **kwargs)

        self.value = None

    def showDialog(self, min_default, max_default):
        self.dialog = QDialog(parent=self.window())
        layout = QVBoxLayout()
        text = QLabel("Set maximum and minimum values for histogram.")
        layout.addWidget(text)
        layout.addSpacing(5)

        label1 = QLabel("Max: ")
        label2 = QLabel("Min: ")

        self.field1 = QDoubleSpinBox()
        self.field2 = QDoubleSpinBox()
        self.field1.setRange(-1000000, 1000000)
        self.field2.setRange(-1000000, 1000000)
        self.field1.setValue(max_default)
        self.field2.setValue(min_default)

        h1 = QHBoxLayout()
        h1.addWidget(label1)
        h1.addWidget(self.field1)
        h2 = QHBoxLayout()
        h2.addWidget(label2)
        h2.addWidget(self.field2)

        valueButton = QPushButton("Ok")
        valueButton.setDefault(True)
        cancelButton = QPushButton("Cancel")
        valueButton.clicked.connect(self.return_vals)
        cancelButton.clicked.connect(self.cancel)

        h3 = QHBoxLayout()
        h3.addWidget(cancelButton)
        h3.addWidget(valueButton)

        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addLayout(h3)
        self.dialog.setLayout(layout)
        self.dialog.setWindowTitle("Set histogram bounds")
        self.dialog.exec_()

    def return_vals(self):
        self.value = [self.field2.value(), self.field1.value()]
        self.dialog.accept()

    def cancel(self):
        self.value = None
        self.dialog.reject()

    def connectToHistWidget(self, hist):
        self.hist = hist
        self.clicked.connect(self.setHistValues)

    def setHistValues(self):
        defaults = self.hist.getLevels()
        self.showDialog(defaults[0], defaults[1])

        if self.value:
            self.hist.setLevels(self.value[0], self.value[1])


if __name__ == '__main__':
    import numpy as np

    app = QApplication([])
    w = VolumeViewer()
    timer = QTimer()
    w.show()


    def mkdata(*args, **kwargs):
        w.appendData(np.random.sample((1, 1000, 1000)))


    timer.timeout.connect(mkdata)
    timer.setInterval(1000)
    timer.start()
    # w.volumeRenderWidget.setData(np.random.sample((200,200,800)))
    app.exec_()
