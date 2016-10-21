from django.shortcuts import render, redirect
from models import User, Book, Review
import bcrypt

# Implemenet a 404 route
# What is the best CSS to set height of "Other Books" in review.html
# userManager = UserManager() = means you cannot use User.objects...

def index(request):
	if ('errors' in request.session) and len(request.session['errors']):
		context = {'errors':request.session['errors']}
		request.session['errors'] = []
		return render(request, 'review/index.html', context)
	return render(request, 'review/index.html')

def register(request):
	if request.method == 'POST':
		request.session['errors'] = []
		if not User.userManager.namev(request.POST['name']):
			request.session['errors'].append('Name is NOT Valid.')
		if not User.userManager.namev(request.POST['alias']):
			request.session['errors'].append('Alias is NOT Valid.')
		if not User.userManager.email(request.POST['email']):
			request.session['errors'].append('Email address is NOT Valid.')
		if not User.userManager.password(request.POST['password']):
			request.session['errors'].append(
									'Password must be at least eight characters.')
		if not User.userManager.confirm(
								request.POST['password'], request.POST['confirm']):
			request.session['errors'].append(
								'Password and Confirm Password must be the same.')

		if len(request.session['errors']) == 0:
			passw = request.POST['password'].encode('utf-8')
			bpassw = bcrypt.hashpw(passw, bcrypt.gensalt())
			u =	User.userManager.create(name=request.POST['name'],
								alias=request.POST['alias'], email=request.POST['email'],
								password=bpassw)
			##############
			request.session['user'] = u.id
			return redirect('/review')
	return redirect('/')

def login(request):
	if request.method == 'POST':
		request.session['errors'] = []
		if not User.userManager.email(request.POST['email']):
			request.session['errors'].append('Email address is NOT Valid.')
		else:
			u = User.userManager.filter(email=request.POST['email'])
			if len(u):
				passw = request.POST['password'].encode('utf-8')
				if bcrypt.checkpw(passw, u[0].password.encode('utf-8')):
					request.session['user'] = u[0].id
					return redirect('/review')
				else:
					request.session['errors'].append('Incorrect password entered.')
			else:
				request.session['errors'].append('Email address not found')
	return redirect('/')

def review(request):
	## Does this reduce the database request size?
	# Is this the standard way for less than all rows?
	revs = Review.objects.all().order_by('-created')[:3]
	rev = []
	for r in revs:
		# Data types in models. Everything a string in POST, but not models
		rating = int(r.rating)
		fav1 = range(0, rating)
		fav2 = range(rating, 5)
		rev.append((r, fav1, fav2))
	titles = []
	for r in revs:
		titles.append(r.book.title)
	books = Book.objects.exclude(title__in=titles)
	u = User.userManager.get(id=request.session['user'])
	context = {'alias':u.alias, 'recents':rev, 'books':books}
	return render(request, 'review/review.html', context)

def add(request):
	books = Book.objects.all()
	authors = []
	for b in books:
		if b.author not in authors:
			authors.append(b.author)
	context = {'authors':authors}
	return render(request, 'review/add.html', context)

def add1(request):
	if request.method == 'POST':
		if 'bookid' in request.POST:
			b = Book.objects.get(id=int(request.POST['bookid']))
		else:
			if ('author' in request.POST) and request.POST['author']:
				author = request.POST['author']
			else:
				author = request.POST['author1']
			title = request.POST['title']
			# Does this filter work?
			b = Book.objects.filter(title__iexact=title, author__iexact=author)
			if len(b):
				b = b[0]
			else:
				b = Book.objects.create(title=title, author=author)

		u = User.userManager.get(id=request.session['user'])
		r = Review.objects.create(review=request.POST['review'],
							rating=int(request.POST['rating']),
							user=u, book=b)
		# Redirect to URL with parameter
		return redirect('/book/' + str(b.id))
	return redirect('/add')

def logout(request):
	# Does not protect other routes after this.
	request.session.pop('user', None)
	return redirect('/')

def book(request, bid):
	b = Book.objects.get(id=bid)
	revs = Review.objects.filter(book__id=bid)
	rev = []
	for r in revs:
		rating = int(r.rating)
		fav1 = range(0, rating)
		fav2 = range(rating, 5)
		rev.append((r, fav1, fav2))
	context = {'book':b, 'reviews':rev}
	return render(request, 'review/book.html', context)

def user(request, uid):
	u = User.userManager.get(id=uid)
	revs = Review.objects.filter(user__id=uid)
	context = {'user':u, 'reviews':revs}
	return render(request, 'review/user.html', context)

def delete(request, rid):
	r = Review.objects.get(id=rid)
	revs = Review.objects.filter(book=r.book)
	if len(revs) == 1:
		b = Book.objects.get(id=r.book.id)
		r.delete()
		b.delete()
		return redirect('/review')
	r.delete()
	return redirect('/book/' + str(r.book.id))