#!/usr/bin/env python3
import os, re, shutil
from kiutils.board import Board
from kiutils.items.common import Position
from kiutils.items.fpitems import FpText

# --- config ---
PCB_FN          = "layouts/default/default.kicad_pcb"
ROWS, COLS      = 6, 6
GRID_SPACING_MM = 100/5        # 20 mm
R_TO_LED_DX_MM  = 3.61
LED_ROT_DEG     = 180
TXT_W, TXT_H    = 1.0, 1.0
TXT_T           = 0.15
LED_OFF         = (0.0, +1.905)
RES_OFF         = (0.0, -1.905)
RES_START, RES_END = 4, 39     # R4..R39

# --- helpers ---
def backup(path):
    bak = path + ".bak"
    shutil.copy2(path, bak)
    return bak

def sanitize_booleans_for_ato(path):
    s = open(path, "r", encoding="utf-8").read()
    s = re.sub(r'(?<=[\s(])true(?=[\s)])', 'yes', s)
    s = re.sub(r'(?<=[\s(])false(?=[\s)])', 'no', s)
    open(path, "w", encoding="utf-8").write(s)

def get_ref(fp):
    return fp.properties.get("Reference", "")

def fp_by_ref(board, ref):
    for fp in board.footprints:
        if get_ref(fp) == ref:
            return fp
    return None

def place_grid(board):
    for i in range(ROWS):
        for j in range(COLS):
            idx = i*COLS + j
            r_ref = f"R{idx + RES_START}"
            l_ref = f"LED{idx + 1}"
            r_fp = fp_by_ref(board, r_ref);  l_fp = fp_by_ref(board, l_ref)
            if r_fp is None or l_fp is None:
                raise RuntimeError(f"Missing {r_ref if r_fp is None else l_ref}")
            x = j*GRID_SPACING_MM; y = i*GRID_SPACING_MM
            r_fp.position = Position(X=x, Y=y, angle=0)
            l_fp.position = Position(X=x + R_TO_LED_DX_MM, Y=y, angle=LED_ROT_DEG)

def ref_text_candidates(fp):
    """Return FpText items that act as the visible reference: %R, ${REFERENCE}, or resolved ref."""
    ref = get_ref(fp).strip()
    cands = []
    for gi in getattr(fp, "graphicItems", []):
        if isinstance(gi, FpText):
            t = gi.text.strip()
            if t in ("%R", "${REFERENCE}", ref):
                cands.append(gi)
    return cands

def size_and_place_reftexts(board):
    sized = moved = 0
    for fp in board.footprints:
        ref = get_ref(fp)
        # choose target offset
        target = None
        if ref.startswith("LED"):
            target = LED_OFF
        elif ref.startswith("R"):
            try:
                n = int(ref[1:])
                if RES_START <= n <= RES_END:
                    target = RES_OFF
            except ValueError:
                pass

        for t in ref_text_candidates(fp):
            # set size/thickness
            if getattr(t, "effects", None) and getattr(t.effects, "font", None):
                font = t.effects.font
                # size
                try: font.size = Position(X=TXT_W, Y=TXT_H)
                except Exception:
                    if hasattr(font, "size"): font.size = [TXT_W, TXT_H]
                    if hasattr(font, "sizeX"): font.sizeX = TXT_W
                    if hasattr(font, "sizeY"): font.sizeY = TXT_H
                # stroke
                if hasattr(font, "thickness"): font.thickness = TXT_T
                elif hasattr(t.effects, "thickness"): t.effects.thickness = TXT_T
                sized += 1
            # move if we know where
            if target is not None:
                tx, ty = target
                if hasattr(t, "at") and isinstance(t.at, Position):
                    ang = t.at.angle or 0
                    t.at = Position(X=tx, Y=ty, angle=ang)
                    moved += 1
                elif hasattr(t, "position") and isinstance(t.position, Position):
                    ang = t.position.angle or 0
                    t.position = Position(X=tx, Y=ty, angle=ang)
                    moved += 1
    return sized, moved

# --- main ---
def main():
    if not os.path.exists(PCB_FN):
        raise FileNotFoundError(PCB_FN)

    print(f"[info] loading: {PCB_FN}")
    pcb = Board.from_file(PCB_FN)

    place_grid(pcb)
    print("[ok] grid placed")

    sized, moved = size_and_place_reftexts(pcb)
    print(f"[ok] sized {sized} ref-like text(s); moved {moved}")

    bak = backup(PCB_FN)
    pcb.to_file(PCB_FN)
    sanitize_booleans_for_ato(PCB_FN)
    print(f"[ok] saved (backup: {bak})")

if __name__ == "__main__":
    main()
