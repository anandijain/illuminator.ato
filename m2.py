#!/usr/bin/env python3
import os, re, shutil
from kiutils.board import Board
from kiutils.items.common import Position

# ---------------- config ----------------
PCB_FN           = "layouts/default/default.kicad_pcb"
ROWS, COLS       = 6, 6
GRID_SPACING_MM  = 100/5       # 20 mm
R_TO_LED_DX_MM   = 3.61
LED_ROT_DEG      = 180
RES_START, RES_END = 4, 39     # R4..R39

# reference text targets and style
LED_OFF          = (0.0, +1.905)
RES_OFF          = (0.0, -1.905)
TXT_W, TXT_H     = 1.0, 1.0
TXT_T            = 0.15

# -------------- helpers --------------
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
    return fp.properties.get("Reference", "").strip()

def fp_by_ref(board, ref):
    for fp in board.footprints:
        if get_ref(fp) == ref:
            return fp
    return None

# --- low-level s-expr surgery inside one (footprint ...) block ---
def paren_block_end(s, start):
    """Return index just past the matching ')' for block starting at start."""
    depth = 0
    i = start
    while i < len(s):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i

def find_footprint_block(s, ref):
    """Find the (footprint ...) block that contains (property "Reference" "<ref>")."""
    pos = 0
    while True:
        p = s.find(f'(property "Reference" "{ref}"', pos)
        if p == -1:
            return None, None, None
        # walk backwards to nearest "(footprint"
        start = s.rfind("(footprint", 0, p)
        if start == -1:
            return None, None, None
        end = paren_block_end(s, start)
        block = s[start:end]
        # ensure this property is inside this footprint (it should be)
        if block.find(f'(property "Reference" "{ref}"') != -1:
            return start, end, block
        pos = p + 1

def patch_reference_property_in_block(block, ref, target_at, keep_angle=True):
    """
    Ensure the property block has (at ...), (layer "F.SilkS"),
    and (effects (font (size w h) (thickness t))).
    Insert missing fields; overwrite if present.
    """
    # locate property block
    p = block.find(f'(property "Reference" "{ref}"')
    if p == -1:
        return block
    # find end of that property sub-block
    # property can be "flat" (no children) or have nested items; handle both
    # If the very next char after closing quote is ')', it's flat: (property "Reference" "R4")
    # In both cases, we’ll rebuild the block to a canonical, expanded form.
    # Preserve angle if present elsewhere in ref rendering? We’ll default to 0 if unknown.
    # Try to sniff an existing angle from any (at ...) found in the property, else 0.
    qend = block.find('"', p + len(f'(property "Reference" "'))  # end of ref string
    qend = block.find('"', qend + 1)
    sub_end = p
    # if there is a '(' following, parse depth; else the sub-block ends at first ')'
    # Simplify: compute the end by matching parens from p
    sub_end = p + block[p:].find(')') + 1
    # But if nested children exist, the first ')' might be within them. Use full matcher:
    # (safe even for flat form)
    sub_end = p + paren_block_end(block[p:], 0)

    prop = block[p:sub_end]

    # try to preserve existing angle if present
    m_at = re.search(r'\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+([-0-9.]+))?\)', prop)
    ang = m_at.group(3) if (keep_angle and m_at and m_at.group(3) is not None) else "0"

    tx, ty = target_at
    new_prop = (
        f'(property "Reference" "{ref}"\n'
        f'  (at {tx} {ty} {ang})\n'
        f'  (layer "F.SilkS")\n'
        f'  (effects (font (size {TXT_W} {TXT_H}) (thickness {TXT_T})))\n'
        f')'
    )

    return block[:p] + new_prop + block[sub_end:]

def remove_ref_like_fp_texts_in_block(block, ref):
    """
    Delete any (fp_text ...) whose quoted text equals "%R", "${REFERENCE}", or the resolved ref.
    """
    kill_set = { "%R", "${REFERENCE}", ref }
    out = []
    i = 0
    while True:
        j = block.find("(fp_text", i)
        if j == -1:
            out.append(block[i:])
            break
        # copy chunk before this fp_text
        out.append(block[i:j])
        k = j + paren_block_end(block[j:], 0)  # end of this fp_text block
        fp = block[j:k]
        # read first quoted string
        m = re.search(r'^\(fp_text\s+\w+\s+"([^"]+)"', fp)
        text = m.group(1) if m else None
        if text in kill_set:
            # drop it
            pass
        else:
            out.append(fp)
        i = k
    return "".join(out)

def set_ref_size_pos_and_dedup_raw(path, refs_to_offsets):
    """
    For each footprint (by ref), rewrite its block:
      - remove any ref-like fp_text clones
      - expand/insert property "Reference" with at/layer/effects
    """
    s = open(path, "r", encoding="utf-8").read()
    changed = 0

    for ref, target_off in refs_to_offsets.items():
        loc = find_footprint_block(s, ref)
        if loc == (None, None, None):
            continue
        start, end, block = loc

        block = remove_ref_like_fp_texts_in_block(block, ref)
        block = patch_reference_property_in_block(block, ref, target_off)

        s = s[:start] + block + s[end:]
        changed += 1

    open(path, "w", encoding="utf-8").write(s)
    return changed

# -------------- placement with kiutils --------------
def place_grid(board):
    for i in range(ROWS):
        for j in range(COLS):
            idx = i*COLS + j
            r_ref = f"R{idx + RES_START}"
            l_ref = f"LED{idx + 1}"

            r_fp = fp_by_ref(board, r_ref)
            l_fp = fp_by_ref(board, l_ref)
            if r_fp is None: raise RuntimeError(f"Missing {r_ref}")
            if l_fp is None: raise RuntimeError(f"Missing {l_ref}")

            x = j*GRID_SPACING_MM
            y = i*GRID_SPACING_MM
            r_fp.position = Position(X=x, Y=y, angle=0)
            l_fp.position = Position(X=x + R_TO_LED_DX_MM, Y=y, angle=LED_ROT_DEG)

# ---------------- main ----------------
def main():
    if not os.path.exists(PCB_FN):
        raise FileNotFoundError(PCB_FN)
    print(f"[info] loading: {PCB_FN}")
    pcb = Board.from_file(PCB_FN)

    # Place parts
    place_grid(pcb)
    print("[ok] grid placed")

    # Save once via kiutils
    bak = backup(PCB_FN)
    pcb.to_file(PCB_FN)
    print(f"[ok] wrote board (backup: {bak})")

    # Build map of refs -> desired offsets
    refs_to_offsets = {}
    for fp in pcb.footprints:
        ref = get_ref(fp)
        if not ref:
            continue
        if ref.startswith("LED"):
            refs_to_offsets[ref] = LED_OFF
        elif ref.startswith("R"):
            try:
                n = int(ref[1:])
                if RES_START <= n <= RES_END:
                    refs_to_offsets[ref] = RES_OFF
            except ValueError:
                pass

    # Do raw s-expr dedup + property expansion for each footprint
    changed = set_ref_size_pos_and_dedup_raw(PCB_FN, refs_to_offsets)
    print(f"[ok] updated ref rendering on {changed} footprint(s)")

    # Ato boolean token compatibility
    sanitize_booleans_for_ato(PCB_FN)
    print("[ok] boolean tokens sanitized")

if __name__ == "__main__":
    main()
