# CampusIQ Sample Documents

This folder contains realistic sample academic PDF documents designed for testing and demonstrating the CampusIQ RAG pipeline.

## Sample Documents Included

1. `College_Syllabus_CS101.pdf`
   - **Topics Covered:** Attendance policy (75%), Grading scheme (40% CIA, 60% ESE), Course Units 1 to 4 (Data Structures & Algorithms, Graph Algorithms, Dynamic Programming).
2. `Examination_Guidelines_2026.pdf`
   - **Topics Covered:** Exam hall ticket requirements, fee clearance, prohibited items, malpractice rules.
3. `Placement_Registration_Guide.pdf`
   - **Topics Covered:** Placement eligibility (CGPA 6.0 / 60%, zero active backlogs), required registration documents (Resume, marksheets, ID proof, NOC).

## How to Generate Sample PDFs

If the `.pdf` files are not present, run the automated Python generator script:

```bash
python sample_documents/generate_samples.py
```

This will instantly generate all three formatted academic PDFs using `reportlab`.
