from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random

# 難易度の選択肢
DIFFICULTY = (
    ('IP', 'Iパス'), 
    ('SG', 'セキュマネ'), 
    ('FE', '基本'), 
    ('AP', '応用')
)

# カスタムユーザーマネージャー
class CustomUserManager(BaseUserManager):
    def create_user(self, nickname, password=None, **extra_fields):
        if not nickname:
            raise ValueError('ニックネームは必須です')
        if password is None:
            raise ValueError('パスワードは必須です')  # パスワード確認

        # ユーザー名の生成とユニークチェック
        username = self.generate_unique_username(nickname)

        # ユーザーIDの生成とユニークチェック
        user_id = self.generate_unique_user_id()

         # extra_fields に既に username が含まれていた場合、それを削除する
        extra_fields.pop('username', None)

        user = self.model(user_id=user_id, username=username, nickname=nickname, **extra_fields)
        user.set_password(password)  # パスワードをハッシュ化
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # スーパーユーザー作成時にもuser_idを自動で生成
        return self.create_user(nickname, password, **extra_fields)

    def generate_unique_username(self, nickname):
        # ユーザー名をnicknameを基に生成
        base_username = nickname
        username = base_username

        # 同じユーザー名が存在しないかチェック
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            # もし既存のユーザー名があれば、数字を追加
            username = f"{base_username}{counter}"
            counter += 1
        
        return username

    def generate_unique_user_id(self):
        # ユーザーIDをランダムに生成（6桁）
        user_id = str(random.randint(100000, 999999))

        # 同じuser_idが存在しないかチェック
        while CustomUser.objects.filter(user_id=user_id).exists():
            user_id = str(random.randint(100000, 999999))  # 再生成
        
        return user_id
    


# カスタムユーザー
class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=6, primary_key=True)  # 6桁の文字列ID（自動生成）
    nickname = models.CharField(max_length=50)  # ユニークは削除
    username = models.CharField(max_length=50, unique=True)  # ユーザー名として追加
    gender = models.CharField(max_length=10, choices=[('male', '男性'), ('female', '女性'), ('private', '非公開')], blank=True, default='private')  # デフォルト値設定
    difficulty = models.CharField(max_length=100, choices=DIFFICULTY)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # 管理者かどうか
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'  # ユーザー名として使用するフィールド
    REQUIRED_FIELDS = ['nickname']  # 他に必須なフィールド（nicknameは必須）

    objects = CustomUserManager()  # マネージャーの指定（ここで CustomUserManager をインスタンス化）

    def __str__(self):
        return self.nickname

class UserProgress(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='progress')  # 外部キーで関連付け
    current_rank = models.IntegerField(default=1)  # 初期ランクは1
    current_experience = models.IntegerField(default=0)  # 現在の経験値
    experience_to_next_rank = models.IntegerField(default=50)  # 次のランクまでの必要経験値

    def add_experience(self, gained_experience):
        """経験値を追加し、ランクアップをチェックする"""
        self.current_experience += gained_experience

        # ランクアップ処理を実行
        while self.current_experience >= self.experience_to_next_rank:
            self.level_up()

        self.save()

    def level_up(self):
        """ランクアップのロジック"""
        if self.current_rank < 10:  # 最大ランクは10
            self.current_experience -= self.experience_to_next_rank  # 次のランクへの経験値を減算
            self.current_rank += 1  # ランクを上げる
            self.experience_to_next_rank = self.calculate_next_rank_experience()  # 次のランク必要経験値を更新
        else:
            self.current_experience = self.experience_to_next_rank  # 最大ランクに到達時

    def calculate_next_rank_experience(self):
        """次のランクに必要な経験値を計算"""
        base_experience = 50  # ランク1の必要経験値
        growth_factor = 1.5  # 必要経験値の増加率
        return int(base_experience * (self.current_rank ** growth_factor))

    def __str__(self):
        return f"{self.user.nickname} - Rank: {self.current_rank}"
