from django.shortcuts import redirect
import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Employee, CustomUser as User, Poll, Leaderboard
from django.contrib import messages
from django.contrib.auth.models import auth
import datetime
from datetime import datetime, date, timedelta
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from django.core.mail import send_mail, send_mass_mail
import io
# import cv2


def home(request):

    return render(request, 'index.html')


def buy_credit(request):

    return render(request, 'buy_credit.html')


def contact(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')

        send_mail(
            'Hey Mezard, you have got a message from email: ' + email,
            message,
            'settings.EMAIL_HOST_USER',
            ['mezardini@gmail.com'],
            fail_silently=False,
        )

    return redirect('home')


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
        print(password1)
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
            company_name=company_name, password=password1, email=email, slug=slug)
        user.is_active = True
        user.save()
        return redirect('login')


class LoginUser(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            print(password)

            if not User.objects.filter(email=email).exists():
                messages.error(request, "User does not exists.")
                return redirect('login')

            if not password:
                messages.error(request, "Password Incorrect.")
                return redirect('login')

            user = auth.authenticate(request, email=email, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('dashboard', user.slug)
            else:
                messages.error(request, "Password Incorrect.")
                return redirect('login')


class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'dashboard.html'

    def get(self, request, slug):
        company = User.objects.get(slug=slug)
        add = 'add'
        remove = 'remove'

        if request.user.slug != company.slug:

            return redirect('dashboard', request.user.slug)

        else:
            current_date = datetime.today()
            formatted_date = current_date.strftime('%B-%Y')

            today_date = datetime.today().date()

            company = User.objects.get(slug=slug)
            all_polls = Poll.objects.filter(organizer=company).order_by("-id")
            leaderboards = Leaderboard.objects.filter(organizer=company)

            active_polls = [
                poll for poll in all_polls if poll.vote_end >= today_date]

            # Filter past polls based on the current date
            past_polls = [
                poll for poll in all_polls if poll.vote_end < today_date]

            past_leaderboards = [
                leaderbd for leaderbd in leaderboards if leaderbd.month > formatted_date]

            # for p_l in past_leaderboards:

            #     pl = p_l.month.replace('-', ' ')
            #     print(pl)
            try:
                poll = Leaderboard.objects.get(
                    organizer=company, month=formatted_date)
                nominees = poll.nominees
                leaderboard = sorted(
                    nominees, key=lambda x: x['vote_count'], reverse=True)
                # past_leaderbd = Leaderboard.objects.filter(
                #     organizer=company).nominees
                # past_leaderboard = sorted(
                #     past_leaderbd, key=lambda x: x['vote_count'], reverse=True)

            except ObjectDoesNotExist:
                poll = None
                nominees = []
                leaderboard = []

            context = {
                'company': company,
                'poll': poll,
                'nominees': nominees,
                'leaderboard': leaderboard,
                'past_leaderboards': past_leaderboards,
                'past_polls': past_polls,
                'active_polls': active_polls,
                'add': add,
                'remove': remove,
                'month': formatted_date,

            }
            return render(request, self.template_name, context)


@login_required(login_url='login')
def create_poll(request, slug):

    company = User.objects.get(slug=slug)
    if request.user.slug != company.slug:

        return redirect('c-poll', request.user.slug)

    else:

        if request.method == 'POST':
            title = request.POST.get('poll_title')
            current_date = datetime.today()
            formatted_date = current_date.strftime('%B-%Y')
            vote_start_date = current_date.strftime('%Y-%m-%d')
            date_str = request.POST.get('end_date')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')

            vote_end_date = date_obj.strftime('%Y-%m-%d')

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
                title=title,
                vote_start=vote_start_date,
                vote_end=vote_end_date,
                nominees=nominees_data
            )
            poll.save()
            company.credit -= 1
            company.save()

            return redirect('c-vote', company.slug, poll.title)

        return render(request, 'create-pollx.html')


@login_required(login_url='login')
def edit_poll(request, slug, pk):
    company = User.objects.get(slug=slug)
    poll = Poll.objects.get(organizer=company,  id=pk)

    vote_end_date = poll.vote_end.strftime('%Y-%m-%d')

    nominees = poll.nominees

    if request.method == 'POST':
        new_nominees = []
        date_str = request.POST.get('end_date')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        vote_end_date = date_obj.strftime('%Y-%m-%d')
        title = request.POST.get('poll_title')

        # Extract new nominee details from the form
        employee_names = request.POST.getlist('employee_name')
        employee_positions = request.POST.getlist('employee_position')
        achievements = request.POST.getlist('achievement')

        # Ensure that each nominee has non-empty details before adding it
        for name, position, achievement in zip(employee_names, employee_positions, achievements):
            if name.strip() and position.strip() and achievement.strip():
                # Create a new nominee dictionary with default vote_count as 0
                new_nominee = {
                    'name': name,
                    'position': position,
                    'note': achievement,
                    'vote_count': 0  # Default vote_count
                }
                new_nominees.append(new_nominee)

        # Update existing vote counts if applicable
        for nominee, new_nominee in zip(nominees, new_nominees):
            # Keep the existing vote_count if present
            new_nominee['vote_count'] = nominee.get('vote_count', 0)

        # Update nominees in the poll
        poll.title = title
        poll.vote_end = vote_end_date
        poll.nominees = new_nominees
        poll.save()

        # Redirect to some success page or another view
        return redirect('dashboard', company.slug)

    context = {'poll': poll, 'nominees': nominees,
               'vote_end_date': vote_end_date}
    return render(request, 'edit-poll.html', context)


def caste_vote(request, slug, title):

    company = User.objects.get(slug=slug)

    poll = Poll.objects.get(organizer=company, title=title)

    date = datetime.today().date()

    # if poll.vote_end > date:

    nominees = poll.nominees

    leaderboard = sorted(
        nominees, key=lambda x: x['vote_count'], reverse=True)

    highest_vote_count = 0
    highest_vote_nominee = None

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

    # else:
    #     date

    #     # return render(request, 'vote-ended.html')

    context = {'company': company, 'poll': poll,
               'nominees': nominees, 'leaderboard': awardee_name, 'cn': slug, 'date': date}

    return render(request, 'caste-votex.html', context)


def count_vote(request, slug, pk, slugz):

    company = User.objects.get(slug=slug)

    poll = Poll.objects.get(organizer=company,  id=pk)

    nominee_name = slugz

    # Retrieve the nominees' data from the 'nominees' field
    nominees_data = poll.nominees

    for nominee in nominees_data:
        if nominee['name'] == nominee_name:
            nominee['vote_count'] += 1  # Increment vote count by 1

    poll.nominees = nominees_data
    poll.save()

    return redirect('voted')


def thanks_for_voting(request):

    return render(request, 'voted.html')


@login_required(login_url='login')
def download_certificate(request, slug,  pk):
    company = User.objects.get(slug=slug)
    poll = Poll.objects.get(organizer=company, id=pk)
    nominees = poll.nominees
    current_date = datetime.today()
    formatted_date = current_date.strftime('%Y-%m-%d')

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

    certificate_data = generate_certificate(
        awardee_name, company.company_name, formatted_date, poll.title)

    # Create an HTTP response with the certificate image data
    response = HttpResponse(content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{awardee_name}-{poll.title}.png"'
    response.write(certificate_data.getvalue())

    return response


@login_required(login_url='login')
def download_award(request, slug,  pk):
    company = User.objects.get(slug=slug)
    poll = Leaderboard.objects.get(organizer=company, id=pk)
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

    title = None
    company_name = None

    certificate_data = generate_badge(
        awardee_name, company.company_name, poll.month)

    # Create an HTTP response with the certificate image data
    response = HttpResponse(content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{awardee_name}-{poll.month}.png"'
    response.write(certificate_data.getvalue())

    return response


def generate_certificate(awardee_name, company_name, month, title):

    # month = month.replace("-", " ")
    # Load the background template
    template = Image.open('static/certificate.png')

    # Create a drawing object
    draw = ImageDraw.Draw(template)

    # Load a font
    # Change 'arial.ttf' to the path of your font file
    font = ImageFont.truetype(
        'static/FontsFree-Net-Poppins-Regular.ttf', size=80)

    # Define text and position
    text = "This is to certify that John Doe\nhas completed the course"
    awardee_name = awardee_name
    presentation_date = month
    cert_title = title
    company_name = company_name
    text_color = (0, 19, 189)
    # Get text size
    text_width, text_height = draw.textsize(awardee_name, font=font)

    # Calculate the position to center text horizontally
    x = (template.width - text_width) // 2
    y = 860

    # Define font thickness
    font_thickness = 2
    text_position = (100, 450)

    # Draw text on the template
    draw.text((x, y), awardee_name, fill=text_color,
              font=font, stroke_width=font_thickness)

    font_title = ImageFont.truetype(
        'static/FontsFree-Net-Poppins-Regular.ttf', size=64)

    text_width_title, text_height_title = draw.textsize(
        cert_title, font=font_title)

    # Calculate the position to center text horizontally
    x_title = (template.width - text_width_title) // 2

    draw.text((x_title, 615), cert_title, fill=(0, 0, 0),
              font=font_title, stroke_width=font_thickness)

    font_date = ImageFont.truetype(
        'static/FontsFree-Net-Poppins-Regular.ttf', size=48)

    draw.text((905, 1240), presentation_date, fill=(0, 0, 0),
              font=font_date, stroke_width=font_thickness)

    text_width_company_name, text_height_company_name = draw.textsize(
        company_name, font=font)

    # Calculate the position to center text horizontally
    x_company = (template.width - text_width_company_name)

    draw.text((x_company, 90), company_name, fill=text_color,
              font=font, stroke_width=font_thickness)

    image_stream = io.BytesIO()
    template.save(image_stream, format='PNG')
    image_stream.seek(0)

    return image_stream


def generate_badge(awardee_name, company_name, month):

    # month = month.replace("-", " ")
    # Load the background template
    template = Image.open('static/materials/Badge-Q.png')

    # Create a drawing object
    draw = ImageDraw.Draw(template)

    # Load a font
    # Change 'arial.ttf' to the path of your font file
    font = ImageFont.truetype(
        'static/materials/Acme-Regular.ttf', size=128)

    # Define text and position
    awardee_name = awardee_name
    month = month
    company_name = company_name
    text_color = (80, 75, 142)
    # Get text size
    text_width, text_height = draw.textsize(awardee_name, font=font)

    # Calculate the position to center text horizontally
    x = (template.width - text_width) // 2
    y = 520

    # Define font thickness
    font_thickness = 2
    text_position = (100, 450)

    # Draw text on the template
    draw.text((x, y), awardee_name, fill=text_color,
              font=font, stroke_width=font_thickness)

    font_month = ImageFont.truetype(
        'static/materials/Acme-Regular.ttf', size=64)

    text_width_title, text_height_title = draw.textsize(
        month, font=font_month)

    # Calculate the position to center text horizontally
    x_month = (template.width - text_width_title) // 2

    draw.text((x_month, 810), month, fill=(0, 0, 0),
              font=font_month, stroke_width=font_thickness)

    text_width_company_name, text_height_company_name = draw.textsize(
        company_name, font=font)

    # Calculate the position to center text horizontally
    x_company = (template.width - text_width_company_name) // 2

    draw.text((x_company, 1100), company_name, fill=text_color,
              font=font, stroke_width=font_thickness)

    image_stream = io.BytesIO()
    template.save(image_stream, format='PNG')
    image_stream.seek(0)

    return image_stream


@login_required(login_url='login')
def generate_random_certificate(request, slug):

    company = User.objects.get(slug=slug)
    company_name = company.company_name
    current_date = datetime.today()
    formatted_date = current_date.strftime('%Y-%m-%d')
    if request.method == 'POST':
        awardee = request.POST['awardee_name']
        title = request.POST['title']
        date = request.POST['date']

        certificate_data = generate_certificate(
            awardee, company_name, formatted_date, title)

        # Create an HTTP response with the certificate image data
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{awardee}-{title}.png"'
        response.write(certificate_data.getvalue())

        return response

    context = {'today': formatted_date}
    return render(request, 'gen-cert.html', context)


@login_required(login_url='login')
def leaderboard_rank(request, slug, month, action, nominee_name):
    company = User.objects.get(slug=slug)
    leaderboard = Leaderboard.objects.get(organizer=company, month=month)

    nominees_data = leaderboard.nominees

    if request.method == 'POST':
        new_nominees = []
        employee_name = request.POST.get('employee_name')

        # for name in employee_name:
        new_nominee = {
            'name': employee_name,
            'vote_count': 0  # Default vote_count
        }
        new_nominees.append(new_nominee)
        leaderboard.nominees = new_nominees
        leaderboard.save()
        return redirect('dashboard', slug)

    nominee_name = nominee_name
    print(nominee_name)
    for nominee in nominees_data:
        if nominee['name'] == nominee_name and action == 'add':
            # if action == 'add':
            nominee['vote_count'] += 1
            # return redirect('dashboard', slug)
        if nominee['name'] == nominee_name and action == 'remove':
            nominee['vote_count'] -= 1
            # return redirect('dashboard', slug)

        # else:
        #     return redirect('dashboard', slug)

    leaderboard.nominees = nominees_data
    leaderboard.save()
    return redirect('dashboard', slug)


@login_required(login_url='login')
def add_leaderboard(request, slug, month,):
    company = User.objects.get(slug=slug)
    # leaderboard = Leaderboard.objects.get(
    #     organizer=company, month=month)
    current_date = datetime.today()
    formatted_date = current_date.strftime('%B-%Y')

    if Leaderboard.objects.filter(organizer=company, month=month).exists():
        leaderboard = Leaderboard.objects.get(
            organizer=company, month=month)

        if request.method == 'POST':
            new_nominees = leaderboard.nominees
            employee_name = request.POST.get('employee_name')

            # for name in employee_name:
            new_nominee = {
                'name': employee_name,
                'vote_count': 0  # Default vote_count
            }
            new_nominees.append(new_nominee)
            leaderboard.nominees = new_nominees
            leaderboard.save()
            return redirect('dashboard', slug)
    else:
        month = formatted_date
        leaderboard = Leaderboard.objects.create(
            organizer=company, month=month)

        if request.method == 'POST':
            new_nominees = leaderboard.nominees
            employee_name = request.POST.get('employee_name')

            # for name in employee_name:
            new_nominee = {
                'name': employee_name,
                'vote_count': 0  # Default vote_count
            }
            new_nominees.append(new_nominee)
            leaderboard.nominees = new_nominees
            leaderboard.save()
            return redirect('dashboard', slug)


def signout(request):
    logout(request)
    return redirect('login')
