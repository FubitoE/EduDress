from django.urls import path
from .views import signup_view, login_view, logout_view, learning_session_view, update_user_info

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path("learning_session/", learning_session_view, name="learning_session"),
    path("update-user-info/", update_user_info, name="update_user_info"),
]
