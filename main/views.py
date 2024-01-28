from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from .models import Recipe, Product, RecipeProduct


def index(request):
    return render(request, 'index.html')


def add_product_to_recipe(request):
    recipe_id = request.GET.get('recipe_id')
    product_id = request.GET.get('product_id')
    weight = request.GET.get('weight')

    if not recipe_id or not product_id or not weight:
        return HttpResponseNotFound('Missing parameters')

    # Проверяем существование рецепта и продукта
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        product = Product.objects.get(id=product_id)
    except (Recipe.DoesNotExist, Product.DoesNotExist):
        return HttpResponseNotFound('Recipe or product not found')

    # Проверяем существование связи между рецептом и продуктом
    recipe_product, created = RecipeProduct.objects.get_or_create(recipe=recipe, product=product)

    # Обновляем вес продукта в связи
    recipe_product.weight = weight
    recipe_product.save()

    return HttpResponse('Product added to recipe')


def cook_recipe(request):
    recipe_id = request.GET.get('recipe_id')
    # Проверяем, что параметр указан
    if not recipe_id:
        return JsonResponse({'error': 'recipe_id parameter is required'})

    # Находим все связи RecipeProduct для указанного recipe_id
    recipe_products = RecipeProduct.objects.filter(recipe_id=recipe_id)

    # Увеличиваем количество приготовленных блюд для каждого продукта
    for recipe_product in recipe_products:
        print(recipe_product)
        recipe_product.product.count += 1
        recipe_product.product.save()

    return JsonResponse({'success': True})


def show_recipes_without_product(request):
    product_id = request.GET.get('product_id')
    recipes = RecipeProduct.objects.filter(product_id=product_id, weight__lt=10).values('recipe_id')

    # Фильтруем записи в модели RecipeProduct, исключая записи с указанным продуктом и весом >= 10 грамм.
    # Получаем только id рецептов

    # Получаем объекты модели Recipe по id рецептов
    recipes = Recipe.objects.filter(id__in=recipes)


    context = {
        'recipes': recipes,
    }
    return render(request, 'recipes.html', context)
