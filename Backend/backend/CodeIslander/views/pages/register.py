from django.shortcuts import render, redirect
from ...forms import CustomUserCreationForm
from django.contrib import messages
from ..security.register.activateEmail import activateEmail
from ...utils import logout_required
from ...models import Theory, Exercise, QCM


@logout_required
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = False
            user.save()
            default_exercises = Exercise.objects.filter(pk__in=[1])
            default_theory = Theory.objects.filter(pk__in=[1])
            default_qcm = QCM.objects.filter(pk__in=[])
            user.unlockedExercises.set(default_exercises)
            user.unlockedTheory.set(default_theory)
            user.unlockedQCM.set(default_qcm)
            
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})