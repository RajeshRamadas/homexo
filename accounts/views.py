"""
accounts/views.py
Registration, login, logout, profile views.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .forms import RegisterForm, LoginForm, ProfileUpdateForm, ProfileCompleteForm, AdvocateRegisterForm
from .models import User, PhoneOTP, Notification
from .sms import generate_otp, send_otp_sms


def register_view(request):
    if request.user.is_authenticated:
        return redirect('pages:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False   # inactive until email confirmed
        user.save()

        token = signing.dumps(user.pk, salt='email-confirm')
        confirm_url = request.build_absolute_uri(
            reverse('accounts:email_confirm', args=[token])
        )
        subject = render_to_string('accounts/email_confirm_subject.txt').strip()
        message = render_to_string('accounts/email_confirm_email.html', {
            'user': user,
            'confirm_url': confirm_url,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return redirect('accounts:email_confirm_sent')

    return render(request, 'accounts/register.html', {'form': form})


def advocate_register_view(request):
    if request.user.is_authenticated:
        return redirect('pages:home')

    form = AdvocateRegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False # Admin must approve
        user.save()

        messages.success(request, "Your application to join as an Advocate has been received! Our team will verify your credentials and activate your account shortly.")
        return redirect('pages:home')

    return render(request, 'accounts/advocate_register.html', {'form': form})



def email_confirm_sent_view(request):
    return render(request, 'accounts/email_confirm_sent.html')


def email_confirm_view(request, token):
    try:
        pk = signing.loads(token, salt='email-confirm', max_age=86400)  # 24 h
        user = User.objects.get(pk=pk)
        if not user.is_verified:
            user.is_active = True
            user.is_verified = True
            user.save(update_fields=['is_active', 'is_verified'])
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'Welcome to HOMEXO, {user.first_name}! Your email has been confirmed.')
        return redirect('pages:home')
    except signing.SignatureExpired:
        return render(request, 'accounts/email_confirm_done.html', {'expired': True})
    except (signing.BadSignature, User.DoesNotExist):
        return render(request, 'accounts/email_confirm_done.html', {'invalid': True})


def resend_confirmation_view(request):
    """Allow an unconfirmed user to request a new confirmation email."""
    if request.user.is_authenticated:
        return redirect('pages:home')

    sent = False
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email, is_active=False, is_verified=False)
            token = signing.dumps(user.pk, salt='email-confirm')
            confirm_url = request.build_absolute_uri(
                reverse('accounts:email_confirm', args=[token])
            )
            subject = render_to_string('accounts/email_confirm_subject.txt').strip()
            message = render_to_string('accounts/email_confirm_email.html', {
                'user': user,
                'confirm_url': confirm_url,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            sent = True
        except User.DoesNotExist:
            # Don't reveal whether the email exists
            sent = True

    return render(request, 'accounts/resend_confirmation.html', {'sent': sent, 'error': error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('pages:home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name}!')
        next_url = request.GET.get('next', 'pages:home')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('pages:home')


@login_required
def profile_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_notifications_read(request):
    """POST — mark all unread notifications for current user as read."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    from django.http import HttpResponseNotAllowed
    return HttpResponseNotAllowed(['POST'])


@login_required
def profile_update_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile_update.html', {'form': form})


# ── Profile Completion (post-social-auth popup) ──────────────────────────────

@login_required
def profile_complete_view(request):
    """AJAX endpoint for the profile-completion modal shown after social signup."""
    user = request.user
    if request.method == 'POST':
        form = ProfileCompleteForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_complete = True
            user.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'ok': True})
            messages.success(request, 'Profile updated!')
            return redirect('pages:home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                errors = {f: e.get_json_data() for f, e in form.errors.items()}
                return JsonResponse({'ok': False, 'errors': errors}, status=400)
    return redirect('pages:home')


# ── Phone OTP Login ───────────────────────────────────────────────────────────

def phone_login_request_view(request):
    """Step 1: enter phone number, receive OTP."""
    if request.user.is_authenticated:
        return redirect('pages:home')

    error = None
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if not phone:
            error = 'Please enter your phone number.'
        else:
            try:
                user = User.objects.get(phone=phone, is_active=True)
            except User.DoesNotExist:
                error = 'No active account found with this phone number. Please register first.'

            if not error:
                # Invalidate previous unused OTPs for this phone
                PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

                otp = generate_otp()
                PhoneOTP.objects.create(phone=phone, otp=otp)
                sent = send_otp_sms(phone, otp)

                if not sent:
                    error = 'Could not send OTP. Please try again.'
                else:
                    request.session['otp_phone'] = phone
                    return redirect('accounts:phone_login_verify')

    return render(request, 'accounts/phone_login.html', {'error': error})


def phone_login_verify_view(request):
    """Step 2: enter OTP, get logged in."""
    if request.user.is_authenticated:
        return redirect('pages:home')

    phone = request.session.get('otp_phone')
    if not phone:
        return redirect('accounts:phone_login')

    error = None
    if request.method == 'POST':
        entered = request.POST.get('otp', '').strip()
        try:
            record = PhoneOTP.objects.filter(
                phone=phone, is_used=False
            ).latest('created_at')
        except PhoneOTP.DoesNotExist:
            error = 'OTP not found. Please request a new one.'
            record = None

        if record:
            if not record.is_valid:
                error = 'OTP has expired. Please request a new one.'
            elif entered != record.otp:
                error = 'Incorrect OTP. Please try again.'
            else:
                record.is_used = True
                record.save(update_fields=['is_used'])
                del request.session['otp_phone']
                try:
                    user = User.objects.get(phone=phone, is_active=True)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('pages:home')
                except User.DoesNotExist:
                    error = 'Account not found.'

    return render(request, 'accounts/phone_otp.html', {'phone': phone, 'error': error})
