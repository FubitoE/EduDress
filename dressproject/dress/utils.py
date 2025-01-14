import random
from dress.models import Question, RandomQuestion

def extract_user_questions(user, num_questions=20):
    """
    ログインユーザーのdifficultyを参照し、Questionモデルからデータを抽出
    """
    # ログインユーザーの難易度を取得
    user_difficulty = user.difficulty

    # Questionモデルから難易度に一致するデータを取得
    questions = Question.objects.filter(difficulty=user_difficulty)

    # ランダムに指定数抽出
    selected_questions = random.sample(list(questions), min(num_questions, questions.count()))

    # RandomQuestionモデルを初期化
    RandomQuestion.objects.all().delete()

    # 抽出結果を保存
    for question in selected_questions:
        RandomQuestion.objects.create(question=question)
