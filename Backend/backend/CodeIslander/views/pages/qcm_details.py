from django.shortcuts import render, get_object_or_404
from ...models import QCM

def qcm_detail(request, qcm_id):
    qcm = get_object_or_404(QCM, pk=qcm_id)

    # Prepare questions with multiple-correct flag
    questions_data = []
    for question in qcm.questions.prefetch_related("choices").all():
        correct_count = question.choices.filter(is_correct=True).count()
        questions_data.append({
            "question": question,
            "choices": question.choices.all(),
            "is_multiple": correct_count > 1
        })

    if request.method == "POST":
        # handle form submission (score calculation)
        total = len(questions_data)
        score = 0
        details = []

        for qd in questions_data:
            question = qd["question"]
            correct_ids = set(c.id for c in qd["choices"] if c.is_correct)
            if qd["is_multiple"]:
                selected_ids = set(map(int, request.POST.getlist(f"question_{question.id}")))
            else:
                val = request.POST.get(f"question_{question.id}")
                selected_ids = {int(val)} if val else set()

            is_correct = selected_ids == correct_ids
            if is_correct:
                score += 1

            details.append({
                "question": question,
                "selected_ids": selected_ids,
                "correct_ids": correct_ids,
                "choices": qd["choices"],
                "is_correct": is_correct
            })

        return render(request, "qcm_result.html", {
            "qcm": qcm,
            "score": score,
            "total": total,
            "details": details
        })

    return render(request, "qcm_detail.html", {"qcm": qcm, "questions_data": questions_data})
