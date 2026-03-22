"""
accounts/pipeline.py
Custom social-auth pipeline for the email-based custom User model.
"""

from django.contrib.auth import get_user_model


def get_or_create_user(strategy, details, backend, uid, user=None, *args, **kwargs):
    """
    Replace social_core.pipeline.user.create_user.
    Looks up an existing user by email; creates one if absent.
    Marks email as verified since the identity came from a trusted provider.
    """
    if user:
        return {'is_new': False}

    email = details.get('email')
    if not email:
        # Provider didn't return an email (e.g. Facebook with denied permission).
        # Return None so the pipeline aborts without creating a broken account.
        return None

    User = get_user_model()

    # Link to an existing account with the same email.
    try:
        existing = User.objects.get(email=email)
        return {'is_new': False, 'user': existing}
    except User.DoesNotExist:
        pass

    # Build first/last name from available detail keys.
    first_name = details.get('first_name', '')
    last_name  = details.get('last_name', '')
    if not first_name:
        fullname = details.get('fullname', '') or details.get('username', '')
        parts      = fullname.split(' ', 1)
        first_name = parts[0] or 'User'
        last_name  = parts[1] if len(parts) > 1 else ''

    new_user = User.objects.create_user(
        email      = email,
        first_name = first_name,
        last_name  = last_name,
        is_verified = True,  # email verified by OAuth provider
    )
    return {'is_new': True, 'user': new_user}


def save_profile_data(backend, user, response, *args, **kwargs):
    """
    Sync first/last name from the OAuth response when the user has none set yet.
    """
    changed = False

    if not user.first_name:
        first_name = response.get('given_name') or response.get('first_name', '')
        if first_name:
            user.first_name = first_name
            changed = True

    if not user.last_name:
        last_name = response.get('family_name') or response.get('last_name', '')
        if last_name:
            user.last_name = last_name
            changed = True

    if changed:
        user.save(update_fields=['first_name', 'last_name'])
