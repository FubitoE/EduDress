from django.db import models


# 難易度の選択肢
DIFFICULTY = (
    ('IP', 'Iパス'), 
    ('SG', 'セキュマネ'), 
    ('FE', '基本'), 
    ('AP', '応用')
)


# 問題モデル
class Question(models.Model):
    questions_id = models.AutoField(primary_key=True)
    questions_number = models.IntegerField(default=0)
    questions_text = models.TextField()
    choice_a = models.TextField()
    choice_b = models.TextField()
    choice_c = models.TextField()
    choice_d = models.TextField()
    correct_answer = models.CharField(max_length=10, choices=[('a', 'ア'), ('b', 'イ'), ('c', 'ウ'), ('d', 'エ')], blank=True, default='a')
    exam_year = models.CharField(max_length=20)
    explanation = models.TextField()
    difficulty = models.CharField(max_length=100, choices=DIFFICULTY)

    def __str__(self):
        return self.questions_text[:50]  # 最初の50文字を返す
    
# 問題画像モデル
class Questionimg(models.Model):
    question = models.ForeignKey(Question, related_name='images', on_delete=models.CASCADE)  # 外部キーを追加
    question_imgA = models.ImageField(upload_to='question_images/', blank=True, null=True)
    question_imgB = models.ImageField(upload_to='question_images/', blank=True, null=True)  # 画像がない場合に備えて
    explanation_imgA = models.ImageField(upload_to='explanation_images/', blank=True, null=True)
    explanation_imgB = models.ImageField(upload_to='explanation_images/', blank=True, null=True)  # 画像がない場合に備えて

    def __str__(self):
        return f"Images for question ID: {self.question.questions_id}"

# 体のパーツモデル

PARTS_CATEGORY = [
    ('hair', '髪'),
    ('eyes', '目'),
    ('clothes','服'),
    ('accessory', 'アクセサリー'),
    ('background', '背景')
]

class Style(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="スタイル名")  # スタイル名のフィールド

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "スタイル"
        verbose_name_plural = "スタイル"

class Parts(models.Model):
    parts_id = models.AutoField(primary_key=True, null=False)
    parts_name = models.CharField(max_length=100)
    parts_category = models.CharField(max_length=10, choices=PARTS_CATEGORY)
    parts_style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="スタイル")  # スタイルへの外部キー
    parts_default = models.BooleanField(default=False)
    parts_image = models.ImageField(upload_to='parts/')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.parts_name} ({self.parts_category}, {self.parts_style})"

    class Meta:
        verbose_name = "パーツ"
        verbose_name_plural = "パーツ"
        ordering = ['parts_category', 'parts_name']