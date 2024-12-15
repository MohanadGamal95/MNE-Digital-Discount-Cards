from django.contrib.auth.backends import ModelBackend
from .models import User

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        This custom authentication backend allows login using either username or email.
        """
        # First, try to authenticate with the username (default behavior)
        user = None
        try:
            # If the provided "username" is an email address
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                # Otherwise, treat it as a username
                user = User.objects.get(username=username)
            
            # Check if the user is valid and password matches
            if user and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
