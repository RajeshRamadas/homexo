"""
enquiries/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
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

        # ── Admin notification email ─────────────────────────────────────────
        try:
            property_line = ''
            if enquiry.property:
                property_line = f'<tr><td style="padding:6px 0;color:#888;">Property</td><td style="padding:6px 0;"><strong>{enquiry.property}</strong></td></tr>'

            admin_html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px;">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
  <div style="background:#1a2e44;padding:24px 32px;">
    <h2 style="margin:0;color:#fff;font-size:18px;">&#128276; New Enquiry — Homexo</h2>
  </div>
  <div style="padding:28px 32px;">
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <tr><td style="padding:6px 0;color:#888;">Name</td><td style="padding:6px 0;"><strong>{enquiry.name}</strong></td></tr>
      <tr><td style="padding:6px 0;color:#888;">Phone</td><td style="padding:6px 0;"><a href="tel:{enquiry.phone}" style="color:#1a2e44;">{enquiry.phone}</a></td></tr>
      <tr><td style="padding:6px 0;color:#888;">Email</td><td style="padding:6px 0;"><a href="mailto:{enquiry.email}" style="color:#1a2e44;">{enquiry.email}</a></td></tr>
      <tr><td style="padding:6px 0;color:#888;">Type</td><td style="padding:6px 0;">{enquiry.get_enquiry_type_display()}</td></tr>
      {property_line}
      <tr><td style="padding:6px 0;color:#888;">Budget</td><td style="padding:6px 0;">{enquiry.budget or '—'}</td></tr>
    </table>
    {'<div style="margin-top:20px;padding:16px;background:#f9f9f9;border-left:3px solid #1a2e44;font-size:14px;"><em>' + enquiry.message + '</em></div>' if enquiry.message else ''}
    <a href="http://127.0.0.1:8000/admin/enquiries/enquiry/{enquiry.id}/change/"
       style="display:inline-block;margin-top:24px;padding:10px 20px;background:#1a2e44;color:#fff;border-radius:4px;text-decoration:none;font-size:13px;">View in Admin →</a>
  </div>
  <div style="padding:16px 32px;background:#f5f5f5;font-size:11px;color:#aaa;">Homexo — automated notification</div>
</div>
</body></html>"""

            admin_plain = (
                f"New enquiry from {enquiry.name}\n"
                f"Phone: {enquiry.phone}\nEmail: {enquiry.email}\n"
                f"Type: {enquiry.get_enquiry_type_display()}\nBudget: {enquiry.budget}\n\n"
                f"{enquiry.message}"
            )
            msg = EmailMultiAlternatives(
                subject=f'[Homexo] New Enquiry from {enquiry.name}',
                body=admin_plain,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.ENQUIRY_NOTIFICATION_EMAIL],
                reply_to=[enquiry.email],
            )
            msg.attach_alternative(admin_html, 'text/html')
            msg.send(fail_silently=True)
        except Exception:
            pass

        # ── Auto-reply to the lead ────────────────────────────────────────────
        try:
            reply_html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px;">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
  <div style="background:#1a2e44;padding:24px 32px;">
    <h2 style="margin:0;color:#fff;font-size:18px;">Thank you, {enquiry.name}!</h2>
  </div>
  <div style="padding:28px 32px;font-size:14px;color:#333;line-height:1.7;">
    <p>We've received your enquiry and our team will get back to you shortly.</p>
    <p style="margin-top:20px;">Here's a summary of what you submitted:</p>
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px;">
      <tr><td style="padding:5px 0;color:#888;">Type</td><td>{enquiry.get_enquiry_type_display()}</td></tr>
      <tr><td style="padding:5px 0;color:#888;">Budget</td><td>{enquiry.budget or '—'}</td></tr>
      {'<tr><td style="padding:5px 0;color:#888;">Message</td><td>' + enquiry.message + '</td></tr>' if enquiry.message else ''}
    </table>
    <p style="margin-top:24px;">In the meantime, feel free to browse more properties at <a href="https://homexo.in" style="color:#1a2e44;">homexo.in</a>.</p>
    <p>— The Homexo Team</p>
  </div>
  <div style="padding:16px 32px;background:#f5f5f5;font-size:11px;color:#aaa;">You're receiving this because you submitted an enquiry on Homexo.</div>
</div>
</body></html>"""

            reply_plain = (
                f"Hi {enquiry.name},\n\nThank you for your enquiry. "
                f"Our team will contact you shortly.\n\n— The Homexo Team"
            )
            reply_msg = EmailMultiAlternatives(
                subject='We received your enquiry — Homexo',
                body=reply_plain,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[enquiry.email],
            )
            reply_msg.attach_alternative(reply_html, 'text/html')
            reply_msg.send(fail_silently=True)
        except Exception:
            pass

        messages.success(request, 'Thank you! We will contact you shortly.')
        return redirect('pages:home')

    return render(request, 'enquiries/form.html', {'form': form})


def enquiry_success(request):
    return render(request, 'enquiries/success.html')
