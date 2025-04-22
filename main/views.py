from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import CakeModel, Flavour

# Create your views here.


class HomeView(View):
      def get(self, request):
        
          popular_cakes = CakeModel.objects.filter(is_popular=True).order_by('-created_at')[:4]
          context = {
              'popular_cakes': popular_cakes,
          }



          return render(request, 'main/home.html', context)



def search(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            cakes = CakeModel.objects.filter(name__icontains=query)

        context = {
            "cakes": cakes
        }

    return render(request, 'main/search.html', context)
    
    