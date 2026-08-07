#!/usr/bin/env python3
import os
import glob
import re

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chapters_dir = os.path.join(PROJ, "chapters")

SECTION_MAP = {
    "What Is This Surgery?": "Introduction \\& Clinical Indications",
    "Alternative Names": "Introduction \\& Clinical Indications",
    "Surgical Principle \\& Rationale": "Introduction \\& Clinical Indications",
    "History \\& Surgical Evolution": "Introduction \\& Clinical Indications",
    "Clinical Indications": "Introduction \\& Clinical Indications",
    "Clinical Positioning": "Introduction \\& Clinical Indications",
    
    "Relevant Surgical Anatomy": "Relevant Surgical Anatomy",
    
    "Preoperative Workup \\& Preparation": "Preoperative Workup \\& Preparation",
    "Contraindications \\& Precautions": "Preoperative Workup \\& Preparation",
    
    "Surgical Technique \\& Procedure": "Surgical Technique \\& Procedure",
    
    "Complications \\& Risks": "Complications \\& Risks",
    
    "Postoperative Recovery Timeline": "Postoperative Care \\& Recovery",
    "Surgical Findings \\& Pathology": "Postoperative Care \\& Recovery",
    "Expected Postoperative Course": "Postoperative Care \\& Recovery",
    "Postoperative Care \\& Follow-up": "Postoperative Care \\& Recovery",
    
    "Epidemiology": "Outcomes \\& Prognosis",
    "Outcomes \\& Prognosis": "Outcomes \\& Prognosis",
    
    "References": "References"
}

NEW_SECTIONS_ORDER = [
    "Introduction \\& Clinical Indications",
    "Relevant Surgical Anatomy",
    "Preoperative Workup \\& Preparation",
    "Surgical Technique \\& Procedure",
    "Complications \\& Risks",
    "Postoperative Care \\& Recovery",
    "Outcomes \\& Prognosis",
    "References"
]

def consolidate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split content by \section*{...}
    parts = re.split(r"\\section\*\{([^}]+)\}", content)
    if len(parts) < 3:
        print(f"Skipping {os.path.basename(filepath)}: no sections found")
        return False
        
    header = parts[0].strip()
    
    # Extract existing sections
    existing_sections = {}
    for i in range(1, len(parts), 2):
        sec_name = parts[i].strip()
        sec_content = parts[i+1].strip()
        # Remove trailing clearpage if present in the last section
        if i+1 == len(parts) - 1:
            sec_content = re.sub(r"\\clearpage\s*$", "", sec_content).strip()
        existing_sections[sec_name] = sec_content
        
    # Group content into new sections
    new_sections = {sec: [] for sec in NEW_SECTIONS_ORDER}
    
    for old_name, old_content in existing_sections.items():
        # Match old section name to new section name, accounting for minor backslash variations
        normalized_old_name = old_name.replace("\\&", "&").replace("&", "\\&").strip()
        
        matched_new_name = None
        for key, val in SECTION_MAP.items():
            norm_key = key.replace("\\&", "&").replace("&", "\\&").strip()
            if normalized_old_name == norm_key:
                matched_new_name = val
                break
                
        if matched_new_name:
            new_sections[matched_new_name].append(old_content)
        else:
            # If not matched, default to Introduction & Clinical Indications
            print(f"  [WARNING] Unmatched section name '{old_name}' in {os.path.basename(filepath)}")
            new_sections["Introduction \\& Clinical Indications"].append(old_content)
            
    # Construct new content
    new_content_parts = [header, ""]
    
    for sec_name in NEW_SECTIONS_ORDER:
        sec_parts = new_sections[sec_name]
        if sec_parts:
            # Join parts with double newlines
            joined_parts = "\n\n".join(sec_parts).strip()
            new_content_parts.append(f"\\section*{{{sec_name}}}")
            new_content_parts.append(joined_parts)
            new_content_parts.append("")
            
    new_content = "\n".join(new_content_parts).strip() + "\n\n\\clearpage\n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    return True

def main():
    files = sorted(glob.glob(os.path.join(chapters_dir, "surgery_*.tex")))
    print(f"Consolidating {len(files)} chapters into standard 8-section layout...")
    
    success_count = 0
    for f in files:
        if consolidate_file(f):
            success_count += 1
            
    print(f"Successfully consolidated {success_count}/{len(files)} chapters.")

if __name__ == "__main__":
    main()
