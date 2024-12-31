from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator, MinLengthValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    national_id = models.CharField(
        max_length=14,
        unique=True,
        validators=[MinLengthValidator(9)]
    )
    phone_number = models.CharField(null=True, blank=True, max_length=14,
        validators=[RegexValidator(regex=r'^\+20\d{10}$')]
    )
    email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'full_name', 'national_id']
    
    @property
    def member(self):
        return getattr(self, '_member', None)

    @member.setter
    def member(self, value):
        self._member = value

    def get_member(self):
        try:
            return self.member_set.first()  # Assuming one Member per user
        except Member.DoesNotExist:
            return None

    def __str__(self):
        return self.email

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    PAYMENT_STATUS = [
        ('verified', 'verified'),
        ('not_verified', 'not_verified')
    ]
    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS, default='not_verified')
    valid_until = models.DateField(null=True, blank=True)
    renewals = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['payment_status', 'valid_until'])
        ]

    def active_subscription(self):
        return self.payment_status == 'verified' and (self.valid_until is None or self.valid_until >= timezone.now().date())

    def __str__(self):
        return f"{self.user.full_name} - {self.user.email}" 

class Coupon(models.Model):
    code = models.CharField(max_length=12)
    active = models.BooleanField(default=True)
    max_uses = models.IntegerField()
    current_uses = models.IntegerField(default=0)
    valid_from = models.DateField(default=timezone.localdate)
    valid_to = models.DateField()

    def __str__(self):
        return self.code

    def use_coupon(self, user):
        if not self.active:
            raise ValueError("Code is no longer active.")
        if self.current_uses >= self.max_uses:
            raise ValueError("Code usage limit reached.")
        if self.valid_to < timezone.now().date():
            raise ValueError("Code has expired.")
        if CouponUser.objects.filter(user=user, coupon=self).exists():
            raise ValueError("Code already used.")
        member = Member.objects.get(user=user)
        if member.payment_status == 'verified':
            raise ValueError("Subscription already active")

        self.current_uses += 1
        self.save()
        CouponUser.objects.create(user=user, coupon=self)
        member.payment_status = 'verified'
        member.start_date = timezone.localdate()
        member.valid_until = timezone.localdate() + timedelta(days=365)
        member.renewals += 1
        member.save()
        return True

class CouponUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'coupon')

    def __str__(self):
        return f"{self.user.email} - {self.coupon.code}"


class Network(models.Model):
    provider_code = models.CharField(max_length=8)
    provider_name = models.CharField(max_length=1000)
    governorate = models.CharField(max_length=64)
    area = models.CharField(max_length=256)
    provider_type = models.CharField(max_length=64)
    provider_specialty = models.CharField(max_length=256)
    address = models.TextField()
    longitude = models.DecimalField(max_digits=27, decimal_places=24)
    latitude = models.DecimalField(max_digits=27, decimal_places=24)
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.provider_name} {self.provider_code}"


class ExcelUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name