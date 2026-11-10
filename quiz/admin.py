from django.contrib import admin
from .models import Tag, Diet, Question, Answer, AnswerScore, Dish


class AnswerScoreInline(admin.TabularInline):
    model = AnswerScore
    extra = 1


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_multiple_choice')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question')
    inlines = [AnswerScoreInline]


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal')
    filter_horizontal = ('tags', 'favorited_by')


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_diets', 'kcal', 'prep_time_minutes')
    list_filter = ('prep_time_minutes',)
    search_fields = ('name', 'ingredients', 'allergens')
    filter_horizontal = ('diets', 'tags', 'favorited_by')
    
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('diets', 'name', 'image')
        }),
        ('Wartości odżywcze (Kalorie i Makro)', {
            'fields': ('kcal', 'protein', 'fat', 'carbs')
        }),
        ('Przepis i Czas', {
            'fields': ('ingredients', 'preparation_method', 'prep_time_minutes')
        }),
        ('Alergeny i Tagi', {
            'fields': ('allergens', 'tags')
        }),
    )

    def display_diets(self, obj):
        return ", ".join([diet.name for diet in obj.diets.all()])
    display_diets.short_description = 'Powiązane diety'


admin.site.register(Tag)