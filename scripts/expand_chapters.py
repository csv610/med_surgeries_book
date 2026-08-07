#!/usr/bin/env python3
import os
import re
import sys
import glob
import subprocess
import concurrent.futures
import openai

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(PROJ, ".measure")
os.makedirs(WORK, exist_ok=True)

REQUIRED_SECTIONS = [
    r"What Is This Surgery\?",
    r"Alternative Names",
    r"Relevant Surgical Anatomy",
    r"Surgical Principle \\& Rationale",
    r"History \\& Surgical Evolution",
    r"Clinical Indications",
    r"Clinical Positioning",
    r"Surgical Technique \\& Procedure",
    r"Preoperative Workup \\& Preparation",
    r"Contraindications \\& Precautions",
    r"Complications \\& Risks",
    r"Postoperative Recovery Timeline",
    r"Surgical Findings \\& Pathology",
    r"Expected Postoperative Course",
    r"Postoperative Care \\& Follow-up",
    r"Epidemiology",
    r"Outcomes \\& Prognosis",
    r"References"
]

def check_completeness(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False
    for sect in REQUIRED_SECTIONS:
        pattern = r"\\section\*\{" + sect + r"\}"
        if not re.search(pattern, content):
            return False
    return True


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
\input{CHAP}
\end{document}
"""

def measure(chap_path):
    chap = os.path.splitext(os.path.basename(chap_path))[0]
    work_dir = os.path.join(WORK, f"thread_{chap}")
    os.makedirs(work_dir, exist_ok=True)
    driver = DRIVER.replace("CHAP", chap)
    dst = os.path.join(work_dir, chap + ".tex")
    
    with open(chap_path, "r", encoding="utf-8") as f:
        content = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(content)
    with open(os.path.join(work_dir, "driver.tex"), "w", encoding="utf-8") as f:
        f.write(driver)
        
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                        "-output-directory", work_dir, "driver.tex"],
                       cwd=work_dir, capture_output=True)
    log = r.stdout.decode("utf-8", errors="replace") + r.stderr.decode("utf-8", errors="replace")
    pdf = os.path.join(work_dir, "driver.pdf")
    pages = -1
    clean = True
    if os.path.exists(pdf):
        p = subprocess.run(["pdfinfo", pdf], capture_output=True)
        pdfinfo_out = p.stdout.decode("utf-8", errors="replace")
        for line in pdfinfo_out.splitlines():
            if line.startswith("Pages"):
                pages = int(line.split(":")[1].strip())
    else:
        clean = False
        
    if "! " in log and ("Error" in log or "Undefined" in log or "Emergency" in log):
        clean = False
    return pages, clean, log

SYSTEM_PROMPT = """You are an expert medical editor and surgical textbook writer.
Your task is to take an existing LaTeX chapter of a surgical textbook and substantially expand/rewrite it to follow the new surgery-specific structural layout. The final chapter must be at least 4 pages long (aiming for roughly 150-180 lines, about 2,000-2,500 words of source code) with rich, detailed, clinically accurate, and specific medical content. Do not pad with fluff or repetition.

You MUST follow these structure and formatting rules precisely:
1. All section headers in this exact order:
   \\section*{What Is This Surgery?}
   \\section*{Alternative Names}
   \\section*{Relevant Surgical Anatomy}
   \\section*{Surgical Principle \\& Rationale}
   \\section*{History \\& Surgical Evolution}
   \\section*{Clinical Indications}
   \\section*{Clinical Positioning}
   \\section*{Surgical Technique \\& Procedure}
   \\section*{Preoperative Workup \\& Preparation}
   \\section*{Contraindications \\& Precautions}
   \\section*{Complications \\& Risks}
   \\section*{Postoperative Recovery Timeline}
   \\section*{Surgical Findings \\& Pathology}
   \\section*{Expected Postoperative Course}
   \\section*{Postoperative Care \\& Follow-up}
   \\section*{Epidemiology}
   \\section*{Outcomes \\& Prognosis}
   \\section*{References}

2. Hard LaTeX safety rules (violating these corrupts the build):
   - Output ONLY valid LaTeX. Escape special characters in prose:
     - & -> \\& (never write a bare ampersand)
     - % -> \\%
     - _ -> \\_
     - # -> \\#
     - $ -> \\$
   - NEVER write a double backslash \\\\ inside prose or list reasons. A real newline is a single carriage return.
   - Use \\begin{itemize} ... \\end{itemize} for lists, each item on its own line:
     \\begin{itemize}
       \\item First point.
       \\item Second point.
     \\end{itemize}
     Keep a blank line before \\begin{itemize} and after \\end{itemize}.
   - Keep the \\chapter{...} title EXACTLY as it currently is. Do not rename or modify it.
   - Keep every \\section*{...} heading EXACTLY as-is.
   - End the file with \\clearpage on its own line.
   - No unicode characters. Use LaTeX escapes for accented letters (e.g. \\\"{o} for o-umlaut, \\'{e} for e-acute, etc.).
   - Do not introduce tables. Use plain paragraphs and itemize lists.
   - Do not add \\index{}, \\label{}, or cross-references.
   - Put a blank line between every paragraph and between lists and surrounding text.

3. Specific instructions per section:
   - What Is This Surgery? — 1 solid paragraph (5-7 sentences) defining the surgery, its anatomical site, clinical scenario, and clinical significance.
   - Alternative Names — Expand into an itemize list of 3-6 synonyms/common names.
   - Relevant Surgical Anatomy — Detailed description of relevant organs, tissues, arterial supply, venous drainage, nerve relations, lymphatic drainage, and surgical landmarks (e.g., McBurney's point, Calot's triangle). 1-2 paragraphs plus a short list where useful. High yield for MBBS.
   - Surgical Principle \\& Rationale — Explain the operative concept: what tissue is excised/repaired, the mechanism of correction, and technical goals. 1-2 paragraphs.
   - History \\& Surgical Evolution — 2-4 historical milestones with dates and names of surgeon pioneers; describe how the technique evolved. 1-2 paragraphs.
   - Clinical Indications — Bulleted list of 5-8 clear clinical indications (disease states, symptoms, findings). Mention standardized diagnostic scores where applicable (e.g., Alvarado Score for appendicitis). Each item one complete sentence.
   - Clinical Positioning — Explanation of whether this is first-line/primary or secondary/salvage/adjunct; describe when each role applies.
   - Surgical Technique \\& Procedure — Detailed step-by-step: anesthesia, patient positioning, incisions, key operative steps (5-8 enumerated steps), closure, and drains/implants. 2-3 paragraphs or an itemized procedure list.
   - Preoperative Workup \\& Preparation — Medical/cardiac evaluation, labs, imaging, NPO, meds adjustments, prophylactic antibiotics, consent. A paragraph plus a short list.
   - Contraindications \\& Precautions — Separate absolute contraindications from relative ones using two itemize lists.
   - Complications \\& Risks — Categorized list: general surgical complications (bleeding, infection, anesthesia) and 6-9 procedure-specific risks (nerve/vascular injury, organ dysfunction).
   - Postoperative Recovery Timeline — PACU monitoring, first 24-48 hours, first 1-2 weeks (diet, activity restrictions), and long-term recovery. 2 paragraphs.
   - Surgical Findings \\& Pathology — What the surgeon documents and what the pathology report on resected tissues represents. 1 paragraph.
   - Expected Postoperative Course — What a normal, successful postoperative course looks like (pain resolution, timeline of healing). 1 paragraph.
   - Postoperative Care \\& Follow-up — Post-op visits, suture/staple removal, rehab/PT, warning signs for when to contact the doctor. A short list plus a sentence.
   - Epidemiology — Incidence, age/sex, common indications frequency, and mortality/morbidity. 1 paragraph.
   - Outcomes \\& Prognosis — Success rates, functional/survival outcomes, recurrence risk, prognostic factors. Cite landmark clinical trials where applicable (e.g., APPAC for appendicitis, NASCET for carotid endarterectomy). 1 paragraph.
   - References — 3-4 numbered bibliography entries using enumerate, citing MedlinePlus, a major textbook (Schwartz's, Sabiston's, etc.), and/or a specialty society guideline.

Your output must contain ONLY the raw LaTeX text of the entire expanded chapter, ready to be written to a file. Do not wrap it in markdown code blocks like ```latex or ```. Keep it as pure LaTeX."""

def expand_chapter(client, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        original_content = f.read()
        
    print(f"Expanding {os.path.basename(filepath)}...")
    
    prompt = f"Here is the current content of the LaTeX chapter file:\n\n{original_content}\n\nPlease expand and rewrite it to follow the new 18-section surgery-specific layout."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            timeout=90.0
        )
        expanded_content = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Error for {os.path.basename(filepath)}: {e}")
        return ""
    
    if expanded_content.startswith("```"):
        lines = expanded_content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        expanded_content = "\n".join(lines).strip()
        
    if not expanded_content.endswith("\\clearpage"):
        if "\\clearpage" in expanded_content:
            pass
        else:
            expanded_content += "\n\n\\clearpage\n"
            
    return expanded_content

def process_file(filepath):
    client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    filename = os.path.basename(filepath)
    
    # We measure current pages and check if it is complete and has >= 4 pages
    orig_pages, orig_clean, _ = measure(filepath)
    if orig_pages >= 4 and orig_clean and check_completeness(filepath):
        print(f"Skipping {filename}: already has {orig_pages} pages and is complete.")
        return True
            
    for attempt in range(3):
        expanded = expand_chapter(client, filepath)
        if not expanded:
            print(f"Attempt {attempt+1} failed for {filename}: empty response from API. Retrying...")
            continue
        
        temp_path = os.path.join(WORK, filename)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(expanded)
            
        pages, clean, log = measure(temp_path)
        if clean and pages >= 4:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(expanded)
            print(f"Successfully expanded {filename}: {orig_pages} -> {pages} pages (Clean: {clean})")
            return True
        else:
            print(f"Attempt {attempt+1} failed for {filename}: pages={pages}, clean={clean}. Retrying...")
            if not clean:
                error_lines = [l for l in log.splitlines() if l.startswith("!") or "Error" in l]
                print(f"  Errors: {error_lines[:3]}")
                
    print(f"FAILED to expand {filename} successfully after 3 attempts.")
    return False

def main():
    if len(sys.argv) > 1:
        files = [os.path.abspath(arg) for arg in sys.argv[1:]]
    else:
        files = sorted(glob.glob(os.path.join(PROJ, "chapters", "surgery_*.tex")))
    
    to_process = []
    for f in files:
        if len(sys.argv) > 1 or not check_completeness(f):
            to_process.append(f)
            
    print(f"Found {len(to_process)} chapters to process out of {len(files)} total chapters.")
    
    max_workers = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_file, to_process))
        
    success_count = sum(1 for r in results if r)
    print(f"Finished processing. Success: {success_count}/{len(to_process)}")

if __name__ == "__main__":
    main()
