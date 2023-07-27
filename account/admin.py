from django.contrib import admin
from django.utils.html import format_html

from .models import User


class UserAdmin(admin.ModelAdmin):
    # list view
    list_display = ('username', 'email', 'is_superuser', 'register_date')

    # 10 items per page
    list_per_page = 10

    # search box
    search_fields = ('username',)

    # filter options
    list_filter = ('is_superuser',)

    # display register date in green
    def register_date(self, obj):
        return format_html(
            '<span style="color: green;">{}</span>',
            obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        )


admin.site.register(User, UserAdmin)
