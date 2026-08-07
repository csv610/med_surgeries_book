# MedSurgeries Chapter Expansion Guide (target: 4+ pages per chapter)

## Goal
Every chapter in `chapters/surgery_*.tex` must render to at least **4 pages** at 12pt/1in margins. Every section must be substantially expanded with clinically accurate, specific content. Every chapter must follow the new surgery-specific structural layout.

## Hard LaTeX safety rules (violating these corrupts the build)
1. Use ONLY valid LaTeX. Escape special chars in prose:
   - `&` -> `\&`  (never use a bare ampersand)
   - `%` -> `\%`
   - `_` -> `\_` (avoid underscores entirely in prose; if needed escape them)
   - `#` -> `\#`, `$` -> `\$`
2. NEVER write a double backslash `\\` inside prose or list reasons. A real newline is a single `<Enter>` byte.
3. Use `\begin{itemize}` ... `\end{itemize}` for lists, each item on its own line:
   ```
   \begin{itemize}
     \item First point.
     \item Second point.
   \end{itemize}
   ```
   Keep a blank line before `\begin{itemize}` and after `\end{itemize}`.
4. Keep the `\chapter{...}` title EXACTLY as it currently is. Do not rename or modify it.
5. Keep every section heading EXACTLY as specified in the new structure below.
6. End the file with `\clearpage` on its own line.
7. No unicode characters. Use LaTeX escapes for accented letters (e.g. `\"{o}`).
8. Do not introduce tables for content; plain paragraphs and itemize lists are preferred and safest.
9. Do not add `\index{}`, `\label{}`, or cross-references. Keep it simple.
10. Blank line between every paragraph and between list and surrounding text.

---

## Chapter structure (all section headers in this exact order)

1. `\section*{What Is This Surgery?}`
2. `\section*{Alternative Names}`
3. `\section*{Relevant Surgical Anatomy}`
4. `\section*{Surgical Principle \& Rationale}`
5. `\section*{History \& Surgical Evolution}`
6. `\section*{Clinical Indications}`
7. `\section*{Clinical Positioning}`
8. `\section*{Surgical Technique \& Procedure}`
9. `\section*{Preoperative Workup \& Preparation}`
10. `\section*{Contraindications \& Precautions}`
11. `\section*{Complications \& Risks}`
12. `\section*{Postoperative Recovery Timeline}`
13. `\section*{Surgical Findings \& Pathology}`
14. `\section*{Expected Postoperative Course}`
15. `\section*{Postoperative Care \& Follow-up}`
16. `\section*{Epidemiology}`
17. `\section*{Outcomes \& Prognosis}`
18. `\section*{References}`

---

## Expansion guidance per section

*   **What Is This Surgery?** — Clear definition of the surgery and its purpose. Add the anatomical site, the clinical scenario, and its clinical significance. 1 solid paragraph (5-7 sentences).
*   **Alternative Names** — Itemize list of 3-6 synonyms/common names for the procedure.
*   **Relevant Surgical Anatomy** — **Crucial for MBBS.** Detailed description of relevant organs, tissues, arterial supply, venous drainage, nerve relations, lymphatic drainage, and surgical landmarks (e.g., McBurney's point, Calot's triangle). 1-2 paragraphs plus a short list where useful.
*   **Surgical Principle \& Rationale** — Explain the operative concept: what tissue is excised/repaired, the mechanism of correction, and technical goals. 1-2 paragraphs.
*   **History \& Surgical Evolution** — 2-4 historical milestones with dates and names of surgeon pioneers; describe how the technique evolved. 1-2 paragraphs.
*   **Clinical Indications** — Bulleted list of 5-8 clear clinical indications (disease states, symptoms, findings). Mention standardized diagnostic scores where applicable (e.g., Alvarado Score for appendicitis). Each item one complete sentence.
*   **Clinical Positioning** — Explanation of whether this is first-line/primary or secondary/salvage/adjunct; describe when each role applies.
*   **Surgical Technique \& Procedure** — Detailed step-by-step: anesthesia, patient positioning, incisions, key operative steps (5-8 enumerated steps), closure, and drains/implants. 2-3 paragraphs or an itemized procedure list.
*   **Preoperative Workup \& Preparation** — Medical/cardiac evaluation, labs, imaging, NPO, meds adjustments, prophylactic antibiotics, consent. A paragraph plus a short list.
*   **Contraindications \& Precautions** — Separate absolute contraindications from relative ones using two itemize lists.
*   **Complications \& Risks** — Categorized list: general surgical complications (bleeding, infection, anesthesia) and 6-9 procedure-specific risks (nerve/vascular injury, organ dysfunction).
*   **Postoperative Recovery Timeline** — PACU monitoring, first 24-48 hours, first 1-2 weeks (diet, activity restrictions), and long-term recovery. 2 paragraphs.
*   **Surgical Findings \& Pathology** — What the surgeon documents and what the pathology report on resected tissues represents. 1 paragraph.
*   **Expected Postoperative Course** — What a normal, successful postoperative course looks like (pain resolution, timeline of healing). 1 paragraph.
*   **Postoperative Care \& Follow-up** — Post-op visits, suture/staple removal, rehab/PT, warning signs for when to contact the doctor. A short list plus a sentence.
*   **Epidemiology** — Incidence, age/sex, common indications frequency, and mortality/morbidity. 1 paragraph.
*   **Outcomes \& Prognosis** — Success rates, functional/survival outcomes, recurrence risk, prognostic factors. Cite landmark clinical trials where applicable (e.g., APPAC for appendicitis, NASCET for carotid endarterectomy). 1 paragraph.
*   **References** — 3-4 entries in a numbered `enumerate` list (major textbooks, specialty society guidelines, MedlinePlus). Use `\item`.

## Length target
Averaged over 12pt/1in margins, aim for the chapter source to be roughly **150-180 lines** (about 2,000-2,500 words) so it fills 4+ pages comfortably. Do not pad with fluff or repetition.
