from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegisterForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from .tokens import account_activation_token
from django.conf import settings
from .models import ProductList, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.core.paginator import Paginator

# Create your views here.
def loginUser(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username= username,password= password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    if request.method == 'POST':
        if request.POST.get('Logout')=='Logout':
            logout(request)
            return redirect('home')
        else:
            return redirect('home')
    context = {}
    return render(request, 'base/logout.html', context)

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('home')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("base/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    # Send email
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        # Success message
        messages.success(request, f'Dear <b>{user.username}</b>, please check your email <b>{to_email}</b> inbox and click on the activation link to complete registration. <b>Note:</b> Check your spam folder.')
    else:
        # Error message in case of failure
        messages.error(request, f'Problem sending email to {to_email}, please check if you typed it correctly.')
    
    return request


def signupUser(request):
    form = RegisterForm()
    if request.method =='POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            
            user.username = user.username.lower()
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))

            return redirect('home')
        else:
            messages.info(request, 'Invalid form')
    context = {'form':form}
    return render(request, 'base/login_register.html', context)
        


def home(request):
    products = ProductList.objects.all()
    p = Paginator(ProductList.objects.all(), 10)
    current_page_number = request.GET.get('page')
    page_obj = p.get_page(current_page_number) #fetches products for current_page_number so number 11-20 products


    context={'page_obj':page_obj}
    return render(request,'base/home.html', context)

# def cart(request, id):
#     prod = ProductList.objects.get(id=id)
#     context = {'prod': prod}
#     return render(request, 'base/cart.html',context ) 


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(ProductList, id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f'Added {product.name} to your cart.')
    else:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Increased quantity of {product.name} in your cart.')

    return redirect('home')  

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user) 
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'base/view_cart.html', context)

@login_required
def remove_cart(request, id):
    item = CartItem.objects.get(id=id)
    item.delete()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    address = request.user.email
    username = request.user.username

    checkout_message = f"Hello {username},\n\nHere are the details of your checkout:\n\n"
    for item in cart_items:
        checkout_message += f"{item.quantity} x {item.product.name} - ${item.product.price} each\n"
    checkout_message += f"\nTotal Price: ${total_price:.2f}\n\nThank you for shopping with us!"

    send_mail('Checkout Details', checkout_message,settings.DEFAULT_FROM_EMAIL, [address] )     
    cart_items.delete()

    return HttpResponse(
        f"<h1>Thank You, {username}!</h1>"
        f"<p>Your order has been processed successfully.</p>"
        f"<p>A confirmation email has been sent to {address}.</p>"
    )