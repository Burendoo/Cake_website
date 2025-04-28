from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import CakeModel1, Flavour1
from django.core.paginator import Paginator, EmptyPage

# Create your views here.


class HomeView(View):
      def get(self, request):
          flavours = Flavour1.objects.all()
          cakes = CakeModel1.objects.all()
          latest_cakes = cakes.order_by('-created_at')
          popular_cakes = cakes.filter(is_popular=True).order_by('-created_at')[:3]
          context = {
              'cakes':cakes,
              'latest_cakes':latest_cakes,
              'popular_cakes': popular_cakes,
              'flavours':flavours
          }



          return render(request, 'main/home.html', context)
      
def about(request):
    return render(request, 'main/about.html')

def flavours(request, flavour_slug):
    flavour = Flavour1.objects.get(slug=flavour_slug)
    cakes = CakeModel1.objects.filter(flavour=flavour)

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
            cakes = CakeModel1.objects.filter(name__icontains=query)
            paginator = Paginator(cakes, 9)  # Show 9 cakes per page
            
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results
                page_obj = paginator.page(paginator.num_pages)
            
            context = {
                "cakes": page_obj,
                "query": query,
                "page_num":page_number

            }
            return render(request, 'main/search.html', context)
    
    # Default return if no query
    return render(request, 'main/search.html', {})
    

def all_cakes(request):
    query = CakeModel1.objects.all()
    


class SingleCakeView(DetailView):
    template_name = "main/view_cake.html"
    model = CakeModel1
    slug_field = 'slug'      
    slug_url_kwarg = 'cake_slug'  
    context_object_name = 'cake'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    


def contact(request):
    return render(request, 'main/contact.html')


