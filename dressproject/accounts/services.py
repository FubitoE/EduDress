# services.py
from .models import UserProgress

def process_learning_session(user, questions_solved):
    """学習セッションで解いた問題数に応じて経験値を加算"""
    experience_per_question = 10  # 問題1問あたりの経験値
    total_experience = questions_solved * experience_per_question

    if hasattr(user, 'progress'):  # UserProgressが存在する場合のみ処理
        user.progress.add_experience(total_experience)
