import re
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from ...models import Theory

def theory_detail(request, theory_id):
    # Fetch theory
    theory = get_object_or_404(Theory, pk=theory_id)

    # Fetch all examples related to this theory and map them by number
    examples = {ex.number: ex.content for ex in theory.examples.all()}

    # Function to replace [[example:n]] placeholders with HTML
    def replace_example(match):
        num = int(match.group(1))
        content = examples.get(num, f"[Missing example {num}]")
        return f'''
            <div class="theory-example">
                <strong>Example {num}:</strong>
                <pre>{content}</pre>
            </div>
        '''

    # Replace all placeholders in the content
    content_with_examples = re.sub(r"\[\[example:(\d+)\]\]", replace_example, theory.content)

    return render(request, "theory.html", {
        "theory": theory,
        "content_with_examples": mark_safe(content_with_examples),
    })
