from io import BytesIO

from flask import Flask, Response, jsonify, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from uplink_model import ETA_TARGET, I_FACTOR, SPEEDS_KMH, build_conclusions_report, build_dashboard_payload


app = Flask(__name__)


def _read_filter_values() -> tuple[int, float, float, float]:
    speed = request.args.get("speed", default=15, type=int)
    activity = request.args.get("activity", default=0.50, type=float)
    eta_target = request.args.get("eta", default=ETA_TARGET, type=float)
    intercell = request.args.get("i", default=I_FACTOR, type=float)

    if speed not in SPEEDS_KMH:
        speed = 15
    activity = min(max(activity, 0.40), 0.70)
    eta_target = min(max(eta_target, 0.65), 0.80)
    intercell = min(max(intercell, 0.50), 0.85)
    return speed, round(activity, 2), round(eta_target, 2), round(intercell, 2)


@app.route("/")
def index():
    speed, activity, eta_target, intercell = _read_filter_values()
    payload = build_dashboard_payload(
        selected_speed=speed,
        selected_activity=activity,
        eta_tgt=eta_target,
        i_factor=intercell,
    )
    return render_template("index.html", payload=payload)


@app.route("/api/uplink")
def api_uplink():
    speed, activity, eta_target, intercell = _read_filter_values()
    payload = build_dashboard_payload(
        selected_speed=speed,
        selected_activity=activity,
        eta_tgt=eta_target,
        i_factor=intercell,
    )
    return jsonify(payload)


@app.route("/export/conclusions.html")
def export_conclusions_html():
    speed, activity, eta_target, intercell = _read_filter_values()
    payload = build_dashboard_payload(
        selected_speed=speed,
        selected_activity=activity,
        eta_tgt=eta_target,
        i_factor=intercell,
    )
    report = build_conclusions_report(payload)
    html = render_template("conclusions_export.html", report=report, payload=payload)
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": "attachment; filename=conclusiones_uplink.html"},
    )


@app.route("/export/conclusions.pdf")
def export_conclusions_pdf():
    speed, activity, eta_target, intercell = _read_filter_values()
    payload = build_dashboard_payload(
        selected_speed=speed,
        selected_activity=activity,
        eta_tgt=eta_target,
        i_factor=intercell,
    )
    report = build_conclusions_report(payload)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    y = height - 48

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(48, y, report["title"])
    y -= 24
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, y, f"Generado: {report['generated_at']}")
    y -= 22

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(48, y, "Resumen:")
    y -= 16
    pdf.setFont("Helvetica", 10)
    for line in report["summary_lines"]:
        pdf.drawString(56, y, f"- {line}")
        y -= 14

    y -= 6
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(48, y, "Conclusiones operativas:")
    y -= 16
    pdf.setFont("Helvetica", 10)
    for item in report["conclusions"]:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(56, y, item["title"])
        y -= 13
        pdf.setFont("Helvetica", 10)
        text = pdf.beginText(64, y)
        text.setLeading(12)
        words = item["detail"].split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 10) > (width - 96):
                text.textLine(line)
                line = word
            else:
                line = test_line
        if line:
            text.textLine(line)
        pdf.drawText(text)
        y = text.getY() - 8
        if y < 80:
            pdf.showPage()
            y = height - 48

    pdf.save()
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="conclusiones_uplink.pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)