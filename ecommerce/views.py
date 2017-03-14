from django.contrib.auth import authenticate, login, logout as django_logout # Use alias like "django_logout" so that django doesnt get confused on which function to use.
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Member, Product
from .forms import RegisterForm

import math


def index(request):
	return render(request, 'ecommerce/index.html')

def products(request):
	return render(request, 'ecommerce/product/index.html')	
	
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
		
		# Check if username exists
		if User.objects.filter(username=request.POST['username']).exists() and user.username != request.POST['username']:
			err_succ['message'] = 'Username aleady taken, please enter a different one.'
		
		# Check if email exists		
		elif User.objects.filter(email=request.POST['email']).exists() and user.email != request.POST['email']:
			err_succ['message'] = 'Email already taken, please enter a different one'
			
		elif request.POST['old_password'] and request.POST['password_repeat'] and request.POST['password']:
			# Check if passwords match
			if request.POST['password_repeat'] != request.POST['password']:
				err_succ['message'] = 'New password do not match.'
			
			# Check if old password is correct
			elif not user.check_password(request.POST['old_password']):
				err_succ['message'] = 'Incorrect old password.'
				
		else:
			user.username = request.POST['username']
			user.first_name = request.POST['first_name']
			user.last_name = request.POST['last_name']
			
			user.member.phone_number = request.POST['phone_number']
			user.member.about = request.POST['about_me']
			
			# Save new password if passes above validations
			if request.POST['password']:
				user.set_password(request.POST['password'])
			
			# Save posted fields to their respective tables
			user.member.save()
			user.save()
			
			# Show success message
			err_succ['status'] = 1
			err_succ['message'] = 'Account successfully updated.'
			
		return JsonResponse(err_succ)
	else:	
		return render(request, 'ecommerce/user/account.html')

def user_products(request):
	# Redirect if not logged-in
	if request.user.is_authenticated() == False:
		return HttpResponseRedirect('/ecommerce/user/login')
	
	if request.method == 'POST':
		pagination_content = ""
		page_number = request.POST['data[page]'] if request.POST['data[page]'] else 1
		page = int(page_number)
		name = request.POST['data[th_name]']
		sort = '-' if request.POST['data[th_sort]'] == 'DESC' else ''
		search = request.POST['data[search]']
		max = int(request.POST['data[max]'])
		
		cur_page = page
		page -= 1
		per_page = max # Set the number of results to display
		start = page * per_page
		
		# If search keyword is not empty, we include a query for searching 
		# the "content" or "name" fields in the database for any matched strings.
		if search:		 
			all_posts = Product.objects.filter(Q(content__contains = search) | Q(name__contains = search), author = request.user.id).order_by(sort + name)[start:per_page]
			count = Product.objects.filter(Q(content__contains = search) | Q(name__contains = search), author = request.user.id).count()
			
		else:
			all_posts = Product.objects.filter(author = request.user.id).order_by(sort + name)[start:cur_page * max]
			count = Product.objects.filter(author = request.user.id).count()
		
		if all_posts:
			for post in all_posts:
				pagination_content += str(start) + "-" + str(per_page) +  '''
					<tr>
						<td><img src='/uploads/%s' width='100' /></td>
						<td>%s</td>
						<td>$%s</td>
						<td>%s</td>
						<td>%s</td>
						<td>%s</td>
						<td>
							<a href='#' class='text-success'>  
								<span class='glyphicon glyphicon-pencil' title='Edit'></span>
							</a> &nbsp; &nbsp;
							<a href='#' class='text-danger delete-product' item_id='%s'>
								<span class='glyphicon glyphicon-remove' title='Delete'></span>
							</a>
						</td>
					</tr>
				''' %(post.featured_image, post.name, post.price, post.status, post.date, post.quantity, post.id)
		else:
			pagination_content += str(start) + "-" + str(per_page) + "<tr><td colspan='7' class='bg-danger p-d'>No results</td></tr>"
		
		return JsonResponse({
			'content': pagination_content, 
			'navigation': nagivation_list(count, per_page, cur_page)
		})
	else:	
		return render(request, 'ecommerce/product/user.html')
	
