from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .....forms.EmailResetForm import EmailResetForm
from .changeEmail import changeEmail


@login_required
def reset_email(request):
    if request.method == 'POST':
        user = request.user
        form = EmailResetForm(request.POST, instance=user)
        print(request.POST)
        if form.is_valid():
            user.emailChangeRequest = request.POST['email']
            user.save()
            changeEmail(request, user, request.POST['email'])
            messages.success(request, 'Email has been sent to the new email to confirm the change.')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid email. Please correct the errors below.')
    else:
        form = EmailResetForm(instance=request.user)

    return render(request, 'security/detailsChange/email_reset.html', {'form': form})
