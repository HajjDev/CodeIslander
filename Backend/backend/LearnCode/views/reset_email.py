from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms.EmailResetForm import EmailResetForm  


@login_required
def reset_email(request):
    if request.method == 'POST':
        form = EmailResetForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid email. Please correct the errors below.')
    else:
        form = EmailResetForm(instance=request.user)

    return render(request, 'email_reset.html', {'form': form})
