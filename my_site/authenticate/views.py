from datetime import datetime
from typing import get_args
from django.db.models.fields import GenericIPAddressField
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages 
from .forms import SignUpForm, EditProfileForm 
from django.db import connections
from django.utils.timezone import now
from .models import Logins
import logging
from django.core.cache import cache
# Create your views here.

cursor = connections['default'].cursor()

def home(request): 
	return render(request, 'authenticate/home.html', {})


def login_user (request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request,("You're logged in"))
			return redirect('home') 
		else:
			messages.success(request,('Error logging in'))
			return redirect('login') 
	else:
		return render(request, 'authenticate/login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request,("You're now logged out"))
	return redirect('home')


def register_user(request):
	if request.method =='POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			email = form.cleaned_data['email']
			user = authenticate(username=username, password=password, email=email)
			login(request,user)
			messages.success(request, ("You're now registered"))
			return redirect('home')
	else: 
		form = SignUpForm() 

	context = {'form': form}
	return render(request, 'authenticate/register.html', context)


def edit_profile(request):
	if request.method =='POST':
		form = EditProfileForm(request.POST, instance= request.user)
		if form.is_valid():
			form.save()
			messages.success(request, ('You have edited your profile'))
			return redirect('home')
	else: 		
		form = EditProfileForm(instance= request.user) 

	context = {'form': form}
	return render(request, 'authenticate/edit_profile.html', context)


def change_password(request):
	if request.method =='POST':
		form = PasswordChangeForm(data=request.POST, user= request.user)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			messages.success(request, ('You have edited your password'))
			return redirect('home')
	else: 		
		form = PasswordChangeForm(user= request.user) 

	context = {'form': form}
	return render(request, 'authenticate/change_password.html', context)

def getIP(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

	if x_forwarded_for:
		IpAddress = x_forwarded_for.split(',')[-1].strip()
	else:
		IpAddress = request.META.get('REMOTE_ADDR')
	get_ip = Logins()
	get_ip.ip_address = IpAddress
	get_ip.pub_date = datetime.date.today()
	get_ip.save()

class SetLastVisit(object):
	def process_response(self, request, response):
		if request.Logins.is_authenticated():
			Logins.objects.filter(pk=request.Logins.pk).update(last_vist=now())
		return response


logger = logging.getLogger(__name__)

class InvalidLoginAttemptsCache(object):
	@staticmethod
	def _key(email):
		return 'invalid_login_attempt_{}'.format(email)

	@staticmethod
	def _value(lockout_timestamp, timebucket):
		return {
			'lockout_start': lockout_timestamp,
			'invalid_attempt_timestamps': timebucket
		}
	
	@staticmethod
	def delete(email):
		try:
			cache.delete(InvalidLoginAttemptsCache._key(email))
		except Exception as e:
			logger.exception(e.message)

	@staticmethod
	def set(email, timebucket, lockout_timestamp=None):
		try:
			key = InvalidLoginAttemptsCache._key(email)
			value = InvalidLoginAttemptsCache._value(lockout_timestamp, timebucket)
			cache.set(key, value)
		except Exception as e: 
			logger.exception(e.message)

	@staticmethod
	def get(email):
		try:
			key = InvalidLoginAttemptsCache._key(email)
			return cache.get(key)
		except Exception as e:
			logger.exception(e.message)
