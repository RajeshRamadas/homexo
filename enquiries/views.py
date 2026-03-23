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

    post_data = request.POST.copy() if request.method == 'POST' else None
    if post_data and not post_data.get('enquiry_type'):
        post_data['enquiry_type'] = 'general'
    form = EnquiryForm(post_data)
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
            prop = enquiry.property
            property_block = ''
            property_plain = ''
            if prop:
                prop_url = request.build_absolute_uri(prop.get_absolute_url()) if hasattr(prop, 'get_absolute_url') else ''
                property_block = f'''
    <tr><td colspan="2" style="padding-top:16px;"></td></tr>
    <tr><td colspan="2" style="padding:10px 14px;background:#f0f4f8;border-left:3px solid #4A90C4;">
      <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#4A90C4;margin-bottom:6px;">Property Enquired</div>
      <div style="font-size:15px;font-weight:600;color:#1a2e44;">{prop}</div>
      <div style="font-size:13px;color:#666;margin-top:3px;">{getattr(prop, "locality", "")}{", " + getattr(prop, "city", "") if getattr(prop, "city", "") else ""}</div>
      <div style="font-size:14px;color:#1a2e44;font-weight:500;margin-top:4px;">{getattr(prop, "display_price", "")}</div>
      {"<a href=\"" + prop_url + "\" style=\"font-size:12px;color:#4A90C4;text-decoration:none;display:inline-block;margin-top:6px;\">View Listing →</a>" if prop_url else ""}
    </td></tr>'''
                property_plain = (
                    f"\nProperty: {prop}\n"
                    f"Location: {getattr(prop, 'locality', '')} {getattr(prop, 'city', '')}\n"
                    f"Price: {getattr(prop, 'display_price', '')}\n"
                    + (f"Link: {prop_url}\n" if prop_url else "")
                )

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
      <tr><td style="padding:6px 0;color:#888;">Budget</td><td style="padding:6px 0;">{enquiry.budget or '—'}</td></tr>
      {property_block}
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
                f"Type: {enquiry.get_enquiry_type_display()}\nBudget: {enquiry.budget}\n"
                f"{property_plain}\n{enquiry.message}"
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
            prop = enquiry.property
            prop_section = ''
            prop_plain = ''
            if prop:
                prop_url = request.build_absolute_uri(prop.get_absolute_url()) if hasattr(prop, 'get_absolute_url') else ''
                prop_section = f'''
    <div style="margin-top:20px;padding:14px 16px;background:#f0f4f8;border-left:3px solid #4A90C4;border-radius:2px;">
      <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#4A90C4;margin-bottom:6px;">Property You Enquired About</div>
      <div style="font-size:15px;font-weight:600;color:#1a2e44;">{prop}</div>
      <div style="font-size:13px;color:#666;margin-top:2px;">{getattr(prop, "locality", "")}{", " + getattr(prop, "city", "") if getattr(prop, "city", "") else ""}</div>
      <div style="font-size:14px;color:#1a2e44;font-weight:500;margin-top:4px;">{getattr(prop, "display_price", "")}</div>
      {"<a href=\"" + prop_url + "\" style=\"font-size:12px;color:#4A90C4;text-decoration:none;display:inline-block;margin-top:6px;\">View Listing →</a>" if prop_url else ""}
    </div>'''
                prop_plain = f"\nProperty: {prop}\nLocation: {getattr(prop, 'locality', '')} {getattr(prop, 'city', '')}\nPrice: {getattr(prop, 'display_price', '')}\n"

            reply_html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px;">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
  <div style="background:#1a2e44;padding:24px 32px;">
    <h2 style="margin:0;color:#fff;font-size:18px;">Thank you, {enquiry.name}!</h2>
  </div>
  <div style="padding:28px 32px;font-size:14px;color:#333;line-height:1.7;">
    <p>We've received your enquiry and our team will get back to you shortly.</p>
    {prop_section}
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
                f"Our team will contact you shortly.\n"
                f"{prop_plain}\n— The Homexo Team"
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
