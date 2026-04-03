from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import LegalOrder

@login_required
def dashboard(request):
    """List all legal orders for the user."""
    orders = LegalOrder.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'legal_services/dashboard.html', {'orders': orders})

@login_required
def order_detail(request, uuid):
    """Show details of a specific legal order. Client can also send messages to advocate."""
    from .models import OrderActivity
    from django.contrib import messages as django_messages

    order = get_object_or_404(LegalOrder, uuid=uuid, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send_client_note':
            note_text = request.POST.get('note_text', '').strip()
            if note_text:
                OrderActivity.objects.create(
                    order=order,
                    actor=request.user,
                    category=OrderActivity.Category.CLIENT_NOTE,
                    message=note_text,
                )
                django_messages.success(request, "Your message has been sent to your advocate.")
            else:
                django_messages.error(request, "Message cannot be empty.")
        from django.shortcuts import redirect
        return redirect('legal_services:order_detail', uuid=uuid)

    steps = order.steps.all()
    checks = order.verdict_checks.all()
    activities = order.activities.all()

    context = {
        'order': order,
        'steps': steps,
        'checks': checks,
        'activities': activities,
    }
    return render(request, 'legal_services/order_detail.html', context)


from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from .models import OrderStep, VerdictCheck, LegalOrder, OrderActivity
from .forms import LegalOrderRequestForm
from django.contrib import messages

Act = OrderActivity.Category

def is_advocate(user):
    return user.is_authenticated and user.role == 'advocate'

def is_legal_admin(user):
    """Returns True for superusers, admins, and legal_admins."""
    return user.is_authenticated and (
        user.is_superuser or
        getattr(user, 'role', None) in ('admin', 'legal_admin')
    )

# ── Package Workflow Definitions ─────────────────────────────────────────────
PACKAGE_WORKFLOW = {
    'starter': [
        ('Order Placed',                 'Your request has been received.'),
        ('Advocate Assignment',          'A legal expert is being assigned to your case.'),
        ('Document Collection',          'Uploading and verifying your property documents.'),
        ('Title Deed Verification',      'Checking ownership title and legitimacy of the deed.'),
        ('Encumbrance Certificate Check','Verifying EC to detect loans, charges or liens.'),
        ('RERA Registration Check',      'Confirming builder/project RERA registration status.'),
        ('Basic Litigation Check',       'Scanning courts for any existing disputes on the property.'),
        ('Report Drafting',              'Advocate is compiling the final 1-page verdict.'),
        ('Verdict Delivered',            'Your Go/No-Go verdict PDF is ready on the dashboard.'),
    ],
    'pro': [
        ('Order Placed',                     'Your request has been received.'),
        ('Advocate Assignment',              'A legal expert is being assigned to your case.'),
        ('Document Collection',              'Uploading and verifying your property documents.'),
        ('30-Year Title History Check',      'Tracing full 30-year ownership chain.'),
        ('Mother Deed Chain Verification',   'Verifying the chain from original grant to current owner.'),
        ('RERA & Compliance Audit',          'RERA check + BBMP/BDA/BMRDA approvals audit.'),
        ('Land Acquisition Notice Check',    'Checking BDA/KIADB acquisition notifications.'),
        ('SRO Physical Field Verification',  'Advocate visiting Sub-Registrar Office for physical cross-check.'),
        ('Buyer-Protective Sale Agreement',  'Drafting sale agreement with protective buyer clauses.'),
        ('Khata & Property Tax Records',     'Verifying Khata and property tax payment history.'),
        ('Report Drafting',                  'Advocate is compiling the comprehensive verdict report.'),
        ('Verdict Delivered',                'Your Go/No-Go verdict PDF is ready on the dashboard.'),
    ],
    'complete': [
        ('Order Placed',                     'Your request has been received.'),
        ('Advocate Assignment',              'A dedicated advocate has been assigned to your case.'),
        ('Document Collection',              'Uploading and verifying your property documents.'),
        ('30-Year Title History Check',      'Tracing full 30-year ownership chain.'),
        ('Mother Deed Chain Verification',   'Verifying the chain from original grant to current owner.'),
        ('RERA & Compliance Audit',          'RERA check + BBMP/BDA/BMRDA approvals audit.'),
        ('Land Acquisition Notice Check',    'Checking BDA/KIADB acquisition notifications.'),
        ('SRO Physical Field Verification',  'Advocate visiting Sub-Registrar Office for physical cross-check.'),
        ('Buyer-Protective Sale Agreement',  'Drafting sale agreement with protective buyer clauses.'),
        ('Khata & Property Tax Records',     'Verifying Khata and property tax payment history.'),
        ('Sale Deed Drafting & Registration','Preparing and registering the final Sale Deed.'),
        ('Khata Transfer (BBMP/BDA)',        'Executing full Khata transfer in buyer\'s name.'),
        ('Property Tax Name Change',         'Updating property tax records to buyer\'s name.'),
        ('BESCOM Name Change Support',       'Processing electricity connection name change.'),
        ('Report Drafting',                  'Advocate is compiling the comprehensive verdict report.'),
        ('Verdict Delivered',                'Your Go/No-Go verdict PDF is ready. 12-month helpline active.'),
    ],
}

def create_workflow_steps(order, advocate_assigned=False):
    """Delete any old steps and create the full package workflow for this order."""
    order.steps.all().delete()
    steps_def = PACKAGE_WORKFLOW.get(order.package, PACKAGE_WORKFLOW['starter'])
    for idx, (title, desc) in enumerate(steps_def, start=1):
        if idx == 1:
            status = 'done'       # Order Placed always done
        elif idx == 2 and advocate_assigned:
            status = 'done'       # Advocate Assignment done if already assigned
        elif idx == 3 and advocate_assigned:
            status = 'active'     # First real work step becomes active
        elif idx == 2 and not advocate_assigned:
            status = 'active'     # Waiting for assignment
        else:
            status = 'pending'
        if idx == 2 and advocate_assigned:
            desc = f"Case assigned to Adv. {order.advocate.get_full_name()}."
        OrderStep.objects.create(order=order, order_idx=idx, title=title, description=desc, status=status)

@login_required
def request_order(request):
    """User requests a new legal package."""
    # Pre-select package if passed via URL (e.g. ?package=pro)
    initial_package = request.GET.get('package', 'pro')
    
    if request.method == 'POST':
        form = LegalOrderRequestForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            create_workflow_steps(order, advocate_assigned=bool(order.advocate))
            
            if order.advocate:
                OrderActivity.objects.create(order=order, actor=request.user, category=Act.ASSIGNMENT, message=f"Order placed and directly assigned to Adv. {order.advocate.get_full_name()}.")
            else:
                OrderActivity.objects.create(order=order, actor=request.user, category=Act.SYSTEM, message="Order placed. Awaiting advocate assignment.")
            
            messages.success(request, f"Your order for the {order.get_package_display()} package has been successfully placed!")
            return redirect('legal_services:dashboard')
    else:
        form = LegalOrderRequestForm(initial={'package': initial_package})
        
    return render(request, 'legal_services/request_order.html', {'form': form})

@login_required
def advocate_dashboard(request):
    """List all legal orders assigned to the logged-in advocate (or all if legal admin)."""
    if not (is_advocate(request.user) or is_legal_admin(request.user)):
        raise PermissionDenied("You must be an advocate or legal admin to view this page.")
    
    if is_legal_admin(request.user):
        orders = LegalOrder.objects.all()
    else:
        orders = LegalOrder.objects.filter(advocate=request.user)
    orders = orders.order_by('-created_at')
    return render(request, 'legal_services/advocate_dashboard.html', {'orders': orders})

@login_required
def advocate_pool(request):
    """Show pending cases that haven't been assigned an advocate."""
    if not (is_advocate(request.user) or is_legal_admin(request.user)):
        raise PermissionDenied("You must be an advocate or legal admin to view this page.")
        
    orders = LegalOrder.objects.filter(advocate__isnull=True).order_by('-created_at')
    return render(request, 'legal_services/case_pool.html', {'orders': orders})

@login_required
def advocate_claim(request, uuid):
    """Advocate claims an unassigned case."""
    if not (is_advocate(request.user) or is_legal_admin(request.user)):
        raise PermissionDenied("You must be an advocate or legal admin to claim cases.")
        
    order = get_object_or_404(LegalOrder, uuid=uuid)
    if order.advocate is None:
        order.advocate = request.user
        order.save()
        
        # Rebuild the workflow with all package-specific steps now that advocate is set
        create_workflow_steps(order, advocate_assigned=True)
        
        OrderActivity.objects.create(order=order, actor=request.user, category=Act.ASSIGNMENT, message=f"Adv. {request.user.get_full_name()} claimed this case from the open pool.")
        messages.success(request, f"You have successfully claimed the case for {order.property_name}.")
    else:
        messages.error(request, "This case has already been claimed by another advocate.")
        
    return redirect('legal_services:advocate_order_detail', uuid=order.uuid)

@login_required
def advocate_order_detail(request, uuid):
    """Advocate view to manage a specific case."""
    if not (is_advocate(request.user) or is_legal_admin(request.user)):
        raise PermissionDenied("You must be an advocate or legal admin to view this page.")
        
    order = get_object_or_404(LegalOrder, uuid=uuid)
    
    # Only the assigned advocate may make changes
    can_edit = (request.user == order.advocate)
    
    if request.method == 'POST':
        if not can_edit:
            messages.error(request, "Only the assigned advocate can update this case.")
            return redirect('legal_services:advocate_order_detail', uuid=uuid)
        
        action = request.POST.get('action')
        
        if action == 'mark_step_done':
            # Sequential workflow: only the active step can be marked done
            step_id = request.POST.get('step_id')
            note = request.POST.get('note', '').strip()
            if step_id:
                step = get_object_or_404(OrderStep, id=step_id, order=order)
                if step.status != 'active':
                    messages.error(request, "Only the currently active step can be marked as done.")
                else:
                    if note:
                        step.description = note
                    step.status = 'done'
                    step.save()
                    # Activate the very next pending step
                    next_step = order.steps.filter(status='pending').order_by('order_idx').first()
                    if next_step:
                        next_step.status = 'active'
                        next_step.save()
                    OrderActivity.objects.create(
                        order=order, actor=request.user, category=Act.STEP,
                        message=f"✅ '{step.title}' completed. {('Note: ' + note) if note else ''}".strip()
                    )
                    messages.success(request, f"'{step.title}' marked as done.")

        elif action == 'send_note':
            note_text = request.POST.get('note_text', '').strip()
            if note_text:
                OrderActivity.objects.create(
                    order=order, actor=request.user, category=Act.NOTE,
                    message=note_text
                )
                messages.success(request, "Your message has been sent to the client.")
            else:
                messages.error(request, "Message cannot be empty.")

        elif action == 'update_step':
            step_id = request.POST.get('step_id')
            status = request.POST.get('status')
            desc = request.POST.get('description')
            if step_id:
                step = get_object_or_404(OrderStep, id=step_id, order=order)
                old_status = step.status
                if status: step.status = status
                if desc is not None: step.description = desc
                step.save()
                OrderActivity.objects.create(
                    order=order, actor=request.user, category=Act.STEP,
                    message=f"Step '{step.title}' updated: status {old_status} → {step.status}. Note: \"{desc or '—'}\""
                )
        
        elif action == 'update_verdict':
            verdict = request.POST.get('verdict')
            summary = request.POST.get('verdict_summary')
            old_verdict = order.verdict
            if verdict: order.verdict = verdict
            if summary is not None: order.verdict_summary = summary
            order.save()
            OrderActivity.objects.create(
                order=order, actor=request.user, category=Act.VERDICT,
                message=f"Verdict updated: {old_verdict} → {order.verdict}. Summary: \"{order.verdict_summary or '—'}\""
            )
            
        elif action == 'toggle_check':
            check_id = request.POST.get('check_id')
            if check_id:
                check = get_object_or_404(VerdictCheck, id=check_id, order=order)
                check.is_passed = request.POST.get('is_passed') == 'on'
                check.save()
                OrderActivity.objects.create(
                    order=order, actor=request.user, category=Act.VERDICT,
                    message=f"Checklist item '{check.title}' marked as {'Passed ✓' if check.is_passed else 'Failed ✗'}."
                )
                
        return redirect('legal_services:advocate_order_detail', uuid=uuid)
        
    steps = order.steps.all()
    checks = order.verdict_checks.all()
    activities = order.activities.all()
    
    context = {
        'order': order,
        'steps': steps,
        'checks': checks,
        'activities': activities,
        'can_edit': can_edit,
        'VerdictChoices': LegalOrder.Verdict,
        'StepChoices': OrderStep.StepStatus,
    }
    return render(request, 'legal_services/advocate_order_detail.html', context)


@login_required
def admin_legal_dashboard(request):
    """Admin & Legal Admin view to manage all unassigned and assigned cases."""
    if not is_legal_admin(request.user):
        raise PermissionDenied("You must be an admin or legal admin to view this page.")
        
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign_advocate':
            order_id = request.POST.get('order_id')
            advocate_id = request.POST.get('advocate_id')
            if order_id and advocate_id:
                order = get_object_or_404(LegalOrder, id=order_id)
                advocate = get_object_or_404(User, id=advocate_id, role='advocate')
                
                was_reassignment = order.advocate is not None and order.advocate.id != advocate.id
                order.advocate = advocate
                order.save()
                
                # Rebuild full package workflow on assignment/reassignment
                create_workflow_steps(order, advocate_assigned=True)
                
                if was_reassignment:
                    msg = f"Case reassigned to Adv. {advocate.get_full_name()} by {request.user.get_full_name()}."
                    messages.success(request, f"Successfully reassigned Case {order.order_id} to Adv. {advocate.get_full_name()}.")
                else:
                    msg = f"Case assigned to Adv. {advocate.get_full_name()} by {request.user.get_full_name()}."
                    messages.success(request, f"Successfully assigned Case {order.order_id} to Adv. {advocate.get_full_name()}.")
                OrderActivity.objects.create(order=order, actor=request.user, category=Act.ASSIGNMENT, message=msg)

        elif action == 'update_payment':
            order_id = request.POST.get('order_id')
            if order_id:
                order = get_object_or_404(LegalOrder, id=order_id)
                old_status = order.payment_status
                order.payment_status = request.POST.get('payment_status', order.payment_status)
                order.payment_id     = request.POST.get('payment_id', order.payment_id)
                order.payment_notes  = request.POST.get('payment_notes', order.payment_notes)
                if 'payment_proof' in request.FILES:
                    order.payment_proof = request.FILES['payment_proof']
                order.save()
                log_msg = f"Payment updated: status {old_status} → {order.payment_status}."
                if order.payment_id:
                    log_msg += f" TX ID: {order.payment_id}."
                if 'payment_proof' in request.FILES:
                    log_msg += " Payment proof uploaded."
                if order.payment_notes:
                    log_msg += f" Notes: \"{order.payment_notes}\""
                OrderActivity.objects.create(order=order, actor=request.user, category=Act.PAYMENT, message=log_msg)
                messages.success(request, f"Payment details updated for {order.order_id}.")

        elif action == 'update_package':
            order_id = request.POST.get('order_id')
            new_package = request.POST.get('package')
            if order_id and new_package:
                order = get_object_or_404(LegalOrder, id=order_id)
                old_package = order.get_package_display()
                order.package = new_package
                order.save()
                OrderActivity.objects.create(
                    order=order, actor=request.user, category=Act.PACKAGE,
                    message=f"Package changed from {old_package} to {order.get_package_display()} by {request.user.get_full_name()}."
                )
                messages.success(request, f"Package for {order.order_id} changed from {old_package} to {order.get_package_display()}.")
                
        return redirect('legal_services:admin_dashboard')
        
    unassigned = LegalOrder.objects.filter(advocate__isnull=True).order_by('-created_at')
    assigned = LegalOrder.objects.filter(advocate__isnull=False).order_by('-created_at')
    advocates = User.objects.filter(role='advocate', is_approved_advocate=True, is_active=True)
    
    return render(request, 'legal_services/admin_dashboard.html', {
        'unassigned': unassigned,
        'assigned': assigned,
        'advocates': advocates
    })

