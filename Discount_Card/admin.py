from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
import pandas as pd
from .models import User, Member, Coupon, CouponUser, Network, ExcelUpload

# Register the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'national_id', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'national_id')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

# Register the Member model
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'payment_status', 'valid_until', 'active_subscription')
    search_fields = ('user__email', 'user__full_name')
    list_filter = ('payment_status', 'valid_until')
    ordering = ('user__email',)

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Full Name'

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


class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelUpload
        fields = ['file']

# Register the Network model
@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'provider_code', 'provider_type', 'governorate', 'area', 'phone_number')
    search_fields = ('provider_name', 'provider_code')
    list_filter = ('provider_type', 'governorate', 'area')
    ordering = ('provider_name',)

# Register the ExcelUpload model with automatic processing
@admin.register(ExcelUpload)
class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        excel_file = obj.file
        df = pd.read_excel(excel_file)

        # Clear existing data
        Network.objects.all().delete()

        # Add new data from Excel
        for index, row in df.iterrows():
            try:
                Network.objects.create(
                    provider_code=row['Provider ID'],
                    provider_name=row['Provider Name'],
                    address=row['Address'],
                    governorate=row['Governorate'],
                    area=row['Area'],
                    provider_type=row['Provider Type'],
                    provider_specialty=row['Provider Specialty'],
                    latitude=row['Latitude'],
                    longitude=row['Longitude'],
                    phone_number=row['Phone Number']
                )
            except Exception as e:
                print(f"Error processing row {index}: {e}")  # Debugging: Print error message

        self.message_user(request, "Data replaced successfully.")