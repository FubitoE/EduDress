import os
from django.db import models
from django.conf import settings  # AUTH_USER_MODEL を参照するためにインポート
from django.db.models.signals import post_delete
from django.dispatch import receiver

# 難易度の選択肢
DIFFICULTY = (
    ('IP', 'Iパス'),
    ('SG', 'セキュマネ'),
    ('FE', '基本'),
    ('AP', '応用')
)

class ExamYear(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="試験年度名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "試験年度"
        verbose_name_plural = "試験年度"


# 問題モデル
class Question(models.Model):
    questions_id = models.AutoField(primary_key=True)
    questions_number = models.IntegerField(default=0)
    questions_text = models.TextField()  # メインの問題文
    choice_a_text = models.TextField(blank=True, null=True)
    choice_a_image = models.ImageField(upload_to='choices_images/', blank=True, null=True)
    choice_b_text = models.TextField(blank=True, null=True)
    choice_b_image = models.ImageField(upload_to='choices_images/', blank=True, null=True)
    choice_c_text = models.TextField(blank=True, null=True)
    choice_c_image = models.ImageField(upload_to='choices_images/', blank=True, null=True)
    choice_d_text = models.TextField(blank=True, null=True)
    choice_d_image = models.ImageField(upload_to='choices_images/', blank=True, null=True)
    correct_answer = models.CharField(max_length=10, choices=[('a', 'ア'), ('b', 'イ'), ('c', 'ウ'), ('d', 'エ')], blank=True, default='a')
    exam_year = models.ForeignKey(ExamYear, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="試験年度")
    explanation = models.TextField()
    difficulty = models.CharField(max_length=100, choices=DIFFICULTY)

    def __str__(self):
        return self.questions_text[:50]  # 最初の50文字を返す


class QuestionPart(models.Model):
    POSITION_CHOICES = [
        ('top', '上部'),
        ('middle', '間'),
        ('bottom', '下部'),
    ]

    question = models.ForeignKey(Question, related_name="parts", on_delete=models.CASCADE)  # Questionと関連付け
    text = models.TextField(blank=True, null=True, verbose_name="テキスト")
    image = models.ImageField(upload_to='question_parts/', blank=True, null=True, verbose_name="画像")
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='middle', verbose_name="画像の位置")
    order = models.PositiveIntegerField(default=0, verbose_name="順序")  # 表示順序

    def __str__(self):
        if self.text:
            return f"Part for {self.question.questions_id}: {self.text[:30]}"
        return f"Part for {self.question.questions_id}: (Image)"

    class Meta:
        verbose_name = "問題の一部"
        verbose_name_plural = "問題の一部"
        ordering = ['order']  # 順序で並び替え

class RandomQuestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    randomquest_id = models.PositiveIntegerField(default=1)  # デフォルト値を設定
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(null=True, blank=True)  # 正誤判定を保存
    selected_choice = models.CharField(max_length=1, null=True, blank=True)  # ユーザーの選択肢を保存
    is_processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 既存の同じユーザーの質問数を取得
        if not self.pk:  # 新しいオブジェクトの場合のみ処理
            existing_count = RandomQuestion.objects.filter(user=self.user).count()
            self.randomquest_id = existing_count + 1  # 連番を設定（1から始まる）

        super().save(*args, **kwargs)  # 通常の保存を実行

    def __str__(self):
        return f"{self.user.username} - {self.question.questions_text} ({self.randomquest_id})"
    
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    randomquest_id = models.PositiveIntegerField()  # RandomQuestion の ID を保存
    is_correct = models.BooleanField(null=True, blank=True)
    is_retry = models.BooleanField(default=False)  # 再挑戦中かどうかを記録
    selected_choice = models.CharField(max_length=1, null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.questions_text} ({self.randomquest_id})"


class Questionimg(models.Model):
    question = models.ForeignKey(Question, related_name='images', on_delete=models.CASCADE)
    question_imgA = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_imgB = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_imgC = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_imgD = models.ImageField(upload_to='question_images/', blank=True, null=True)
    explanation_imgA = models.ImageField(upload_to='explanation_images/', blank=True, null=True)
    explanation_imgB = models.ImageField(upload_to='explanation_images/', blank=True, null=True)
    explanation_imgC = models.ImageField(upload_to='explanation_images/', blank=True, null=True)
    explanation_imgD = models.ImageField(upload_to='explanation_images/', blank=True, null=True)

    def __str__(self):
        return f"Images for question ID: {self.question.questions_id}"


PARTS_CATEGORY = [
    ('base', '素体'),
    ('hair', '髪'),
    ('eyes', '目'),
    ('clothes', '服'),
    ('accessory', 'アクセサリー')
]

class Style(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="スタイル名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "スタイル"
        verbose_name_plural = "スタイル"


class Parts(models.Model):
    parts_id = models.AutoField(primary_key=True, null=False)
    parts_name = models.CharField(max_length=100)
    parts_category = models.CharField(max_length=10, choices=PARTS_CATEGORY)
    parts_style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="スタイル")
    parts_default = models.BooleanField(default=False)
    parts_image = models.ImageField(upload_to='parts/')
    unlock_rank = models.IntegerField(default=1, verbose_name="アンロックランク")  # 新しいフィールドを追加
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.parts_name} ({self.parts_category}, {self.parts_style})"

    class Meta:
        verbose_name = "パーツ"
        verbose_name_plural = "パーツ"
        ordering = ['parts_category', 'parts_name']


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )
    avatar_image = models.ImageField(
        upload_to="avatars/", 
        blank=True, 
        null=True, 
        default="avatars/default.png"
    )
    selected_parts = models.ManyToManyField(Parts, blank=True)  # selected_parts を追加

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # 既存のインスタンスを取得し、古い画像を削除する準備をする
        try:
            old_instance = UserProfile.objects.get(pk=self.pk)
            if old_instance.avatar_image and old_instance.avatar_image != self.avatar_image:
                if old_instance.avatar_image.name != "avatars/default.png":  # デフォルト画像は削除しない
                    old_instance.avatar_image.delete(save=False)
        except UserProfile.DoesNotExist:
            pass  # 新しいインスタンスの場合は何もしない

        super().save(*args, **kwargs)


# プロファイルが削除された際に画像も削除する
@receiver(post_delete, sender=UserProfile)
def delete_avatar_on_profile_delete(sender, instance, **kwargs):
    if instance.avatar_image and instance.avatar_image.name != "avatars/default.png":
        instance.avatar_image.delete(save=False)