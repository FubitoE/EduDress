from django.contrib import admin
from .models import CustomUser, UserProgress

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nickname', 'gender', 'difficulty', 'is_staff', 'date_joined')
    search_fields = ('nickname', 'gender')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('user_id',)
        return ()
    
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_rank', 'current_experience', 'experience_to_next_rank')  # 表示項目
    search_fields = ('user__nickname', 'user__username')  # 関連フィールドで検索可能
    list_filter = ('current_rank',)  # フィルタリングオプション
