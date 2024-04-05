from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import Nominee, Vote, CustomUser as User
from django.contrib import messages
from django.contrib.auth.models import auth
import datetime
from django.template.defaultfilters import slugify


def home(request):

    return HttpResponse('Welcome to Acclaimtrove')


class RegisterUser(View):
    template_name = 'signup.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        company_name = request.POST['company_name']
        slug = slugify(request.POST['company_name'])
        # global token
        # token = str(random.randint(100001, 999999))

        # Validation checks
        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists.")
            # return redirect('creator')

        if not password1:
            messages.error(request, "Password cannot be blank.")
            # return redirect('creator')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            # return redirect('creator')

        # If validation passes, create the user
        user = User.objects.create_user(
            company_name=company_name, password=password1, email=email)
        user.is_active = False
        user.save()
        return HttpResponse('Successfully Signed Up To Acclaimtrove')


class LoginUser(View):
    template_name = 'signin.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            if not email:
                messages.error(request, "Email cannot be blank.")

                return redirect('login')

            if not password:
                messages.error(request, "Password cannot be blank.")
                return redirect('login')

            user = auth.authenticate(request, email=email, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Incorrect email or password.")
                # return redirect('signin')


class Dashboard(View):

    template_name = 'dashboard.html'

    def get(self, request):
        return render(request, self.template_name)


def create_poll(request):

    nominee_list = []

    if request.method == 'POST':
        nominee_names = request.POST.getlist('employee_name')  # List of values
        nominee_notes = request.POST.getlist('achievement')  # List of values
        month = datetime.date(2024, 4, 19)  # List of values

        # Process the data as needed
        for nominee_name, nominee_note in zip(nominee_names, nominee_notes):
            Nominee.objects.create(
                nominee_name=nominee_name, nominee_note=nominee_note, month=month)

    return render(request, 'create-poll.html')


def caste_vote(request, slug, slugx):

    company = User.objects.get(slug=slug)

    nominees = Nominee.objects.filter(company=company).filter(month=slugx)

    context = {'company': company,
               'nominees': nominees, 'cn': slug, 'dt': slugx}

    return render(request, 'caste-vote.html', context)


def count_vote(request, slug, slugx, pk):

    company = User.objects.get(slug=slug)

    nominees = Nominee.objects.filter(company=company, month=slugx)
    nominee = nominees.get(id=pk)
    nominee.vote_count += 1
    nominee.save()

    # context = {'company': company,
    #            'nominees': nominees, 'cn': slug, 'dt': slugx}

    return HttpResponse('Thanks for voting, see you next month!')
