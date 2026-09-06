#!/usr/bin/env python3
"""
Post-process a Markdown article so every LaTeX equation becomes something
Medium actually understands:

  - Simple INLINE equations ($...$ or \\(...\\)) are converted to plain
    Unicode text (Greek letters, symbols, sub/superscripts where Unicode
    has the glyphs, italics/bold via Markdown *_*/**_**, combining
    diacritics for hat/bar/tilde/vec).
  - DISPLAY equations ($$...$$ or \\[...\\]) are always rendered as PNG
    images and replaced with a Markdown image link -- Medium has no
    display-math support.
  - Inline equations too complex to express in Unicode (fractions with
    non-trivial parts, nested sub/superscripts, sums/integrals with
    limits, etc.) also fall back to a rendered PNG image link, since
    that's the only other thing Medium understands. Note this means the
    equation becomes a standalone block and breaks the sentence it sat
    in -- the manifest flags every equation this happens to, so you can
    go reword that sentence if you don't like the break.

USAGE
    python3 convert_equations.py ../_posts/article.md
    python3 convert_equations.py ../_posts/article.md \\
        --output ../medium/article.md \\
        --outdir ../assets/posts/<post-slug>/eqn

OUTPUT
    - <output>.md               the rewritten article, ready to paste into Medium
    - <outdir>/eqNN.png         one PNG per equation that needed an image
    - <outdir>/manifest.txt     what happened to every equation found

    Image links in the output .md are relative to that output file's location,
    not the shell working directory.

FONT (for rendered images)
    matplotlib's "cm" (Computer Modern) mathtext set -- the classic TeX
    typeface MathJax's default rendering is also based on.

SIZE (for rendered images)
    --size sets the apparent height, in CSS pixels, of every rendered
    equation image once pasted into Medium. Since Medium always displays
    a pasted image as its own block (never truly inline), all rendered
    equations use one consistent size rather than a smaller "inline"
    size -- default 26px, a bit larger than Medium's 21px body text,
    since equations standing alone on their own line read better a
    touch bigger. --quality controls anti-aliasing oversampling.
"""
import argparse
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# ---------------------------------------------------------------------------
# Image rendering (unchanged approach: oversample then downsample for AA)
# ---------------------------------------------------------------------------

CSS_DPI = 96.0  # 1 CSS pixel = 1/96 inch, the standard browser reference.

matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["mathtext.rm"] = "serif"


