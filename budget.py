#!/usr/bin/env python3
"""Print a note's character budget, scaled to the paper's main text.

Usage: python3 -I budget.py <paper.txt>
       python3 -I budget.py --pages <N> --columns 1|2
The main text runs from the start to the first References, Acknowledgments, Appendix or
Supplementary heading. For a PDF, count the pages before the references; a page holds about
6000 characters in two columns and 4000 in one. Prints `budget <lo>-<hi>`.
"""
import argparse
import re

RATE, FLOOR, CAP = 0.09, 2500, 8000  # 9% puts VLA's 64 papers at 3100 (p10), 3900 (median), 6700 (p90)
PER_PAGE = {1: 4000, 2: 6000}
END = re.compile(r"^#{1,6}\s*(?:[\w.\-]+\s+)?(References|Bibliography|Acknowledg|Appendix|Supplementary)", re.I | re.M)


def main_chars(text):
    m = END.search(text)
    return len(text[:m.start()] if m else text)


def budget(chars):
    hi = round(min(CAP, max(FLOOR, chars * RATE)), -2)
    return round(hi * 0.75, -2), hi


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("--pages", type=int)
    ap.add_argument("--columns", type=int, choices=(1, 2))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        assert main_chars("## 1 Intro\nabc\n## References\nxyz") == len("## 1 Intro\nabc\n")
        assert main_chars("## VII Conclusion\nab\n### -A Appendix x\nzz") == len("## VII Conclusion\nab\n")
        assert budget(10_000) == (1900, 2500) and budget(43_000) == (2900, 3900) and budget(200_000) == (6000, 8000)
        print("selftest ok")
    elif a.text:
        print("budget %d-%d" % budget(main_chars(open(a.text).read())))
    elif a.pages and a.columns:
        print("budget %d-%d" % budget(a.pages * PER_PAGE[a.columns]))
    else:
        ap.error("give paper.txt, or --pages and --columns")
