from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .services import process_learning_session
from django.contrib.auth.decorators import login_required

User = get_user_model()

def index_view(request):
    return render(request, "dress/index.html", {"user": request.user})

def login_view(request):
    if request.method == "POST":
        # フォームからニックネームとパスワードを取得
        username = request.POST["username"]
        password = request.POST["password"]

        # ユーザーを認証
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 認証成功
            login(request, user)
            return redirect('home')  # ログイン後、questionsページにリダイレクト
        else:
            # 認証失敗
            messages.error(request, "ニックネームまたはパスワードが間違っています")
    
    return render(request, "dress/index.html")  # ログインフォームを含むテンプレートを表示

def logout_view(request):
    logout(request)
    return redirect("/")  # ログアウト後にトップページに戻る

def signup_view(request):
    if request.method == "POST":
        nickname = request.POST['nickname']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, "パスワードが一致しません")
            return redirect('accounts:signup')  # パスワードが一致しない場合は再度signup画面に戻る
        
        # ユーザーを作成
        try:
            user = User.objects.create_user(username=nickname, password=password)
            user.save()
            
            # 自動ログイン処理
            login(request, user)
            return redirect('question_list')  # 登録後、質問一覧ページに遷移
        except Exception as e:
            messages.error(request, f"ユーザー作成エラー: {e}")
            return redirect('accounts:signup')
    
    return render(request, 'accounts/signup.html')  # GETリクエスト時はサインアップフォームを表示

@login_required
def learning_session_view(request):
    if request.method == "POST":
        questions_solved = int(request.POST.get("questions_solved", 0))  # 解いた問題数を取得
        process_learning_session(request.user, questions_solved)  # 学習セッションを処理
        return redirect('home')  # 処理後にリダイレクト

    return render(request, "dress/learning_session.html")