def render_equation_image(latex, outpath, target_px, quality, color="black"):
    fontsize_pt = target_px * 72.0 / CSS_DPI
    render_dpi = CSS_DPI * quality

    # Matplotlib mathtext cannot parse raw newlines inside $...$; they
    # draw a filled error box instead of raising. Collapse whitespace.
    cleaned = " ".join(latex.split())

    fig = plt.figure()
    text_obj = fig.text(0, 0, f"${cleaned}$", fontsize=fontsize_pt, color=color)
    fig.canvas.draw()

    bbox = text_obj.get_window_extent()
    pad_px = 6
    width_in = (bbox.width + 2 * pad_px) / fig.dpi
    height_in = (bbox.height + 2 * pad_px) / fig.dpi
    fig.set_size_inches(width_in, height_in)
    text_obj.set_position((pad_px / (bbox.width + 2 * pad_px),
                            pad_px / (bbox.height + 2 * pad_px)))

    tmp_path = outpath + ".tmp.png"
    fig.savefig(tmp_path, dpi=render_dpi, transparent=True,
                bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    with Image.open(tmp_path) as im:
        target_w = max(1, round(im.width / quality))
        target_h = max(1, round(im.height / quality))
        im.resize((target_w, target_h), Image.LANCZOS).save(outpath)
    os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Equation extraction from Markdown
# ---------------------------------------------------------------------------

EQUATION_PATTERN = re.compile(
    r"(?<!\\)\$\$(?P<display1>.+?)(?<!\\)\$\$"
    r"|\\\[(?P<display2>.+?)\\\]"
    r"|\\\((?P<inline1>.+?)\\\)"
    r"|(?<!\\)(?<!\$)\$(?!\$)(?P<inline2>[^\n$]+?)(?<!\\)\$(?!\$)",
    re.DOTALL,
)


def strip_code(text):
    """Blank out fenced code blocks / inline code spans (preserving
    length & offsets) so their literal $ signs are never mistaken for
    math delimiters."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"```.*?```", blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", blank, text)
    return text


def find_equations(md_text):
    """Returns a list of (start, end, latex, is_display) in the ORIGINAL
    text's coordinates (strip_code preserves offsets)."""
    cleaned = strip_code(md_text)
    out = []
    for m in EQUATION_PATTERN.finditer(cleaned):
        if m.group("display1") is not None:
            latex, is_display = m.group("display1"), True
        elif m.group("display2") is not None:
            latex, is_display = m.group("display2"), True
        elif m.group("inline1") is not None:
            latex, is_display = m.group("inline1"), False
        else:
            latex, is_display = m.group("inline2"), False
        latex = latex.strip()
        if latex:
            out.append((m.start(), m.end(), latex, is_display))
    return out


# ---------------------------------------------------------------------------
# LaTeX -> Unicode/Markdown conversion for simple inline equations
# ---------------------------------------------------------------------------

GREEK = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "epsilon": "\u03b5", "varepsilon": "\u03b5", "zeta": "\u03b6", "eta": "\u03b7",
    "theta": "\u03b8", "vartheta": "\u03d1", "iota": "\u03b9", "kappa": "\u03ba",
    "lambda": "\u03bb", "mu": "\u03bc", "nu": "\u03bd", "xi": "\u03be",
    "omicron": "\u03bf", "pi": "\u03c0", "varpi": "\u03d6", "rho": "\u03c1",
    "varrho": "\u03f1", "sigma": "\u03c3", "varsigma": "\u03c2", "tau": "\u03c4",
    "upsilon": "\u03c5", "phi": "\u03c6", "varphi": "\u03d5", "chi": "\u03c7",
    "psi": "\u03c8", "omega": "\u03c9",
    "Alpha": "\u0391", "Beta": "\u0392", "Gamma": "\u0393", "Delta": "\u0394",
    "Epsilon": "\u0395", "Zeta": "\u0396", "Eta": "\u0397", "Theta": "\u0398",
    "Iota": "\u0399", "Kappa": "\u039a", "Lambda": "\u039b", "Mu": "\u039c",
    "Nu": "\u039d", "Xi": "\u039e", "Omicron": "\u039f", "Pi": "\u03a0",
    "Rho": "\u03a1", "Sigma": "\u03a3", "Tau": "\u03a4", "Upsilon": "\u03a5",
    "Phi": "\u03a6", "Chi": "\u03a7", "Psi": "\u03a8", "Omega": "\u03a9",
}

SYMBOLS = {
    "pm": "\u00b1", "mp": "\u2213", "times": "\u00d7", "div": "\u00f7",
    "cdot": "\u00b7", "ast": "\u2217", "star": "\u22c6", "circ": "\u2218",
    "bullet": "\u2022", "leq": "\u2264", "le": "\u2264", "geq": "\u2265",
    "ge": "\u2265", "neq": "\u2260", "ne": "\u2260", "approx": "\u2248",
    "equiv": "\u2261", "sim": "\u223c", "simeq": "\u2243", "cong": "\u2245",
    "propto": "\u221d", "infty": "\u221e", "partial": "\u2202",
    "nabla": "\u2207", "forall": "\u2200", "exists": "\u2203",
    "nexists": "\u2204", "in": "\u2208", "notin": "\u2209", "ni": "\u220b",
    "subset": "\u2282", "supset": "\u2283", "subseteq": "\u2286",
    "supseteq": "\u2287", "cup": "\u222a", "cap": "\u2229",
    "setminus": "\u2216", "emptyset": "\u2205", "varnothing": "\u2205",
    "wedge": "\u2227", "vee": "\u2228", "neg": "\u00ac", "oplus": "\u2295",
    "otimes": "\u2297", "perp": "\u22a5", "parallel": "\u2225",
    "angle": "\u2220", "rightarrow": "\u2192", "to": "\u2192",
    "leftarrow": "\u2190", "leftrightarrow": "\u2194", "Rightarrow": "\u21d2",
    "Leftarrow": "\u21d0", "Leftrightarrow": "\u21d4", "mapsto": "\u21a6",
    "longrightarrow": "\u27f6", "longleftarrow": "\u27f5",
    "sum": "\u2211", "prod": "\u220f", "int": "\u222b", "oint": "\u222e",
    "ldots": "\u2026", "dots": "\u2026", "cdots": "\u22ef", "vdots": "\u22ee",
    "ddots": "\u22f1", "degree": "\u00b0", "hbar": "\u0127", "ell": "\u2113",
    "Re": "\u211c", "Im": "\u2111", "aleph": "\u2135", "wp": "\u2118",
    "top": "\u22a4", "bot": "\u22a5", "langle": "\u27e8", "rangle": "\u27e9",
    "prime": "\u2032",
}

