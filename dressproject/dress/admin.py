from django.contrib import admin
from .models import Question, Questionimg, Parts, Style

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('questions_id', 'questions_text', 'difficulty', 'exam_year')
    search_fields = ('questions_text', 'questions_id')

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
