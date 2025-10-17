import re
from io import StringIO
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape
from ...models import Theory # Make sure this import path is correct for your project

def smarter_csv_parser(csv_text):
    """
    A robust custom parser that correctly handles the user's specific data format.
    It splits by commas, but intelligently ignores commas that are inside:
    1. Double quotes ("...")
    2. Brackets, parentheses, or braces ([...], (...), {...})
    
    This allows data like ['a', 'b', 'c'] and "Hello, world" to be treated as single fields.
    """
    lines = csv_text.strip().splitlines()
    parsed_data = []

    for line in lines:
        row = []
        start_index = 0
        in_quotes = False
        depth = 0 # For brackets/parentheses/braces

        for i, char in enumerate(line):
            # Toggle in_quotes state if we find a double quote
            if char == '"':
                in_quotes = not in_quotes
            
            # Track depth of brackets only if we are NOT inside quotes
            if not in_quotes:
                if char in "([{":
                    depth += 1
                elif char in ")]}":
                    depth -= 1
            
            # A comma is a delimiter ONLY if we are not in quotes and not inside any brackets.
            if char == ',' and not in_quotes and depth == 0:
                cell = line[start_index:i].strip()
                # If the cell is quoted, remove the outer quotes
                if len(cell) > 1 and cell.startswith('"') and cell.endswith('"'):
                    cell = cell[1:-1]
                row.append(cell)
                start_index = i + 1
        
        # Add the final cell of the row
        last_cell = line[start_index:].strip()
        if len(last_cell) > 1 and last_cell.startswith('"') and last_cell.endswith('"'):
            last_cell = last_cell[1:-1]
        row.append(last_cell)
        parsed_data.append(row)
    
    return parsed_data

def csv_to_html_table(csv_text):
    """
    Converts CSV text to an HTML table using our new, smarter parser.
    """
    # Use the new parser that is tailored to the data format
    parsed_data = smarter_csv_parser(csv_text)
    
    if not parsed_data:
        return ""

    html = "<table style='border-collapse: collapse; margin: 1em 0; width: 100%;'>"
    
    try:
        # Headers are the first row
        headers = parsed_data[0]
        html += "<thead><tr>"
        for h in headers:
            html += f"<th style='border: 1px solid #ccc; padding: 8px; background: #f5f5f5; text-align: left;'>{h}</th>"
        html += "</tr></thead>"

        # Body is the rest of the rows
        html += "<tbody>"
        for row in parsed_data[1:]:
            html += "<tr>"
            for c in row:
                # Escape the content to prevent HTML injection issues, e.g., <script>
                escaped_c = escape(c)
                html += f"<td style='border: 1px solid #ccc; padding: 8px;'>{escaped_c}</td>"
            html += "</tr>"
        html += "</tbody>"
    except IndexError:
        # Handles empty or malformed CSV
        pass

    html += "</table>"
    return html

# --- The rest of your view remains the same ---

def theory_detail(request, theory_id):
    theory = get_object_or_404(Theory, pk=theory_id)

    examples = {ex.number: ex.content for ex in theory.examples.all()}
    tables = {tb.number: tb.csv_content for tb in theory.tables.all()}

    def replace_example(match):
        language = match.group(1)
        number = int(match.group(2))
        content = examples.get(number, f"[Missing example {number}]")
        escaped_content = escape(content)
        if language:
            return f'<pre><code class="{language}">{escaped_content}</code></pre>'
        else:
            return f'<div class="theory-example-text">{escaped_content}</div>'

    def replace_table(match):
        num = int(match.group(1))
        csv_text = tables.get(num)
        if not csv_text:
            return f"<p>[Missing table {num}]</p>"
        # This now uses the correct, smart parser
        return csv_to_html_table(csv_text)

    content = theory.content
    content = re.sub(r"\[\[example:(?:(\w+):)?(\d+)\]\]", replace_example, content)
    content = re.sub(r"\[\[table:(\d+)\]\]", replace_table, content)

    return render(request, "theory.html", {
        "theory": theory,
        "content_with_examples": mark_safe(content),
    })