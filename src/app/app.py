from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)

REPORT_PATH = os.path.abspath("reports/drift_report.html")

@app.route("/")
def view_report():
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report_html = f.read()
        return render_template_string(report_html)
    else:
        return "<h2>⚠️ Drift report not found.</h2>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
