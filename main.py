import skip
from sexpdata import loads, dumps
from kiutils.board import Board
from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Position
from kiutils.items.fpitems import FpText

# board = Board.from_file('/my/fancy/project/title.kicad_pcb')

def readfile(fn):
    with open(fn) as f:
        return f.read()

def reference_gi(x):
    # Change identifier to C105
    for item in x.graphicItems:
        if isinstance(item, FpText):
            if item.type == 'reference':
                return item

def get_ref(fp):
    return fp.properties['Reference']


def allunique(l):
    return len(l) == len(set(l))

def fp_from_ref(board, ref):
    for fp in board.footprints:
        if get_ref(fp) == ref:
            return fp
    return None

def main():
    sch_fn = "illuminator.kicad_sch"
    pcb_fn = "illuminator.kicad_pcb"
    # s = readfile(pcb_fn)
    # sexp = loads(s)
    # print(sexp)

    # sch = skip.Schematic(sch_fn)
    # pcb = skip.PCB(pcb_fn)

    pcb = Board.from_file(pcb_fn)


if __name__ == "__main__":
    main()
