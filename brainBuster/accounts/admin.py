from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_terms_accepted')
    list_filter = BaseUserAdmin.list_filter + ('profile__terms_accepted',)
    
    def get_terms_accepted(self, obj):
        return obj.profile.terms_accepted
    get_terms_accepted.short_description = 'Terms Accepted'
    get_terms_accepted.boolean = True

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register UserProfile model on its own
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'terms_accepted')
    list_filter = ('terms_accepted',)
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('user',)