from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Question, Diet, Tag, AnswerScore, UserQuizResult, CalorieProfile, Dish

def home_view(request):
    return render(request, 'quiz/home.html')

def quiz_view(request):
    if request.method == 'POST':
        tag_scores = {}

        for key, value_list in request.POST.lists():
            if key.startswith('question_'):
                answer_ids = value_list
                scores = AnswerScore.objects.filter(answer_id__in=answer_ids)
                
                for score in scores:
                    tag_id = score.tag_id
                    tag_scores[tag_id] = tag_scores.get(tag_id, 0) + score.points

        diets = Diet.objects.prefetch_related('tags').all()
        diet_results = []

        for diet in diets:
            total_score = 0
            for tag in diet.tags.all():
                total_score += tag_scores.get(tag.id, 0)
            
            diet_results.append({
                'diet': diet,
                'score': total_score
            })

        diet_results.sort(key=lambda x: x['score'], reverse=True)

        best_match = diet_results[0]['diet'] if diet_results else None
        best_score = diet_results[0]['score'] if diet_results and diet_results[0]['score'] > 0 else 0

        if request.user.is_authenticated:
            UserQuizResult.objects.filter(user=request.user).delete()
            for item in diet_results:
                if item['score'] > 0:
                    UserQuizResult.objects.create(
                        user=request.user,
                        diet=item['diet'],
                        score=item['score']
                    )

        context = {
            'best_match': best_match,
            'best_score': best_score,
            'all_results': diet_results,
        }
        return render(request, 'quiz/result.html', context)

    questions = Question.objects.prefetch_related('answers').all()
    return render(request, 'quiz/quiz.html', {'questions': questions})

def diet_list_view(request):
    query = request.GET.get('q', '').strip()
    selected_tag = request.GET.get('tag', '')

    diets = Diet.objects.prefetch_related('tags').all()

    if query:
        diets = diets.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if selected_tag:
        diets = diets.filter(tags__id=selected_tag)

    tags = Tag.objects.filter(is_hidden=False)

    context = {
        'diets': diets.distinct(),
        'tags': tags,
        'query': query,
        'selected_tag': int(selected_tag) if selected_tag.isdigit() else None,
    }
    return render(request, 'quiz/diet_list.html', context)

def register_view(request):
    error = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        if not u or not p:
            error = "Wypełnij oba pola!"
        elif User.objects.filter(username=u).exists():
            error = "Użytkownik o takim loginie już istnieje!"
        else:
            user = User.objects.create_user(username=u, password=p)
            login(request, user)
            return redirect('profile')

    return render(request, 'quiz/register.html', {'error': error})

