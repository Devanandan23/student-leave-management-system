"""
generate_leave_report_pdf.py  –  place alongside views.py
Uses the exact LeaveApplication and student models from studentleaveapp.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ── Palette ────────────────────────────────────────────────────────────────────
PRIMARY  = colors.HexColor("#1A3C6E")
ACCENT   = colors.HexColor("#2E86DE")
LIGHT_BG = colors.HexColor("#EBF2FB")
SUCCESS  = colors.HexColor("#27AE60")
WARNING  = colors.HexColor("#E67E22")
DANGER   = colors.HexColor("#E74C3C")
MUTED    = colors.HexColor("#7F8C8D")
PURPLE   = colors.HexColor("#8E44AD")
TEAL     = colors.HexColor("#16A085")
WHITE    = colors.white
DARK     = colors.HexColor("#2C3E50")

LEAVE_TYPE_COLORS = {
    "medical":   colors.HexColor("#2980B9"),
    "personal":  colors.HexColor("#8E44AD"),
    "emergency": colors.HexColor("#C0392B"),
    "others":    colors.HexColor("#16A085"),
    "other":     colors.HexColor("#16A085"),
}

# ── DB fetch (uses exact model/app names) ──────────────────────────────────────
def _get_data(email, start_date=None, end_date=None):
    from django.apps import apps
    Student          = apps.get_model("studentleaveapp", "student")
    LeaveApplication = apps.get_model("studentleaveapp", "LeaveApplication")

    student = Student.objects.filter(email=email).first()
    if student is None:
        return None, []

    qs = LeaveApplication.objects.filter(
        student=student, hide=False
    )
    if start_date:
        qs = qs.filter(start_date__gte=start_date)
    if end_date:
        qs = qs.filter(end_date__lte=end_date)

    leaves = list(qs.order_by("-start_date"))
    return student, leaves


# ── Header / footer drawn on every page ───────────────────────────────────────
def _make_header_footer(student, report_date):
    def on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # top banner
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, h - 62, w, 62, fill=True, stroke=False)

        # accent strip
        canvas.setFillColor(ACCENT)
        canvas.rect(0, h - 65, w, 3, fill=True, stroke=False)

        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 20)
        canvas.drawString(22, h - 40, "Student Leave Report")

        canvas.setFont("Helvetica", 8.5)
        canvas.drawRightString(w - 22, h - 26, f"Generated: {report_date}")
        canvas.drawRightString(w - 22, h - 39, f"Student: {student.username or student.email}")

        # bottom footer
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, 0, w, 24, fill=True, stroke=False)
        canvas.setFillColor(ACCENT)
        canvas.rect(0, 24, w, 2, fill=True, stroke=False)

        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(22, 8, "Confidential – For Internal Use Only")
        canvas.drawRightString(w - 22, 8, f"Page {doc.page}")

        canvas.restoreState()
    return on_page


# ── Main public function ───────────────────────────────────────────────────────
def generate_leave_report_pdf(email: str, start_date=None, end_date=None) -> io.BytesIO:
    student, leaves = _get_data(email, start_date, end_date)

    buf = io.BytesIO()

    if student is None:
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        doc.build([Paragraph(f"No student record found for: {email}", styles["Normal"])])
        buf.seek(0)
        return buf

    report_date = datetime.now().strftime("%d %b %Y, %I:%M %p")

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.8*cm, bottomMargin=1.6*cm,
    )

    # ── Style factory ─────────────────────────────────────────────────────────
    _base = getSampleStyleSheet()
    _used_names = {}

    def S(name, **kw):
        # avoid duplicate-name warnings from ReportLab
        count = _used_names.get(name, 0)
        _used_names[name] = count + 1
        unique = name if count == 0 else f"{name}_{count}"
        return ParagraphStyle(unique, parent=_base["Normal"], **kw)

    sec_title  = S("SecTitle", fontName="Helvetica-Bold", fontSize=11,
                   textColor=PRIMARY, spaceAfter=5)
    lbl        = S("Lbl", fontName="Helvetica-Bold", fontSize=9, textColor=MUTED)
    val        = S("Val", fontName="Helvetica", fontSize=10, textColor=DARK)
    ctr        = S("Ctr", alignment=TA_CENTER, fontName="Helvetica", fontSize=9, textColor=DARK)
    ctr_bold   = S("CtrB", alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=9, textColor=DARK)
    hdr_cell   = S("Hdr", fontName="Helvetica-Bold", fontSize=9,
                   textColor=WHITE, alignment=TA_CENTER)
    small_ctr  = S("SmCtr", alignment=TA_CENTER, fontName="Helvetica", fontSize=8, textColor=DARK)

    story = [Spacer(1, 4)]

    # ── Section 1: Student info ───────────────────────────────────────────────
    story += [
        Paragraph("Student Information", sec_title),
        HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=7),
    ]

    sem_map = {str(i): f"Semester {i}" for i in range(1, 9)}

    # leave_count from student model
    lc = student.leave_count
    lc_display = str(lc) if lc is not None else "0"

    info_rows = [
        [Paragraph("Full Name",        lbl), Paragraph(student.username or "—",                           val)],
        [Paragraph("Student ID",       lbl), Paragraph(str(student.studentid),                            val)],
        [Paragraph("Email",            lbl), Paragraph(student.email,                                     val)],
        [Paragraph("Department",       lbl), Paragraph(student.department or "—",                         val)],
        [Paragraph("Semester",         lbl), Paragraph(sem_map.get(str(student.semester), "—"),           val)],
        [Paragraph("Phone",            lbl), Paragraph(str(student.phone),                                val)],
        [Paragraph("Total Leave Days Used", lbl), Paragraph(lc_display,                                   val)],
        [Paragraph("Last Leave Year",  lbl), Paragraph(str(student.last_leave_year) if student.last_leave_year else "—", val)],
    ]

    it = Table(info_rows, colWidths=[5.2*cm, 11*cm], hAlign="LEFT")
    it.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, WHITE]),
        ("GRID",           (0, 0), (-1, -1), 0.4, colors.HexColor("#D0DCE8")),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story += [it, Spacer(1, 14)]

    # ── Section 2: Date filter note ───────────────────────────────────────────
    if start_date or end_date:
        f1 = start_date.strftime("%d %b %Y") if start_date else "—"
        f2 = end_date.strftime("%d %b %Y")   if end_date   else "today"
        story.append(Paragraph(
            f"Period filter applied:  {f1}  →  {f2}",
            S("Flt", fontName="Helvetica-Oblique", fontSize=9, textColor=MUTED, spaceAfter=8),
        ))

    # ── Section 3: Leave records ──────────────────────────────────────────────
    story += [
        Paragraph("Leave Records", sec_title),
        HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=7),
    ]

    if not leaves:
        story.append(Paragraph(
            "No leave records found for the selected period.",
            S("Empty", fontName="Helvetica-Oblique", fontSize=10, textColor=MUTED),
        ))
    else:
        # ── helpers ──────────────────────────────────────────────────────────
        def fmt_date(d):
            return d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d)

        def leave_type_pill(lt_raw):
            lt = (lt_raw or "others").strip().lower()
            col = LEAVE_TYPE_COLORS.get(lt, TEAL)
            label = (lt_raw or "Others").title()
            return Paragraph(label, S(f"LT_{lt_raw}", fontName="Helvetica-Bold",
                                      fontSize=8, textColor=col, alignment=TA_CENTER))

        def status_cell(approved, rejected):
            if approved:
                return Paragraph(
                    "Approved",
                    S("StA", fontName="Helvetica-Bold", fontSize=8,
                      textColor=SUCCESS, alignment=TA_CENTER),
                )
            if rejected:
                return Paragraph(
                    "Rejected",
                    S("StR", fontName="Helvetica-Bold", fontSize=8,
                      textColor=DANGER, alignment=TA_CENTER),
                )
            return Paragraph(
                "Pending",
                S("StP", fontName="Helvetica-Bold", fontSize=8,
                  textColor=WARNING, alignment=TA_CENTER),
            )

        def medsub_cell(medsub):
            if medsub:
                return Paragraph("Yes", S("MsY", fontName="Helvetica-Bold", fontSize=8,
                                           textColor=SUCCESS, alignment=TA_CENTER))
            return Paragraph("No", S("MsN", fontName="Helvetica", fontSize=8,
                                      textColor=MUTED, alignment=TA_CENTER))

        # ── table header ─────────────────────────────────────────────────────
        col_w = [0.7*cm, 2.3*cm, 2.3*cm, 1.2*cm, 2.5*cm, 4.0*cm, 2.2*cm, 1.3*cm]
        hdr   = ["#", "From", "To", "Days", "Type", "Reason", "Status", "Med Doc"]
        tbl_data = [[Paragraph(h, hdr_cell) for h in hdr]]

        # count per leave_count field on LeaveApplication (days debited)
        total_days_in_period = 0

        for idx, lv in enumerate(leaves, 1):
            sd   = lv.start_date
            ed   = lv.end_date
            days = (ed - sd).days + 1 if sd and ed else "—"
            if isinstance(days, int):
                total_days_in_period += days

            reason_text = (lv.reason or "—")[:80]

            tbl_data.append([
                Paragraph(str(idx), small_ctr),
                Paragraph(fmt_date(sd), small_ctr),
                Paragraph(fmt_date(ed), small_ctr),
                Paragraph(str(days),    small_ctr),
                leave_type_pill(lv.leave_type),
                Paragraph(reason_text, S(f"Rsn{idx}", fontSize=8, textColor=DARK,
                                          leading=11)),
                status_cell(lv.approved, lv.rejected),
                medsub_cell(lv.medsub),
            ])

        lt = Table(tbl_data, colWidths=col_w, repeatRows=1, hAlign="LEFT")
        lt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), PRIMARY),
            ("ROWBACKGROUNDS",(0, 1), (-1,-1), [LIGHT_BG, WHITE]),
            ("GRID",          (0, 0), (-1,-1), 0.35, colors.HexColor("#C8D8E8")),
            ("TOPPADDING",    (0, 0), (-1,-1), 5),
            ("BOTTOMPADDING", (0, 0), (-1,-1), 5),
            ("LEFTPADDING",   (0, 0), (-1,-1), 4),
            ("RIGHTPADDING",  (0, 0), (-1,-1), 4),
            ("VALIGN",        (0, 0), (-1,-1), "MIDDLE"),
            ("ALIGN",         (0, 0), (-1,-1), "CENTER"),
        ]))
        story += [lt, Spacer(1, 14)]

        # ── Section 4: Summary ────────────────────────────────────────────────
        story += [
            Paragraph("Summary", sec_title),
            HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=7),
        ]

        approved_list = [l for l in leaves if l.approved and not l.rejected]
        rejected_list = [l for l in leaves if l.rejected]
        pending_list  = [l for l in leaves if not l.approved and not l.rejected]

        # per-type breakdown
        type_counts = {}
        for lv in leaves:
            t = (lv.leave_type or "Others").title()
            type_counts[t] = type_counts.get(t, 0) + 1

        # big stat boxes
        stat_data = [[
            Paragraph(f"Total Applications\n{len(leaves)}",
                      S("S0", fontName="Helvetica-Bold", fontSize=13, textColor=PRIMARY, alignment=TA_CENTER)),
            Paragraph(f"Approved\n{len(approved_list)}",
                      S("S1", fontName="Helvetica-Bold", fontSize=13, textColor=SUCCESS, alignment=TA_CENTER)),
            Paragraph(f"Pending\n{len(pending_list)}",
                      S("S2", fontName="Helvetica-Bold", fontSize=13, textColor=WARNING, alignment=TA_CENTER)),
            Paragraph(f"Rejected\n{len(rejected_list)}",
                      S("S3", fontName="Helvetica-Bold", fontSize=13, textColor=DANGER, alignment=TA_CENTER)),
            Paragraph(f"Days (this period)\n{total_days_in_period}",
                      S("S4", fontName="Helvetica-Bold", fontSize=13, textColor=ACCENT, alignment=TA_CENTER)),
        ]]
        stat_bg = [LIGHT_BG,
                   colors.HexColor("#EAFAF1"),
                   colors.HexColor("#FEF9E7"),
                   colors.HexColor("#FDEDEC"),
                   colors.HexColor("#EBF5FB")]
        st = Table(stat_data, colWidths=[3.4*cm]*5)
        st.setStyle(TableStyle([
            *[("BACKGROUND", (i, 0), (i, 0), stat_bg[i]) for i in range(5)],
            ("BOX",          (0, 0), (-1,-1), 0.5, colors.HexColor("#C8D8E8")),
            ("INNERGRID",    (0, 0), (-1,-1), 0.5, colors.HexColor("#C8D8E8")),
            ("TOPPADDING",   (0, 0), (-1,-1), 13),
            ("BOTTOMPADDING",(0, 0), (-1,-1), 13),
            ("ALIGN",        (0, 0), (-1,-1), "CENTER"),
            ("VALIGN",       (0, 0), (-1,-1), "MIDDLE"),
        ]))
        story += [st, Spacer(1, 12)]

        # per-type breakdown mini table
        if type_counts:
            story.append(Paragraph(
                "Breakdown by Leave Type",
                S("Brkdwn", fontName="Helvetica-Bold", fontSize=9, textColor=MUTED, spaceAfter=5),
            ))
            type_rows = [[Paragraph("Leave Type", hdr_cell),
                          Paragraph("Applications", hdr_cell)]]
            for t, cnt in sorted(type_counts.items()):
                col = LEAVE_TYPE_COLORS.get(t.lower(), TEAL)
                type_rows.append([
                    Paragraph(t, S(f"TC_{t}", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=col)),
                    Paragraph(str(cnt), ctr),
                ])
            bt = Table(type_rows, colWidths=[6*cm, 4*cm], hAlign="LEFT")
            bt.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), PRIMARY),
                ("ROWBACKGROUNDS",(0, 1), (-1,-1), [LIGHT_BG, WHITE]),
                ("GRID",          (0, 0), (-1,-1), 0.35, colors.HexColor("#C8D8E8")),
                ("TOPPADDING",    (0, 0), (-1,-1), 5),
                ("BOTTOMPADDING", (0, 0), (-1,-1), 5),
                ("LEFTPADDING",   (0, 0), (-1,-1), 8),
                ("VALIGN",        (0, 0), (-1,-1), "MIDDLE"),
            ]))
            story.append(bt)

    doc.build(
        story,
        onFirstPage=_make_header_footer(student, report_date),
        onLaterPages=_make_header_footer(student, report_date),
    )
    buf.seek(0)
    return buf