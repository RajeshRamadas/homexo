"""
enquiries/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, ExpressionWrapper, DurationField, F, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.urls import reverse
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
    if not request.user.is_authenticated:
        from django.utils.http import urlencode as django_urlencode
        messages.warning(request, 'Please log in to your account to submit an enquiry.')
        next_url = request.META.get('HTTP_REFERER', '/')
        login_url = f"{reverse('accounts:login')}?{django_urlencode({'next': next_url})}"
        return redirect(login_url)

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
    <a href="https://homexo.in/admin/enquiries/enquiry/{enquiry.id}/change/"
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
        next_success_url = request.POST.get('next')
        if next_success_url:
            return redirect(next_success_url)
        return redirect('pages:home')

    return render(request, 'enquiries/form.html', {'form': form})


def enquiry_success(request):
    return render(request, 'enquiries/success.html')


# ── Enquiry Dashboard ─────────────────────────────────────────────────────────

@dashboard_access_required
def enquiry_dashboard(request):
    from accounts.models import User as UserModel
    qs = Enquiry.objects.select_related('property', 'assigned_to').all()

    # ── Filters ───────────────────────────────────────────────────────────────
    status_filter   = request.GET.get('status', '')
    type_filter     = request.GET.get('enquiry_type', '')
    source_filter   = request.GET.get('source', '')
    priority_filter = request.GET.get('priority', '')
    search          = request.GET.get('q', '').strip()
    mine            = request.GET.get('mine', '')
    date_from       = request.GET.get('date_from', '')
    date_to         = request.GET.get('date_to', '')
    sort            = request.GET.get('sort', '-created_at')

    if mine:
        qs = qs.filter(assigned_to=request.user)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(enquiry_type=type_filter)
    if source_filter:
        qs = qs.filter(source__icontains=source_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(message__icontains=search)
        )
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    # ── Sort ──────────────────────────────────────────────────────────────────
    SORT_MAP = {
        'name': 'name', '-name': '-name',
        'status': 'status', '-status': '-status',
        'followup': 'follow_up_at', '-followup': '-follow_up_at',
        'created_at': 'created_at', '-created_at': '-created_at',
    }
    priority_order = Case(
        When(priority=Enquiry.Priority.CRITICAL, then=Value(0)),
        When(priority=Enquiry.Priority.HIGH,     then=Value(1)),
        When(priority=Enquiry.Priority.MEDIUM,   then=Value(2)),
        When(priority=Enquiry.Priority.LOW,      then=Value(3)),
        output_field=IntegerField(),
    )
    if sort == 'priority':
        qs = qs.annotate(_prio_order=priority_order).order_by('_prio_order')
    elif sort == '-priority':
        qs = qs.annotate(_prio_order=priority_order).order_by('-_prio_order')
    elif sort in SORT_MAP:
        qs = qs.order_by(SORT_MAP[sort])
    else:
        qs = qs.order_by('-created_at')

    # ── Annotate is_overdue ───────────────────────────────────────────────────
    now = timezone.now()
    open_statuses = ['new', 'contacted', 'qualified']

    # ── Stats ─────────────────────────────────────────────────────────────────
    total         = Enquiry.objects.count()
    new_count     = Enquiry.objects.filter(status='new').count()
    contacted     = Enquiry.objects.filter(status='contacted').count()
    qualified_cnt = Enquiry.objects.filter(status='qualified').count()
    closed        = Enquiry.objects.filter(status='closed').count()
    critical_open = Enquiry.objects.filter(priority=Enquiry.Priority.CRITICAL, status__in=open_statuses).count()

    avg_resp = (
        Enquiry.objects
        .filter(first_response_at__isnull=False)
        .annotate(resp_dur=ExpressionWrapper(F('first_response_at') - F('created_at'), output_field=DurationField()))
        .aggregate(avg=Avg('resp_dur'))['avg']
    )
    avg_response_hours = round(avg_resp.total_seconds() / 3600, 1) if avg_resp else None

    source_data = (
        Enquiry.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    type_data = (
        Enquiry.objects.values('enquiry_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    followup_due = Enquiry.objects.filter(
        follow_up_at__lte=now, status__in=open_statuses
    ).count()
    my_count = Enquiry.objects.filter(
        assigned_to=request.user, status__in=open_statuses,
    ).count()

    # ── Pagination ────────────────────────────────────────────────────────────
    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    # Add is_overdue flag to each enquiry in the page
    for eq in page_obj:
        eq.is_overdue = bool(eq.follow_up_at and eq.follow_up_at < now)

    support_users = UserModel.objects.filter(
        role__in=['customer_support', 'admin']
    ).order_by('first_name')

    context = {
        'enquiries':         page_obj,          # backward compat for {% if enquiries %}
        'page_obj':          page_obj,
        'status_filter':     status_filter,
        'type_filter':       type_filter,
        'source_filter':     source_filter,
        'priority_filter':   priority_filter,
        'search':            search,
        'mine':              mine,
        'date_from':         date_from,
        'date_to':           date_to,
        'sort':              sort,
        'my_count':          my_count,
        'status_choices':    Enquiry.Status.choices,
        'type_choices':      Enquiry.EnquiryType.choices,
        'priority_choices':  Enquiry.Priority.choices,
        'support_users':     support_users,
        'stats': {
            'total':     total,
            'new':       new_count,
            'contacted': contacted,
            'qualified': qualified_cnt,
            'closed':    closed,
        },
        'critical_open':      critical_open,
        'avg_response_hours': avg_response_hours,
        'source_data':        list(source_data),
        'type_data':          list(type_data),
        'followup_due':       followup_due,
    }
    return render(request, 'enquiries/dashboard.html', context)


@dashboard_access_required
def enquiry_update_status(request, pk):
    """AJAX endpoint: update status/priority/notes/follow_up_at/assigned_to, log everything."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    enquiry = get_object_or_404(Enquiry, pk=pk)
    new_status    = request.POST.get('status', '').strip()
    new_priority  = request.POST.get('priority', '').strip()
    follow_up_at  = request.POST.get('follow_up_at', '').strip()
    notes         = request.POST.get('notes', None)
    assigned_raw  = request.POST.get('assigned_to', '').strip()

    valid_statuses   = [s[0] for s in Enquiry.Status.choices]
    valid_priorities = [p[0] for p in Enquiry.Priority.choices]
    update_fields    = ['updated_at']
    logs = []
    prev_assignee = enquiry.assigned_to  # track for email

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

    if new_priority and new_priority in valid_priorities and new_priority != enquiry.priority:
        old_p = enquiry.get_priority_display()
        enquiry.priority = new_priority
        update_fields.append('priority')
        logs.append(EnquiryActivity(
            enquiry=enquiry, actor=request.user,
            kind=EnquiryActivity.Kind.SYSTEM,
            body=f'Priority changed from "{old_p}" → "{enquiry.get_priority_display()}"',
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
        enquiry.notes = notes
        update_fields.append('notes')
        if notes:
            logs.append(EnquiryActivity(
                enquiry=enquiry, actor=request.user,
                kind=EnquiryActivity.Kind.COMMENT,
                body=notes,
            ))

    new_assignee = None
    if assigned_raw:
        from django.contrib.auth import get_user_model
        try:
            assignee = get_user_model().objects.get(pk=int(assigned_raw))
            if enquiry.assigned_to_id != assignee.pk:
                enquiry.assigned_to = assignee
                new_assignee = assignee
                update_fields.append('assigned_to')
                logs.append(EnquiryActivity(
                    enquiry=enquiry, actor=request.user,
                    kind=EnquiryActivity.Kind.ASSIGNED,
                    body=f'Assigned to {assignee.get_full_name() or assignee.email}',
                ))
        except (ValueError, get_user_model().DoesNotExist):
            pass
    elif 'assigned_to' in request.POST:
        enquiry.assigned_to = None
        update_fields.append('assigned_to')

    # Track first_response_at — set on the first agent action
    if logs and not enquiry.first_response_at:
        enquiry.first_response_at = timezone.now()
        update_fields.append('first_response_at')

    enquiry.save(update_fields=list(dict.fromkeys(update_fields)))
    EnquiryActivity.objects.bulk_create(logs)

    # Email notification to newly assigned agent
    if new_assignee and new_assignee.email:
        _send_assignment_email(request, enquiry, new_assignee)

    return JsonResponse({
        'ok': True,
        'status': enquiry.status,
        'status_display': enquiry.get_status_display(),
        'priority': enquiry.priority,
        'updated_at': enquiry.updated_at.strftime('%d %b %Y, %H:%M'),
    })


def _send_assignment_email(request, enquiry, assignee):
    """Send a ticket-assigned notification email to the assignee."""
    try:
        ticket_url = request.build_absolute_uri(
            reverse('enquiries:detail', args=[enquiry.pk])
        )
        actor_name = request.user.get_full_name() or request.user.email
        html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px;">
<div style="max-width:520px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
  <div style="background:#1a2e44;padding:22px 32px;">
    <h2 style="margin:0;color:#fff;font-size:17px;">&#128203; Ticket Assigned to You</h2>
  </div>
  <div style="padding:24px 32px;font-size:14px;color:#333;line-height:1.7;">
    <p>Hi {assignee.get_full_name() or assignee.email},</p>
    <p><strong>{actor_name}</strong> has assigned ticket <strong>#{enquiry.pk}</strong> to you.</p>
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin:12px 0;">
      <tr><td style="padding:4px 0;color:#888;">Customer</td><td><strong>{enquiry.name}</strong></td></tr>
      <tr><td style="padding:4px 0;color:#888;">Phone</td><td><a href="tel:{enquiry.phone}" style="color:#1a2e44;">{enquiry.phone}</a></td></tr>
      <tr><td style="padding:4px 0;color:#888;">Type</td><td>{enquiry.get_enquiry_type_display()}</td></tr>
      <tr><td style="padding:4px 0;color:#888;">Priority</td><td>{enquiry.get_priority_display()}</td></tr>
      <tr><td style="padding:4px 0;color:#888;">Status</td><td>{enquiry.get_status_display()}</td></tr>
    </table>
    <a href="{ticket_url}" style="display:inline-block;margin-top:16px;padding:10px 22px;background:#1a2e44;color:#fff;border-radius:4px;text-decoration:none;font-size:13px;">Open Ticket →</a>
  </div>
  <div style="padding:14px 32px;background:#f5f5f5;font-size:11px;color:#aaa;">Homexo CRM — automated notification</div>
</div>
</body></html>"""
        plain = (
            f"Hi {assignee.get_full_name()},\n\n"
            f"{actor_name} has assigned ticket #{enquiry.pk} ({enquiry.name}) to you.\n"
            f"Priority: {enquiry.get_priority_display()}\n\nOpen ticket: {ticket_url}"
        )
        msg = EmailMultiAlternatives(
            subject=f'[Homexo] Ticket #{enquiry.pk} assigned to you — {enquiry.name}',
            body=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[assignee.email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=True)
    except Exception:
        pass


@dashboard_access_required
def enquiry_bulk_action(request):
    """Bulk-assign, bulk-status, bulk-priority for selected ticket PKs."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    pks_raw = request.POST.getlist('pks')
    action  = request.POST.get('action', '').strip()

    if not pks_raw or not action:
        return JsonResponse({'error': 'Missing pks or action.'}, status=400)

    try:
        pks = [int(p) for p in pks_raw]
    except ValueError:
        return JsonResponse({'error': 'Invalid PKs.'}, status=400)

    qs    = Enquiry.objects.filter(pk__in=pks)
    count = qs.count()

    if action == 'assign':
        assignee_pk = request.POST.get('assigned_to', '').strip()
        if not assignee_pk:
            qs.update(assigned_to=None, updated_at=timezone.now())
        else:
            from django.contrib.auth import get_user_model
            try:
                assignee = get_user_model().objects.get(pk=int(assignee_pk))
                qs.update(assigned_to=assignee, updated_at=timezone.now())
                acts = [
                    EnquiryActivity(
                        enquiry_id=pk, actor=request.user,
                        kind=EnquiryActivity.Kind.ASSIGNED,
                        body=f'Assigned to {assignee.get_full_name() or assignee.email} (bulk)',
                    ) for pk in pks
                ]
                EnquiryActivity.objects.bulk_create(acts)
                if assignee.email:
                    for enq in qs.select_related('property'):
                        _send_assignment_email(request, enq, assignee)
            except (ValueError, get_user_model().DoesNotExist):
                return JsonResponse({'error': 'Invalid assignee.'}, status=400)

    elif action.startswith('status:'):
        new_status = action.split(':', 1)[1]
        valid = [s[0] for s in Enquiry.Status.choices]
        if new_status not in valid:
            return JsonResponse({'error': 'Invalid status.'}, status=400)
        status_map = {e.pk: e.get_status_display() for e in qs}
        new_label  = dict(Enquiry.Status.choices)[new_status]
        qs.update(status=new_status, updated_at=timezone.now())
        acts = [
            EnquiryActivity(
                enquiry_id=pk, actor=request.user,
                kind=EnquiryActivity.Kind.STATUS_CHANGE,
                body=f'Status changed from "{status_map[pk]}" → "{new_label}" (bulk)',
            ) for pk in pks
        ]
        EnquiryActivity.objects.bulk_create(acts)

    elif action.startswith('priority:'):
        new_priority = action.split(':', 1)[1]
        valid = [p[0] for p in Enquiry.Priority.choices]
        if new_priority not in valid:
            return JsonResponse({'error': 'Invalid priority.'}, status=400)
        qs.update(priority=new_priority, updated_at=timezone.now())

    else:
        return JsonResponse({'error': 'Unknown action.'}, status=400)

    return JsonResponse({'ok': True, 'count': count})


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

    # Days open
    days_open = (timezone.now() - enquiry.created_at).days

    # Avg response hours for this ticket
    if enquiry.first_response_at:
        delta = enquiry.first_response_at - enquiry.created_at
        response_hours = round(delta.total_seconds() / 3600, 1)
    else:
        response_hours = None

    return render(request, 'enquiries/ticket.html', {
        'enquiry':          enquiry,
        'activities':       activities,
        'status_choices':   Enquiry.Status.choices,
        'priority_choices': Enquiry.Priority.choices,
        'support_users':    support_users,
        'days_open':        days_open,
        'response_hours':   response_hours,
    })