FUNCTION_NAMES = {
    "sin", "cos", "tan", "csc", "sec", "cot", "sinh", "cosh", "tanh",
    "log", "ln", "exp", "min", "max", "arg", "det", "dim", "gcd", "lim",
    "sup", "inf", "mod",
}

SUP_MAP = {c: u for c, u in zip(
    "0123456789+-=()niabcdefghjklmoprstuvwxyzT",
    "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079"
    "\u207a\u207b\u207c\u207d\u207e\u207f\u2071"
    "\u1d43\u1d47\u1d9c\u1d48\u1d49\u1da0\u1d4d\u02b0\u02b2\u1d4f\u02e1\u1d50"
    "\u1d52\u1d56\u02b3\u02e2\u1d57\u1d58\u1d5b\u02b7\u02e3\u02b8\u1dbb\u1d40"
)}

SUB_MAP = {c: u for c, u in zip(
    "0123456789+-=()aehijklmnoprstuvx",
    "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089"
    "\u208a\u208b\u208c\u208d\u208e"
    "\u2090\u2091\u2095\u1d62\u2c7c\u2096\u2097\u2098\u2099\u2092\u209a"
    "\u1d63\u209b\u209c\u1d64\u1d65\u2093"
)}

FRACTIONS = {
    ("1", "2"): "\u00bd", ("1", "3"): "\u2153", ("2", "3"): "\u2154",
    ("1", "4"): "\u00bc", ("3", "4"): "\u00be", ("1", "5"): "\u2155",
    ("2", "5"): "\u2156", ("3", "5"): "\u2157", ("4", "5"): "\u2158",
    ("1", "6"): "\u2159", ("5", "6"): "\u215a", ("1", "8"): "\u215b",
    ("3", "8"): "\u215c", ("5", "8"): "\u215d", ("7", "8"): "\u215e",
}

COMBINING = {
    "hat": "\u0302", "bar": "\u0304", "tilde": "\u0303",
    "vec": "\u20d7", "dot": "\u0307", "ddot": "\u0308",
}


class NotSimple(Exception):
    """Raised internally when an equation can't be expressed in Unicode."""
    pass


def _read_group(s, i):
    """At s[i], read either a {...} balanced group or a single char.
    Returns (content, next_index)."""
    if i < len(s) and s[i] == "{":
        depth = 1
        j = i + 1
        while j < len(s) and depth > 0:
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
            j += 1
        return s[i + 1:j - 1], j
    elif i < len(s):
        return s[i], i + 1
    else:
        raise NotSimple("unexpected end of equation")


