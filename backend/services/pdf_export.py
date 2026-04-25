
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import json
import os

# Basic PDF export with metadata, notes, and placeholder sections
def generate_experiment_pdf(exp_data: dict, output_path: str) -> str:
    c = canvas.Canvas(output_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 10.5*inch, f"Experiment: {exp_data.get('title', '')}")

    c.setFont("Helvetica", 11)
    c.drawString(1*inch, 10.1*inch, f"Author: {exp_data.get('author', '')}")
    c.drawString(1*inch, 9.8*inch, f"Status: {exp_data.get('status', '')}")

    # Notes
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, 9.3*inch, "Experiment Notes:")
    c.setFont("Helvetica", 10)

    text = c.beginText(1*inch, 9.1*inch)
    text.setLeading(14)
    notes = exp_data.get("notes", "")
    for line in notes.split(""):
        text.textLine(line)
    c.drawText(text)

    c.showPage()
    c.save()
    return output_path
