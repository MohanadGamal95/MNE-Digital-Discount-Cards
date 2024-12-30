from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from .decorators import email_verified_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from datetime import timedelta
import json
from .forms import RegistrationForm
from . import models
from weasyprint import HTML


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            #Create user but logged out
            user = form.save()
            models.Member.objects.create(user=user)
            send_activation_email(user, request)

            messages.success(request, 'Registration successful! Please check your email to verify your account')
            return redirect('Discount_Card:logout')  #Redirect to login page after successful registration
        else:
            #Display error
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)

    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

#login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if not user.email_verified:
            messages.error(self.request, 'Please verify your email first')
            return redirect('Discount_Card:email_not_verified')
        else:
            messages.success(self.request, f'Welcome, {user.full_name}!')
            return super().form_valid(form)  # Proceed with the normal flow (redirection)

    def form_invalid(self, form):
        # You can add error messages after an invalid login attempt
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)  # Proceed with the normal flow (display form errors)

#send activation
def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    domain = get_current_site(request).domain
    now = timezone.now()
    last_email_sent = request.session.get('last_activation_email_sent') # Check if 10 minutes have passed since the last email
    if last_email_sent and now - last_email_sent < timedelta(minutes=10):
        raise ValueError("You can only request a new activation email once every 10 minutes.")

    # Construct the activation URL
    activation_url = request.build_absolute_uri(
        reverse('Discount_Card:activate', kwargs={'uidb64': uid, 'token': token})
    )

    # Compose the email
    subject = 'Account Activation'
    message = render_to_string('activation_email.html', {
        'user': user,
        'activation_url': activation_url,
        'domain': domain
    })
    send_mail(subject, '', settings.EMAIL_HOST_USER, [user.email], html_message=message)
    # Update the timestamp of the last sent email in the session
    request.session['last_activation_email_sent'] = str(now)

#activate account
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    # Validate the token
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True  # Activate the user account
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('Discount_Card:login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('Discount_Card:register')  # Redirect to the registration page

#resend activation link
@login_required
def resend_activation(request):
    try:
        send_activation_email(request.user, request)
        messages.success(request, 'Activation email resent! Please check your email.')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect ('Discount_Card:register')

    return redirect('Discount_Card:login')

#verification required
def email_not_verified(request):
    print(request)
    return render(request, 'email_not_verified.html')


#logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('Discount_Card:login')

#homepage

@login_required
def index(request):
    if not request.user.email_verified:
        messages.error(request, "Please verify your email first")
        return redirect('Discount_Card:email_not_verified')
    try:
        member = models.Member.objects.get(user=request.user)
        member_active_subscription = member.active_subscription()
    except models.Member.DoesNotExist:
        member = None
        member_active_subscription = None
    current_time = timezone.now()
    print(request)
    return render(request, 'index.html', {
        'user': request.user,
        'member':member,
        'member_active_subscription': member_active_subscription,
        'current_time': current_time
    })


@email_verified_required
@login_required
def download_card_pdf(request, member_id):
    member = get_object_or_404(models.Member, pk=member_id)

    if member.user != request.user:
        return HttpResponseForbidden()

    html = render_to_string('card_template.html', {
        'member': member,
        'current_time': timezone.now() # Pass current time to the template })
    })
    pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Discount_Card_{member_id}.pdf"'

    return response

# Fetch providers for autocomplete
def fetch_providers(request):
    query = request.GET.get('query', '')
    providers = models.Network.objects.filter(provider_name__icontains=query)[:5]
    data = list(providers.values('provider_name', 'latitude', 'longitude', 'address', 'phone_number'))
    return JsonResponse(data, safe=False)

# Fetch filters
def fetch_filters(request):
    governates = models.Network.objects.values_list('governorate', flat=True).distinct()
    areas = models.Network.objects.values('area', 'governorate').distinct()
    provider_types = models.Network.objects.values_list('provider_type', flat=True).distinct()
    specialties = models.Network.objects.values_list('provider_specialty', flat=True).distinct()
    data = {
        'governates': list(governates),
        'areas': list(areas),
        'provider_types': list(provider_types),
        'specialties': list(specialties)
    }
    return JsonResponse(data)

# Fetch filtered results
def fetch_filtered_results(request):
    filters = json.loads(request.body)
    query = Q()
    if filters.get('governate'):
        query &= Q(governorate=filters['governate'])
    if filters.get('area'):
        query &= Q(area=filters['area'])
    if filters.get('provider_type'):
        query &= Q(provider_type=filters['provider_type'])
    if filters.get('speciality'):
        query &= Q(provider_specialty=filters['speciality'])
    results = models.Network.objects.filter(query)
    data = list(results.values('provider_name', 'latitude', 'longitude', 'address', 'phone_number'))
    return JsonResponse(data, safe=False)

@email_verified_required
@login_required
def medical_network(request):
    try:
        member = models.Member.objects.get(user=request.user)
    except models.Member.DoesNotExist:
        member = None
    return render(request, 'network.html', {'member': member})



@login_required
def payment(request):
    if not request.user.email_verified:
        messages.error(request, "Please verify your email first")
        return redirect('Discount_Card:email_not_verified')
    member = models.Member.objects.get(user=request.user)
    message = ""
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        try:
            coupon = models.Coupon.objects.get(code=code, active=True)
            print(f"Coupon found: {coupon.code}, valid_to: {coupon.valid_to}, today: {timezone.localdate()}")  # Debugging line
            coupon.use_coupon(request.user)
            message = "Code applied successfully!"
            return redirect('Discount_Card:index')
        except ValueError as e:
            message = str(e)
        except models.Coupon.DoesNotExist:
            print(f"Coupon not found or invalid.")  # Debugging line
            message = "Invalid code"
    return render(request, 'payment.html',{
        'member':member, 'message': message
    })



