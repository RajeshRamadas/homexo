"""
enquiries/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from .forms import EnquiryForm
from .models import Enquiry, EnquiryActivity


def _can_access_dashboard(user):
    """Returns True for superusers, admins and customer_support agents."""
    return user.is_authenticated and (
        user.is_superuser or
        getattr(user, 'role', None) in ('admin', 'customer_support')
    )


def dashboard_access_required(view_func):
    """Decorator: allow only admin / customer_support roles."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _can_access_dashboard(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped


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

    # ── Determine source label from hidden field or HTTP Referer ─────────────
    _PAGE_SOURCE_MAP = {
        'legal':          'Legal Services Page',
        'security':       'Security Services Page',
        'home_service':   'Home Services Page',
        'home_loan':      'Home Loan Page',
        'legal_homeloan': 'Legal + Home Loan Page',
        'nri':            'NRI Services Page',
        'contact':        'Contact Page',
        'property':       'Property Detail Page',
        'footer':         'Footer CTA',
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

        # ── Capture source ────────────────────────────────────────────────────
        raw_source = request.POST.get('source', '').strip()
        if raw_source:
            enquiry.source = _PAGE_SOURCE_MAP.get(raw_source, raw_source)
        else:
            referer = request.META.get('HTTP_REFERER', '')
            if '/legal-homeloan' in referer or 'legal_homeloan' in referer:
                enquiry.source = 'Legal + Home Loan Page'
            elif '/legal' in referer:
                enquiry.source = 'Legal Services Page'
            elif '/security' in referer:
                enquiry.source = 'Security Services Page'
            elif '/home-service' in referer or '/home_service' in referer:
                enquiry.source = 'Home Services Page'
            elif '/home-loan' in referer or '/home_loan' in referer:
                enquiry.source = 'Home Loan Page'
            elif '/nri' in referer:
                enquiry.source = 'NRI Services Page'
            elif '/contact' in referer:
                enquiry.source = 'Contact Page'
            elif '/properties/' in referer:
                enquiry.source = 'Property Detail Page'
            elif referer:
                enquiry.source = 'Website (other)'
            else:
                enquiry.source = 'Direct / Unknown'

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


# ── Enquiry Dashboard ─────────────────────────────────────────────────────────

@dashboard_access_required
def enquiry_dashboard(request):
    qs = Enquiry.objects.select_related('property', 'assigned_to').all()

    # ── Filters ───────────────────────────────────────────────────────────────
    status_filter = request.GET.get('status', '')
    type_filter   = request.GET.get('enquiry_type', '')
    source_filter = request.GET.get('source', '')
    search        = request.GET.get('q', '').strip()

    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(enquiry_type=type_filter)
    if source_filter:
        qs = qs.filter(source__icontains=source_filter)
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(message__icontains=search)
        )

    # ── Stats ─────────────────────────────────────────────────────────────────
    total     = Enquiry.objects.count()
    new_count = Enquiry.objects.filter(status='new').count()
    contacted = Enquiry.objects.filter(status='contacted').count()
    qualified = Enquiry.objects.filter(status='qualified').count()
    closed    = Enquiry.objects.filter(status='closed').count()

    # Source breakdown for chart
    source_data = (
        Enquiry.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Type breakdown
    type_data = (
        Enquiry.objects.values('enquiry_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Follow-ups due today or overdue
    now = timezone.now()
    followup_due = Enquiry.objects.filter(
        follow_up_at__lte=now, status__in=['new', 'contacted', 'qualified']
    ).count()

    context = {
        'enquiries':    qs,
        'status_filter': status_filter,
        'type_filter':   type_filter,
        'source_filter': source_filter,
        'search':        search,
        'status_choices': Enquiry.Status.choices,
        'type_choices':   Enquiry.EnquiryType.choices,
        'stats': {
            'total':     total,
            'new':       new_count,
            'contacted': contacted,
            'qualified': qualified,
            'closed':    closed,
        },
        'source_data':   list(source_data),
        'type_data':     list(type_data),
        'followup_due':  followup_due,
    }
    return render(request, 'enquiries/dashboard.html', context)


@dashboard_access_required
def enquiry_update_status(request, pk):
    """AJAX endpoint: update status + notes + follow_up_at, log everything."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    enquiry = get_object_or_404(Enquiry, pk=pk)
    new_status   = request.POST.get('status', '').strip()
    follow_up_at = request.POST.get('follow_up_at', '').strip()
    notes        = request.POST.get('notes', None)
    assigned_raw = request.POST.get('assigned_to', '').strip()

    valid_statuses = [s[0] for s in Enquiry.Status.choices]
    update_fields  = ['updated_at']
    logs = []

    if new_status and new_status in valid_statuses and new_status != enquiry.status:
        old_label = enquiry.get_status_display()
        enquiry.status = new_status
        new_label = enquiry.get_status_display()
        update_fields.append('status')
        logs.append(EnquiryActivity(
            enquiry=enquiry, actor=request.user,
            kind=EnquiryActivity.Kind.STATUS_CHANGE,
            body=f'Status changed from "{old_label}" → "{new_label}"',
        ))

    if follow_up_at:
        try:
            new_dt = timezone.datetime.fromisoformat(follow_up_at)
            enquiry.follow_up_at = new_dt
            update_fields.append('follow_up_at')
            logs.append(EnquiryActivity(
                enquiry=enquiry, actor=request.user,
                kind=EnquiryActivity.Kind.FOLLOWUP_SET,
                body=f'Follow-up scheduled for {new_dt.strftime("%d %b %Y at %H:%M")}',
            ))
        except ValueError:
            pass
    elif request.POST.get('clear_followup'):
        enquiry.follow_up_at = None
        update_fields.append('follow_up_at')

    if notes is not None and notes != enquiry.notes:
        old_notes = enquiry.notes
        enquiry.notes = notes
        update_fields.append('notes')
        if notes:
            logs.append(EnquiryActivity(
                enquiry=enquiry, actor=request.user,
                kind=EnquiryActivity.Kind.COMMENT,
                body=notes,
            ))

    if assigned_raw:
        from django.contrib.auth import get_user_model
        try:
            assignee = get_user_model().objects.get(pk=int(assigned_raw))
            if enquiry.assigned_to_id != assignee.pk:
                enquiry.assigned_to = assignee
                update_fields.append('assigned_to')
                logs.append(EnquiryActivity(
                    enquiry=enquiry, actor=request.user,
                    kind=EnquiryActivity.Kind.ASSIGNED,
                    body=f'Assigned to {assignee.get_full_name() or assignee.email}',
                ))
        except (ValueError, get_user_model().DoesNotExist):
            pass
    elif 'assigned_to' in request.POST:
        # empty string = unassign
        enquiry.assigned_to = None
        update_fields.append('assigned_to')

    enquiry.save(update_fields=list(dict.fromkeys(update_fields)))
    EnquiryActivity.objects.bulk_create(logs)

    return JsonResponse({
        'ok': True,
        'status': enquiry.status,
        'status_display': enquiry.get_status_display(),
        'updated_at': enquiry.updated_at.strftime('%d %b %Y, %H:%M'),
    })


@dashboard_access_required
def enquiry_add_comment(request, pk):
    """AJAX endpoint: add a comment to the activity log."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    enquiry = get_object_or_404(Enquiry, pk=pk)
    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)

    activity = EnquiryActivity.objects.create(
        enquiry=enquiry,
        actor=request.user,
        kind=EnquiryActivity.Kind.COMMENT,
        body=body,
    )
    return JsonResponse({
        'ok': True,
        'id': activity.pk,
        'actor': request.user.get_full_name() or request.user.email,
        'body': activity.body,
        'created_at': activity.created_at.strftime('%d %b %Y, %H:%M'),
        'kind': activity.kind,
    })


@dashboard_access_required
def enquiry_detail_view(request, pk):
    enquiry = get_object_or_404(
        Enquiry.objects.select_related('property', 'user', 'assigned_to'),
        pk=pk,
    )
    activities  = enquiry.activities.select_related('actor').order_by('created_at')
    from accounts.models import User as UserModel
    support_users = UserModel.objects.filter(
        role__in=['admin', 'customer_support'], is_active=True
    ).order_by('first_name')

    return render(request, 'enquiries/ticket.html', {
        'enquiry':       enquiry,
        'activities':    activities,
        'status_choices': Enquiry.Status.choices,
        'support_users': support_users,
    })

