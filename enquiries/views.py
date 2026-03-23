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
    property_id = request.GET.get('property') or request.POST.get('property')
    agent_id    = request.GET.get('agent') or request.POST.get('agent')

    # Map ?service= values that come from service pages to enquiry_type
    _SERVICE_TYPE_MAP = {
        'legal': 'legal', 'legal_homeloan': 'legal',
        'security': 'security',
        'plumbing': 'home_service', 'electrical': 'home_service',
        'painting': 'home_service', 'cleaning': 'home_service',
        'carpentry': 'home_service', 'ac': 'home_service',
        'pest_control': 'home_service', 'renovation': 'home_service',
        'home_service': 'home_service',
        'home_loan': 'home_loan',
    }

    form = EnquiryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        enquiry = form.save(commit=False)
        if request.user.is_authenticated:
            enquiry.user = request.user
        if property_id:
            enquiry.property_id = property_id
        if agent_id:
            enquiry.agent_id = agent_id
        # Append service detail to message if provided via hidden field
        service_detail = request.POST.get('service_detail', '').strip()
        if service_detail and enquiry.message:
            enquiry.message = f'[Service: {service_detail}]\n\n{enquiry.message}'
        elif service_detail:
            enquiry.message = f'[Service: {service_detail}]'
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
