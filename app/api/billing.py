"""
Mock Billing API - Subscription management with simulated payments
/api/v1/billing/
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models import Institution, User, SubscriptionTier
from app.api.auth import get_current_user
from app.core.middleware import require_admin_or_above

router = APIRouter()

# =============================================================================
# SCHEMAS
# =============================================================================
class SubscriptionPlan(BaseModel):
    tier: str
    name: str
    price_monthly: float
    price_yearly: float
    max_students: int
    features: list[str]

class PaymentRequest(BaseModel):
    plan: str  # basic, pro, enterprise
    billing_cycle: str = "monthly"  # monthly, yearly
    
class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    message: str
    new_tier: str
    expires_at: datetime

class InvoiceItem(BaseModel):
    id: str
    date: datetime
    amount: float
    status: str
    plan: str

# =============================================================================
# PRICING DATA
# =============================================================================
PLANS = {
    "free": SubscriptionPlan(
        tier="free",
        name="Free",
        price_monthly=0,
        price_yearly=0,
        max_students=50,
        features=["Up to 50 students", "Basic attendance", "1 admin user"]
    ),
    "basic": SubscriptionPlan(
        tier="basic",
        name="Basic",
        price_monthly=29.99,
        price_yearly=299.99,
        max_students=500,
        features=["Up to 500 students", "CSV exports", "3 admin users", "Email support"]
    ),
    "pro": SubscriptionPlan(
        tier="pro",
        name="Pro",
        price_monthly=79.99,
        price_yearly=799.99,
        max_students=2000,
        features=["Up to 2000 students", "Analytics dashboard", "10 admin users", "Priority support", "API access"]
    ),
    "enterprise": SubscriptionPlan(
        tier="enterprise",
        name="Enterprise",
        price_monthly=199.99,
        price_yearly=1999.99,
        max_students=999999,
        features=["Unlimited students", "Custom integrations", "Unlimited admins", "Dedicated support", "SLA guarantee"]
    ),
}

# Mock invoice storage (in-memory)
mock_invoices: dict[int, list[InvoiceItem]] = {}

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/plans")
def get_subscription_plans():
    """Get all available subscription plans"""
    return list(PLANS.values())

@router.get("/current")
def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current institution's subscription status"""
    require_admin_or_above(current_user)
    
    if not current_user.institution_id:
        raise HTTPException(status_code=400, detail="No institution associated")
    
    institution = db.get(Institution, current_user.institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    current_plan = PLANS.get(institution.subscription_tier, PLANS["free"])
    
    return {
        "institution": institution.name,
        "current_tier": institution.subscription_tier,
        "plan_details": current_plan,
        "max_students": institution.max_students,
        "expires_at": institution.subscription_expires,
        "is_active": institution.is_active
    }

@router.post("/subscribe", response_model=PaymentResponse)
def subscribe_to_plan(
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Subscribe to a plan (MOCK PAYMENT)
    In production, this would integrate with Stripe/Paystack
    """
    require_admin_or_above(current_user)
    
    if payment.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    if not current_user.institution_id:
        raise HTTPException(status_code=400, detail="No institution associated")
    
    institution = db.get(Institution, current_user.institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    plan = PLANS[payment.plan]
    
    # Calculate expiry
    if payment.billing_cycle == "yearly":
        expires = datetime.utcnow() + timedelta(days=365)
        amount = plan.price_yearly
    else:
        expires = datetime.utcnow() + timedelta(days=30)
        amount = plan.price_monthly
    
    # Generate mock transaction ID
    transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
    
    # Update institution
    institution.subscription_tier = payment.plan
    institution.subscription_expires = expires
    institution.max_students = plan.max_students
    db.commit()
    
    # Create mock invoice
    if institution.id not in mock_invoices:
        mock_invoices[institution.id] = []
    
    mock_invoices[institution.id].append(InvoiceItem(
        id=transaction_id,
        date=datetime.utcnow(),
        amount=amount,
        status="paid",
        plan=payment.plan
    ))
    
    return PaymentResponse(
        success=True,
        transaction_id=transaction_id,
        message=f"Successfully subscribed to {plan.name} plan",
        new_tier=payment.plan,
        expires_at=expires
    )

@router.post("/cancel")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel subscription (downgrade to free at period end)"""
    require_admin_or_above(current_user)
    
    if not current_user.institution_id:
        raise HTTPException(status_code=400, detail="No institution associated")
    
    institution = db.get(Institution, current_user.institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Schedule downgrade (in real system, would happen at period end)
    institution.subscription_tier = SubscriptionTier.FREE.value
    institution.max_students = 50
    institution.subscription_expires = None
    db.commit()
    
    return {"message": "Subscription cancelled. Downgraded to Free plan."}

@router.get("/invoices")
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice history"""
    require_admin_or_above(current_user)
    
    if not current_user.institution_id:
        return []
    
    return mock_invoices.get(current_user.institution_id, [])

@router.post("/webhook/mock")
def mock_payment_webhook(event_type: str = "payment.success"):
    """
    Simulate payment webhook (for testing)
    In production, this would be called by Stripe/Paystack
    """
    return {
        "received": True,
        "event_type": event_type,
        "message": "Mock webhook processed"
    }
