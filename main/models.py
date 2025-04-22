from django.db import models
import os
from django.utils.text import slugify

# Create your models here.


class Flavour(models.Model):
      flavour_name = models.CharField(max_length=100, unique=True)
      
      def __str__(self):
            return self.flavour_name

      def delete(self, *args, **kwargs):
            super().delete(*args, **kwargs)


class CakeModel(models.Model):
      name = models.CharField(max_length=100)
      short_description = models.CharField(max_length=200,  null=True, blank=True)
      description = models.TextField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      image = models.ImageField(upload_to="cakes_image")
      flavour = models.ManyToManyField(Flavour, related_name="flavour", blank=True)
      is_popular = models.BooleanField(default=False)
      is_available = models.BooleanField(default=True)
      created_at = models.DateTimeField(auto_now_add=True)
      slug = models.SlugField(max_length=100, unique=True, db_index=True)


      def __str__(self):
            return self.name

      class Meta:
        verbose_name = "Cake"  # Singular name in admin
        verbose_name_plural = "Cakes"

      def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

      def delete(self, *args, **kwargs):
        # Delete the associated image file first
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        # Then delete the database record
        super().delete(*args, **kwargs)
