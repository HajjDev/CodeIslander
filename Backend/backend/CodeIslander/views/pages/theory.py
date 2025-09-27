from django.shortcuts import render, get_object_or_404
from ...models import Theory

def theory_detail(request, theory_id):
    """
    Display a single theory page.
    """
    theory = get_object_or_404(Theory, pk=theory_id)
    return render(request, "theory.html", {"theory": theory})