from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import MyUserCreationForm,MyUserChangeForm
from .models import MyUser,Tutor,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday,Orders,Review
class MyUserAdmin(UserAdmin):
    model = MyUser
    add_form = MyUserCreationForm
    form=MyUserChangeForm
    list_display = ['username','email','phn_num']
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('phn_num','locality','is_tutor','is_student')}),
    )
admin.site.register(MyUser,MyUserAdmin)
admin.site.register(Tutor)
admin.site.register(Monday)
admin.site.register(Tuesday)
admin.site.register(Wednesday)
admin.site.register(Thursday)
admin.site.register(Friday)
admin.site.register(Saturday)
admin.site.register(Sunday)
admin.site.register(Orders)
admin.site.register(Review)