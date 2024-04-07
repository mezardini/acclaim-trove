from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import Nominee, Vote, CustomUser as User, Poll
from django.contrib import messages
from django.contrib.auth.models import auth
import datetime
from datetime import datetime, date, timedelta
from django.template.defaultfilters import slugify
import imgkit


def home(request):

    return HttpResponse('Welcome to Acclaimtrove')
    # imgkit.from_file('templates/cert.html', 'out2.jpg')
    # return render(request, 'cert.html')


class RegisterUser(View):
    template_name = 'register.html'

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
            return redirect('register')

        if not password1:
            messages.error(request, "Password cannot be blank.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # If validation passes, create the user
        user = User.objects.create_user(
            company_name=company_name, password=password1, email=email)
        user.is_active = False
        user.save()
        return HttpResponse('Successfully Signed Up To Acclaimtrove')


class LoginUser(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            if not User.objects.filter(email=email).exists():
                messages.error(request, "User does not exists.")
                return redirect('login')

            if not password:
                messages.error(request, "Password Incorrect.")
                return redirect('login')

            user = auth.authenticate(request, email=email, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Password Incorrect.")
                return redirect('login')


class Dashboard(View):
    template_name = 'dashboard.html'

    def get(self, request, slug):
        current_date = datetime.today()
        formatted_date = current_date.strftime('%B-%Y')

        company = User.objects.get(slug=slug)
        all_polls = Poll.objects.filter(organizer=company).order_by("-id")

        # Filter past polls based on the current date
        past_polls = [
            poll for poll in all_polls if poll.month < formatted_date]

        try:
            poll = Poll.objects.get(organizer=company, month=formatted_date)
            nominees = poll.nominees
            leaderboard = sorted(
                nominees, key=lambda x: x['vote_count'], reverse=True)
            # past_nominees = all_polls.nominees
            # past_leaderboard = sorted(
            #     past_nominees, key=lambda x: x['vote_count'], reverse=True)

        except ObjectDoesNotExist:
            poll = None
            nominees = []
            leaderboard = []

        context = {
            'company': company,
            'poll': poll,
            'nominees': nominees,
            'leaderboard': leaderboard,
            'past_polls': all_polls,
        }
        return render(request, self.template_name, context)


def create_poll(request, slug):

    company = User.objects.get(slug=slug)

    if request.method == 'POST':
        current_date = datetime.today()
        formatted_date = current_date.strftime('%B-%Y')
        vote_start_date = current_date.strftime('%Y-%m-%d')
        vote_end_date = current_date.replace(
            day=1, month=current_date.month+1) - timedelta(days=1)
        end_date = vote_end_date.strftime("%Y-%m-%d")

        nominee_names = request.POST.getlist('employee_name')
        nominee_positions = request.POST.getlist('employee_position')
        nominee_notes = request.POST.getlist('achievement')

        nominees_data = []

        # Process the data as needed
        for nominee_name, nominee_position, nominee_note in zip(nominee_names, nominee_positions, nominee_notes):
            nominee_data = {
                'name': nominee_name,
                'position': nominee_position,
                'note': nominee_note,
                'vote_count': 0  # Default vote count is set to 0
            }
            nominees_data.append(nominee_data)

        poll = Poll.objects.create(
            organizer=company,
            month=formatted_date,
            vote_start=vote_start_date,
            vote_end=end_date,
            nominees=nominees_data
        )
        poll.save()

        return redirect('c-vote', company.slug, poll.month)

    return render(request, 'create-pollx.html')


def caste_vote(request, slug, slugx):

    company = User.objects.get(slug=slug)

    poll = Poll.objects.get(organizer=company, month=slugx)

    nominees = poll.nominees

    leaderboardx = Vote.objects.filter(poll=poll)

    queryset = leaderboardx

    leaderboard = queryset.order_by('-vote_count')

    context = {'company': company, 'poll': poll,
               'nominees': nominees, 'leaderboard': leaderboard, 'cn': slug, 'dt': slugx}

    return render(request, 'caste-votex.html', context)


def count_vote(request, slug, slugx, slugz):

    company = User.objects.get(slug=slug)

    poll = Poll.objects.get(organizer=company, month=slugx)

    nominee_name = slugz

    # Retrieve the nominees' data from the 'nominees' field
    nominees_data = poll.nominees

    # Find the nominee you want to update and update their vote count
    for nominee in nominees_data:
        if nominee['name'] == nominee_name:
            nominee['vote_count'] += 1  # Increment vote count by 1

    poll.nominees = nominees_data
    poll.save()

    # nominee = Nominee.objects.get(id=slugz)

    # vote = Vote.objects.get(poll=poll, choice=nominee)
    # # nominee = nominees.get(nominee_name=slugz)
    # vote.vote_count += 1
    # vote.save()

    # # context = {'company': company,
    # #            'nominees': nominees, 'cn': slug, 'dt': slugx}

    return render(request, 'voted.html')
