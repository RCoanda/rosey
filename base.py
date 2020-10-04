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
    
    def path(self, opacity, fill_color):
        side_l, side_r = self.v2 - self.v1, self.v3 - self.v2 

        # MOVE TO
        d = "m {}, {} ".format(self.v1[0], self.v1[1])
        # LINE TO
        d += "l {}, {} ".format(side_l[0], side_l[1])
        d += "l {}, {} ".format(side_r[0], side_r[1])
        # LINE TO, CLOSE PATH
        d += "l {}, {}z".format(-side_l[0], -side_l[1])

        return '<path fill="{}" opacity="{}" d="{}"/>'.format(fill_color, opacity, d)

    def dotted(self, stroke_width, stroke_color="black", tile_color="black", radius=0.1):
        svg_circle = lambda point: '<circle cx="{}" cy="{}" r="{}" stroke="{}" stroke-width="{}" fill="{}" />\n'.format(point[0], point[1], radius, stroke_color, stroke_width, tile_color)
        
        side_l, side_r = self.v2 - self.v1, self.v3 - self.v2 

        d = svg_circle(self.v1)
        d += svg_circle(side_l)
        d += svg_circle(side_r)
        d += svg_circle(-side_l)

        return d

    @property
    def center(self):
        return (self.v1 + self.v3)/2
        
    def mirror(self):
        v1 = np.array([self.v1[0], -self.v1[1]])
        v2 = np.array([self.v2[0], -self.v2[1]])
        v3 = np.array([self.v3[0], -self.v3[1]])
        return self.__class__(v1, v2, v3)

class Fatty(Triangle):

    def split(self):
        s1 = PSI_2 * self.v1 + PSI * self.v3
        s2 = PSI_2 * self.v1 + PSI * self.v2

        return (Fatty(s1, s2, self.v1),
                Tiny(s2, s1, self.v2),
                Fatty(self.v3, s1, self.v2))

class Tiny(Triangle):

    def split(self):
        s1 = PSI * self.v1 + PSI_2 * self.v2

        return (Tiny(s1, self.v3, self.v1),
                Fatty(self.v3, s1, self.v2))

class Tiling:
    def __init__(self, initial=None, depth = 5, scale = 100, mirror=True):
        """Tiling manager class.

        Args:
            initial (list of `Triangle`, optional): The initial tiling. Defaults to None.
        """
        if initial is None or initial == "rombus":
            theta = 2 * math.pi / 5
            rot = np.array([math.cos(theta), math.sin(theta)])
            v1 = np.array([-scale / 2, 0])
            v2 = scale / 2 * rot
            v3 = np.array([scale / 2 / PSI, 0])
            initial = [Fatty(v1, v2, v3)]

        elif initial == "hexagon":
            theta = math.pi / 5
            alpha = math.cos(theta)
            rot = np.array([math.cos(theta), math.sin(theta)])
            v1 = np.array([scale, 0])
            c = np.array([0, 0])
            u1 = u2 = np.array([v1[0]*rot[0]-v1[1]*rot[1], v1[0]*rot[1]+v1[1]*rot[0]]) 
            v2 = v3 = np.array([u1[0]*rot[0]-u1[1]*rot[1], u1[0]*rot[1]+u1[1]*rot[0]]) 
            u3 = u4 = np.array([v3[0]*rot[0]-v3[1]*rot[1], v3[0]*rot[1]+v3[1]*rot[0]]) 
            v4 = v5 = np.array([u4[0]*rot[0]-u4[1]*rot[1], u4[0]*rot[1]+u4[1]*rot[0]]) 
            u5 = -v1

            initial = [ 
                Tiny(v1, c, u1), 
                Tiny(v2, c, u2), 
                Tiny(v3, c, u3),
                Tiny(v4, c, u4),
                Tiny(v5, c, u5)
            ]

        self.tiling = initial

        self.depth = depth 
        self.mirror = mirror
        self.scale = scale

        self._create(depth, mirror)
       
    def _create(self, depth, mirror):
        # Cut the tiles recursively
        for _ in range(depth):
            new_tiling = []
            for tile in self.tiling:
                new_tiling.extend(tile.split())
            self.tiling = new_tiling

        # Mirror the tiling along the x-Axis
        if mirror:
            self.tiling.extend([tile.mirror() for tile in self.tiling])

    def to_svg(self, filepath, dotted=False, width=0.005, margin=1.05, fill_color="white", stroke_color="black", radius=.0005):
        stroke_width = str(PSI ** self.depth * self.scale * width)

        # Create viewport
        xmin = ymin = - self.scale * margin
        width =  height = 2 * self.scale * margin
        viewbox ='{} {} {} {}'.format(xmin, ymin, width, height)

        svg = ['<?xml version="1.0" encoding="utf-8"?>']   
        svg.append('<svg width="100%" height="100%" viewBox="{}"'.format(viewbox))
        svg.append(' preserveAspectRatio="xMidYMid meet" version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">')

        # Elements container
        svg.append('<g style="stroke:{}; stroke-width: {};">'.format(stroke_color, stroke_width))

        # Generates elements
        if dotted:
            for tile in self.tiling:
                svg.append(tile.dotted(stroke_width, stroke_color, fill_color, .0005))
        else:
            for tile in self.tiling:
                svg.append(tile.path(1, fill_color))
                

        svg.append('</g>\n</svg>')
        svg = '\n'.join(svg)

        filepath = "{}_{}_{}".format(filepath, self.depth, width)
        with open(filepath, 'w') as fo:
            fo.write(svg)


if __name__ == "__main__":
    t1 = Tiling(initial="hexagon", depth=8, scale=400)
    t1.to_svg("output/rose", fill_color="pink", dotted=True, width=0.4)

    # print_svg("penrose_2_3.svg", intial_tiling=t2, depth=2, base_width=.3)
    # print_svg_dotted("penrose_dotted_9_3.svg", intial_tiling=t2, scale=scale, depth=9, base_width=.05)