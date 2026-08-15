from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import LeaveApplication

def generate_leave_report_pdf(email, start_date=None, end_date=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Leave Report")

    # Fetch leave records via student relationship
    leaves = LeaveApplication.objects.filter(student__email=email)
    if start_date:
        leaves = leaves.filter(start_date__gte=start_date)
    if end_date:
        leaves = leaves.filter(end_date__lte=end_date)

    # Table headers
    c.setFont("Helvetica-Bold", 12)
    y = height - 100
    headers = ["Leave Type", "Start Date", "End Date", "Approved", "Reason"]
    x_positions = [50, 150, 250, 350, 450]
    for header, x in zip(headers, x_positions):
        c.drawString(x, y, header)

    # Table content
    c.setFont("Helvetica", 12)
    y -= 20
    for leave in leaves:
        row = [
            leave.leave_type,
            str(leave.start_date),
            str(leave.end_date),
            "Yes" if leave.approved else "No",
            (leave.reason[:25] + '...') if len(leave.reason) > 25 else leave.reason
        ]
        for value, x in zip(row, x_positions):
            c.drawString(x, y, value)
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer