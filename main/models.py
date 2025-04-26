from django.db import models
import os
from django.utils.text import slugify

# Create your models here.


class Flavour(models.Model):
      flavour_name = models.CharField(max_length=100, unique=True)
      slug = models.SlugField(max_length=100, unique=True, db_index=True)
      
      def __str__(self):
            return self.flavour_name
      
      def save(self, *args, **kwargs):
        self.slug = slugify(self.flavour_name)
        super().save(*args, **kwargs)

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
      slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True)



      def __str__(self):
            return self.name

      class Meta:
        verbose_name = "Cake"  # Singular name in admin
        verbose_name_plural = "Cakes"

      

      def save(self, *args, **kwargs):
        if not self.slug or self._name_changed():
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

      def _name_changed(self):
          """Check if name was modified (for existing instances)."""
          if self.pk:
              old = CakeModel.objects.get(pk=self.pk)
              return old.name != self.name
          return True  # New instance

      def _generate_unique_slug(self):
          """Create a unique slug by appending numbers if needed."""
          slug = slugify(self.name)
          unique_slug = slug
          counter = 1
          while CakeModel.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
              unique_slug = f"{slug}-{counter}"
              counter += 1
          return unique_slug
      

      def delete(self, *args, **kwargs):
        # Delete the associated image file first
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        # Then delete the database record
        super().delete(*args, **kwargs)
