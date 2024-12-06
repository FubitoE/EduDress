from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.http import JsonResponse
from .models import Question, ExamYear

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
