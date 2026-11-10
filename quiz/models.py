from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nazwa tagu")
    is_hidden = models.BooleanField(default=False, verbose_name="Ukryj w filtrach")
    
    def __str__(self):
        return self.name

class Diet(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa diety")
    description = models.TextField(verbose_name="Opis diety")
    
    goal = models.CharField(max_length=20, choices=[
        ('reduction', 'Redukcja wagi'),
        ('maintenance', 'Utrzymanie masy'),
        ('mass', 'Budowanie masy')
    ], default='any', verbose_name="Cel diety")
    pros = models.TextField(blank=True, verbose_name="Zalety diety (oddzielone nowymi liniami)")
    cons = models.TextField(blank=True, verbose_name="Wady diety (oddzielone nowymi liniami)")
    tags = models.ManyToManyField(Tag, related_name='diets', verbose_name="Tagi diety")
    favorited_by = models.ManyToManyField(User, related_name='favorite_diets', blank=True)
    def __str__(self):
        return f"{self.name} (Cel: {self.get_goal_display()})"

class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa dania")
    diets = models.ManyToManyField(Diet, related_name='dishes', verbose_name="Powiązana dieta")
    kcal = models.IntegerField(verbose_name="Kalorie (kcal)", default=0)
    protein = models.FloatField(verbose_name="Białko (g)", default=0.0)
    fat = models.FloatField(verbose_name="Tłuszcze (g)", default=0.0)
    carbs = models.FloatField(verbose_name="Węglowodany (g)", default=0.0)
    ingredients = models.TextField(verbose_name="Lista składników (każda w nowej linii)", blank=True)
    preparation_method = models.TextField(verbose_name="Sposób przyrządzenia", blank=True)
    prep_time_minutes = models.IntegerField(verbose_name="Czas przygotowania (min)", default=15)
    allergens = models.CharField(max_length=255, verbose_name="Alergeny (np. gluten, laktoza, orzechy)", blank=True)
    tags = models.ManyToManyField(Tag, related_name='dishes', blank=True, verbose_name="Tagi dania")
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name="Zdjęcie dania")
    favorited_by = models.ManyToManyField(User, related_name='favorite_dishes', blank=True)
    
    def __str__(self):
        diets_str = ", ".join([diet.name for diet in self.diets.all()])
        return f"{self.name} ({self.kcal} kcal) - Diety: [{diets_str}]"

class Question(models.Model):
    text = models.CharField(max_length=255, verbose_name="Treść pytania")
    is_multiple_choice = models.BooleanField(
        default=False,
        verbose_name="Czy wielokrotnego wyboru? (checkbox)"
    )

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Pytanie")
    text = models.CharField(max_length=255, verbose_name="Treść odpowiedzi")

    def __str__(self):
        return f"{self.question.text[:20]}... -> {self.text}"

class AnswerScore(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='scores', verbose_name="Odpowiedź")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Tag")
    points = models.IntegerField(default=1, verbose_name="Liczba punktów")

    def __str__(self):
        return f"{self.answer.text[:15]} -> {self.tag.name} (+{self.points})"

class UserQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.diet.name} ({self.score} pkt)"

class CalorieProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calorie_profile')
    
    weight = models.FloatField()
    height = models.FloatField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('mężczyzna', 'Mężczyzna'), ('kobieta', 'Kobieta')])
    pal = models.FloatField()
    bmi_value = models.FloatField()
    bmi_category = models.CharField(max_length=50)
    bmr_value = models.FloatField()
    tdee_value = models.FloatField()
    water_intake = models.FloatField()
    protein_grams = models.FloatField()
    fat_grams = models.FloatField()
    carbs_grams = models.FloatField()
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil kaloryczny: {self.user.username} (TDEE: {self.tdee_value} kcal)"