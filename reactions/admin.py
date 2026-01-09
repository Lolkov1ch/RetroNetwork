from django.contrib import admin
from .models import Like

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "comment", "created")

    def created(self, obj):
        return obj.created_at
    created.admin_order_field = "created_at"
    created.short_description = "Created At"
