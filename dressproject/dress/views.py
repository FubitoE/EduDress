from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now  # 追加
from .models import Question, ExamYear, Parts, UserProfile, RandomQuestion, Review
from accounts.models import UserProgress
from django.core.files.base import ContentFile
from .utils import extract_user_questions
import json
import base64
import random  # randomをインポート

def page_not_found(request, exception):
    return render(request, 'error_page.html', status=404)

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

    # ランクが上がったかどうかを判定
    previous_rank = progress.previous_rank  # previous_rankを保存しておく必要があります
    current_rank = progress.current_rank
    if current_rank > previous_rank:
        messages.success(request, "ランクが上がりました！")

    # ランクを保存しておく
    progress.previous_rank = current_rank
    progress.save()

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
                return JsonResponse({"success": False, "message": "資格を選択してください。"})

            # ログイン中のユーザーに難易度を保存
            user = request.user
            user.difficulty = difficulty
            user.save()

            return JsonResponse({"success": True, "message": "資格が保存されました！"})
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
    - pk が指定されている場合: 特定の問題を取得
    - pk が指定されていない場合: ランダムな問題を取得 (learn/study)
    """
    if pk:
        # 特定の問題を取得
        question = get_object_or_404(Question, pk=pk)
    else:
        # ランダムな問題を取得: ユーザーの選択した難易度に基づく
        user = request.user
        difficulty = getattr(user, "difficulty", None)  # ユーザーが選択した難易度を取得
        if not difficulty:
            return render(request, "dress/question_detail.html", {"error": "難易度が選択されていません。"})
        # 指定された難易度の問題を取得
        questions = Question.objects.filter(difficulty=difficulty)
        if not questions.exists():
            return render(request, "dress/question_detail.html", {"error": f"{difficulty}の問題が見つかりません。"})
        # ランダムに問題を選択
        question = random.choice(questions)
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
        })
    # GETリクエストで問題を表示
    return render(request, "dress/question_detail.html", {"question": question})
# トップページビュー
def index_view(request):
    return render(request, "dress/index.html", {"user": request.user})

# 出題年度一覧ビュー
@login_required
def exam_year_list(request):
    # 現在ログイン中のユーザーのdifficultyを取得
    user_difficulty = request.user.difficulty

    # ExamYearを全取得し、difficultyに基づいてフィルタリング
    exam_years = ExamYear.objects.all().order_by('-name')
    exam_years_with_questions = []

    for exam_year in exam_years:
        # 現在のユーザーのdifficultyと一致する問題が存在するか確認
        questions = Question.objects.filter(exam_year=exam_year, difficulty=user_difficulty)

        # データが存在する年度のみリストに追加
        if questions.exists():
            exam_years_with_questions.append({
                'name': exam_year.name,
                'has_questions': True,
            })
        else:
            exam_years_with_questions.append({
                'name': exam_year.name,
                'has_questions': False,
            })

    context = {
        'exam_years': exam_years_with_questions,
        'difficulty': user_difficulty,  # 現在の難易度をコンテキストに渡す
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
from django.urls import reverse

class QuestionDetailView(DetailView):
    template_name = 'dress/question_detail.html'
    model = Question
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 関連する年度名 (exam_year_name) を取得してテンプレートに渡す
        context['back_url'] = reverse('questions_by_year', kwargs={'exam_year_name': self.object.exam_year.name}) # 必要に応じて正しいフィールド名に変更
        return context

    def post(self, request, *args, **kwargs):
        # 対象の問題オブジェクトを取得
        self.object = self.get_object()
        selected_choice = request.POST.get('choice')  # ユーザーが選択した選択肢

        # 正解判定
        correct = selected_choice == self.object.correct_answer

        # 戻る先の URL を生成
        back_url = reverse('questions_by_year', kwargs={'exam_year_name': self.object.exam_year.name})

        # テンプレートを再レンダリング
        return render(request, self.template_name, {
            'question': self.object,
            'selected_choice': selected_choice,
            'correct': correct,
            'back_url': back_url,  # 戻るボタン用の URL を渡す
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
            ('accessory', 'アクセサリー')
        ],
        "parts": parts,
    }
    return render(request, "dress/customize.html", context)


def start_quiz(request):
    # ログイン中のユーザーの難易度に基づき問題を抽出
    extract_user_questions(request.user)

    # 最初の問題を取得
    first_question = RandomQuestion.objects.order_by('id').first()

    if not first_question:
        return render(request, 'no_questions.html')  # 該当問題がない場合のページ

    # クイズ開始画面を表示
    return redirect('question_detail', question_id=first_question.id)

@login_required
def random_question_view(request):
    user = request.user
    difficulty = user.difficulty  # CustomUserモデルのdifficultyを取得

    # 既存のランダム質問をクリア
    RandomQuestion.objects.filter(user=user).delete()

    # 指定された難易度の質問を取得
    questions = Question.objects.filter(difficulty=difficulty)

    if not questions.exists():
        return render(request, 'dress/no_questions.html', {"error": f"{difficulty}の問題が見つかりません。"})

    # ランダムに20問選択
    random_questions = random.sample(list(questions), min(len(questions), 20))

    # バルク作成用のオブジェクトリスト
    random_question_objects = [
        RandomQuestion(user=user, question=question, randomquest_id=i + 1)
        for i, question in enumerate(random_questions)
    ]

    # 一括作成
    RandomQuestion.objects.bulk_create(random_question_objects)

    # 最初の質問ページにリダイレクト
    first_question = RandomQuestion.objects.filter(user=user).order_by('id').first()
    if not first_question:
        return render(request, 'dress/no_questions.html', {"error": "質問を作成できませんでした。"})
    return redirect('random_question_detail', pk=first_question.id)



@login_required
def random_question_detail(request, pk):
    user = request.user
    
    try:
        # 存在しないIDの場合、404エラーが発生する
        question_entry = get_object_or_404(RandomQuestion, pk=pk, user=user)
    except Http404:
        # カスタムエラーページを返す
        return render(request, 'dress/error_page.html', {
            'error': '指定された質問は存在しません。',
        })
    
    question = question_entry.question

    # 次の問題を取得
    next_question = RandomQuestion.objects.filter(
        user=user,
        randomquest_id__gt=question_entry.randomquest_id
    ).order_by('randomquest_id').first()

    # 前の問題を取得
    previous_question = RandomQuestion.objects.filter(
        user=user,
        randomquest_id__lt=question_entry.randomquest_id
    ).order_by('-randomquest_id').first()

    if request.method == "POST":
        selected_choice = request.POST.get("choice")
        if not selected_choice or selected_choice not in ["a", "b", "c", "d"]:
            return render(request, "dress/random_quest.html", {
                "question": question,
                "error": "無効な選択肢です。",
                "next_question_id": next_question.id if next_question else None,
                "previous_question_id": previous_question.id if previous_question else None,
            })

        correct = selected_choice == question.correct_answer

        # 正誤と選択肢を保存
        question_entry.is_correct = correct
        question_entry.selected_choice = selected_choice
        question_entry.save()

        # 回答結果を表示するための情報をテンプレートに渡す
        context = {
            "question": question,
            "randomquest_id": question_entry.randomquest_id,
            "correct": correct,
            "selected_choice": selected_choice,
            "next_question_id": next_question.id if next_question else None,
            "previous_question_id": previous_question.id if previous_question else None,
        }
        return render(request, "dress/random_quest.html", context)

    # 初回表示用
    return render(request, "dress/random_quest.html", {
        "question": question,
        "randomquest_id": question_entry.randomquest_id,
        "next_question_id": next_question.id if next_question else None,
        "previous_question_id": previous_question.id if previous_question else None,
    })


@login_required
def result_view(request):
    # ユーザーの進行状況を取得または作成
    user_progress, created = UserProgress.objects.get_or_create(user=request.user)

    # 未処理の`RandomQuestion`を取得
    unprocessed_questions = RandomQuestion.objects.filter(user=request.user, is_processed=False)

    if not unprocessed_questions.exists():
        return render(request, 'dress/result.html', {
            'error': "新しい回答データがありません。",
            'user_progress': user_progress,
        })

    # 正解数と不正解数を集計
    correct_count = unprocessed_questions.filter(is_correct=True).count()
    incorrect_count = unprocessed_questions.filter(is_correct=False).count()

    # 経験値を計算
    total_experience = (correct_count * 3) + (incorrect_count * 1)

    # ユーザーに経験値を追加
    user_progress.add_experience(total_experience)

    # データ移行処理をトランザクションで実行
    with transaction.atomic():
        for question in unprocessed_questions:
            # Reviewにデータを移行
            Review.objects.create(
                user=question.user,
                question=question.question,
                is_correct=question.is_correct,
                selected_choice=question.selected_choice,
                processed_at=now()  # 現在時刻を保存
            )

        # 未処理データを`is_processed=True`に設定
        unprocessed_questions.update(is_processed=True)

    # 全回答数と正答率を計算
    total_questions = RandomQuestion.objects.filter(user=request.user).count()
    correct_answers = RandomQuestion.objects.filter(user=request.user, is_correct=True).count()
    accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    # 結果をテンプレートに渡す
    return render(request, 'dress/result.html', {
        'user_progress': user_progress,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy': round(accuracy, 2),
        'gained_experience': total_experience,
        'remaining_experience': user_progress.experience_to_next_rank - user_progress.current_experience,
    })


@login_required
def review_view(request):
    # ログイン中のユーザーの過去の間違い問題を降順で取得
    incorrect_reviews = Review.objects.filter(user=request.user, is_correct=False).order_by('id')

    return render(request, 'dress/review.html', {
        'incorrect_reviews': incorrect_reviews,
    })

from django.shortcuts import redirect

@login_required
def solve_review_question(request, review_id):
    user = request.user
    review = get_object_or_404(Review, id=review_id, user=user)
    question = review.question

    if request.method == "POST":
        selected_choice = request.POST.get("choice")
        if not selected_choice or selected_choice not in ["a", "b", "c", "d"]:
            return render(request, "dress/solve_question.html", {
                "review": review,
                "question": question,
                "error": "無効な選択肢です。",
            })

        correct = selected_choice == question.correct_answer

        # 正誤結果を保存
        review.selected_choice = selected_choice
        review.is_correct = correct
        review.save()

        # リダイレクトして結果画面を表示
        return redirect("review_result", review_id=review.id)

    # 初回表示用
    return render(request, "dress/solve_question.html", {
        "review": review,
        "question": question,
    })

@login_required
def review_result(request, review_id):
    user = request.user
    review = get_object_or_404(Review, id=review_id, user=user)
    question = review.question

    # ユーザープログレスを取得または作成
    user_progress, created = UserProgress.objects.get_or_create(user=user)

    # 正解の場合は経験値を追加
    gained_experience = 1 if review.is_correct else 0
    if gained_experience > 0:
        user_progress.add_experience(gained_experience)

    # 正解の場合、Reviewモデルから削除
    if review.is_correct:
        review.delete()

    remaining_experience = max(0, user_progress.experience_to_next_rank - user_progress.current_experience)

    return render(request, "dress/review_result.html", {
        "review": review,
        "question": question,
        "correct": review.is_correct,
        "gained_experience": gained_experience,
        "remaining_experience": remaining_experience,
    })

