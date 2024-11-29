from django.db import models

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
    ('hair', '髪'),
    ('base', '素体'),
    ('eyes', '目'),
    ('clothes', '服'),
    ('accessory', 'アクセサリー'),
    ('background', '背景')
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.parts_name} ({self.parts_category}, {self.parts_style})"

    class Meta:
        verbose_name = "パーツ"
        verbose_name_plural = "パーツ"
        ordering = ['parts_category', 'parts_name']
