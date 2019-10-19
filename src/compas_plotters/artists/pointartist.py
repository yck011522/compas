from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.transforms import ScaledTranslation

from compas_plotters.artists import Artist

__all__ = ['PointArtist']


class PointArtist(Artist):
    """"""

    zorder = 9000

    def __init__(self, point):
        super(PointArtist, self).__init__()
        self._radius = 5.0
        self.point = point
        self.facecolor = '#ffffff'
        self.edgecolor = '#000000'
        self.circle = None

    @property
    def radius(self):
        return self._radius / self.plotter.dpi

    @radius.setter
    def radius(self, radius):
        self._radius = radius

    @property
    def T(self):
        F = self.plotter.figure.dpi_scale_trans
        S = ScaledTranslation(self.point[0], self.point[1], self.plotter.axes.transData)
        T = F + S
        return T

    def set_transform(self):
        self.circle.set_transform(self.T)

    def draw(self):
        circle = Circle([0, 0],
                        radius=self.radius,
                        facecolor=self.facecolor,
                        edgecolor=self.edgecolor,
                        transform=self.T,
                        zorder=self.zorder)
        self.circle = self.plotter.add_circle(circle)

    def move_to(self, x, y):
        self.point[0] = x
        self.point[1] = y
        self.set_transform()

    def move_by(self, dx=0, dy=0):
        self.point[0] += dx
        self.point[1] += dy
        self.set_transform()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas.geometry import Point
    from compas_plotters import Plotter2
    from compas_plotters import PointArtist

    plotter = Plotter2(view=([0, 16], [0, 10]), size=(8, 5), bgcolor='#cccccc')

    PointArtist.plotter = plotter

    a = PointArtist(Point(1.0, 1.0))
    b = PointArtist(Point(9.0, 5.0))
    c = PointArtist(Point(9.0, 1.0))

    a.draw()
    b.draw()
    c.draw()

    plotter.update(pause=1.0)
    for i in range(10):
        a.move_by(dx=0.5)
        plotter.update(pause=0.1)

    plotter.show()
