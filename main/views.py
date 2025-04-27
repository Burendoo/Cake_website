from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import CakeModel, Flavour
from django.core.paginator import Paginator, EmptyPage

# Create your views here.


class HomeView(View):
      def get(self, request):
          flavours = Flavour.objects.all()
          cakes = CakeModel.objects.all()
          latest_cakes = cakes.order_by('-created_at')
          popular_cakes = cakes.filter(is_popular=True).order_by('-created_at')[:3]
          context = {
              'cakes':cakes,
              'latest_cakes':latest_cakes,
              'popular_cakes': popular_cakes,
              'flavours':flavours
          }



          return render(request, 'main/home.html', context)
      

def flavours(request, flavour_slug):
    flavour = Flavour.objects.get(slug=flavour_slug)
    cakes = CakeModel.objects.filter(flavour=flavour)

    context = {
        "flavour":flavour,
        "cakes":cakes
    }

    return render(request, "main/flavour.html", context)



def search(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        page_number = request.GET.get('page', 1)  # Default to page 1
        
        if query:
            cakes = CakeModel.objects.filter(name__icontains=query)
            paginator = Paginator(cakes, 9)  # Show 6 cakes per page
            
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results
                page_obj = paginator.page(paginator.num_pages)
            
            context = {
                "cakes": page_obj,
                "query": query
            }
            return render(request, 'main/search.html', context)
    
    # Default return if no query
    return render(request, 'main/search.html', {})
    
    
class SingleCakeView(DetailView):
    template_name = "main/view_cake.html"
    model = CakeModel
    slug_field = 'slug'      
    slug_url_kwarg = 'cake_slug'  
    context_object_name = 'cake'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context