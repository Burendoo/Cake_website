from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import CakeModel1, Flavour1, Payment
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe
from django.http import JsonResponse
import json

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
    query = CakeModel1.objects.filter(flavour=flavour)
    page_number = request.GET.get('page', 1)

    if query:
        cakes = query
        paginator = Paginator(cakes, 9)

        try:
            page_obj = paginator.page(page_number)

        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)


        context = {
            "flavour":flavour,
            "cakes":page_obj,
            "query":query,
            "page_number":page_number
        }

        return render(request, "main/flavour.html", context)
    
    return render(request, 'main/flavour.html', {})



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
    page_number = request.GET.get('page', 1) 

    if query:
        cakes = query
        paginator = Paginator(cakes, 12)

        try:
            page_obj = paginator.page(page_number)

        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {
                "cakes": page_obj,
                "query": query,
                "page_num":page_number

            }
        return render(request, 'main/all_cakes.html', context)
    
    # Default return if no query
    return render(request, 'main/all_cakes.html', {})
    


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


# views for payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request, cake_id):
    cake = get_object_or_404(CakeModel1, id=cake_id)
    return render(request, 'main/checkout.html', {'cake': cake})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

@csrf_exempt  # Temporarily add this for testing, then implement proper CSRF
def create_checkout_session(request, cake_id):
    cake = get_object_or_404(CakeModel1, id=cake_id)
    
    try:
        # Build absolute URLs
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        success_url = f"{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&cake_id={cake.id}"
        cancel_url = f"{base_url}/payment-failed"
        

        try:
            unit_amount = int(float(cake.price) * 100)
            if unit_amount <= 0:
                return JsonResponse({'error': 'Price must be positive'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid price format'}, status=400)
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': cake.name,
                    },
                    'unit_amount': int(float(cake.price) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url
        )
        return JsonResponse({'checkout_url': session.url})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_success(request):
    session_id = request.GET.get('session_id')
    cake_id = request.GET.get('cake_id')
    
    
    if not session_id or not cake_id:
        return JsonResponse({"error": "Invalid session or cake ID"}, status=400)
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        cake = get_object_or_404(CakeModel1, id=cake_id)
        
        customer_email = session.customer_email or session.customer_details.get('email')
        customer_name = session.customer_details.name

        if session.payment_status == 'paid':
            Payment.objects.create(
                cake=cake,
                customer_name= session.customer_details.name,
                customer_email=customer_email,
                amount= session.amount_total / 100,  # Convert cents to dollars
                payment_intent_id=session.payment_intent,
                status='paid',
            )

            return render(request, 'main/payment_success.html', {'customer_name': customer_name})
        
        return JsonResponse({"error": "Payment not successful"}, status=400)
    
    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def payment_failed(request):
    error_message = request.GET.get('error_message', 'Payment failed. Please try again.')
    return render(request, 'main/payment_failed.html', {'error_message': error_message})



endpoint_secret = ''

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({"error":"Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error":"Invalid signature"}, status=400)

    print("Received event: ", json.loads(payload))
        # Fulfill the purchase...

    return JsonResponse({'status': 'success'}, status=200)














    