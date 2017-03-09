from django.contrib.auth import authenticate, login, logout as django_logout # Use alias like "django_logout" so that django doesnt get confused on which function to use.
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # So you can use @login_required on top of method to protect the view.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .forms import RegisterForm


def index(request):
    return render(request, 'ecommerce/index.html')

def products(request):
    return render(request, 'ecommerce/products.html')    
    
def about(request):
    return render(request, 'ecommerce/about.html')
    
def contact(request):
    return render(request, 'ecommerce/contact.html')

def user_login(request):
    # Redirect if already logged-in
    if request.user.is_authenticated():
        return HttpResponseRedirect('/ecommerce/user/account')
    
    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Success, now let's login the user. 
            login(request, user)
            # Then redirect to the accounts page.
            return HttpResponseRedirect('/ecommerce/user/account')
        else:
            # Incorrect credentials, let's throw an error to the screen.
            return render(request, 'ecommerce/user/login.html', {'error_message': 'Incorrect username and / or password.'})
    else:
        # No post data availabe, let's just show the page to the user.
        return render(request, 'ecommerce/user/login.html')
 
def user_account(request):
    err_succ = {'status': 0, 'message': 'An unknown error occured'}
    
    # Redirect if not logged-in
    if request.user.is_authenticated() == False:
        return HttpResponseRedirect('/ecommerce/user/login') 
    
    if request.method == 'POST':
        # Query data of currently logged-in user.
        user = User.objects.get(username=request.user.username)
        
        # Save posted fields.
        user.username = request.POST['username']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        
        # user.old_password = request.POST['old_password']
        # user.password = request.POST['password']
        # user.password_confirm = request.POST['password_confirm']
        
        user.member.phone_number = request.POST['phone_number']
        user.member.about = request.POST['about_me']
        
        user.member.save()
        user.save()
            
        return JsonResponse(err_succ)
    else:    
        return render(request, 'ecommerce/user/account.html')

def user_products(request):
    # Redirect if not logged-in
    if request.user.is_authenticated() == False:
        return HttpResponseRedirect('/ecommerce/user/login')
        
    return render(request, 'ecommerce/user/products.html')

def user_register(request):
    # Redirect if already logged-in
    if request.user.is_authenticated():
        return HttpResponseRedirect('/ecommerce/user/account')
    
    # if this is a POST request we need to process the form data
    template = 'ecommerce/user/register.html'
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, template, {
                    'form': form, 
                    'error_message': 'Username already exists.'
                })
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, template, {
                    'form': form, 
                    'error_message': 'Email already exists.'
                })
            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                return render(request, template, {
                    'form': form, 
                    'error_message': 'Passwords do not match.'
                })
            else:
                # Create the user: 
                user = User.objects.create_user(
                    form.cleaned_data['username'], 
                    form.cleaned_data['email'], 
                    form.cleaned_data['password']
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.phone_number = form.cleaned_data['phone_number']
                user.save()
                
                # Login the user
                login(request, user)
                
                # redirect to accounts page:
                return HttpResponseRedirect('/ecommerce/user/account')

   # No post data availabe, let's just show the page.
    else:
        form = RegisterForm()

    return render(request, template, {'form': form})
    
def logout(request):
    # Clear the session cookies to logout the user. 
    django_logout(request)
    # Redirect after logout
    return HttpResponseRedirect('/ecommerce/user/login')