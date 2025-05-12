from typing import Optional
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from app.models.user.user import User


def send_email(to: str, subject: str, template: str, **kwargs) -> None:
    """Send an email using the configured mail server"""
    msg = Message(
        subject=subject,
        recipients=[to],
        html=render_template(f'email/{template}.html', **kwargs),
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


def send_password_reset_email(user: User, reset_token: str) -> None:
    """Send password reset email to user"""
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
    send_email(
        to=user.email,
        subject='Reset Your Password',
        template='reset_password',
        user=user,
        reset_url=reset_url
    )


def send_welcome_email(user: User) -> None:
    """Send welcome email to new user"""
    login_url = f"{current_app.config['FRONTEND_URL']}/login"
    send_email(
        to=user.email,
        subject='Welcome to DSP Ad System',
        template='welcome',
        user=user,
        login_url=login_url
    )


def send_verification_email(user: User, verification_token: str) -> None:
    """Send email verification email to user"""
    verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={verification_token}"
    send_email(
        to=user.email,
        subject='Verify Your Email',
        template='verify_email',
        user=user,
        verification_url=verification_url
    )


def send_campaign_approval_email(user: User, campaign_name: str, is_approved: bool, reason: Optional[str] = None) -> None:
    """Send campaign approval/rejection email to user"""
    template = 'campaign_approved' if is_approved else 'campaign_rejected'
    subject = f"Campaign {'Approved' if is_approved else 'Rejected'}: {campaign_name}"
    send_email(
        to=user.email,
        subject=subject,
        template=template,
        user=user,
        campaign_name=campaign_name,
        reason=reason
    )


def send_creative_approval_email(user: User, creative_name: str, is_approved: bool, reason: Optional[str] = None) -> None:
    """Send creative approval/rejection email to user"""
    template = 'creative_approved' if is_approved else 'creative_rejected'
    subject = f"Creative {'Approved' if is_approved else 'Rejected'}: {creative_name}"
    send_email(
        to=user.email,
        subject=subject,
        template=template,
        user=user,
        creative_name=creative_name,
        reason=reason
    )


def send_budget_alert_email(user: User, campaign_name: str, budget_type: str, current_amount: float, threshold: float) -> None:
    """Send budget alert email to user"""
    send_email(
        to=user.email,
        subject=f'Budget Alert: {campaign_name}',
        template='budget_alert',
        user=user,
        campaign_name=campaign_name,
        budget_type=budget_type,
        current_amount=current_amount,
        threshold=threshold
    )


def send_performance_alert_email(user: User, campaign_name: str, metric: str, current_value: float, threshold: float) -> None:
    """Send performance alert email to user"""
    send_email(
        to=user.email,
        subject=f'Performance Alert: {campaign_name}',
        template='performance_alert',
        user=user,
        campaign_name=campaign_name,
        metric=metric,
        current_value=current_value,
        threshold=threshold
    ) 