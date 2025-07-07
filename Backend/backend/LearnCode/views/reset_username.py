from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms.UsernameResetForm import UsernameResetForm  # adjust if needed

@login_required
def reset_username(request):
    if request.method == 'POST':
        form = UsernameResetForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully changed username.')
            return redirect('profile')  # ✅ FIXED: this should be the URL name, not `redirect(request, ...)`
        else:
            messages.error(request, 'Invalid username. Please correct the errors below.')
    else:
        form = UsernameResetForm(instance=request.user)
    
    return render(request, 'username_reset.html', {'form': form})
