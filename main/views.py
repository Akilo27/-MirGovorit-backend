from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from .models import Recipe, Product, RecipeProduct
from django.db import transaction
from django.db.models import F, Sum

def index(request):
    return render(request, 'index.html')


@transaction.atomic
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
    try:
        # Попытка получить запись RecipeProduct с указанными параметрами
        recipe_product = RecipeProduct.objects.get(recipe=recipe, product=product)
        recipe_product.weight = weight
        recipe_product.save()
    except:
        recipe.products.add(product)
        RecipeProduct.objects.create(product=product, recipe=recipe, weight=weight)

    return HttpResponse(f'{product.name} added to {recipe.name} ({weight}.g)')


from django.db.models import F, Sum

@transaction.atomic
@transaction.atomic
def cook_recipe(request):
    recipe_id = request.GET.get('recipe_id')
    # Проверяем, что параметр указан
    if not recipe_id:
        return JsonResponse({'error': 'recipe_id parameter is required'})

    # Находим все связи RecipeProduct для указанного recipe_id с блокировкой для обновления
    recipe_products = RecipeProduct.objects.select_for_update().filter(recipe_id=recipe_id)

    # Увеличиваем количество приготовленных блюд для каждого продукта с использованием агрегации
    recipe_products.update(count=F('count') + 1)

    # Обновляем счетчик приготовленных блюд для каждого продукта в отдельном запросе
    products = recipe_products.values('product_id').annotate(total_count=Sum('count'))
    for product in products:
        Product.objects.filter(id=product['product_id']).update(count=product['total_count'])

    return JsonResponse({'success': f'Количество приготовленных блюд для каждого продукта рецепта - {recipe_products[0].recipe.name}'})

def show_recipes_without_product(request):
    product_id = request.GET.get('product_id')
    recipe_ids = RecipeProduct.objects.filter(product_id=product_id).exclude(weight__gte=10).values('recipe_id')


    recipes = Recipe.objects.filter(id__in=recipe_ids)

    context = {
        'recipes': recipes,
    }
    return render(request, 'recipes.html', context)