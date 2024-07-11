from django.contrib import admin

from .models import User, Post

admin.site.register(User)
admin.site.register(Post)

from .models import Dialogue


# class DialogueExampleAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None, {'fields': ['name']}),
#         ('JSON', {'fields': ['detail_json_formatted']}),
#     ]
#     list_display = ('name',)
#     readonly_fields = ('detail_json', 'detail_json_formatted')


admin.site.register(Dialogue)
