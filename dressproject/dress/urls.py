from django.urls import path
from . import views
from .views import ListQuestionsView, QuestionDetailView

urlpatterns = [
    path('', views.index_view, name='index'),  # トップページ
    path('home/', views.home_view, name='home'),  # ホームページ
    path('exam-years/', views.exam_year_list, name='exam_year_list'),  # 出題年度一覧
    path('questions/', ListQuestionsView.as_view(), name='question_list'),  # 問題一覧ページ
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),  # 問題詳細ページ
    path('questions/year/<str:exam_year_name>/', ListQuestionsView.as_view(), name='questions_by_year'),  # 年度別問題ページ
]
