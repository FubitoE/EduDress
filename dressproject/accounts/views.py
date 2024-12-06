from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .services import process_learning_session
from .models import UserProgress

User = get_user_model()

def index_view(request):
    return render(request, "dress/index.html", {"user": request.user})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "ニックネームまたはパスワードが間違っています")
    
    return render(request, "dress/index.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def signup_view(request):
    if request.method == "POST":
        nickname = request.POST['nickname']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, "パスワードが一致しません")
            return redirect('accounts:signup')

        try:
            user = User.objects.create_user(nickname=nickname, password=password)
            user.save()
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, f"ユーザー作成エラー: {e}")
            return redirect('accounts:signup')
    
    return render(request, 'accounts/signup.html')

@login_required
def learning_session_view(request):
    if request.method == "POST":
        questions_solved = int(request.POST.get("questions_solved", 0))
        process_learning_session(request.user, questions_solved)
        return redirect('home')

    return render(request, "dress/learning_session.html")

@login_required
def home(request):
    user = request.user
    progress = UserProgress.objects.get(user=user)
    progress_percentage = (progress.current_experience / progress.experience_to_next_rank) * 100
    return render(request, 'home.html', {
        'progress': progress,
        'progress_percentage': progress_percentage,
    })

@login_required
def update_user_info(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_nickname = data.get("nickname")
        new_username = data.get("username")

        # ユーザー名の重複チェック
        if new_username and User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
            return JsonResponse({"success": False, "message": "このユーザー名は既に使用されています。"})

        user = request.user
        if new_nickname:
            user.nickname = new_nickname
        if new_username:
            user.username = new_username
        user.save()

        return JsonResponse({"success": True, "message": "情報が正常に更新されました。"})
