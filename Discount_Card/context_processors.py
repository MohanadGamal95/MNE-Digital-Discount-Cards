from .models import Member

def member_status(request):
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            member = None
    else:
        member = None

    return {'member': member}
