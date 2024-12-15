from django.test import TestCase

# # Create your tests here.
# # Register User model (customizing it if needed)
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'is_active')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('-date_joined',)
#     list_filter = ('is_active',)

# # Register Member model
# @admin.register(Member)
# class MemberAdmin(admin.ModelAdmin):
#     list_display = ('user', 'start_date', 'payment_status', 'valid_until', 'is_active')
#     list_filter = ('payment_status', 'renewals')
#     search_fields = ('user__email',)

# # Register Coupon model
# @admin.register(Coupon)
# class CouponAdmin(admin.ModelAdmin):
#     list_display = ('code', 'active', 'max_uses', 'current_uses', 'valid_from', 'valid_to')
#     list_filter = ('active', 'valid_from', 'valid_to')
#     search_fields = ('code',)

# # Register CouponUser model
# @admin.register(CouponUser)
# class CouponUserAdmin(admin.ModelAdmin):
#     list_display = ('user', 'coupon', 'user_email', 'coupon_code')
#     search_fields = ('user__email', 'coupon__code')

#     def user_email(self, obj):
#         return obj.user.email

#     def coupon_code(self, obj):
#         return obj.coupon.code

# # Register Network model
# @admin.register(Network)
# class NetworkAdmin(admin.ModelAdmin):
#     list_display = ('provider_name', 'provider_code', 'provider_type', 'governate', 'area', 'longitude', 'latitude')
#     list_filter = ('provider_type', 'governate', 'provider_specialty')
#     search_fields = ('provider_name', 'provider_code', 'area')

