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
    """Show details of a specific legal order."""
    order = get_object_or_404(LegalOrder, uuid=uuid, user=request.user)
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
            
            # Auto-create some default initial steps
            OrderStep.objects.create(order=order, order_idx=1, title="Order Placed", description="We have received your verification request.", status="done")
            
            if order.advocate:
                OrderStep.objects.create(order=order, order_idx=2, title="Advocate Assignment", description=f"Case assigned to Adv. {order.advocate.get_full_name()}.", status="done")
                OrderStep.objects.create(order=order, order_idx=3, title="Initial Review", description="Advocate is reviewing property details.", status="active")
                OrderActivity.objects.create(order=order, actor=request.user, category=Act.ASSIGNMENT, message=f"Order placed and directly assigned to Adv. {order.advocate.get_full_name()}.")
            else:
                OrderStep.objects.create(order=order, order_idx=2, title="Advocate Assignment", description="Assigning a legal expert to your case.", status="active")
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
        
        step = order.steps.filter(title="Advocate Assignment").first()
        if step:
            step.status = 'done'
            step.description = f"Case claimed by Adv. {request.user.get_full_name()}."
            step.save()
            OrderStep.objects.create(order=order, order_idx=3, title="Initial Review", description="Advocate is reviewing property details.", status="active")
        
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
        
        if action == 'update_step':
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
                
                step = order.steps.filter(title="Advocate Assignment").first()
                if step:
                    step.status = 'done'
                    step.description = f"Case {'re' if was_reassignment else ''}assigned to Adv. {advocate.get_full_name()}."
                    step.save()
                    if not order.steps.filter(title="Initial Review").exists():
                        OrderStep.objects.create(order=order, order_idx=3, title="Initial Review", description="Advocate is reviewing property details.", status="active")
                
                if was_reassignment:
                    msg = f"Case reassigned from Adv. {order.advocate.get_full_name()} to Adv. {advocate.get_full_name()} by {request.user.get_full_name()}."
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

