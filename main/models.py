from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField()

    def __str__(self):
        return f'{self.name} - {str(self.count)}'


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, through='RecipeProduct')

    def __str__(self):
        return self.name


class RecipeProduct(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)
    count = models.IntegerField(default=0)  # Добавьте поле count

    def __str__(self):
        return 'ингридиент для - ' + self.recipe.name + ' = ' + self.product.name + ': ' + str(self.weight)
