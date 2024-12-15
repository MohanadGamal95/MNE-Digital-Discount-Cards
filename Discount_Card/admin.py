from django.contrib import admin
from .models import User, Member, Coupon, CouponUser, Network

# Register the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

# Register the Member model
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'payment_status', 'valid_until', 'active_subscription')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('payment_status', 'valid_until')
    ordering = ('user__email',)

# Register the Coupon model
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'active', 'max_uses', 'current_uses', 'valid_from', 'valid_to')
    search_fields = ('code',)
    list_filter = ('active', 'valid_from', 'valid_to')
    ordering = ('valid_from',)

# Register the CouponUser model
@admin.register(CouponUser)
class CouponUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon')
    search_fields = ('user__email', 'coupon__code')
    ordering = ('user__email',)

# Register the Network model
@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'provider_code', 'provider_type', 'governate', 'area', 'phone_number')
    search_fields = ('provider_name', 'provider_code')
    list_filter = ('provider_type', 'governate', 'area')
    ordering = ('provider_name',)
