from django.contrib import admin


from .models import Profile, Task

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "managed_by")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "status", "due_date")
    list_filter = ("status", "due_date")