def user_product_create(request):
	err_succ = {'status': 0, 'message': 'An unknown error occured'}
	
	# Redirect if not logged-in
	if request.user.is_authenticated() == False:
		return HttpResponseRedirect('/ecommerce/user/login')
	
	if request.method == 'POST':
		product = Product.objects.create(
			name = request.POST['name'],
			content = request.POST['content'],
			excerpt = request.POST['excerpt'],
			price = request.POST['price'],
			status = request.POST['status'],
			quantity = request.POST['quantity'],
			author = request.user.id
		)	
		product.save()
		
		err_succ['status'] = 1
		err_succ['message'] = product.id
		
		return JsonResponse(err_succ)
	else:	
		return render(request, 'ecommerce/product/create.html')
	
	
def user_product_update(request, product_id):
	product = get_object_or_404(Product, pk=product_id) # Query object of given product id
	err_succ = {'status': 0, 'message': 'An unknown error occured'}
		
	# Redirect if not logged-in
	if request.user.is_authenticated() == False:
		return HttpResponseRedirect('/ecommerce/user/login')
	
	if request.method == 'POST':
					
		return JsonResponse(err_succ)
	else:	
		return render(request, 'ecommerce/product/update.html', {'product': product}) # Include product object when rendering the view.

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
				
				member = Member.objects.create(
					user = user,
					phone_number = form.cleaned_data['phone_number'],
					about = ''
				)
				
				member.save()
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
	
def nagivation_list(count, per_page, cur_page):
	pagination_nav = ""
	previous_btn = True
	next_btn = True
	first_btn = True
	last_btn = True
		
	no_of_paginations = int(math.ceil(count / per_page))
	
	if cur_page >= 7:
		start_loop = cur_page - 3
		if no_of_paginations > cur_page + 3:
			end_loop = cur_page + 3
		elif cur_page <= no_of_paginations and cur_page > no_of_paginations - 6:
			start_loop = no_of_paginations - 6
			end_loop = no_of_paginations
		else:
			end_loop = no_of_paginations
	else:
		start_loop = 1
		if no_of_paginations > 7:
			end_loop = 7
		else:
			end_loop = no_of_paginations

	# Pagination Buttons logic     
	pagination_nav += "<div class='pagination-container'><ul>"

	if first_btn and cur_page > 1:
		pagination_nav += "<li p='1' class='active'>First</li>"
	elif first_btn:
		pagination_nav += "<li p='1' class='inactive'>First</li>"

	if previous_btn and cur_page > 1:
		pre = cur_page - 1
		pagination_nav += "<li p='" + str(pre) + "' class='active'>Previous</li>"
	elif previous_btn:
		pagination_nav += "<li class='inactive'>Previous</li>"
	
	for i in range(start_loop, end_loop + 1):
		if cur_page == i:
			pagination_nav += "<li p='" + str(i) + "' class = 'selected'>" + str(i) + "</li>"
		else:
			pagination_nav += "<li p='" + str(i) + "' class='active'>" + str(i) + "</li>"

	if next_btn and cur_page < no_of_paginations:
		nex = cur_page + 1
		pagination_nav += "<li p='" + str(nex) + "' class='active'>Next</li>"
	elif next_btn:
		pagination_nav += "<li class='inactive'>Next</li>"

	if last_btn and cur_page < no_of_paginations:
		pagination_nav += "<li p='" + str(no_of_paginations) + "' class='active'>Last</li>"
	elif last_btn:
		pagination_nav += "<li p='" + str(no_of_paginations) + "' class='inactive'>Last</li>"

	pagination_nav = pagination_nav + "</ul></div>"
	
	return pagination_nav