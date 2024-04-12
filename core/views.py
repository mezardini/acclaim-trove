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
from django.http import HttpResponse
from PIL import Image
import io
import cv2


def home(request):
    # image_path = 'templates/page.png'

    # # Open the image file in binary mode
    # with open(image_path, 'rb') as f:
    #     image_data = f.read()

    # # Create an HTTP response with the image content
    # response = HttpResponse(image_data, content_type='image/png')

    # # Optionally, set additional HTTP headers if needed
    # # For example, to cache the image for a certain duration
    # response['Cache-Control'] = 'max-age=3600'  # Cache for 1 hour

    # return response
    return render(request, 'home.html')


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

        today_date = datetime.today().date()

        company = User.objects.get(slug=slug)
        all_polls = Poll.objects.filter(organizer=company).order_by("-id")

        active_polls = [
            poll for poll in all_polls if poll.vote_end >= today_date]

        # Filter past polls based on the current date
        past_polls = [
            poll for poll in all_polls if poll.month > formatted_date]

        # try:
        #     poll = Poll.objects.get(organizer=company, month=formatted_date)
        #     nominees = poll.nominees
        #     leaderboard = sorted(
        #         nominees, key=lambda x: x['vote_count'], reverse=True)
        #     # past_nominees = all_polls.nominees
        #     # past_leaderboard = sorted(
        #     #     past_nominees, key=lambda x: x['vote_count'], reverse=True)

        # except ObjectDoesNotExist:
        #     poll = None
        #     nominees = []
        #     leaderboard = []

        context = {
            'company': company,
            # 'poll': poll,
            # 'nominees': nominees,
            # 'leaderboard': leaderboard,
            'past_polls': past_polls,
            'active_polls': active_polls
        }
        return render(request, self.template_name, context)


def create_poll(request, slug):

    company = User.objects.get(slug=slug)

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

        return redirect('c-vote', company.slug, poll.month, poll.id)

    return render(request, 'create-pollx.html')


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


def download_certificate(request, slug,  pk):
    company = User.objects.get(slug=slug)
    poll = Poll.objects.get(organizer=company, id=pk)
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

    certificate_data = generate_certificate(
        awardee_name, company.company_name, poll.month, poll.title)

    # Create an HTTP response with the certificate image data
    response = HttpResponse(content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{awardee_name}-{poll.title}.png"'
    response.write(certificate_data.getvalue())

    return response


def generate_certificate(awardee_name, company_name, month, title):

    month = month.replace("-", " ")

    template = cv2.imread('templates/certy.png')

    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 3
    font_thickness = 8
    text_color = (142, 75, 80)
    line_type = cv2.LINE_AA

    # Get the size of the text
    text_size, _ = cv2.getTextSize(
        awardee_name, font, font_scale, font_thickness)
    text_width, text_height = text_size

    # Calculate the starting position to center the text horizontally
    x = (template.shape[1] - text_width) // 2
    y = 905  # Adjust the y-coordinate as needed

    # Render the text at the calculated position
    cv2.putText(template, awardee_name, (x, y), font, font_scale,
                text_color, font_thickness, line_type)
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

    # Define font sizes and colors
    month_font_scale = 2
    title_font_scale = 1.5
    font_thicknessx = 5
    text_color = (0, 0, 0)  # Black color

    # Get the size of the month text
    month_text_size, _ = cv2.getTextSize(
        month, font, month_font_scale, font_thicknessx)
    month_text_width, _ = month_text_size

    # Calculate the starting position to center the month text horizontally
    month_x = (template.shape[1] - month_text_width) // 2
    month_y = 1130  # Adjust the y-coordinate as needed

    # Get the size of the title text
    title_text_size, _ = cv2.getTextSize(
        title, font, title_font_scale, font_thicknessx)
    title_text_width, _ = title_text_size

    # Calculate the starting position to center the title text horizontally
    title_x = (template.shape[1] - title_text_width) // 2
    title_y = 647  # Adjust the y-coordinate as needed

    # Render the month text at the calculated position
    cv2.putText(template, month, (month_x, month_y), font,
                month_font_scale, text_color, font_thickness, line_type)

    # Render the title text at the calculated position
    cv2.putText(template, title, (title_x, title_y), font,
                1.5, text_color, 2, line_type)

    _, buffer = cv2.imencode('.png', template)

    return io.BytesIO(buffer)