def login_view(request):
    error = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            error = "Błędny login lub hasło!"

    return render(request, 'quiz/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    top_results = request.user.quiz_results.order_by('-score')[:3]
    favorite_diets = request.user.favorite_diets.all()
    favorite_dishes = request.user.favorite_dishes.all()

    try:
        calorie_profile = request.user.calorie_profile
    except CalorieProfile.DoesNotExist:
        calorie_profile = None
    
    context = {
        'top_results': top_results,
        'favorite_diets': favorite_diets,
        'favorite_dishes': favorite_dishes,
        'calorie_profile': calorie_profile,
    }
    return render(request, 'quiz/profile.html', context)

def calculator_view(request):
    error = None
    existing_profile = None

    if request.user.is_authenticated:
        try:
            existing_profile = request.user.calorie_profile
        except CalorieProfile.DoesNotExist:
            existing_profile = None

    if request.method == 'POST':
        try:
            weight_str = request.POST.get('weight', '').replace(',', '.')
            height_str = request.POST.get('height', '').replace(',', '.')
            age_str = request.POST.get('age', '')
            gender = request.POST.get('gender', 'mężczyzna')
            pal_str = request.POST.get('pal', '1.2').replace(',', '.')

            weight = float(weight_str)
            height_cm = float(height_str)
            age = int(age_str)
            pal = float(pal_str)

            if weight <= 0 or height_cm <= 0 or age <= 0:
                raise ValueError()

            height_m = height_cm / 100.0
            bmi = round(weight / (height_m ** 2), 2)

            if bmi < 18.5:
                category = "Niedowaga"
            elif 18.5 <= bmi < 25:
                category = "Waga prawidłowa"
            elif 25 <= bmi < 30:
                category = "Nadwaga"
            else:
                category = "Otyłość"

            if gender == 'mężczyzna':
                bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161

            tdee = round(bmr * pal, 2)
            bmr = round(bmr, 2)
            protein = round(weight * 2.0, 1)
            protein_kcal = protein * 4

            fat = round(weight * 1.0, 1)
            fat_kcal = fat * 9

            remaining_kcal = tdee - (protein_kcal + fat_kcal)
            if remaining_kcal < 200:
                remaining_kcal = 200
            carbs = round(remaining_kcal / 4.0, 1)
            water = round((weight * 0.035) * (pal / 1.4), 2)

            if request.user.is_authenticated:
                CalorieProfile.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'weight': weight,
                        'height': height_cm,
                        'age': age,
                        'gender': gender,
                        'pal': pal,
                        'bmi_value': bmi,
                        'bmi_category': category,
                        'bmr_value': bmr,
                        'tdee_value': tdee,
                        'water_intake': water,
                        'protein_grams': protein,
                        'fat_grams': fat,
                        'carbs_grams': carbs
                    }
                )
                return redirect('profile')
            else:
                error = "Musisz być zalogowany, aby zapisać profil w systemie!"

        except (ValueError, TypeError):
            error = "Wprowadź poprawne wartości numeryczne we wszystkich polach!"

    context = {
        'error': error,
        'existing_profile': existing_profile,
    }
    return render(request, 'quiz/kalkulator.html', context)

def diet_detail_view(request, pk):
    diet = get_object_or_404(Diet, pk=pk)
    dishes = diet.dishes.all()
    pros_list = [p.strip() for p in diet.pros.split('\n') if p.strip()] if hasattr(diet, 'pros') and diet.pros else []
    cons_list = [c.strip() for c in diet.cons.split('\n') if c.strip()] if hasattr(diet, 'cons') and diet.cons else []
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user in diet.favorited_by.all()
        for dish in dishes:
            dish.is_favorite = request.user in dish.favorited_by.all()

    context = {
        'diet': diet,
        'dishes': dishes,
        'pros_list': pros_list,
        'cons_list': cons_list,
        'is_favorite': is_favorite,
    }
    return render(request, 'quiz/diet_detail.html', context)

def dish_list_view(request):
    query = request.GET.get('q', '').strip()
    selected_tag = request.GET.get('tag', '')
    selected_diet = request.GET.get('diet', '')

    dishes = Dish.objects.prefetch_related('tags', 'diets').all()

    if query:
        dishes = dishes.filter(
            Q(name__icontains=query) | Q(ingredients__icontains=query) | Q(allergens__icontains=query)
        )

    if selected_tag:
        dishes = dishes.filter(tags__id=selected_tag)
        
    if selected_diet:
        dishes = dishes.filter(diets__id=selected_diet)

    tags = Tag.objects.filter(is_hidden=False)
    diets = Diet.objects.all()

    context = {
        'dishes': dishes.distinct(),
        'tags': tags,
        'diets': diets,
        'query': query,
        'selected_tag': int(selected_tag) if selected_tag.isdigit() else None,
        'selected_diet': int(selected_diet) if selected_diet.isdigit() else None,
    }
    return render(request, 'quiz/dish_list.html', context)

def dish_detail_view(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user in dish.favorited_by.all()

    context = {
        'dish': dish,
        'is_favorite': is_favorite,
    }
    return render(request, 'quiz/dish_detail.html', context)

@login_required
def toggle_diet_favorite(request, pk):
    diet = get_object_or_404(Diet, pk=pk)
    if diet.favorited_by.filter(pk=request.user.pk).exists():
        diet.favorited_by.remove(request.user)
    else:
        diet.favorited_by.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def toggle_dish_favorite(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if dish.favorited_by.filter(pk=request.user.pk).exists():
        dish.favorited_by.remove(request.user)
    else:
        dish.favorited_by.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'profile'))