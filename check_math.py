#!/usr/bin/env python3
"""Flag math written outside $...$ / $$...$$ in a digest note.

Usage: python3 -I check_math.py <note.md>
Prints each offending line and exits 1; prints nothing and exits 0 when clean.
"""
import re
import sys

# Display math, inline math, fenced code, code spans and image embeds are exempt.
ALLOWED = re.compile(r"\$\$.*?\$\$|```.*?```|`[^`\n]*`|!\[[^\]\n]*\]\([^)\n]*\)|\$[^$\n]+\$", re.S)
BARE = re.compile(
    r"\\[A-Za-z]+"                       # TeX command
    r"|[A-Za-z0-9)\]}]['′]*[\^_][{A-Za-z0-9]"  # sub/superscript
    r"|[\u0391-\u03A9\u03B1-\u03C9\u2113]"  # Greek letters, ell
    r"|[∑∏∫∈∉⊂⊆≤≥≈≠∞∇∂∼]"                 # math operators
    r"|[\u0300-\u036F]"                  # combining accents (Q-hat, a-bar)
)
SPANS = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$")


def problems(text):
    out = []
    masked = ALLOWED.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)
    for n, (raw, line) in enumerate(zip(text.splitlines(), masked.splitlines()), 1):
        why = []
        if BARE.search(line):
            why.append("math outside $")
        if "$" in line:
            why.append("unmatched $")
        # renderers skip `$ x $`: inline math must hug its delimiters
        if any(m.group()[1] == " " or m.group()[-2] == " " for m in SPANS.finditer(raw) if m.group()[1] != "$"):
            why.append("space inside $ $")
        if why:
            out.append(f"{n}: {', '.join(why)}: {raw.strip()[:120]}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        assert problems("ok $\\gamma^{t}$ 和 $$\n\\sum_i x_i\n$$ 以及 `a_b`\n") == []
        assert problems("$K_p$ 越小，改 $K_p$ 就改了映射\n") == []
        assert problems("  ![model_arch](figs/2511.14759/fig_2a.png)\n") == []
        assert len(problems("![a](x.png) 其中 x_t 未包\n")) == 1
        assert len(problems("Q̂ = Σ_{t} γ^t\n$x\n$ y $\n")) == 3
        print("ok")
        sys.exit(0)
    bad = problems(open(sys.argv[1]).read())
    print("\n".join(bad)) if bad else None
    sys.exit(1 if bad else 0)
