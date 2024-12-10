from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Question, ExamYear
import json
import random  # randomをインポート

# 難易度を更新するAPIエンドポイント
@login_required
@csrf_exempt  # 必要に応じて追加（APIエンドポイント用）
def update_difficulty(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # JSONデータを解析
            difficulty = data.get("difficulty")
            valid_choices = ['IP', 'SG', 'FE', 'AP']

            if difficulty not in valid_choices:
                return JsonResponse({"success": False, "message": "無効な難易度が選択されました。"})

            # ログイン中のユーザーに難易度を保存
            user = request.user
            user.difficulty = difficulty
            user.save()

            return JsonResponse({"success": True, "message": "難易度が保存されました！"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"エラーが発生しました: {str(e)}"})
    return JsonResponse({"success": False, "message": "無効なリクエストです。"})

@login_required
def study_view(request):
    """ランダム問題学習画面"""
    return render(request, 'dress/study.html')  # study.htmlを返す

# 難易度に基づいてランダムな問題を取得するAPIエンドポイント
@login_required
def question_list_by_difficulty(request):
    user = request.user
    difficulty = user.difficulty  # ユーザーが設定した難易度
    questions = Question.objects.filter(difficulty=difficulty)

    if not questions:
        return JsonResponse({"error": "この難易度には問題がありません。"}, status=404)

    # ランダムに問題を選択
    question = random.choice(questions)

    # 問題の選択肢を含むデータを返す
    data = {
        "questions_number": question.questions_number,
        "questions_text": question.questions_text,
        "choices": {
            "a": question.choice_a_text,
            "b": question.choice_b_text,
            "c": question.choice_c_text,
            "d": question.choice_d_text,
        },
        "question_id": question.id,
    }

    return JsonResponse(data)

# トップページビュー
def index_view(request):
    return render(request, "dress/index.html", {"user": request.user})

# 出題年度一覧ビュー
def exam_year_list(request):
    exam_years = ExamYear.objects.all().order_by('-name')  # 年度を降順で取得
    context = {
        'exam_years': exam_years,
    }
    return render(request, 'dress/quest_year.html', context)

# 問題一覧表示
class ListQuestionsView(ListView):
    template_name = 'dress/quest_list.html'
    model = Question
    context_object_name = 'questions'

    def get_queryset(self):
        # URLクエリパラメータまたはkwargsから年度名を取得
        exam_year_name = self.kwargs.get('exam_year_name')
        if exam_year_name:
            # question_numberを昇順に並び替える
            return Question.objects.filter(exam_year__name=exam_year_name).order_by('questions_number')
        return Question.objects.all().order_by('questions_number')

    def get_context_data(self, **kwargs):
        # コンテキストに年度名を追加
        context = super().get_context_data(**kwargs)
        exam_year_name = self.kwargs.get('exam_year_name')
        context['year'] = exam_year_name  # 年度名をテンプレートに渡す
        return context

# 問題詳細ビュー
class QuestionDetailView(DetailView):
    template_name = 'dress/question_detail.html'
    model = Question
    context_object_name = 'question'

    def post(self, request, *args, **kwargs):
        # 対象の問題オブジェクトを取得
        self.object = self.get_object()
        selected_choice = request.POST.get('choice')  # ユーザーが選択した選択肢

        # 正解判定
        correct = selected_choice == self.object.correct_answer

        # テンプレートを再レンダリング
        return render(request, self.template_name, {
            'question': self.object,
            'selected_choice': selected_choice,
            'correct': correct,
        })

# ホームページビュー
def home_view(request):
    return render(request, "dress/home.html", {"user": request.user})

# 学習関連ビュー
def learn_view(request):
    return render(request, 'dress/learn.html')  # 中間学習画面

def study_view(request):
    return render(request, 'dress/study.html')  # ランダム問題学習画面

def review_view(request):
    return render(request, 'dress/review.html')  # 復習画面

def all_questions_view(request):
    return render(request, 'dress/all_questions.html')  # 問題一覧画面

def select_difficulty_view(request):
    return render(request, 'dress/select_difficulty.html')  # 難易度選択画面
