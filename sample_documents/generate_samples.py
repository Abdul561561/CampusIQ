"""
Sample Academic PDF Document Generator for CampusIQ
Generates test PDF documents (Syllabus, Examination Guidelines, Placement Guide)
for demonstration and evaluation purposes.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLE_DIR = Path(__file__).parent

def create_syllabus_pdf():
    pdf_path = SAMPLE_DIR / "College_Syllabus_CS101.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E3A8A'))
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2563EB'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("Department of Computer Science & Engineering", title_style))
    story.append(Paragraph("Course Syllabus: CS101 - Data Structures & Algorithms", heading_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Academic Regulations & Policies (Page 1)", heading_style))
    story.append(Paragraph("<b>1. Attendance Requirement:</b> Students must maintain a minimum of <b>75% attendance</b> in both lectures and practical sessions to be eligible for university examinations. Students with attendance between 65% and 74% may apply for condonation on medical grounds with valid documentation.", body_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>2. Grading System:</b> Continuous Internal Assessment (CIA) accounts for 40% of final marks. End Semester Examination (ESE) accounts for 60% of final marks. Passing mark is 40% overall.", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Course Modules (Page 2)", heading_style))
    story.append(Paragraph("<b>Unit 1: Linear Data Structures</b> - Arrays, Linked Lists, Stacks, Queues, Infix/Postfix Conversions, Applications.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Unit 2: Trees & Hierarchical Structures</b> - Binary Search Trees, AVL Trees, Heaps, Priority Queues, Trie Data Structure.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Unit 3: Graph Algorithms & Dynamic Programming</b> - BFS, DFS, Dijkstra's Shortest Path, Minimum Spanning Trees (Kruskal & Prim), Dynamic Programming principles, Knapsack Problem, Longest Common Subsequence.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Unit 4: Sorting & Searching Technologies</b> - QuickSort, MergeSort, HeapSort, External Sorting, Hash Tables, Collision Resolution Strategies.", body_style))

    doc.build(story)
    print(f"[Generated] {pdf_path.name}")

def create_exam_guidelines_pdf():
    pdf_path = SAMPLE_DIR / "Examination_Guidelines_2026.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#831843'))
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#BE185D'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("Office of Controller of Examinations", title_style))
    story.append(Paragraph("Academic Examination Guidelines 2026", heading_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 1: Examination Eligibility & Hall Ticket (Page 1)", heading_style))
    story.append(Paragraph("To appear in the final semester examinations, candidates must satisfy the following conditions:<br/>"
                           "- Clearance of all semester fee dues prior to hall ticket issuance.<br/>"
                           "- Verified minimum attendance of 75% as certified by the Head of Department.<br/>"
                           "- Physical possession of Official Physical Student ID Card and printed Hall Ticket in the examination hall.", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 2: Examination Rules & Prohibited Items (Page 2)", heading_style))
    story.append(Paragraph("Programmable calculators, mobile phones, smartwatches, and unauthorized notes are strictly prohibited inside the examination hall. Possession of prohibited items will result in immediate disqualification under malpractice regulations.", body_style))
    
    doc.build(story)
    print(f"[Generated] {pdf_path.name}")

def create_placement_guide_pdf():
    pdf_path = SAMPLE_DIR / "Placement_Registration_Guide.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#065F46'))
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#047857'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("Campus Training & Placement Cell", title_style))
    story.append(Paragraph("Campus Recruitment Placement Manual 2026", heading_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Placement Eligibility Criteria (Page 1)", heading_style))
    story.append(Paragraph("Students seeking placement registration must possess a minimum Cumulative Grade Point Average (CGPA) of <b>6.0 or 60% equivalent</b> across all completed semesters. Students must have <b>zero active backlogs</b> at the time of company registration.", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Required Placement Registration Documents (Page 2)", heading_style))
    story.append(Paragraph("Candidates must upload verified copies of the following documents during placement portal registration:<br/>"
                           "1. Updated One-Page Professional Resume (PDF format)<br/>"
                           "2. 10th and 12th Standard Original Marksheets<br/>"
                           "3. All Semester Consolidated Grade Cards<br/>"
                           "4. College ID Card and Government Identity Proof (Aadhar/Passport)<br/>"
                           "5. NOC (No Objection Certificate) for final semester internship training.", body_style))

    doc.build(story)
    print(f"[Generated] {pdf_path.name}")

if __name__ == "__main__":
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    create_syllabus_pdf()
    create_exam_guidelines_pdf()
    create_placement_guide_pdf()
    print("All sample PDF documents created successfully.")
