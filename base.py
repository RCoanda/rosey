import math
import numpy as np

PSI = (math.sqrt(5) - 1) / 2
PSI_2 = 1 - PSI
TOL = 1.e-5

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    @property
    def d(self):
        side_l, side_r = self.v2 - self.v1, self.v3 - self.v2 

        # MOVE TO
        d = "m {}, {} ".format(self.v1[0], self.v1[1])
        # LINE TO
        d += "l {}, {} ".format(side_l[0], side_l[1])
        d += "l {}, {} ".format(side_r[0], side_r[1])
        # LINE TO, CLOSE PATH
        d += "l {}, {}z".format(-side_l[0], -side_l[1])

        return d

    @property
    def center(self):
        return (self.v1 + self.v3)/2
        
    def mirror(self):
        v1 = np.array([self.v1[0], -self.v1[1]])
        v2 = np.array([self.v2[0], -self.v2[1]])
        v3 = np.array([self.v3[0], -self.v3[1]])
        return self.__class__(v1, v2, v3)

class Biggy(Triangle):

    def split(self):
        s1 = PSI_2 * self.v1 + PSI * self.v3
        s2 = PSI_2 * self.v1 + PSI * self.v2

        return (Biggy(s1, s2, self.v1),
                Tiny(s2, s1, self.v2),
                Biggy(self.v3, s1, self.v2))

class Tiny(Triangle):

    def split(self):
        s1 = PSI * self.v1 + PSI_2 * self.v2

        return (Tiny(s1, self.v3, self.v1),
                Biggy(self.v3, s1, self.v2))


def create(intial_tiling=None, depth=5):
    if intial_tiling is None:
        pass
    
    tiling = intial_tiling

    for i in range(depth):
        elems = []
        for elem in tiling:
            elems.extend(elem.split())
        tiling = elems

    # Remove duplicates based on their romboid center
    # selements = sorted(tiling, key=lambda elem: (elem.center[0], elem.center[1]))
    # tiling = [selements[0]]
    # for i, elem in enumerate(selements[1:], start=1):
    #     if (np.abs(elem.center - selements[i-1].center) > TOL).all() :
    #         tiling.append(elem)

    # Mirror
    tiling.extend([elems.mirror() for elems in tiling])
    
    return tiling


def print_svg(depth=5, base_width = 0.005, scale=100, margin=1.05, tile_color="pink", stroke_color="green"):
    stroke_width = str(PSI ** depth * scale * base_width)
    xmin = ymin = - scale * margin
    width =  height = 2 * scale * margin
    viewbox ='{} {} {} {}'.format(xmin, ymin, width, height)

    svg = ['<?xml version="1.0" encoding="utf-8"?>']   
    svg.append('<svg width="100%" height="100%" viewBox="{}"'.format(viewbox))
    svg.append(' preserveAspectRatio="xMidYMid meet" version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">') 
    svg.append('<g style="stroke:{}; stroke-width: {};">'.format(stroke_color, stroke_width))

    theta = 2 * math.pi / 5
    rot = np.array([math.cos(theta), math.sin(theta)])
    v1 = np.array([-scale / 2, 0])
    v2 = scale / 2 * rot
    v3 = np.array([scale / 2 / PSI, 0])

    tiling = create(intial_tiling=[Biggy(v1, v2, v3)], depth=depth)

    for elem in tiling:
        svg.append('<path fill="{}" opacity="{}" d="{}"/>'.format(tile_color , 0.3, elem.d))

    svg.append('</g>\n</svg>')
    svg = '\n'.join(svg)

    with open("penrose.svg", 'w') as fo:
        fo.write(svg)

if __name__ == "__main__":
    print_svg(depth=6)
