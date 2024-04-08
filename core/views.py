from django.shortcuts import redirect
import json
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
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import cv2


def home(request):

    return HttpResponse('home')


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
            poll for poll in all_polls if poll.month > formatted_date]

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
            'past_polls': past_polls,
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


def edit_poll(request, slug, slugx):
    company = User.objects.get(slug=slug)
    poll = Poll.objects.get(organizer=company, month=slugx)

    nominees = poll.nominees

    if request.method == 'POST':
        new_nominees = []
        employee_names = request.POST.getlist('employee_name')
        employee_positions = request.POST.getlist('employee_position')
        achievements = request.POST.getlist('achievement')

        for name, position, achievement in zip(employee_names, employee_positions, achievements):
            # Create a new nominee dictionary
            new_nominee = {
                'name': name,
                'position': position,
                'note': achievement
            }
            new_nominees.append(new_nominee)

        # Update existing vote counts
        for nominee, new_nominee in zip(nominees, new_nominees):
            new_nominee['vote_count'] = nominee['vote_count']

        # Update nominees in the poll
        poll.nominees = new_nominees
        poll.save()

        # Redirect to some success page or another view
        return redirect('dashboard', company.slug)

    context = {'poll': poll, 'nominees': nominees}
    return render(request, 'edit-poll.html', context)


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


def download_certificate(request, slug, slugx):
    company = User.objects.get(slug=slug)
    poll = Poll.objects.get(organizer=company, month=slugx)
    nominees = poll.nominees

    # Initialize variables to store the highest vote count and the corresponding nominee name
    highest_vote_count = 0
    highest_vote_nominee = None

    # Iterate through the list of nominees to find the one with the highest vote count
    for nominee in nominees:
        vote_count = nominee.get('vote_count', 0)
        if vote_count > highest_vote_count:
            highest_vote_count = vote_count
            highest_vote_nominee = nominee.get('name')

    # Check if a nominee with the highest vote count was found
    if highest_vote_nominee:
        # Use the nominee name with the highest vote count
        awardee_name = highest_vote_nominee
    else:
        # If no nominee was found, set a default name
        awardee_name = "No Awardee"

    certificate_path = generate_certificate(
        awardee_name, company.company_name, poll.month)

    # Open the generated certificate file
    with open(certificate_path, 'rb') as f:
        certificate_data = f.read()

    # Create an HTTP response with the certificate image data
    response = HttpResponse(certificate_data, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{awardee_name}-{poll.month}.png"'

    return response


def generate_certificate(awardee_name, company_name, month):

    template = cv2.imread('templates/certy.png')

    cv2.putText(template, awardee_name, (703, 905),
                cv2.FONT_HERSHEY_DUPLEX, 3, (142, 75, 80), 8, cv2.LINE_AA)
    cv2.putText(template, month, (830, 1130),
                cv2.FONT_HERSHEY_DUPLEX, 2, (00, 00, 00), 5, cv2.LINE_AA)
    text = company_name
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 3
    font_thickness = 8
    text_color = (142, 75, 80)
    line_type = cv2.LINE_AA

    # Get the width and height of the text
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)

    # Calculate the starting position for right alignment
    text_width = text_size[0]
    text_height = text_size[1]
    # Adjust the Y position as needed
    position = (template.shape[1] - text_width - 10, 113)

    # Render the text with right alignment
    cv2.putText(template, text, position, font, font_scale,
                text_color, font_thickness, line_type)
    cv2.putText(template, 'July 01, 2024', (890, 1290),
                cv2.FONT_HERSHEY_DUPLEX, 1.5, (00, 00, 00), 2, cv2.LINE_AA)

    certificate_path = f'core/{awardee_name}-{month}.png'
    cv2.imwrite(certificate_path, template)

    return certificate_path
