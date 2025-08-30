# import skip # broken on kicad >=8
from sexpdata import loads, dumps
from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Position
from kiutils.items.fpitems import FpText
import re

def set_reftext_positions(pcb, x_led=0.0, y_led=1.905, x_r=0.0, y_r=-1.905):
    def set_at(gi, x, y):
        # Keep existing angle, just change local offset
        if hasattr(gi, 'at') and isinstance(gi.at, Position):
            ang = gi.at.angle or 0
            gi.at = Position(X=float(x), Y=float(y), angle=ang)
        elif hasattr(gi, 'position') and isinstance(gi.position, Position):
            ang = gi.position.angle or 0
            gi.position = Position(X=float(x), Y=float(y), angle=ang)

    for fp in pcb.footprints:
        ref = fp.properties.get('Reference', '')
        for gi in fp.graphicItems:
            if not isinstance(gi, FpText) or gi.type != 'reference':
                continue

            if ref.startswith('LED'):
                set_at(gi, x_led, y_led)
            elif ref.startswith('R'):
                # R4..R39 only
                try:
                    n = int(ref[1:])
                except ValueError:
                    continue
                if 4 <= n <= 39:
                    set_at(gi, x_r, y_r)

# --- use it ---
def main():
    pcb_fn = "layouts/default/default.kicad_pcb"
    pcb = Board.from_file(pcb_fn)

    # ... your placement code for R/LED footprints ...

    # size pass (optional, from earlier)
    # set_all_fptext_sizes(pcb, w=1.0, h=1.0, thickness=0.15)

    # position pass (this request)
    set_reftext_positions(pcb, x_led=0.0, y_led=1.905, x_r=0.0, y_r=-1.905)

    pcb.to_file(pcb_fn)
    # sanitize_booleans_for_ato(pcb_fn)  # if Ato needs yes/no

if __name__ == "__main__":
    main()

def set_all_fptext_sizes(pcb, w=1.0, h=1.0, thickness=None):
    """
    Make all footprint texts (reference/value/user) the same size.
    thickness=None -> leave existing stroke thickness unchanged.
    """
    for fp in pcb.footprints:
        for gi in fp.graphicItems:
            if isinstance(gi, FpText) and getattr(gi, "effects", None):
                font = getattr(gi.effects, "font", None)
                if not font:
                    continue
                # Most kiutils versions store size as a Position
                try:
                    font.size = Position(X=float(w), Y=float(h))
                except Exception:
                    # Fallbacks for other schemas
                    if hasattr(font, "size"):
                        try:
                            font.size = [float(w), float(h)]
                        except Exception:
                            pass
                    if hasattr(font, "sizeX"): font.sizeX = float(w)
                    if hasattr(font, "sizeY"): font.sizeY = float(h)
                if thickness is not None:
                    # Typical KiCad stroke for 1mm text is ~0.12–0.15 mm
                    if hasattr(font, "thickness"):
                        font.thickness = float(thickness)
                    elif hasattr(gi.effects, "thickness"):
                        gi.effects.thickness = float(thickness)

def clean_duplicate_reftexts(fp):
    ref = fp.properties.get('Reference')
    to_remove = []
    for gi in fp.graphicItems:
        if isinstance(gi, FpText):
            # Case 1: user text placed as ${REFERENCE} in lib → becomes "R4" on board
            is_refclone = (
                gi.type == 'user' and
                gi.text.strip() in (ref, '${REFERENCE}')
            )
            # If it’s on silkscreen, we don’t want it
            if is_refclone and gi.layer in ('F.SilkS', 'B.SilkS'):
                to_remove.append(gi)

    for gi in to_remove:
        fp.graphicItems.remove(gi)

def sanitize_booleans_for_ato(path):
    s = readfile(path)
    # Replace ONLY whole boolean tokens (not inside strings)
    s = re.sub(r'(?<=\s)true(?=(\s|\)))', 'yes', s)
    s = re.sub(r'(?<=\s)false(?=(\s|\)))', 'no', s)
    with open(path, 'w') as f:
        f.write(s)

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

def mapl(f, xs):
    return list(map(f, xs))

""" 
tallys objects by equality and then returns the pairs in descending count order
"""
def tally(xs):
    counts = {}
    for x in xs:
        if x not in counts:
            counts[x] = 0
        counts[x] += 1
    items = list(counts.items())
    items.sort(key=lambda kv: kv[1], reverse=True)
    return items


def main():
    pcb_fn = "layouts/default/default.kicad_pcb"
    pcb = Board.from_file(pcb_fn)

    rled_x_delta = 3.61 # mm distance between the resistor and its LED
    start_r_ref = 'R4' # shifted by 3 
    start_led_ref = 'LED1'
    spacing = 100/5
    for i in range(6):
        for j in range(6):
            idx = i*6 + j
            # idx=0
            r_ref = f'R{idx+1+3}'
            led_ref = f'LED{idx+1}'
            r_fp = fp_from_ref(pcb, r_ref)
            led_fp = fp_from_ref(pcb, led_ref)
            if led_fp is None:
                print(f"Could not find {led_ref}")
                raise Exception('I know Python!')
            if r_fp is None:
                print(f"Could not find {r_ref}")
                raise Exception('I know Python!')
            # gis = led_fp.graphicItems
            
            r_fp.position = Position(X=j*spacing, Y=i*spacing,angle=0)
            led_fp.position = Position(X=j*spacing + rled_x_delta, Y=i*spacing,angle=180)

    # filter(lambda x: type(x) == FpText and x.layer == "F.SilkS", gis)
    # why is this like duplicating the silkscreen footprint text???
    for fp in pcb.footprints:
        clean_duplicate_reftexts(fp)
    
    set_all_fptext_sizes(pcb, w=1.0, h=1.0, thickness=None)
    set_reftext_positions(pcb, x_led=0.0, y_led=1.905, x_r=0.0, y_r=-1.905)
    pcb.to_file(pcb_fn)
    sanitize_booleans_for_ato(pcb_fn)

if __name__ == "__main__":
    main()
