from django.contrib import admin

from users.models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email',)
    list_display = (
        'id',
        'email',
        'is_staff',
        'is_active',
    )
    search_fields = ('email',)
    exclude = ('password',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    list_display = (
        'id',
        'user',
        'date_payment',
    )