def _script_arg_to_plain(s):
    """Convert a sub/superscript argument to plain Unicode text (Greek +
    symbols resolved, no italics markup). Raises NotSimple if it uses
    anything we can't resolve to plain characters."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            j = i + 1
            while j < len(s) and s[j].isalpha():
                j += 1
            cmd = s[i + 1:j]
            if not cmd:
                raise NotSimple(f"unsupported escape in script: {s[i:i+2]!r}")
            i = j
            if cmd in GREEK:
                out.append(GREEK[cmd])
            elif cmd in SYMBOLS:
                out.append(SYMBOLS[cmd])
            else:
                raise NotSimple(f"unsupported command in script: \\{cmd}")
        elif c == "{":
            inner, i = _read_group(s, i)
            out.append(_script_arg_to_plain(inner))
        elif c == "}":
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _to_super_or_sub(s, mapping, kind):
    plain = _script_arg_to_plain(s)
    if not plain:
        raise NotSimple(f"empty {kind}")
    if not all(ch in mapping for ch in plain):
        raise NotSimple(f"{kind} has no Unicode form: {plain!r}")
    return "".join(mapping[ch] for ch in plain)


def _convert(s, italic=True):
    """Convert a LaTeX snippet to Markdown-ready Unicode text. Raises
    NotSimple if any part can't be faithfully represented. `italic`
    controls whether bare letter runs get wrapped in Markdown italics
    (the normal math convention) -- turned off inside \\mathrm/\\text
    and \\mathbf (upright bold), since those explicitly mean "not
    italic" in LaTeX regardless of the surrounding context."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]

        if c == "\\":
            j = i + 1
            if j < n and s[j].isalpha():
                k = j
                while k < n and s[k].isalpha():
                    k += 1
                cmd = s[j:k]
                i = k

                if cmd in GREEK:
                    out.append(GREEK[cmd])
                elif cmd in SYMBOLS:
                    out.append(SYMBOLS[cmd])
                elif cmd in FUNCTION_NAMES:
                    out.append(cmd)
                elif cmd in ("left", "right"):
                    pass  # sizing hint only; the following delimiter char follows naturally
                elif cmd in ("quad", "qquad"):
                    out.append("  ")
                elif cmd == "frac":
                    num_raw, i = _read_group(s, i)
                    while i < n and s[i] == " ":
                        i += 1
                    den_raw, i = _read_group(s, i)
                    key = (num_raw.strip(), den_raw.strip())
                    if key in FRACTIONS:
                        out.append(FRACTIONS[key])
                    else:
                        num_c = _convert(num_raw, italic=italic)
                        den_c = _convert(den_raw, italic=italic)
                        if len(num_c) > 1 or len(den_c) > 1:
                            out.append(f"({num_c}/{den_c})")
                        else:
                            out.append(f"{num_c}/{den_c}")
                elif cmd == "sqrt":
                    if i < n and s[i] == "[":
                        raise NotSimple("nth root not supported")
                    arg_raw, i = _read_group(s, i)
                    arg_c = _convert(arg_raw, italic=italic)
                    if len(arg_c) > 4:
                        raise NotSimple("sqrt argument too complex")
                    out.append("\u221a" + arg_c)
                elif cmd in ("mathbf", "boldsymbol", "bm"):
                    arg_raw, i = _read_group(s, i)
                    out.append(f"**{_convert(arg_raw, italic=False)}**")
                elif cmd in ("mathrm", "text", "operatorname"):
                    arg_raw, i = _read_group(s, i)
                    out.append(_convert(arg_raw, italic=False))
                elif cmd == "mathit":
                    arg_raw, i = _read_group(s, i)
                    out.append(_convert(arg_raw, italic=True))
                elif cmd in COMBINING:
                    arg_raw, i = _read_group(s, i)
                    if len(arg_raw) != 1:
                        raise NotSimple(f"\\{cmd} on multi-char argument")
                    out.append(arg_raw + COMBINING[cmd])
                else:
                    raise NotSimple(f"unsupported command: \\{cmd}")
            else:
                if j >= n:
                    raise NotSimple("trailing backslash")
                esc = s[j]
                i = j + 1
                if esc in "%&_{}$#~^":
                    out.append(esc)
                elif esc in ",;:! ":
                    out.append(" ")
                else:
                    raise NotSimple(f"unsupported escape: \\{esc}")
            continue

        if c == "^":
            arg_raw, i = _read_group(s, i + 1)
            out.append(_to_super_or_sub(arg_raw, SUP_MAP, "superscript"))
            continue

        if c == "_":
            arg_raw, i = _read_group(s, i + 1)
            out.append(_to_super_or_sub(arg_raw, SUB_MAP, "subscript"))
            continue

        if c == "{":
            inner, i = _read_group(s, i)
            out.append(_convert(inner, italic=italic))
            continue

        if c == "}":
            i += 1
            continue

        if c.isalpha():
            j = i + 1
            while j < n and s[j].isalpha():
                j += 1
            run = s[i:j]
            i = j
            out.append(f"*{run}*" if italic else run)
            continue

        if c.isdigit():
            j = i + 1
            while j < n and s[j].isdigit():
                j += 1
            out.append(s[i:j])
            i = j
            continue

        if c in "&":
            raise NotSimple("alignment character (matrix/align environment)")

        out.append(c)
        i += 1

    return "".join(out)


