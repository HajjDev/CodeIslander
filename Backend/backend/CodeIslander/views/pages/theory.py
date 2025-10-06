import re
import csv
from io import StringIO
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from ...models import Theory

def csv_to_html_table(csv_text):
    """Convert CSV text to an HTML table."""
    f = StringIO(csv_text.strip())
    reader = csv.reader(f)

    html = "<table style='border-collapse: collapse; margin: 1em 0; width: 100%;'>"

    # Headers
    headers = next(reader, None)
    if headers:
        html += "<thead><tr>"
        for h in headers:
            html += f"<th style='border: 1px solid #ccc; padding: 8px; background: #f5f5f5; text-align: left;'>{h}</th>"
        html += "</tr></thead>"

    # Body
    html += "<tbody>"
    for row in reader:
        html += "<tr>"
        for c in row:
            html += f"<td style='border: 1px solid #ccc; padding: 8px;'>{c}</td>"
        html += "</tr>"
    html += "</tbody></table>"

    return html

def theory_detail(request, theory_id):
    theory = get_object_or_404(Theory, pk=theory_id)

    # Examples
    examples = {ex.number: ex.content for ex in theory.examples.all()}

    # Tables (CSV to HTML conversion later)
    tables = {tb.number: tb.csv_content for tb in theory.tables.all()}

    def replace_example(match):
        num = int(match.group(1))
        content = examples.get(num, f"[Missing example {num}]")
        return f'''
            <div class="theory-example">
                <strong>Example {num}:</strong>
                <pre>{content}</pre>
            </div>
        '''

    def replace_table(match):
        num = int(match.group(1))
        csv_text = tables.get(num)
        if not csv_text:
            return f"[Missing table {num}]"
        return csv_to_html_table(csv_text)

    # Process content
    content = theory.content
    content = re.sub(r"\[\[example:(\d+)\]\]", replace_example, content)
    content = re.sub(r"\[\[table:(\d+)\]\]", replace_table, content)

    return render(request, "theory.html", {
        "theory": theory,
        "content_with_examples": mark_safe(content),
    })
