import os

from cycler import cycler
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

DPI = 96
FIGSIZE_X = 1280
FIGSIZE_Y = 960

kaleidoscope_colors = {
    'blue'         : "#0000FF",
    'green'        : "#00FF00",
    'red'          : "#FF0000",
    'yellow'       : "#FFFF00",
    'orange'       : "#FF6600",
    'purple'       : "#660066",

    'light-blue'   : "#9999FF",
    'light-green'  : "#99FF99",
    'light-red'    : "#FF9999",
    'light-yellow' : "#FFFF99",
    'light-orange' : "#FF9900",
    'light-purple' : "#9966FF"
}

# Define our own dark style and use it as default
plt.style.use(os.path.join('.', 'dark.mplstyle'))


class GraphicsView(QtWidgets.QGraphicsView):   
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.NoButton:
            print("Simple mouse motion")
        elif event.buttons() == QtCore.Qt.LeftButton:
            print("Left click drag")
        elif event.buttons() == QtCore.Qt.RightButton:
            print("Right click drag")
        super(GraphicsView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print("Press!")
        super(GraphicsView, self).mousePressEvent(event)


class DrawingCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self.fig)

        self.axes = self.fig.add_subplot(111)

        self.setParent(parent)        

        FigureCanvas.setSizePolicy(self,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)



    def setColorScheme(self, scheme):

        if scheme == 'default':
            # Use the default style that has been loaded with plt.style.use()
            return
        
        # I also like the solution of using the context manager to change the 
        # rcParam settings temporary for a number of plots.
        # See https://matplotlib.org/users/style_sheets.html#temporary-styling
        # and http://stackoverflow.com/a/41527038/2166823

        if scheme == "dark":
            n = 8 # Number of colors
            dark_colors = [plt.get_cmap('tab10')(1. * i/n) for i in range(n)]
            axes_spine_color         = 'white'
            axes_label_color         = 'white'
            axes_ticks_color         = 'white'
            axes_title_color         = 'white'
            axes_lines_color_cycler  = cycler('color', ['c', 'm', 'y', 'k'])
            axes_lines_color_cycler  = cycler('color', dark_colors)
            axes_facecolor           = 'None'
            axes_edgecolor           = 'white'
            figure_patch_color       = 'None'

        if scheme == "kaleidoscope":
            axes_spine_color         = 'red'
            axes_label_color         = 'yellow'
            axes_ticks_color         = 'purple'
            axes_title_color         = 'black'
            axes_lines_color_cycler  = cycler('color', ['r', 'g', 'b', 'y'])
            axes_facecolor           = 'blue'
            axes_edgecolor           = 'green'
            figure_patch_color       = 'orange'

        self.fig.patch.set_facecolor(figure_patch_color)

        # You can either set the background color of the axes hardcoded and equal 
        # to the color used in the GUI. But perhaps better is to make the axes patch
        # transparent. When the color of the GUI then changes the patch has the same color.

        if scheme == 'kaleidoscope':
            self.axes.set_facecolor(axes_facecolor)
        else:
            # WATCHOUT: When you call axes.cla() this color will also be cleared
            # So this line should be after the call to axes.cla()
            self.axes.patch.set_alpha(0.0)

        self.axes.spines['bottom'].set_color(axes_spine_color)
        self.axes.spines['top'].set_color(axes_spine_color) 
        self.axes.spines['right'].set_color(axes_spine_color)
        self.axes.spines['left'].set_color(axes_spine_color)

        # Make the background of the canvas transparent
        self.setStyleSheet("background-color:transparent;")

        self.axes.xaxis.label.set_color(axes_label_color)
        self.axes.yaxis.label.set_color(axes_label_color)

        self.axes.tick_params(axis='x', colors=axes_ticks_color, which='both')
        self.axes.tick_params(axis='y', colors=axes_ticks_color, which='both')

        self.axes.title.set_color(axes_title_color)

        self.axes.set_prop_cycle(axes_lines_color_cycler)


