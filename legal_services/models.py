from django.db import models
from django.conf import settings
import uuid

class LegalOrder(models.Model):
    class PackageType(models.TextChoices):
        STARTER = 'starter', 'Shield Starter'
        PRO = 'pro', 'Shield Pro'
        COMPLETE = 'complete', 'Shield Complete'

    class Verdict(models.TextChoices):
        PENDING = 'pending', 'Pending'
        GREEN = 'green', 'Green — Safe to proceed'
        YELLOW = 'yellow', 'Yellow — Caution'
        RED = 'red', 'Red — Do not proceed'

    class PaymentStatus(models.TextChoices):
        UNPAID    = 'unpaid',    'Unpaid'
        PENDING   = 'pending',   'Payment Pending'
        PAID      = 'paid',      'Paid'
        REFUNDED  = 'refunded',  'Refunded'

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='legal_orders')
    
    property_name = models.CharField(max_length=255, help_text="e.g., 3BHK Apartment, Koramangala")
    property_address = models.TextField()
    package = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.PRO)
    
    advocate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='assigned_cases', blank=True, null=True, limit_choices_to={'role': 'advocate'})
    advocate_notes = models.TextField(blank=True, null=True)
    
    verdict = models.CharField(max_length=15, choices=Verdict.choices, default=Verdict.PENDING)
    verdict_summary = models.TextField(blank=True, null=True, help_text="E.g. No critical issues detected · 12 checks passed")
    
    # Payment tracking
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    payment_id     = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction / UTR / Razorpay ID")
    payment_proof  = models.ImageField(upload_to='legal_payments/', blank=True, null=True, help_text="Screenshot or receipt image")
    payment_notes  = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            # Just a simple random ID for the sake of the clone
            self.order_id = f"HXL-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.property_name}"


class OrderStep(models.Model):
    class StepStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        DONE = 'done', 'Done'

    order = models.ForeignKey(LegalOrder, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=StepStatus.choices, default=StepStatus.PENDING)
    order_idx = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order_idx']

    def __str__(self):
        return f"{self.order.order_id} Step {self.order_idx}: {self.title}"


class VerdictCheck(models.Model):
    order = models.ForeignKey(LegalOrder, on_delete=models.CASCADE, related_name='verdict_checks')
    title = models.CharField(max_length=255)
    is_passed = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {'Passed' if self.is_passed else 'Failed'}"


class OrderActivity(models.Model):
    """Immutable audit log entry recording every meaningful change on a LegalOrder."""

    class Category(models.TextChoices):
        ASSIGNMENT = 'assignment', 'Advocate Assignment'
        STEP       = 'step',       'Step Update'
        VERDICT    = 'verdict',    'Verdict Update'
        PAYMENT    = 'payment',    'Payment Update'
        PACKAGE    = 'package',    'Package Change'
        SYSTEM     = 'system',     'System'

    order      = models.ForeignKey(LegalOrder, on_delete=models.CASCADE, related_name='activities')
    actor      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='legal_activities')
    category   = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.order.order_id}: {self.message[:60]}"
