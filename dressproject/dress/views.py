from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Question, ExamYear, Parts, UserProfile
from accounts.models import UserProgress
from django.core.files.base import ContentFile
import json
import base64
import random  # randomをインポート

# パーツカテゴリーの描画順序
PARTS_CATEGORY_ORDER = {
    'background': 0,
    'base': 1,
    'clothes': 2,
    'eyes': 3,
    'accessory': 4,
    'hair': 5,
}

# デフォルトアバター生成ロジック
def render_default_avatar(user):
    """
    parts_default=Trueのパーツを`parts_category`順にソートして取得。
    """
    default_parts = Parts.objects.filter(parts_default=True)
    sorted_parts = sorted(default_parts, key=lambda part: PARTS_CATEGORY_ORDER[part.parts_category])
    return [part.parts_image.url for part in sorted_parts]

@login_required
def home_view(request):
    """
    ユーザーの進行状況、アバター情報を統合して表示。
    """
    # ユーザー進行状況の取得または作成
    progress, created = UserProgress.objects.get_or_create(user=request.user)

    # ユーザープロフィールとアバター
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    avatar_url = user_profile.avatar_image.url if user_profile.avatar_image else None
    default_avatar_urls = None

    # カスタムアバターがない場合はデフォルトを生成
    if not avatar_url:
        default_avatar_urls = render_default_avatar(request.user)

    context = {
        "user": request.user,
        "progress": progress,  # ランクと経験値情報
        "avatar_url": avatar_url,  # カスタムアバターURL
        "default_avatar_urls": default_avatar_urls,  # デフォルトアバター画像URL
    }

    return render(request, "dress/home.html", context)

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

@login_required
def question_view(request, pk=None):
    """
    - pk が指定されている場合: 指定された問題を取得し、questions_number 昇順で次の問題を取得
    - pk が指定されていない場合: ランダム出題ではなく固定された問題
    """
    if pk:
        # 現在の問題を取得
        question = get_object_or_404(Question, pk=pk)

        # 次の問題を取得: 同じ難易度・年度で、questions_number の昇順で取得
        next_question = (
            Question.objects.filter(
                difficulty=question.difficulty,
                exam_year=question.exam_year,
                questions_number__gt=question.questions_number  # 現在の番号より大きい問題を取得
            ).order_by('questions_number').first()  # 昇順で最初の1件を取得
        )
        next_question_id = next_question.id if next_question else None

    else:
        # pk がない場合の処理 (通常はランダム出題やエラー処理)
        return render(request, "dress/question_detail.html", {"error": "問題が指定されていません。"})

    # POSTリクエストで回答処理
    if request.method == "POST":
        selected_choice = request.POST.get("choice")
        if not selected_choice or selected_choice not in ["a", "b", "c", "d"]:
            return render(request, "dress/question_detail.html", {
                "question": question,
                "error": "無効な選択肢です。",
            })

        correct = selected_choice == question.correct_answer
        return render(request, "dress/question_detail.html", {
            "question": question,
            "selected_choice": selected_choice,
            "correct": correct,
            "next_question_id": next_question_id,  # 次の問題のIDを渡す
        })

    # GETリクエストで問題を表示
    return render(request, "dress/question_detail.html", {
        "question": question,
        "next_question_id": next_question_id,  # 次の問題のIDをテンプレートに渡す
    })
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

# 学習関連ビュー
def learn_view(request):
    return render(request, 'dress/learn.html')  # 中間学習画面

@login_required
def study_view(request):
    """
    ランダム問題学習画面: ユーザーが選択した難易度に基づいてランダムな問題を出題。
    """
    user = request.user
    difficulty = getattr(user, "difficulty", None)  # ユーザーが選択した難易度を取得

    if not difficulty:
        return render(request, 'dress/study.html', {"error": "難易度が選択されていません。"})

    # 指定された難易度の問題を取得
    questions = Question.objects.filter(difficulty=difficulty)

    if not questions.exists():
        return render(request, 'dress/study.html', {"error": f"{difficulty}の問題が見つかりません。"})

    # ランダムに問題を選択
    question = random.choice(questions)

    # 選択した問題をテンプレートに渡す
    context = {
        "question": question,
        "choices": {
            "a": question.choice_a_text,
            "b": question.choice_b_text,
            "c": question.choice_c_text,
            "d": question.choice_d_text,
        },
    }

    return render(request, 'dress/question_detail.html', context)

def review_view(request):
    return render(request, 'dress/review.html')  # 復習画面

def all_questions_view(request):
    return render(request, 'dress/all_questions.html')  # 問題一覧画面

def select_difficulty_view(request):
    return render(request, 'dress/select_difficulty.html')  # 難易度選択画面

# パーツカテゴリーの描画順序
PARTS_CATEGORY_ORDER = {
    'background': 0,
    'base': 1,
    'clothes': 2,
    'eyes': 3,
    'accessory': 4,
    'hair': 5,
}

# アバター保存API
@login_required
@csrf_exempt
def save_avatar(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_data = data.get("image")

            if not image_data:
                return JsonResponse({"success": False, "message": "画像データがありません。"})

            # 画像データをデコードして保存
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"user_{request.user.user_id}.png"
            file_data = ContentFile(base64.b64decode(imgstr), name=file_name)

            # ユーザープロフィールに保存
            user_profile = UserProfile.objects.get(user_id=request.user.user_id)
            user_profile.avatar_image.save(file_name, file_data)
            user_profile.save()

            return JsonResponse({"success": True, "message": "アバターが保存されました！"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"エラーが発生しました: {str(e)}"})

    return JsonResponse({"success": False, "message": "無効なリクエストです。"})

# デフォルトアバターの生成
@login_required
def render_default_avatar(user):
    """
    parts_default=Trueのパーツを`parts_category`順にソートして取得。
    """

    file_name = f"user_{user.user_id}.png"

    default_parts = Parts.objects.filter(parts_default=True)
    sorted_parts = sorted(default_parts, key=lambda part: PARTS_CATEGORY_ORDER[part.parts_category])
    image_urls = [part.parts_image.url for part in sorted_parts]
    return image_urls

# アバターカスタマイズ画面
@login_required
def customize_view(request):
    """
    パーツリストを`parts_category`と`parts_name`でソートして渡す。
    """
    parts = Parts.objects.all().order_by('parts_category', 'parts_name')
    context = {
        "PARTS_CATEGORY": [
            ('hair', '髪'),
            ('base', '素体'),
            ('eyes', '目'),
            ('clothes', '服'),
            ('accessory', 'アクセサリー'),
            ('background', '背景')
        ],
        "parts": parts,
    }
    return render(request, "dress/customize.html", context)

