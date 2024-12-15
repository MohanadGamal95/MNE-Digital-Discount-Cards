from django.contrib.auth.decorators import user_passes_test

def email_verified_required(user):
    return user.is_authenticated and user.email_verified

email_verified_required = user_passes_test(email_verified_required)
