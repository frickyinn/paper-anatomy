#!/usr/bin/env python3
"""Fetch an arXiv paper's HTML version and flatten it to plain text for reading.

Usage: python3 -I fetch_arxiv.py <arxiv-id> <out-dir>
Writes <out-dir>/<arxiv-id>.txt and prints its path. Exits 2 when arXiv has no
HTML version (the caller falls back to the PDF).
"""
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

SKIP = {"script", "style", "nav", "header", "footer", "button"}
BLOCK = {"p", "div", "section", "li", "tr", "figcaption", "br", "table", "h1",
         "h2", "h3", "h4", "h5", "h6", "blockquote", "dt", "dd"}
HEADING = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "#####"}


class Flatten(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.out = base, []
        self.skip = 0      # depth inside skipped subtrees (chrome, bibliography)
        self.math = 0      # depth inside <math>; its alttext was already emitted
        self.cell = 0      # depth inside <td>/<th>; blocks there stay on the row

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.skip:
            if tag not in ("br", "img", "hr", "meta", "link", "input"):
                self.skip += 1
            return
        if tag in SKIP or "ltx_bibliography" in cls or "ltx_page_footer" in cls:
            self.skip = 1
            return
        if tag == "math":
            self.math += 1
            if self.math == 1:
                self.out.append(f" ${a.get('alttext', '')}$ ")
            return
        if self.math:
            return
        if tag in HEADING:
            self.out.append(f"\n\n{HEADING[tag]} ")
        elif tag in ("td", "th"):
            self.cell += 1
            self.out.append(" | ")
        elif tag in BLOCK:
            self.out.append(" " if self.cell and tag != "tr" else "\n")
        elif tag == "img" and "ltx_graphics" in cls:
            self.out.append(f"\n[image: {urljoin(self.base, a.get('src', ''))}]\n")

    def handle_endtag(self, tag):
        if self.skip:
            if tag not in ("br", "img", "hr", "meta", "link", "input"):
                self.skip -= 1
            return
        if tag == "math":
            self.math -= 1
        elif self.math:
            return
        elif tag in ("td", "th"):
            self.cell -= 1
        elif tag in BLOCK | set(HEADING):
            self.out.append(" " if self.cell and tag != "tr" else "\n")

    def handle_data(self, data):
        if not self.skip and not self.math:
            self.out.append(data.replace("\n", " "))  # layout comes from tags, not source newlines


def flatten(html, base):
    p = Flatten(base)
    p.feed(html)
    lines = (" ".join(line.split()) for line in "".join(p.out).splitlines())
    text, blank = [], False
    for line in lines:
        if line or not blank:
            text.append(line)
        blank = not line
    return "\n".join(text).strip() + "\n"


def main():
    arxiv_id, out_dir = sys.argv[1], sys.argv[2]
    url = f"https://arxiv.org/html/{arxiv_id}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "paper-digest"}), timeout=60) as r:
            html, final = r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        print(f"no HTML version for {arxiv_id}: {e}", file=sys.stderr)
        sys.exit(2 if e.code == 404 else 1)
    text = flatten(html, final)
    if "ltx_document" not in html or len(text) < 5000:
        print(f"no usable HTML version for {arxiv_id}", file=sys.stderr)
        sys.exit(2)
    path = f"{out_dir.rstrip('/')}/{arxiv_id}.txt"
    with open(path, "w") as f:
        f.write(text)
    print(path)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        t = flatten('<nav>x</nav><h2>1 Intro</h2><p>a <math alttext="x^2"><mi>x</mi></math> b</p>'
                    '<section class="ltx_bibliography"><p>ref</p></section>'
                    '<img class="ltx_graphics" src="1v2/f/a.png">'
                    '<table><tr><td><p>A</p></td><td>1</td></tr><tr><td>B</td><td>2</td></tr></table>', "https://arxiv.org/html/1v2")
        assert t == "## 1 Intro\n\na $x^2$ b\n\n[image: https://arxiv.org/html/1v2/f/a.png]\n\n| A | 1\n\n| B | 2\n", repr(t)
        print("ok")
    else:
        main()
