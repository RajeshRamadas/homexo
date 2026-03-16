"""
enquiries/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import EnquiryForm
from .models import Enquiry


def enquiry_create(request):
    property_id = request.GET.get('property')
    agent_id    = request.GET.get('agent')

    form = EnquiryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        enquiry = form.save(commit=False)
        if request.user.is_authenticated:
            enquiry.user = request.user
        if property_id:
            enquiry.property_id = property_id
        if agent_id:
            enquiry.agent_id = agent_id
        enquiry.save()

        # Email notification
        try:
            send_mail(
                subject=f'New Enquiry from {enquiry.name}',
                message=f'Name: {enquiry.name}\nEmail: {enquiry.email}\nPhone: {enquiry.phone}\nType: {enquiry.enquiry_type}\nBudget: {enquiry.budget}\n\nMessage:\n{enquiry.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ENQUIRY_NOTIFICATION_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Thank you! We will contact you shortly.')
        return redirect('pages:home')

    return render(request, 'enquiries/form.html', {'form': form})


def enquiry_success(request):
    return render(request, 'enquiries/success.html')
