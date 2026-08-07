#!/usr/bin/env python3
import os
import glob
import re

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chapters_dir = os.path.join(PROJ, "chapters")

REQUIRED_SECTIONS = [
    r"Introduction \\& Clinical Indications",
    r"Relevant Surgical Anatomy",
    r"Preoperative Workup \\& Preparation",
    r"Surgical Technique \\& Procedure",
    r"Complications \\& Risks",
    r"Postoperative Care \\& Recovery",
    r"Outcomes \\& Prognosis",
    r"References"
]

def audit_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    filename = os.path.basename(filepath)
    issues = []
    
    # 1. Check sections
    missing_sections = []
    for sect in REQUIRED_SECTIONS:
        pattern = r"\\section\*\{" + sect + r"\}"
        if not re.search(pattern, content):
            # Clean up the regex pattern for display
            clean_sect = sect.replace("\\?", "?").replace("\\\\&", "&").replace("\\", "")
            missing_sections.append(clean_sect)
            
    if missing_sections:
        issues.append(f"Missing sections: {', '.join(missing_sections)}")
        
    # 2. Check placeholders
    placeholders = ["TODO", "TBD", "PLACEHOLDER", "LOREM IPSUM", "XXXX"]
    found_placeholders = []
    for p in placeholders:
        if re.search(r"\b" + p + r"\b", content, re.IGNORECASE):
            found_placeholders.append(p)
    if found_placeholders:
        issues.append(f"Contains placeholders: {', '.join(found_placeholders)}")
        
    # 3. Check line and word count
    lines = content.splitlines()
    word_count = len(content.split())
    if len(lines) < 140:
        issues.append(f"Short line count: {len(lines)} lines (Target: >=150)")
    if word_count < 1800:
        issues.append(f"Low word count: {word_count} words (Target: 2000-2500)")
        
    # 4. Check readability & simple language metrics
    # Count sentences longer than 35 words as they can be difficult to read
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
    long_sentences = 0
    total_words = 0
    sentence_count = 0
    for s in sentences:
        s_words = s.split()
        if not s_words:
            continue
        sentence_count += 1
        total_words += len(s_words)
        if len(s_words) > 35:
            long_sentences += 1
            
    avg_sentence_len = total_words / sentence_count if sentence_count > 0 else 0
    
    # Check for unescaped special LaTeX characters
    # e.g., bare ampersands not preceded by backslash
    # Look for ampersand that does not have a backslash before it
    # We allow it inside \begin{tabular} or similar, but let's check general text
    # A simple regex for bare ampersands in text:
    bare_ampersands = len(re.findall(r'(?<!\\)&', content))
    if bare_ampersands > 0:
        issues.append(f"Unescaped ampersands: {bare_ampersands} found")

    return {
        "filename": filename,
        "line_count": len(lines),
        "word_count": word_count,
        "avg_sentence_len": avg_sentence_len,
        "long_sentences": long_sentences,
        "issues": issues
    }

def main():
    files = sorted(glob.glob(os.path.join(chapters_dir, "surgery_*.tex")))
    print(f"Auditing {len(files)} chapters...")
    
    total_issues = 0
    results = []
    for f in files:
        res = audit_file(f)
        results.append(res)
        if res["issues"]:
            print(f"\n[ISSUE] {res['filename']}:")
            for issue in res["issues"]:
                print(f"  - {issue}")
                total_issues += 1
                
    # Summary metrics
    avg_lines = sum(r["line_count"] for r in results) / len(results) if results else 0
    avg_words = sum(r["word_count"] for r in results) / len(results) if results else 0
    avg_sent_len = sum(r["avg_sentence_len"] for r in results) / len(results) if results else 0
    total_long_sents = sum(r["long_sentences"] for r in results)
    
    print("\n" + "="*50)
    print("AUDIT SUMMARY REPORT")
    print("="*50)
    print(f"Total Chapters Audited: {len(files)}")
    print(f"Total Issues Found:     {total_issues}")
    print(f"Average Lines/Chapter:  {avg_lines:.1f}")
    print(f"Average Words/Chapter:  {avg_words:.1f}")
    print(f"Average Sentence Len:   {avg_sent_len:.1f} words")
    print(f"Total Long Sentences (>35 words): {total_long_sents}")
    print("="*50)

if __name__ == "__main__":
    main()
