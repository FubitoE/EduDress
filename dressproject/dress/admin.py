from django.contrib import admin
from .models import Question, Questionimg, Parts, Style, ExamYear, QuestionPart, UserProfile

from django.utils.html import format_html  # HTMLをレンダリングするためにインポート

@admin.register(ExamYear)
class ExamYearAdmin(admin.ModelAdmin):
    list_display = ['name']


# QuestionPart のインライン編集設定
class QuestionPartInline(admin.TabularInline):
    model = QuestionPart
    extra = 1
    fields = ('text', 'image', 'position', 'order')
    ordering = ['order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('questions_id','questions_number', 'questions_text', 'difficulty', 'exam_year')
    search_fields = ('questions_text', 'questions_id', 'exam_year__name')  # exam_year__name に修正
    inlines = [QuestionPartInline]  # QuestionPart をインラインで表示

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('questions_id',)
        return ()


@admin.register(Questionimg)
class QuestionImgAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'question_imgA', 'question_imgB', 'explanation_imgA', 'explanation_imgB')
    search_fields = ('question__questions_text',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('id',)
        return ()


@admin.register(Parts)
class PartsAdmin(admin.ModelAdmin):
    list_display = ('parts_id', 'parts_name', 'parts_category', 'parts_default', 'parts_image', 'created_at', 'updated_at')


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_preview')  # リスト表示で画像をプレビュー
    readonly_fields = ('avatar_preview',)  # 編集画面で画像プレビューを表示

    def avatar_preview(self, obj):
        if obj.avatar_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.avatar_image.url)
        return "No image"
    avatar_preview.short_description = "Avatar Preview"  # カラム名を設定

admin.site.register(UserProfile, UserProfileAdmin)