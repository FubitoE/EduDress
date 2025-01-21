from django.urls import path
from django.conf.urls import handler404
from . import views
from .views import ListQuestionsView, QuestionDetailView

urlpatterns = [
    path('', views.index_view, name='index'),  # トップページ
    path('home/', views.home_view, name='home'),  # ホームページ
    path('customize/', views.customize_view, name='customize'),  # アバター着せ替え画面
    path('api/save-avatar/', views.save_avatar, name='save_avatar'),  # アバター保存API
    path('exam-years/', views.exam_year_list, name='exam_year_list'),  # 出題年度一覧
    path('questions/', ListQuestionsView.as_view(), name='question_list'),  # 問題一覧ページ
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),  # 問題詳細ページ
    path('questions/year/<str:exam_year_name>/', ListQuestionsView.as_view(), name='questions_by_year'),  # 年度別問題ページ

    # 学習関連のルート
    path('learn/', views.learn_view, name='learn'),  # 中間学習画面
    path('random_question/', views.random_question_view, name='random_question'),  # ランダム問題生成
    path('random_question/<int:pk>/', views.random_question_detail, name='random_question_detail'),  # ランダム問題学習画面
    path('random_question/result/', views.result_view, name='result'),
    path('learn/review/', views.review_view, name='review'),  # 復習画面
    path('review/solve/<int:review_id>/', views.review_result, name='review_result'),
    path('solve/<int:review_id>/', views.solve_review_question, name='solve_review_question'),
    path('learn/all-questions/', views.all_questions_view, name='all_questions'),  # 問題一覧画面
    path('learn/select-difficulty/', views.select_difficulty_view, name='select_difficulty'),  # 難易度選択画面
    path('api/update-difficulty/', views.update_difficulty, name='update_difficulty'),  # 難易度更新API
    path('api/question/', views.question_list_by_difficulty, name='question_list_by_difficulty'),  # ランダム問題取得API
]

# handler404 を設定して、存在しないページにアクセスされた場合にエラーページを表示
handler404 = 'dress.views.page_not_found'
