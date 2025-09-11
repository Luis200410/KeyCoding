from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm, ProfileForm, ProfileDetailsForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created and you are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.success(self.request, 'Welcome back! You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    # Ensure immediate redirect to landing page on GET/POST
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out.')
        return super().dispatch(request, *args, **kwargs)


def logout_immediate(request):
    messages.info(request, 'You have been logged out.')
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


@login_required
def my_account(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=user)
        profile_form = ProfileDetailsForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('my_account')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = ProfileForm(instance=user)
        profile_form = ProfileDetailsForm(instance=profile)
    return render(request, 'accounts/my_account.html', {"user_form": user_form, "profile_form": profile_form})
