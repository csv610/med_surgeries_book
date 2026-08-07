#!/usr/bin/env python3
"""Measure per-chapter page count by compiling each chapter standalone.
Usage: python3 scripts/measure_chapters.py [chapters/surgery_*.tex ...]
Prints: filename<TAB>pages<TAB>clean
"""
import os, re, subprocess, sys, glob

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(PROJ, ".measure")

DRIVER = r"""\documentclass[12pt,oneside]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{multirow}
\usepackage{array}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{tocloft}
\geometry{margin=1in}
\begin{document}
\mainmatter
\include{CHAP}
\end{document}
"""

os.makedirs(WORK, exist_ok=True)

def measure(chap_path):
    chap = os.path.splitext(os.path.basename(chap_path))[0]
    # copy chapter into work dir with .tex include name compatibility
    driver = DRIVER.replace("CHAP", chap).replace("\\include", "\\input")
    # we use \input so we can compile directly; copy the chapter file
    dst = os.path.join(WORK, chap + ".tex")
    with open(chap_path) as f:
        content = f.read()
    with open(dst, "w") as f:
        f.write(content)
    with open(os.path.join(WORK, "driver.tex"), "w") as f:
        f.write(driver)
    # compile in work dir
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                        "-output-directory", WORK, "driver.tex"],
                       cwd=WORK, capture_output=True, text=True)
    log = r.stdout + r.stderr
    texname = chap + ".tex"
    # page count: count pages in pdf
    pdf = os.path.join(WORK, "driver.pdf")
    pages = -1
    clean = True
    if os.path.exists(pdf):
        p = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
        for line in p.stdout.splitlines():
            if line.startswith("Pages"):
                pages = int(line.split(":")[1].strip())
    else:
        clean = False
    # detect errors
    if "! " in log and ("Error" in log or "Undefined" in log or "Emergency" in log):
        clean = False
    return pages, clean

def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(PROJ, "chapters", "surgery_*.tex")))
    for f in files:
        pages, clean = measure(f)
        print(f"{os.path.basename(f)}\t{pages}\t{'OK' if clean else 'ERR'}")

if __name__ == "__main__":
    main()
