import sys
import os

basedoc = r'''
    \documentclass[a4paper,oneside]{scrbook}
    \usepackage[utf8]{inputenc}
    \usepackage{tikz}
    \begin{document}
    \begin{tikzpicture}
    [TIKZ_CODE]
    \end{tikzpicture}
    \end{document}
'''


class Picture(object):
    def __init__(self):
        self.drawlst = []

    def draw_line(self, start, end):
        self.drawlst.append(('line', [start, end]))

    def draw_rect(self, topleft, size):
        bottomright = tuple(topleft[i]+size[i] for i in range(2))
        self.drawlst.append(('rect', [topleft, bottomright]))

    def code(self):
        ostr = ''
        for drawobj in self.drawlst:
            if drawobj[0] == 'line':
                start, end = drawobj[1]
                sx, sy = start
                ex, ey = end
                ostr += r'\tikz \draw ({}pt,{}pt) -- ({}pt,{}pt);'.format(sx, sy, ex, ey)
            elif drawobj[0] == 'rect':
                topleft, bottomright = drawobj[1]
                sx, sy = topleft
                ex, ey = bottomright
                ostr += r'\tikz \draw ({}pt,{}pt) rectangle ({}pt,{}pt);'.format(sx, sy, ex, ey)
        return ostr


def simple_pic():
    pic = Picture()
    pic.draw_line((0, 0), (10, 10))
    pic.draw_rect((50, 50), (50, 50))
    return pic.code()


def write_doc(tikz_code, ofn='tikzdraw.tex'):
    with open(ofn, 'w') as fp:
        fp.write(basedoc.replace('[TIKZ_CODE]', tikz_code))
    os.system('pdflatex ' + ofn)


def main(args):
    write_doc(simple_pic())


if __name__ == '__main__':
    main(sys.argv)