def try_unicode(latex):
    """Returns the Unicode/Markdown text if `latex` is simple enough,
    else None."""
    if "\\begin" in latex or "\\end" in latex or "\\\\" in latex:
        return None
    try:
        return _convert(latex)
    except NotSimple:
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def markdown_link_path(image_path, output_md_path):
    """Return a Markdown-friendly path from the output .md file to an image."""
    output_dir = os.path.dirname(os.path.abspath(output_md_path)) or os.getcwd()
    rel = os.path.relpath(os.path.abspath(image_path), output_dir)
    return rel.replace("\\", "/")


def main():
    ap = argparse.ArgumentParser(
        description="Rewrite a Markdown article so equations become Unicode text or image links")
    ap.add_argument("input_file", help="Markdown (.md) file containing LaTeX equations")
    ap.add_argument("--output", default=None,
                     help="Output markdown file (default: <input>.medium.md)")
    ap.add_argument("--outdir", default="equations_out", help="Directory for rendered PNGs")
    ap.add_argument("--size", type=float, default=26.0,
                     help="Apparent size in CSS pixels for rendered equation images "
                          "(default 26, a bit above Medium's 21px body text)")
    ap.add_argument("--quality", type=int, default=4,
                     help="Internal oversampling factor for anti-aliasing (default 4)")
    args = ap.parse_args()

    if args.output is None:
        stem, _ = os.path.splitext(args.input_file)
        args.output = f"{stem}.medium.md"

    with open(args.input_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    equations = find_equations(md_text)
    if not equations:
        print("No equations found. Looked for $$...$$, \\[...\\], $...$, and \\(...\\).")
        return

    os.makedirs(args.outdir, exist_ok=True)

    pieces = []
    cursor = 0
    manifest_rows = []
    n_unicode = 0
    n_image = 0
    n_broke_flow = 0
    img_counter = 0

    for start, end, latex, is_display in equations:
        pieces.append(md_text[cursor:start])
        cursor = end

        unicode_text = None if is_display else try_unicode(latex)

        if unicode_text is not None:
            pieces.append(unicode_text)
            n_unicode += 1
            manifest_rows.append(f"unicode\t{latex}\t->\t{unicode_text}")
        else:
            img_counter += 1
            name = f"eq{img_counter:02d}.png"
            outpath = os.path.join(args.outdir, name)
            try:
                render_equation_image(latex, outpath, target_px=args.size, quality=args.quality)
                rel_path = markdown_link_path(outpath, args.output)
                pieces.append(f"\n\n![{latex}]({rel_path})\n\n")
                n_image += 1
                flow_note = ""
                if not is_display:
                    n_broke_flow += 1
                    flow_note = "  [was inline -- now breaks paragraph flow]"
                manifest_rows.append(f"image\t{latex}\t->\t{rel_path}{flow_note}")
            except Exception as e:
                pieces.append(f"[EQUATION RENDER FAILED: {latex}]")
                manifest_rows.append(f"FAILED\t{latex}\t->\t{e}")

    pieces.append(md_text[cursor:])
    new_md = "".join(pieces)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(new_md)

    manifest_path = os.path.join(args.outdir, "manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_rows) + "\n")

    print(f"{len(equations)} equations found: {n_unicode} -> Unicode text, {n_image} -> images")
    if n_broke_flow:
        print(f"NOTE: {n_broke_flow} of those images came from inline equations that were too "
              f"complex for Unicode -- they'll now break their sentence into its own block. "
              f"See {manifest_path} (flagged) to find and reword them if you'd rather not.")
    print(f"\nRewritten article: {args.output}")
    print(f"Images + manifest: {args.outdir}/")


if __name__ == "__main__":
    main()
