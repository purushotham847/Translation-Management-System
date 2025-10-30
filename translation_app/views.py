import csv
import io
import json
import logging
from datetime import datetime, timedelta
from django.utils.timezone import now
import pytz
from dateutil import parser
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db import models, transaction, connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.utils import timezone
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone
import pytz
from django.http import JsonResponse
from django.db import connection
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.db.models import Avg
from django.conf import settings

import os


from .models import (
    JobTable,
    FileImport,
    TranslatorTable,
    TLogTable,
    CorpusTable,
    ReviewerTable,
    RegistrationTable as Registration,
    MajorTable,
    AdminTable,
    RLogTable,
    ALogTable
)

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def logindashboard(request):
    return render(request, 'logindashboard.html')



def user_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

       
        language_proficiencies = request.POST.getlist('language_profeciency[]')  
        experiences = request.POST.getlist('experience[]') 

        
        language_experience_pairs = []
        for lang, exp in zip(language_proficiencies, experiences):
            language_experience_pairs.append({
                'language': lang,
                'experience': exp
            })

       
        language_experience_json = json.dumps(language_experience_pairs)

        
        if Registration.objects.filter(email=email).exists():
            messages.error(request, "This username or email is already registered.")
            return render(request, 'userregistration.html')  

     
        org_details_file = request.FILES.get('biodata')
       
        if org_details_file:
            org_details_binary = org_details_file.read()  
        else:
            org_details_binary = None 
       
        custom_id = generate_admin_id(user_type,name)
        user = Registration(
            id=custom_id,
            user_name=name,
            email=email,
            password=make_password(password),  
            user_type=user_type,
            language_profeciency=language_experience_json, 
            org_details=org_details_binary,
            flag='N'
        )
        user.save()

        userdetails = get_object_or_404(Registration, id=custom_id)

        messages.success(request, "Registration successful! ")
        return render(request, 'registration_success.html', {'user': userdetails})
         

  
    language_options = CorpusTable.objects.values_list('language_profeciency', flat=True)

    return render(request, 'userregistration.html', {'language_options': language_options})





def generate_admin_id(model_type, name):
    model_mapping = {
        'admin': (AdminTable, 'a_id', 'A'),
        'translator': (TranslatorTable, 't_id', 'T'),
        'reviewer': (ReviewerTable, 'r_id', 'R')
    }

    if model_type not in model_mapping:
        raise ValueError("Invalid model type provided.")

    model_class, id_field, initial = model_mapping[model_type]

    first_name = name.split()[0]
    today = datetime.now()
    date_str = today.strftime('%d%m%Y')
    prefix = f"{first_name}{date_str}{initial}"

 
    count = model_class.objects.filter(**{f"{id_field}__startswith": prefix}).count()

    serial_number = count + 1

    return f"{prefix}{serial_number:02d}"



def download_pdf(request, user_id):
    user = get_object_or_404(Registration, id=user_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{user.user_name}_registration.pdf"'

    p = canvas.Canvas(response, pagesize=letter)

    p.setFont("Helvetica-Bold", 24)
    p.drawString(1 * inch, 10 * inch, "Registration Confirmation")

    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(0.5 * inch, 9.5 * inch, 7.5 * inch, 9.5 * inch)

    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 8.5 * inch, f"User   ID: {user.id}")
    p.drawString(1 * inch, 8 * inch, f"Name: {user.user_name}")
    p.drawString(1 * inch, 7.5 * inch, f"Email: {user.email}")
    p.drawString(1 * inch, 7 * inch, f"User   Type: {user.user_type}")

    p.drawString(1 * inch, 6.5 * inch, "Thank you for registering with us!")
    p.drawString(1 * inch, 6 * inch, "We are excited to have you on board.")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(1 * inch, 1 * inch, "Best regards,")
    p.drawString(1 * inch, 0.8 * inch, "Translation App Team")

    p.showPage()
    p.save()
    
    return response



def registrations_view(request):
    registrations = Registration.objects.filter(flag='N')
    approved_translators = TranslatorTable.objects.all().order_by('-creation_date')
    approved_reviewers = ReviewerTable.objects.all().order_by('-creation_date')

    translators = registrations.filter(user_type='translator')
    reviewers = registrations.filter(user_type='reviewer')

    formatted_translators = []
    formatted_reviewers = []
    formatted_approved_translators = []
    formatted_approved_reviewers = []

    def parse_language_proficiencies(proficiency_data):
       
        try:
            language_proficiencies = json.loads(proficiency_data)
            return [
                f"{prof.get('language', 'Unknown')} : {prof.get('experience', 'N/A')}"
                for prof in language_proficiencies
            ]
        except (json.JSONDecodeError, TypeError) as e:
           
            print(f"Error decoding JSON: {e}")
            return ["Invalid data"]

    for translator in translators:
        formatted_translators.append({
            'translator': translator,
            'formatted_proficiencies': parse_language_proficiencies(translator.language_profeciency)
        })


    for reviewer in reviewers:
        formatted_reviewers.append({
            'reviewer': reviewer,
            'formatted_proficiencies': parse_language_proficiencies(reviewer.language_profeciency)
        })


    for translator in approved_translators:
        formatted_approved_translators.append({
            'translator': translator,
            'formatted_proficiencies': parse_language_proficiencies(translator.language_profeciency)
        })


    for reviewer in approved_reviewers:
        formatted_approved_reviewers.append({
            'reviewer': reviewer,
            'formatted_proficiencies': parse_language_proficiencies(reviewer.language_profeciency)
        })

    context = {
        'translators': formatted_translators,
        'reviewers': formatted_reviewers,
        'approved_translators': formatted_approved_translators,
        'approved_reviewers': formatted_approved_reviewers,
    }

    return render(request, 'registrations.html', context)





def download_biodata(request, email):
    user = get_object_or_404(Registration, email=email)
    pdf_data = user.org_details  
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="biodata.pdf"'
        return response
    else:
        return HttpResponse("No PDF found for this user.", status=404)



def approve_user(request, email):
    if request.method == "POST":
        registration = get_object_or_404(Registration, email=email)

        if registration.flag.upper() == 'Y':
            return JsonResponse({"error": "User is already approved."}, status=400)

        language_profeciency_str = registration.language_profeciency

        try:
            language_profeciencies = json.loads(language_profeciency_str)
            languages = [entry['language'] for entry in language_profeciencies]
        except json.JSONDecodeError:
            languages = []

        corpus_entries = CorpusTable.objects.filter(language_profeciency__in=languages)

        if not corpus_entries.exists():
            return JsonResponse({"error": "No corpus found for the given language proficiencies."}, status=404)

        corpus_ids = ",".join(str(corpus.corpus_id) for corpus in corpus_entries)

        with transaction.atomic():
            if registration.user_type == 'translator':
                translator, created = TranslatorTable.objects.get_or_create(
                    email=registration.email,  # Use email to ensure uniqueness
                    defaults={
                        't_id': registration.id,
                        't_name': registration.user_name,
                        'password': registration.password,
                        'language_profeciency': registration.language_profeciency,
                        'corpus_id': corpus_ids,
                        'job_assigned': 'N',
                        'major_job_id': None,
                        'minor_job_id': None,
                        'deadline': None,
                        'rating': None,
                        'batch_range': None,
                        't_review': None,
                    }
                )
                if not created:
                    existing_corpus_ids = translator.corpus_id.split(",") if translator.corpus_id else []
                    combined_corpus_ids = list(set(existing_corpus_ids + corpus_ids.split(",")))
                    translator.corpus_id = ",".join(combined_corpus_ids)
                    translator.save()

                user_id = translator.t_id
                user_type = 'translator'

            elif registration.user_type == 'reviewer':
                # Handle multiple existing records
                reviewers = ReviewerTable.objects.filter(email=registration.email)
                if reviewers.exists():
                    reviewer = reviewers.first()  # Pick the first reviewer if duplicates exist
                    created = False
                else:
                    reviewer = ReviewerTable.objects.create(
                        r_id=registration.id,
                        r_name=registration.user_name,
                        password=registration.password,
                        email=registration.email,
                        language_profeciency=registration.language_profeciency,
                        job_assigned='N',
                        major_job_id=None,
                        minor_job_id=None,
                        creation_date=None,
                        deadline=None,
                        rating=None,
                        batch_range=None,
                        corpus_id=None,
                    )
                    created = True

                user_id = reviewer.r_id
                user_type = 'reviewer'

            registration.flag = 'Y'
            registration.save()

            # Update the ALogTable for the logged-in admin
            admin_name = request.session.get('admin_name')
            if admin_name:
                ist_now_str = request.session.get('ist_now')

                # Check for an existing log entry for the admin
                existing_log = ALogTable.objects.filter(admin_name=admin_name, logout__isnull=True).last()
                if existing_log and not existing_log.user_id and not existing_log.user_type:
                    # Update the existing log entry
                    existing_log.user_id = user_id
                    existing_log.user_type = user_type
                    existing_log.save()
                else:
                    # Create a new log entry
                    ALogTable.objects.create(
                        admin_name=admin_name,
                        login=ist_now_str,
                        user_id=user_id,
                        user_type=user_type
                    )

        registration.delete()

        return JsonResponse({"message": "User approved successfully with multiple corpus entries."}, status=200)

    return JsonResponse({"error": "Invalid request."}, status=400)


def send_approval_email(request, email, user_type, name, user_id):
    subject = f"Approval Notification - {user_type.capitalize()}"
    message = f"Dear {name},\n\nYou have been successfully approved as a {user_type} and are ready to login with your userId {user_id}.\n\nBest regards,\nTranslation App Team"
    send_mail(
        subject,
        message,
        'purushothamgowda847@gmail.com', # Replace this gmail with your gmail from where the email message will be sent , same gmail id should be used in the setting.py file for EMAIL_HOST_USER
        [email],
        fail_silently=False,
    )
    return HttpResponse("Approval email sent successfully.")

def admin_registration(request):
    if request.method == 'POST':
        admin_name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        
        if not admin_name or not email or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'adminregistration.html')

        if AdminTable.objects.filter(a_name=admin_name).exists():
            messages.error(request, "Admin name already exists.")
            return render(request, 'adminregistration.html')

        try:
           
            custom_id =  custom_id = generate_admin_id("admin",admin_name)
            encrypted_password = make_password(password)
            admin = AdminTable(a_id=custom_id, a_name=admin_name, a_password=encrypted_password, a_email=email)
            admin.save()

            messages.success(request, 'Admin registration successful! Redirecting to login...')
            return render(request, 'adminregistration.html')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}. Please try again.')
            return render(request, 'adminregistration.html')

    return render(request, 'adminregistration.html')




def admin_login(request):
    if request.method == 'POST':
        admin_name = request.POST.get('admin_name')
        password = request.POST.get('password')

        try:
            admin = AdminTable.objects.get(a_name=admin_name)
            if check_password(password, admin.a_password):
                # Log the successful login
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_time = timezone.now().astimezone(ist_timezone)
                ist_now_naive = ist_time.replace(tzinfo=None)
                print(ist_now_naive)
                log_entry = ALogTable(
                    admin_name=admin_name,  # Assuming a_id is the admin_name
                    login=ist_now_naive,  # Store the current timestamp
                )
                request.session['ist_now'] = ist_now_naive.isoformat()
                log_entry.save()
                request.session['admin_name'] = admin_name

                return redirect('admindashboard')
            else:
                return render(request, 'adminlogin.html', {'error_message': 'Invalid admin name or password'})
        except AdminTable.DoesNotExist:
            return render(request, 'adminlogin.html', {'error_message': 'Admin does not exist'})

    return render(request, 'adminLogin.html')


def admindashboard(request):
    major_ids = MajorTable.objects.all()

    total_jobs = JobTable.objects.count()
    allotted_jobs = JobTable.objects.filter(t_flag='Y').count()
    pending_jobs = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'), r_flag='N').count()
    completed_jobs = JobTable.objects.filter(t_flag='Y', r_flag='Y').count()

    translator_total_jobs = JobTable.objects.filter(t_flag='Y').count()
    translator_allotted_jobs = JobTable.objects.filter(t_flag='Y', r_flag='N').count()
    translator_pending_jobs = JobTable.objects.filter(t_flag='N').count()
    translator_completed_jobs = JobTable.objects.filter(t_flag='Y').count()

    reviewer_total_jobs = JobTable.objects.filter(r_flag='Y').count()
    reviewer_allotted_jobs = JobTable.objects.filter(r_flag='Y', t_flag='N').count()
    reviewer_pending_jobs = JobTable.objects.filter(r_flag='N', t_flag='Y').count()
    reviewer_completed_jobs = JobTable.objects.filter(r_flag='Y').count()

    context = {
        'total_jobs': total_jobs,
        'allotted_jobs': allotted_jobs,
        'pending_jobs': pending_jobs,
        'completed_jobs': completed_jobs,
        'translator_total_jobs': translator_total_jobs,
        'translator_allotted_jobs': translator_allotted_jobs,
        'translator_pending_jobs': translator_pending_jobs,
        'translator_completed_jobs': translator_completed_jobs,
        'reviewer_total_jobs': reviewer_total_jobs,
        'reviewer_allotted_jobs': reviewer_allotted_jobs,
        'reviewer_pending_jobs': reviewer_pending_jobs,
        'reviewer_completed_jobs': reviewer_completed_jobs,
        'major_ids': major_ids,
    }

    return render(request, 'admindashboard.html', context)






def translator_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            translator = TranslatorTable.objects.get(t_id=username)
            if check_password(password, translator.password):
                request.session['t_id'] = translator.t_id

                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_now = timezone.now().astimezone(ist_timezone)

                request.session['ist_now'] = ist_now.isoformat()

                return redirect(reverse('translatordashboard'))

            else:
                return render(request, 'translatorLogin.html', {'error': 'Invalid credentials'})

        except TranslatorTable.DoesNotExist:
            return render(request, 'translatorLogin.html', {'error': ' Translator does not exist'})
        except Exception as e:

            return render(request, 'translatorLogin.html', {'error': 'An error occurred. Please try again.'})

    return render(request, 'translatorLogin.html')








def translatordashboard(request):
    ist = pytz.timezone('Asia/Kolkata')
    t_id = request.session.get('t_id')
    if not t_id:
        return redirect('translator_login')

    ist_now_str = request.session.get('ist_now')
    if ist_now_str:
        try:
            ist_now = parser.isoparse(ist_now_str)
            if ist_now.tzinfo is None:
                ist_now = ist.localize(ist_now)
            else:
                ist_now = ist_now.astimezone(ist)
            ist_now_naive = ist_now.replace(tzinfo=None)
        except (ValueError, TypeError):
            ist_now_naive = None
    else:
        ist_now_naive = None

    try:
        translator = TranslatorTable.objects.get(t_id=t_id)
    except TranslatorTable.DoesNotExist:
        return redirect('translator_login')

    allocated_jobs = []
    completed_batches = set(translator.completed_batches.split(',')) if translator.completed_batches else set()

    if translator.job_assigned == 'Y' and translator.batch_range:
        batch_ids = [batch_id.strip() for batch_id in translator.batch_range.split(',')]
        for batch_id in batch_ids:
            jobs = JobTable.objects.filter(batch_id=batch_id).values('sen_id', 'source_data', 't_flag')
            if jobs.exists():
                is_completed = jobs.first()['t_flag'] == 'Y'
                status = 'Completed' if is_completed else 'Pending'
                allocated_jobs.append({
                    'batch_id': batch_id,
                    'status': status,
                    't_flag': jobs.first()['t_flag'],
                    'jobs': list(jobs)
                })
                if status == 'Completed':
                    completed_batches.add(batch_id)
            else:
                allocated_jobs.append({
                    'batch_id': batch_id,
                    'status': 'Job not found',
                    't_flag': None
                })

    # Update the completed_batches column in TranslatorTable
    translator.completed_batches = ','.join(sorted(completed_batches))  # Store as sorted, comma-separated string
    translator.save()

    corpus = CorpusTable.objects.filter(corpus_id=translator.corpus_id).first()
    language_proficiency = corpus.language_profeciency if corpus else 'N/A'

    if request.method == 'POST':
        data = json.loads(request.body)
        print("last")

        if 'batch_id' in data:
            batch_id = data['batch_id']
            module_access_timestamp = now().astimezone(ist).replace(tzinfo=None)
            log_entry = TLogTable(
                t_id=t_id,
                batch_range=translator.batch_range,
                creation_date=translator.creation_date,
                deadline=translator.deadline,
                login=ist_now_naive,
                module_access_timestamp=module_access_timestamp,
                batch_id=batch_id
            )
            log_entry.save()
            return JsonResponse({'status': 'success'})

        elif data.get('action') == 'logout':
            logout_time = now().astimezone(ist).replace(tzinfo=None)
            log_entry = TLogTable.objects.filter(t_id=t_id, logout=None).last()
            if log_entry:
                log_entry.logout = logout_time
                if log_entry.login:
                    login_time = log_entry.login
                    logout_time_only = logout_time
                    log_duration = logout_time_only - login_time
                    current_date = datetime.now().date()
                    log_entry.log_duration = datetime.combine(current_date, datetime.min.time()) + log_duration
                log_entry.save()

            request.session.flush()
            return JsonResponse({'status': 'success', 'redirect_url': reverse('translator_login')})

        elif data.get('action') == 'update_translator':
            try:
                translator.major_job_id = None
                translator.minor_job_id = None
                translator.creation_date = None
                translator.deadline = None
                translator.batch_range = None
                translator.t_review = None


                translator.save()
                return JsonResponse({'status': 'success'})
            except TranslatorTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Translator not found.'})


        elif data.get('action') == 'quit_job':
          
            corpus_id = data.get('corpus_id')

            batch_ids = data.get('batch_ids')

            translator_id = data.get('translator_id')

            quit_reason = data.get('quit_reason')  # Get the quit reason from the request

            JobTable.objects.filter(corpus_id=corpus_id, batch_id__in=batch_ids).update(

                t_target_data=None,

                r_target_data=None,

                minor_job_id=None,

                t_flag="N",

                t_assigned="N",

                t_rating=0,

                t_reviews=None

            )

            TranslatorTable.objects.filter(t_id=translator_id).update(

                job_assigned='N',

                batch_range=None,

                major_job_id=None,

                minor_job_id=None,

                creation_date=None,

                deadline=None,

                t_review=None,

                corpus_id=None,

                completed_batches=None,

                quit_flag='Y',  # Set quit_flag to 'Y'

                quit_reason=quit_reason,  # Store the quit reason

            )

            return JsonResponse({'status': 'success'})

    context = {

            'translator': translator,

            'allocated_jobs': allocated_jobs,

            'language_proficiency': language_proficiency,

            'deadline': translator.deadline,

        }
    
    return render(request, 'td.html', context)


def t_user_view(request, batch_id):
    print(f"Received batch_id: {batch_id}")
    jobs = JobTable.objects.filter(batch_id=batch_id)

    if not jobs.exists():
        jobs = None

    t_id = request.session.get('t_id')

    if not t_id:
        return redirect('translator_login')

    try:
        translator = TranslatorTable.objects.get(t_id=t_id)
        corpus = CorpusTable.objects.filter(corpus_id=translator.corpus_id).first()
        language_proficiency = corpus.language_profeciency if corpus else 'N/A'
    except TranslatorTable.DoesNotExist:
        return redirect('translator_login')

    if request.method == 'POST':
        data = json.loads(request.body)
        target_texts = data.get('target_texts', [])
        sen_ids = data.get('sen_ids', [])
        review = data.get('review', '')

        for sen_id, text in zip(sen_ids, target_texts):
            job = jobs.filter(sen_id=sen_id).first()
            if job:
                job.t_target_data = text
                job.t_flag = 'Y'
                job.t_reviews = review
                translator.t_review = review
                job.save()
                translator.save()

        # Get current timestamp in IST
        ist = now().astimezone(pytz.timezone('Asia/Kolkata'))
        module_submission_timestamp = ist.strftime('%Y-%m-%d %H:%M:%S')

        # Retrieve all entries with the specified batch_id and order by ID to get the latest
        tlog_entries = TLogTable.objects.filter(batch_id=batch_id).order_by('-slno')
        print(tlog_entries)

        if tlog_entries.exists():
            # Get the latest entry
            latest_entry = tlog_entries.first()  # Most recent entry based on the order
            latest_entry.module_submission_timestamp = module_submission_timestamp
            latest_entry.save()
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No TLog entries found for this batch.'
            })

        return JsonResponse({'status': 'success', 'message': 'Data submitted successfully!'})

    context = {
        'batch_id': batch_id,
        'jobs': jobs,
        'language_proficiency': language_proficiency,
        'keyboard_id': corpus.keyboard_id,
        'keyboard_name': corpus.keyboard_name,
        'language_id': corpus.language_id,
        'language_name': corpus.language_name,
        'keyboard_filename': corpus.keyboard_filename,
        

    }

    return render(request, 'translatordashboard.html', context)



def reviewer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(password,username)

        try:
            reviewer = ReviewerTable.objects.get(r_id=username)

            if check_password(password, reviewer.password):
                request.session['r_id'] = reviewer.r_id

                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_now = timezone.now().astimezone(ist_timezone)

                request.session['ist_now'] = ist_now.isoformat()

                return redirect(reverse('reviewerdashboard'))

            else:
                return render(request, 'reviewerLogin.html', {'error': 'Invalid credentials'})

        except TranslatorTable.DoesNotExist:
            return render(request, 'reviewerLogin.html', {'error': ' Translator does not exist'})
        except Exception as e:
            return render(request, 'reviewerLogin.html', {'error': 'An error occurred. Please try again.'})

    return render(request, 'reviewerLogin.html')


def reviewerdashboard(request):
    ist = pytz.timezone('Asia/Kolkata')
    r_name = request.session.get('r_id')

    if not r_name:
        return redirect('reviewer_login')

    ist_now_str = request.session.get('ist_now_r')
    print(f"Received ist_now_str: {ist_now_str}")

    if ist_now_str:
        try:
            ist_now = parser.isoparse(ist_now_str)

            if ist_now.tzinfo is None:
                ist_now = ist.localize(ist_now)
            else:
                ist_now = ist_now.astimezone(ist)

            ist_now_naive = ist_now.replace(tzinfo=None)
            print(f"Parsed IST Now (Naive): {ist_now_naive}")
        except (ValueError, TypeError) as e:
            print(f"Error parsing ist_now: {e}")
            ist_now_naive = None
    else:
        ist_now_naive = None

    try:

        reviewer = ReviewerTable.objects.get(r_id=r_name)
    except ReviewerTable.DoesNotExist:
        return redirect('reviewer_login')

    allocated_jobs = []
    completed_batches = set(reviewer.completed_batches.split(',')) if reviewer.completed_batches else set()

    if reviewer.job_assigned == 'Y':

        batch_ids = [batch_id.strip() for batch_id in
                     reviewer.batch_range.split(',')] if reviewer.batch_range else []

        for batch_id in batch_ids:

            jobs = JobTable.objects.filter(batch_id=batch_id).values('sen_id', 'source_data', 'r_flag',
                                                                     't_rating')

            if jobs.exists():

                is_completed = jobs.first()['r_flag'] == 'Y'
                status = 'Completed' if is_completed else 'Pending'
                allocated_jobs.append({
                    'batch_id': batch_id,
                    'status': status,
                    'r_flag': jobs.first()['r_flag'],
                    't_rating': jobs.first()['t_rating'],
                    'jobs': list(jobs)
                })
                if status == 'Completed':
                    completed_batches.add(batch_id)
            else:

                allocated_jobs.append({
                    'batch_id': batch_id,
                    'status': 'Job not found',
                    'r_flag': None,
                    't_rating': None
                })
    else:
        batch_ids = []

    reviewer.completed_batches = ','.join(sorted(completed_batches))  # Store as sorted, comma-separated string
    reviewer.save()
    corpus = CorpusTable.objects.filter(corpus_id=reviewer.corpus_id).first()
    language_proficiency = corpus.language_profeciency if corpus else 'N/A'

    if request.method == 'POST':
        data = json.loads(request.body)

        if 'batch_id' in data:
            batch_id = data['batch_id']
            module_access_timestamp = now().astimezone(ist).replace(tzinfo=None)  # Convert to naive datetime
            log_entry = RLogTable(
                r_id=r_name,
                batch_range=reviewer.batch_range,
                creation_date=reviewer.creation_date,
                deadline=reviewer.deadline,
                login=ist_now_naive,
                module_access_timestamp=module_access_timestamp,
                batch_id=batch_id

            )
            log_entry.save()
            return JsonResponse({'status': 'success'})

        elif data.get('action') == 'logout':
            logout_time = now().astimezone(ist).replace(tzinfo=None)
            log_entry = RLogTable.objects.filter(r_id=r_name, logout=None).last()
            if log_entry:
                log_entry.logout = logout_time
                if log_entry.login:
                    login_time = log_entry.login  # Assuming login is a datetime object
                    logout_time_only = logout_time  # This is also a datetime object

                    # Calculate duration
                    log_duration = logout_time_only - login_time

                    # Use the current date as the base date
                    current_date = datetime.now().date()  # Get the current date

                    # Combine the current date with the duration
                    log_entry.log_duration = datetime.combine(current_date, datetime.min.time()) + log_duration

                    # Debugging output
                    print(
                        f"Login Time: {login_time}, Logout Time: {logout_time_only}, Log Duration: {log_entry.log_duration}")

                log_entry.save()

            # Clear session and redirect to login
            request.session.flush()
            return JsonResponse({'status': 'success', 'redirect_url': reverse('reviewer_login')})

        elif data.get('action') == 'update_reviewer':
            try:

                reviewer.major_job_id = None
                reviewer.minor_job_id = None
                reviewer.creation_date = None
                reviewer.deadline = None
                reviewer.batch_range = None
                reviewer.corpus_id = None
                reviewer.job_assigned = 'N'

                
                reviewer.save()

                return JsonResponse({'status': 'success'})
            except ReviewerTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Reviewer not found.'})

        elif data.get('action') == 'quit_job':
            corpus_id = data.get('corpus_id')
            batch_ids = data.get('batch_ids')
            reviewer_id = data.get('reviewer_id')

            JobTable.objects.filter(corpus_id=corpus_id, batch_id__in=batch_ids).update(
                r_target_data=None,
                minor_job_id=None,
                r_flag="N",
                r_assigned="N",
                r_rating=0,
                r_reviews=None
            )

            ReviewerTable.objects.filter(r_id=reviewer_id).update(
                job_assigned='N',
                batch_range=None,
                major_job_id=None,
                minor_job_id=None,
                creation_date=None,
                deadline=None,
                r_review=None,
                corpus_id=None,
                # completed_batches=None
            )
            print(reviewer_id)
            return JsonResponse({'status': 'success'})

    # Prepare context for rendering the template
    context = {
        'reviewer': reviewer,
        'allocated_jobs': allocated_jobs,  # Pass the job statuses and jobs to the template
        'language_proficiency': language_proficiency,
        'deadline': reviewer.deadline,
        'batch_range': reviewer.batch_range  # Include language proficiency in context
    }

    return render(request, 'Rd.html', context)


def r_user_view(request, batch_id):
    try:
        batch_id = int(batch_id)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid batch_id.'})

    
    jobs = JobTable.objects.filter(batch_id=batch_id)

    if not jobs.exists():
        jobs = None

    r_name = request.session.get('r_id')

    if not r_name:
        
        return redirect('reviewer_login')

    try:
        reviewer = ReviewerTable.objects.get(r_id=r_name)
        corpus = CorpusTable.objects.filter(corpus_id=reviewer.corpus_id).first()
        language_proficiency = corpus.language_profeciency if corpus else 'N/A'
        
    except ReviewerTable.DoesNotExist:
        return redirect('reviewer_login')

    if request.method == 'POST':
        data = json.loads(request.body)
        target_texts = data.get('target_texts', [])
        sen_ids = data.get('sen_ids', [])
        ratings = data.get('ratings', [])
        review = data.get('review', '')

        if not target_texts or not sen_ids or not ratings:
            return JsonResponse({'status': 'error', 'message': 'Missing data.'}, status=400)

        total_rating = 0
        for sen_id, text, rating in zip(sen_ids, target_texts, ratings):
            job = jobs.filter(sen_id=sen_id).first()
            if job:
                job.r_target_data = text
                job.r_flag = 'Y'
                job.r_reviews = review
                job.save()
                reviewer.save()
                total_rating += int(rating)

        average_rating = total_rating / len(ratings) if ratings else 0

        for sen_id in sen_ids:
            job = jobs.filter(sen_id=sen_id).first()
            if job:
                job.t_rating = average_rating
                job.save()


        file_numbers = reviewer.file_assigned 
       # Get the file number from the reviewer
        if file_numbers:
            file_numbers = [file_number for file_number in file_numbers.split(',') if file_number.strip().isdigit()]
           
            for file_number in file_numbers:
                # Check if all jobs for this file_number have r_flag = 'Y'
                
                all_jobs_completed = JobTable.objects.filter(file_number=file_number, r_flag='Y').count() == JobTable.objects.filter(file_number=file_number).count()
                
                if all_jobs_completed:
                    # Update the status in the FileImport table
                    file_import_entry = FileImport.objects.filter(id=file_number).first()
                    
                    if file_import_entry:
                        file_import_entry.status = 'Y'
                        file_import_entry.save()

                    average_rating = JobTable.objects.filter(file_number=file_number).aggregate(Avg('t_rating'))['t_rating__avg']
                    
                    translators_to_update = TranslatorTable.objects.filter(file_assigned__contains=str(file_number))
                    


                    for translator in translators_to_update:
                       translator.rating = average_rating
                       translator.save()

                    # Remove the file number from the ReviewerTable
                    reviewer.file_assigned = ', '.join([fn for fn in file_numbers if fn != file_number])
                      # Remove the completed file number
                    reviewer.save()
                           
        try:
            # Get the current IST timestamp
            ist = timezone.now().astimezone(pytz.timezone('Asia/Kolkata'))
            module_submission_timestamp = ist.strftime('%Y-%m-%d %H:%M:%S')

            # Retrieve all entries with the specified batch_id and order by ID to get the latest
            rlog_entries = RLogTable.objects.filter(batch_id=batch_id).order_by('-slno')
            
            if rlog_entries.exists():
                # Get the latest entry
                latest_entry = rlog_entries.first()  # This will give you the most recent entry based on the order
                latest_entry.module_submission_timestamp = module_submission_timestamp
                latest_entry.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'No TLog entries found for this batch.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'success', 'message': 'Data submitted successfully!'})

    context = {
        'batch_id': batch_id,
        'jobs': jobs,
        'language_proficiency': language_proficiency,
        'keyboard_id': corpus.keyboard_id,
        'keyboard_name': corpus.keyboard_name,
        'language_id': corpus.language_id,
        'language_name': corpus.language_name,
        'keyboard_filename': corpus.keyboard_filename,}

    return render(request, 'reviewerdashboard.html', context)

#-------------------------------------------------------------------------------------------------------------------------------------------




def translations_view(request):
    # Fetch all translators
    translators = TranslatorTable.objects.all()
    translatortable = TranslatorTable.objects.filter(job_assigned='Y')
    major_ids = MajorTable.objects.values('major_id', 'language')  # Fetch major IDs and languages

    translator_data = []
    pending_jobs_data = []

    # Check if a major_id is provided to fetch language proficiencies
    if 'major_id' in request.GET:
        major_id = request.GET.get('major_id')
        # Get unique corpus_ids for the selected major_id
        corpus_ids_jobtable = JobTable.objects.filter(major_job_id=major_id).values_list('corpus_id', flat=True).distinct()
        # Fetch language proficiencies based on these corpus_ids
        corpus_data = CorpusTable.objects.filter(corpus_id__in=corpus_ids_jobtable).values('corpus_id', 'language_profeciency')

        return JsonResponse({'corpus_data': list(corpus_data)})

    # Filter translators by language proficiency if provided
    proficiency = request.GET.get('proficiency')
    if proficiency:
        # Filter translators and files based on the language proficiency
        translators = []
        file_data = FileImport.objects.filter(language_proficiency__icontains=proficiency).values('id', 'generated_file_name', 'language_proficiency')

        for translator in TranslatorTable.objects.all():
            try:
                # Attempt to load the JSON data
                languages = json.loads(translator.language_profeciency)
                # Check if the selected proficiency exists in the languages (partial match)
                for lang in languages:
                    if proficiency in lang['language']:
                        translators.append({
                            't_id': translator.t_id,
                            'rating': 'New User' if translator.rating is None else translator.rating,
                            'experience': lang.get('experience', 'N/A'),  # Add experience here
                            'minor_job_id': translator.minor_job_id,
                        })
                        break  # Avoid duplicate entries for the same translator
            except (json.JSONDecodeError, TypeError):
                continue  # Skip translators with invalid JSON data

        return JsonResponse({'translator_data': translators, 'file_data': list(file_data)})

    # Prepare translator data for the initial load or when no proficiency is selected
    for translator in translators:
        try:
            # Parse the language_profeciency JSON
            languages = json.loads(translator.language_profeciency or "[]")
            experience = "N/A"  # Default value
            if languages:
                # Extract the first experience or set fallback
                experience = languages[0].get('experience', "N/A")
        except (json.JSONDecodeError, TypeError):
            experience = "N/A"  # Handle invalid JSON

        translator_data.append({
            't_id': translator.t_id,
            'rating': 'New User' if translator.rating is None else translator.rating,
            'experience': experience,  # Include experience
            'minor_job_id': translator.minor_job_id,
        })

    # Prepare pending jobs data
    for translator in translatortable:
        assigned_jobs_count = len(translator.batch_range.split(',')) if translator.batch_range else 0
        batch_range = set(translator.batch_range.split(',')) if translator.batch_range else set()
        completed_batches = set(translator.completed_batches.split(',')) if translator.completed_batches else set()
        pending_batches = batch_range - completed_batches
        pending_count = len(pending_batches)

        # Fetch corpus_id and match with CorpusTable for language proficiency
        corpus_ids = translator.corpus_id.split(',') if translator.corpus_id else []
        corpus_languages = CorpusTable.objects.filter(corpus_id__in=corpus_ids).values_list('language_profeciency',
                                                                                            flat=True)
        language_profeciency = ", ".join(corpus_languages) if corpus_languages else "N/A"

        pending_jobs_data.append({
            't_id': translator.t_id,
            'assigned_jobs_count': assigned_jobs_count,
            'pending_count': pending_count,
            'language_profeciency': language_profeciency,  # Add language proficiency
        })

    file_data = FileImport.objects.filter(status='N').values('id', 'generated_file_name', 'language_proficiency')
    context = {
        'translator_data': translator_data,
        'pending_jobs_data': pending_jobs_data,
        'major_ids': major_ids,
        'file_data': file_data
    }
    return render(request, 'admintranslations.html', context)





def fetch_available_batches(request):
    """
    Fetches available batches based on selected language proficiency, priority, and file.

    Parameters:
    - request: Django HTTP request object containing 'proficiency', 'priority', and 'file_id'.

    Returns:
    - JSON response with HTML content for the batch table and batch IDs.
    """
    # Extract query parameters
    proficiency = request.GET.get('proficiency')
    priority = request.GET.get('priority', '').lower()
    file_id = request.GET.get('file_id')

    try:
        # Validate input parameters
        if not proficiency or not priority or not file_id:
            return JsonResponse({
                'available_batches_html': '<tr><td class="border-b border-gray-700 p-2">Invalid input for proficiency, priority, or file</td></tr>',
                'batch_ids': []
            })

        # SQL query to fetch batch IDs
        query = """
            SELECT DISTINCT batch_id 
            FROM job_table 
            WHERE corpus_id IN (
                SELECT corpus_id FROM corpus_table WHERE language_profeciency = %s
            ) 
            AND LOWER(priority) = %s
            AND t_assigned = 'N'  -- Ensure the batch is unassigned
            AND file_number = %s       -- Match the selected file
            ORDER BY batch_id
        """

        # Execute the query and fetch results
        with connection.cursor() as cursor:
            cursor.execute(query, [proficiency, priority, file_id])
            batch_ids = [row[0] for row in cursor.fetchall()]

        # Generate HTML for available batches
        if batch_ids:
            batch_html = ''.join([
                f'<tr><td class="border-b border-gray-700 p-2 cursor-pointer hover:bg-gray-700" '
                f'onclick="addBatchToInput({batch_id})">{batch_id}</td></tr>'
                for batch_id in batch_ids
            ])
        else:
            batch_html = '<tr><td class="border-b border-gray-700 p-2">No batches available</td></tr>'

        # Return the response
        return JsonResponse({
            'available_batches_html': batch_html,
            'batch_ids': batch_ids
        })

    except Exception as e:
        # Log and return an error response
        print(f"Error occurred in fetch_available_batches: {e}")
        return JsonResponse({
            'available_batches_html': '<tr><td class="border-b border-gray-700 p-2">Error loading batches</td></tr>',
            'batch_ids': []
        })





def fetch_available_batches_for_validation(translator_id, proficiency):
    available_batches = []

  
    corpus = CorpusTable.objects.filter(language_profeciency=proficiency).first()
    if corpus:
        query = """
                SELECT DISTINCT batch_id 
                FROM job_table 
                WHERE corpus_id = %s 
                AND t_assigned = 'N'
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [corpus.corpus_id])
            available_batches = [row[0] for row in cursor.fetchall()]
    return available_batches




def assign_batch(request):
    if request.method == 'POST':
        try:
            translator_id = request.POST.get('translator_id', '').strip()
            batch_ids = request.POST.get('batch_ids', '').strip()  # Can be a range like "2-8" or comma-separated
            proficiency = request.POST.get('proficiency', '').strip()

            # Validate input fields
            if not translator_id or not batch_ids or not proficiency:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Parse and normalize batch IDs
            batch_id_list = []
            for batch_part in batch_ids.split(','):
                batch_part = batch_part.strip()
                if '-' in batch_part:
                    try:
                        start, end = map(int, batch_part.split('-'))
                        if start > end:
                            raise ValueError(f"Invalid range: {batch_part}")
                        batch_id_list.extend(range(start, end + 1))
                    except ValueError:
                        return JsonResponse({'error': f'Invalid range: {batch_part}'}, status=400)
                elif batch_part.isdigit():
                    batch_id_list.append(int(batch_part))
                else:
                    return JsonResponse({'error': f'Invalid batch ID: {batch_part}'}, status=400)

            # Remove duplicates and sort
            batch_id_list = sorted(set(batch_id_list))

            # Fetch available batches for validation
            available_batches = fetch_available_batches_for_validation(translator_id, proficiency)
            available_batches = [int(batch_id) for batch_id in available_batches]

            # Validate entered batch IDs against available batches
            invalid_batches = [batch_id for batch_id in batch_id_list if batch_id not in available_batches]
            if invalid_batches:
                return JsonResponse({
                    'error': f'The following Batch IDs are not available for assignment: {", ".join(map(str, invalid_batches))}'
                }, status=400)

            # Generate current date and deadline
            current_date = datetime.now().date()
            deadline_date = current_date + timedelta(days=90)

            # Get the first job from the first batch to get the major_job_id
            first_batch_id = batch_id_list[0]  # Use the first batch ID from the list
            job = JobTable.objects.filter(batch_id=first_batch_id, t_assigned='N').first()  # Check if t_assigned is 'N'

            if not job:
                return JsonResponse({'error': 'No job found for the given batch ID or job already assigned'}, status=400)

            # Generate unique and sequential minor job ID
            existing_minor_job_ids = set(TranslatorTable.objects.values_list('minor_job_id', flat=True))
            minor_job_id = 1
            while minor_job_id in existing_minor_job_ids:
                minor_job_id += 1

            # Update translator table
            translator = TranslatorTable.objects.get(t_id=translator_id)

            # Append new batch IDs to existing batch_range
            if translator.batch_range:
                existing_batches = translator.batch_range.split(', ')
                updated_batches = sorted(set(existing_batches + list(map(str, batch_id_list))))
                translator.batch_range = ', '.join(updated_batches)
            else:
                translator.batch_range = ', '.join(map(str, batch_id_list))  # First-time assignment

            translator.creation_date = current_date
            translator.deadline = deadline_date
            translator.major_job_id = job.major_job_id
            translator.minor_job_id = minor_job_id
            translator.corpus_id = job.corpus_id
            translator.job_assigned = 'Y'
            corpus_entry = CorpusTable.objects.filter(language_profeciency=proficiency).first()
            
            if not corpus_entry:
                return JsonResponse({'error': 'Invalid proficiency level.'}, status=400)
            corpus_id = corpus_entry.corpus_id
           
            # **Initialize a list to store filenames**
            file_numbers = set() 

            # **Loop through batch IDs to find file numbers and filenames**
            for batch_id in batch_id_list:
                job_entry = JobTable.objects.filter(batch_id=batch_id, corpus_id=corpus_id).first()
                
                if job_entry:
                    file_number = job_entry.file_number
                    file_numbers.add(file_number) 
                   
            
            # **Store the filenames in the translator table**
            
            if translator.file_assigned:
                 existing_file_numbers  =set(str(translator.file_assigned).split(', '))
                 updated_file_numbers  =  existing_file_numbers.union(map(str, file_numbers)) # Remove duplicates and sort
                 translator.file_assigned =  ', '.join(sorted(updated_file_numbers))  # Join updated filenames
            else:
    # If no filenames are assigned yet, just join the new filenames
                translator.file_assigned = ', '.join(map(str, sorted(file_numbers)))

              # Print the final filenames
            translator.save()   # Mark translator as assigned
           

            # Update job table for each unique batch_id
            for batch_id in batch_id_list:
                # Update all records with the same batch_id
                JobTable.objects.filter(batch_id=batch_id).update(t_assigned='Y', minor_job_id=minor_job_id)  # Mark all related batches as assigned

            admin_name = request.session.get('admin_name')
            # Assuming admin_name is stored in the session
            if admin_name:
                # Find the matching log entry for the admin
                log_entry = ALogTable.objects.filter(admin_name=admin_name).first()
                if log_entry:
                    # Now find the corresponding user_id in the ALogTable
                    user_id = log_entry.user_id  # Get the user_id from the log entry

                    # Update the log entry with the new values
                    ALogTable.objects.filter(user_id=translator_id).update(
                        minor_job_id=minor_job_id,
                        creation_date=current_date,
                        deadline=deadline_date
                    )
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Log the error to the console or a log file
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)





def assigned_jobs(request):
    # Fetch translators where job_assigned is 'Y'
    translators = TranslatorTable.objects.filter(job_assigned='Y')

    # Debugging: print the number of translators fetched
    print(f"Number of translators fetched: {translators.count()}")

    # Debugging: print the actual data fetched
    for translator in translators:
        print(f"Translator ID: {translator.t_id}, Name: {translator.t_name}, Job Assigned: {translator.job_assigned}")

    return render(request, 'assignedjobs.html', {'translators': translators})

#-----------------------------------------------------------------------------------------------------------------------------------------
#reviewer

def adminreview_view(request):
    reviewers = ReviewerTable.objects.all()
    reviewertable = ReviewerTable.objects.filter(job_assigned='Y')
    major_ids = MajorTable.objects.values('major_id', 'language')  # Fetch major IDs and languages

    reviewer_data = []
    pending_jobs_data = []

    # Check if a major_id is provided to fetch language proficiencies
    if 'major_id' in request.GET:
        major_id = request.GET.get('major_id')
        # Get unique corpus_ids for the selected major_id
        corpus_ids_jobtable = JobTable.objects.filter(major_job_id=major_id).values_list('corpus_id',
                                                                                         flat=True).distinct()
        # Fetch language proficiencies based on these corpus_ids
        corpus_data = CorpusTable.objects.filter(corpus_id__in=corpus_ids_jobtable).values('corpus_id',
                                                                                           'language_profeciency')

        return JsonResponse({'corpus_data': list(corpus_data)})


    proficiency = request.GET.get('proficiency')
    if proficiency:

        reviewers = []
        file_data = FileImport.objects.filter(language_proficiency__icontains=proficiency).values('id',
                                                                                                  'generated_file_name',
                                                                                                  'language_proficiency')

        for reviewer in ReviewerTable.objects.all():
            try:
                # Attempt to load the JSON data
                languages = json.loads(reviewer.language_profeciency)
                # Check if the selected proficiency exists in the languages (partial match)
                for lang in languages:
                    if proficiency in lang['language']:
                        reviewers.append({
                            'r_id': reviewer.r_id,

                            'experience': lang.get('experience', 'N/A'),  # Add experience here
                            'minor_job_id': reviewer.minor_job_id,
                        })
                        break  # Avoid duplicate entries for the same reviewer
            except (json.JSONDecodeError, TypeError):
                continue

        return JsonResponse({'reviewer_data': reviewers, 'file_data': list(file_data)})

    # Prepare reviewer data for the initial load or when no proficiency is selected
    for reviewer in reviewers:
        try:
            # Parse the language_profeciency JSON
            languages = json.loads(reviewer.language_profeciency or "[]")
            experience = "N/A"  # Default value
            if languages:
                # Extract the first experience or set fallback
                experience = languages[0].get('experience', "N/A")
        except (json.JSONDecodeError, TypeError):
            experience = "N/A"  # Handle invalid JSON

        reviewer_data.append({
            'r_id': reviewer.r_id,

            'experience': experience,  # Include experience
            'minor_job_id': reviewer.minor_job_id,
        })

    # Prepare pending jobs data
    for reviewer in reviewertable:
        assigned_jobs_count = len(reviewer.batch_range.split(',')) if reviewer.batch_range else 0
        batch_range = set(reviewer.batch_range.split(',')) if reviewer.batch_range else set()
        completed_batches = set(reviewer.completed_batches.split(',')) if reviewer.completed_batches else set()
        pending_batches = batch_range - completed_batches
        pending_count = len(pending_batches)

        # Fetch corpus_id and match with CorpusTable for language proficiency
        corpus_ids = reviewer.corpus_id.split(',') if reviewer.corpus_id else []
        corpus_languages = CorpusTable.objects.filter(corpus_id__in=corpus_ids).values_list('language_profeciency',
                                                                                            flat=True)
        language_profeciency = ", ".join(corpus_languages) if corpus_languages else "N/A"

        pending_jobs_data.append({
            'r_id': reviewer.r_id,
            'assigned_jobs_count': assigned_jobs_count,
            'pending_count': pending_count,
            'language_profeciency': language_profeciency,  # Add language proficiency
        })

    file_data = FileImport.objects.filter(status='N').values('id', 'generated_file_name', 'language_proficiency')
    context = {
        'reviewer_data': reviewer_data,
        'pending_jobs_data': pending_jobs_data,
        'major_ids': major_ids,
        'file_data': file_data
    }
    return render(request, 'adminreviews.html', context)




def fetch_available_batches_r(request):
    """
    Fetches available batches based on selected language proficiency, priority, and file.

    Parameters:
    - request: Django HTTP request object containing 'proficiency', 'priority', and 'file_id'.

    Returns:
    - JSON response with HTML content for the batch table and batch IDs.
    """
    # Extract query parameters
    proficiency = request.GET.get('proficiency')
    priority = request.GET.get('priority', '').lower()
    file_id = request.GET.get('file_id')

    try:
        # Validate input parameters
        if not proficiency or not priority or not file_id:
            return JsonResponse({
                'available_batches_html': '<tr><td class="border-b border-gray-700 p-2">Invalid input for proficiency, priority, or file</td></tr>',
                'batch_ids': []
            })

        # SQL query to fetch batch IDs
        query = """
            SELECT DISTINCT batch_id 
            FROM job_table 
            WHERE corpus_id IN (
                SELECT corpus_id FROM corpus_table WHERE language_profeciency = %s
            ) 
            AND LOWER(priority) = %s
            
            AND t_flag = 'Y' 
            AND r_assigned = 'N' 
            AND file_number = %s       -- Match the selected file
            ORDER BY batch_id
        """

        # Execute the query and fetch results
        with connection.cursor() as cursor:
            cursor.execute(query, [proficiency, priority, file_id])
            batch_ids = [row[0] for row in cursor.fetchall()]

        # Generate HTML for available batches
        if batch_ids:
            batch_html = ''.join([
                f'<tr><td class="border-b border-gray-700 p-2 cursor-pointer hover:bg-gray-700" '
                f'onclick="addBatchToInput({batch_id})">{batch_id}</td></tr>'
                for batch_id in batch_ids
            ])
        else:
            batch_html = '<tr><td class="border-b border-gray-700 p-2">No batches available</td></tr>'

        # Return the response
        return JsonResponse({
            'available_batches_html': batch_html,
            'batch_ids': batch_ids
        })

    except Exception as e:
        # Log and return an error response
        print(f"Error occurred in fetch_available_batches: {e}")
        return JsonResponse({
            'available_batches_html': '<tr><td class="border-b border-gray-700 p-2">Error loading batches</td></tr>',
            'batch_ids': []
        })


def fetch_available_batches_for_validation_r(reviewer_id, proficiency):
    available_batches = []

    # Fetch available batches using the existing logic
    corpus = CorpusTable.objects.filter(language_profeciency=proficiency).first()
    if corpus:
        query = """
                SELECT DISTINCT batch_id 
                FROM job_table 
                WHERE corpus_id = %s 
                AND t_flag = 'Y'
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [corpus.corpus_id])
            available_batches = [row[0] for row in cursor.fetchall()]
    return available_batches


def assign_batch_r(request):
    if request.method == 'POST':
        try:
            reviewer_id = request.POST.get('reviewer_id', '').strip()
            batch_ids = request.POST.get('batch_ids', '').strip()  # Can be a range like "2-8" or comma-separated
            proficiency = request.POST.get('proficiency', '').strip()

            # Validate input fields
            if not reviewer_id or not batch_ids or not proficiency:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Parse and normalize batch IDs
            batch_id_list = []
            for batch_part in batch_ids.split(','):
                batch_part = batch_part.strip()
                if '-' in batch_part:
                    try:
                        start, end = map(int, batch_part.split('-'))
                        if start > end:
                            raise ValueError(f"Invalid range: {batch_part}")
                        batch_id_list.extend(range(start, end + 1))
                    except ValueError:
                        return JsonResponse({'error': f'Invalid range: {batch_part}'}, status=400)
                elif batch_part.isdigit():
                    batch_id_list.append(int(batch_part))
                else:
                    return JsonResponse({'error': f'Invalid batch ID: {batch_part}'}, status=400)

            # Remove duplicates and sort
            batch_id_list = sorted(set(batch_id_list))

            # Fetch available batches for validation
            available_batches = fetch_available_batches_for_validation_r(reviewer_id, proficiency)
            available_batches = [int(batch_id) for batch_id in available_batches]

            # Validate entered batch IDs against available batches
            invalid_batches = [batch_id for batch_id in batch_id_list if batch_id not in available_batches]
            if invalid_batches:
                return JsonResponse({
                    'error': f'The following Batch IDs are not available for assignment: {", ".join(map(str, invalid_batches))}'
                }, status=400)

            # Generate current date and deadline
            current_date = datetime.now().date()
            deadline_date = current_date + timedelta(days=90)

            # Get the first job from the first batch to get the major_job_id
            first_batch_id = batch_id_list[0]  # Use the first batch ID from the list
            job = JobTable.objects.filter(batch_id=first_batch_id, r_assigned='N').first()  # Check if t_assigned is 'N'

            if not job:
                return JsonResponse({'error': 'No job found for the given batch ID or job already assigned'}, status=400)

            # Generate unique and sequential minor job ID
            existing_minor_job_ids = set(ReviewerTable.objects.values_list('minor_job_id', flat=True))
            minor_job_id = 1
            while minor_job_id in existing_minor_job_ids:
                minor_job_id += 1


            reviewer = ReviewerTable.objects.get(r_id=reviewer_id)

            # Append new batch IDs to existing batch_range
            if reviewer.batch_range:
                existing_batches = reviewer.batch_range.split(', ')
                updated_batches = sorted(set(existing_batches + list(map(str, batch_id_list))))
                reviewer.batch_range = ', '.join(updated_batches)
            else:
                reviewer.batch_range = ', '.join(map(str, batch_id_list))  # First-time assignment

            reviewer.creation_date = current_date
            reviewer.deadline = deadline_date
            reviewer.major_job_id = job.major_job_id
            reviewer.minor_job_id = minor_job_id
            reviewer.corpus_id = job.corpus_id
            reviewer.job_assigned = 'Y'
            corpus_entry = CorpusTable.objects.filter(language_profeciency=proficiency).first()
            
            if not corpus_entry:
                return JsonResponse({'error': 'Invalid proficiency level.'}, status=400)
            corpus_id = corpus_entry.corpus_id
            
            # **Initialize a list to store filenames**
            file_numbers = set() 

            # **Loop through batch IDs to find file numbers and filenames**
            for batch_id in batch_id_list:
                job_entry = JobTable.objects.filter(batch_id=batch_id, corpus_id=corpus_id).first()
                
                if job_entry:
                    file_number = job_entry.file_number
                    file_numbers.add(file_number) 
                   
            
            # **Store the filenames in the translator table**
            
            if reviewer.file_assigned:
                 existing_file_numbers  =set(str(reviewer.file_assigned).split(', '))
                 updated_file_numbers  =  existing_file_numbers.union(map(str, file_numbers)) # Remove duplicates and sort
                 reviewer.file_assigned =  ', '.join(sorted(updated_file_numbers))  # Join updated filenames
            else:
    # If no filenames are assigned yet, just join the new filenames
                reviewer.file_assigned = ', '.join(map(str, sorted(file_numbers)))

              # Print the final filenames
              # Print the final filenames
            
            reviewer.save()

            # Update job table for each unique batch_id
            for batch_id in batch_id_list:
                # Update all records with the same batch_id
                JobTable.objects.filter(batch_id=batch_id).update(r_assigned='Y', minor_job_id=minor_job_id)  # Mark all related batches as assigned

            admin_name = request.session.get('admin_name')
            # Assuming admin_name is stored in the session
            if admin_name:
                # Find the matching log entry for the admin
                log_entry = ALogTable.objects.filter(admin_name=admin_name).first()
                if log_entry:
                    # Now find the corresponding user_id in the ALogTable
                    user_id = log_entry.user_id  # Get the user_id from the log entry

                    # Update the log entry with the new values
                    ALogTable.objects.filter(user_id=reviewer_id).update(
                        minor_job_id=minor_job_id,
                        creation_date=current_date,
                        deadline=deadline_date
                    )
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Log the error to the console or a log file
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def assigned_jobs_r(request):
    # Fetch translators where job_assigned is 'Y'
    reviewers = ReviewerTable.objects.filter(job_assigned='Y')

    # Debugging: print the number of translators fetched
    print(f"Number of translators fetched: {reviewers.count()}")

    for reviewer in reviewers:
        print(f"Translator ID: {reviewer.r_id}, Name: {reviewer.r_name}, Job Assigned: {reviewer.job_assigned}")

    return render(request, 'assignedjobs_r.html', {'reviewers': reviewers})


def allocate_job(request):
    return render(request, 'admintranslations.html')


def allocate_job_r(request):
    return render(request, 'adminreviews.html')



def get_corpus_of_major(request, major_id):
    text = request.GET.get('text', None)
    corpus_ids = []
    files = []       
    
    if text is None:
        corpus_ids_jobtable = JobTable.objects.filter(major_job_id=major_id).values_list('corpus_id', flat=True)
        corpus_ids = CorpusTable.objects.filter(corpus_id__in=corpus_ids_jobtable).values('corpus_id', 'language_profeciency')
    elif text == "file-title":
        languagedirection = CorpusTable.objects.get(corpus_id=major_id).language_profeciency
        files = FileImport.objects.filter(language_proficiency=languagedirection).values('id','original_file_name')

    return JsonResponse({
        'corpus_ids': list(corpus_ids),   
        'corpus_ids_translators': list(corpus_ids),   
        'corpus_ids_reviewers': list(corpus_ids),   
        'file_names':list(files),   
    })


def job_counts_M(request, major_id):
    total_jobs = JobTable.objects.filter(major_job_id=major_id).count()
    allotted_jobs = JobTable.objects.filter(major_job_id=major_id, t_assigned='Y', r_assigned='Y').count()
    pending_jobs = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'), major_job_id=major_id, r_flag='N').count()
    completed_jobs_count = JobTable.objects.filter(major_job_id=major_id, t_flag='Y', r_flag='Y').count()
    
    total_jobs_file = JobTable.objects.filter(major_job_id=major_id).count()
    allotted_jobs_file = JobTable.objects.filter(major_job_id=major_id, t_assigned='Y', r_assigned='Y').count()
    pending_jobs_file = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'), major_job_id=major_id, r_flag='N').count()
    completed_jobs_count_file = JobTable.objects.filter(major_job_id=major_id, t_flag='Y', r_flag='Y').count()

    allotted_jobs_translator = JobTable.objects.filter(major_job_id=major_id, t_assigned='Y').count()
    pending_jobs_translator = JobTable.objects.filter(major_job_id=major_id, t_assigned='Y', t_flag='N').count()
    completed_jobs_translator = JobTable.objects.filter(major_job_id=major_id, t_assigned='Y', t_flag='Y').count()
    
    allotted_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id, r_assigned='Y').count()
    pending_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id, r_assigned='Y', r_flag='N').count()
    completed_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id, r_assigned='Y', r_flag='Y').count()

    
    
   
    return JsonResponse({
        'total_jobs': total_jobs,
        'allotted_jobs': allotted_jobs,
        'pending_jobs': pending_jobs,
        'completed_jobs': completed_jobs_count,  
        'total_jobs_file': total_jobs_file,
        'allotted_jobs_file': allotted_jobs_file,
        'pending_jobs_file': pending_jobs_file,
        'completed_jobs_file': completed_jobs_count_file,  
        'allotted_jobs_translator': allotted_jobs_translator,
        'pending_jobs_translator': pending_jobs_translator,
        'completed_jobs_translator': completed_jobs_translator,
        'allotted_jobs_reviewer': allotted_jobs_reviewer,
        'pending_jobs_reviewer': pending_jobs_reviewer,
        'completed_jobs_reviewer': completed_jobs_reviewer,
        
    
    })


def job_counts_MC(request, major_id,corpus_id):

    total_jobs = JobTable.objects.filter(major_job_id=major_id, corpus_id=corpus_id,).count()
    allotted_jobs = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, t_assigned='Y',r_assigned='Y').count()
    pending_jobs = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'),corpus_id=corpus_id, major_job_id=major_id, r_flag='N').count()
    completed_jobs = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, t_flag='Y', r_flag='Y').count()
    total_jobs_file = JobTable.objects.filter(major_job_id=major_id, corpus_id=corpus_id,).count()
    allotted_jobs_file = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, t_assigned='Y',r_assigned='Y').count()
    pending_jobs_file = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'),corpus_id=corpus_id, major_job_id=major_id, r_flag='N').count()
    completed_jobs_file = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, t_flag='Y', r_flag='Y').count()
    allotted_jobs_translator = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, t_assigned='Y').count()
    pending_jobs_translator = JobTable.objects.filter(major_job_id=major_id, corpus_id=corpus_id,t_assigned='Y',t_flag='N').count()
    completed_jobs_translator = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id,t_assigned='Y', t_flag='Y').count()
    allotted_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id, r_assigned='Y').count()
    allotted_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id,r_assigned='Y', r_flag='N').count()
    completed_jobs_reviewer = JobTable.objects.filter(major_job_id=major_id,corpus_id=corpus_id,r_assigned='Y', r_flag='Y').count()

    
    
    languagedirection = CorpusTable.objects.get(corpus_id=corpus_id).language_profeciency
    
    files = FileImport.objects.filter(language_proficiency=languagedirection,status='Y').values_list('id', flat=True)
 
    
    job_data_mc = []
    for filenumber in files:
        filedetails = FileImport.objects.get(id=filenumber)
        
        

        job_data_mc.append({
            'filenumber': filenumber,
            'major_job_id': major_id,
            'corpus_id': corpus_id,
            'language_proficiency': languagedirection ,
            'originalfilename':filedetails.original_file_name,
            'generatedfilename':filedetails.generated_file_name,
            'importdate':filedetails.import_date,
            
        })
   

    return JsonResponse({
        'total_jobs': total_jobs,
        'allotted_jobs': allotted_jobs,
        'pending_jobs': pending_jobs,
        'completed_jobs': completed_jobs,
        'total_jobs_file': total_jobs_file,
        'allotted_jobs_file': allotted_jobs_file,
        'pending_jobs_file': pending_jobs_file,
        'completed_jobs_file': completed_jobs_file,  
        'allotted_jobs_translator': allotted_jobs_translator,
        'pending_jobs_translator': pending_jobs_translator,
        'completed_jobs_translator': completed_jobs_translator,
        'allotted_jobs_reviewer': allotted_jobs_reviewer,
        'pending_jobs_reviewer': allotted_jobs_reviewer,
        'completed_jobs_reviewer': completed_jobs_reviewer,
        'job_data': job_data_mc,
         
    })

def job_counts_filenames(request ,fileNumber, fileName):
   
    total_jobs_file = JobTable.objects.filter(file_number=fileNumber).count()
    allotted_jobs_file = JobTable.objects.filter(file_number=fileNumber, t_assigned='Y',r_assigned='Y').count()
    pending_jobs_file = JobTable.objects.filter(Q(t_flag='N') | Q(t_flag='Y'),file_number=fileNumber, r_flag='N').count()
    completed_jobs_file = JobTable.objects.filter(file_number=fileNumber, t_flag='Y', r_flag='Y').count()
    
    return JsonResponse({
       
        'total_jobs_file': total_jobs_file,
        'allotted_jobs_file': allotted_jobs_file,
        'pending_jobs_file': pending_jobs_file,
        'completed_jobs_file': completed_jobs_file,  
        
        
    })
    

def download_csv(request, major_job_id, corpus_id,filenumber):
    """
    Generates and downloads a CSV file for the given job and corpus IDs.
    Only includes rows where r_flag is 'Y'.
    Additionally, updates the ALogTable with export_file and export_timestamp after download.
    """
    print(major_job_id, corpus_id,filenumber)
    
    job_data = JobTable.objects.filter(
        major_job_id=major_job_id,
        corpus_id=corpus_id,
        file_number=filenumber, 
    )
   
    corpus = CorpusTable.objects.get(corpus_id=corpus_id)

    response = HttpResponse(content_type='text/csv')
    file_name = f'translations_{corpus.language_profeciency}.csv'
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    writer = csv.writer(response)

    writer.writerow(['sen_id', 'source_data', 'r_target_data', 'batch_id', 'corpus_id'])


    for job in job_data:
        
        r_target_data = job.r_target_data or ""
        writer.writerow([job.sen_id, job.source_data, r_target_data, job.batch_id, job.corpus_id])

    admin_name = request.session.get('admin_name')
    if admin_name:
     
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_time = now().astimezone(ist_timezone)
        ist_now_naive = ist_time.replace(tzinfo=None)

        
        log_entry = ALogTable.objects.filter(admin_name=admin_name, logout__isnull=True).last()
        if log_entry:
            log_entry.export_file = file_name
            log_entry.export_timestamp = ist_now_naive
            log_entry.save()

    return response


def import_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        language_proficiency = request.POST.get('language_proficiency')
        keyboardId = request.POST.get('keyboardId')
        keyboardName = request.POST.get('keyboardName')
        languageId = request.POST.get('languageId')
        languageName = request.POST.get('languageName')
        keyboardFile = request.FILES.get('keyboardFile')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return redirect('import_csv')

        decoded_file = csv_file.read().decode('utf-8-sig')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        error_occurred = False  
        success_count = 0 

        timezone = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now().astimezone(timezone)
        now_naive = current_time.replace(tzinfo=None)
        formatted_date = now_naive.strftime("%Y%m%d")
        today_date = now_naive.date()

        today_imports = FileImport.objects.filter(import_date__date=today_date)
        serial_number = today_imports.count() + 1  
        
        
        generated_file_name = f"{csv_file.name.split('.')[0]}_{formatted_date}{serial_number}.csv"
        
        original_file_name = csv_file.name.split('.')[0]
        

        
        
        max_corpus_id = CorpusTable.objects.aggregate(max_id=models.Max('corpus_id'))['max_id']
        
       
        if max_corpus_id is not None:
            
            numeric_part = int(max_corpus_id)  
            next_corpus_id = numeric_part + 1
        else:
            next_corpus_id = 1  

       
        while CorpusTable.objects.filter(corpus_id=str(next_corpus_id)).exists():
            next_corpus_id += 1  

       
        corpus_exists = CorpusTable.objects.filter(language_profeciency=language_proficiency).exists()

        if corpus_exists:
            # If it exists, reuse the existing entry (keyboard details are optional)
            corpus_entry = CorpusTable.objects.get(language_profeciency=language_proficiency)
        else:
            # If it doesn’t exist, require all keyboard fields
            if not all([keyboardId, keyboardName, languageId, languageName, keyboardFile]):
                messages.error(request, 'All keyboard details are required for a new language proficiency.')
                return redirect('import_csv')

            # Validate keyboard file
            if not keyboardFile.name.endswith('.js'):
                messages.error(request, 'Keyboard file must be a .js file')
                return redirect('import_csv')   
            
            keyboard_filename = os.path.splitext(keyboardFile.name)[0]  # e.g., "isis_kannada"
            keyboard_dir = os.path.join(settings.MEDIA_ROOT, "static", "keyman","languages")
            keyboard_filepath = os.path.join(keyboard_dir, f"{keyboard_filename}.js")

            os.makedirs(keyboard_dir, exist_ok=True)

            try:
                with open(keyboard_filepath, 'wb') as f:
                    for chunk in keyboardFile.chunks():
                        f.write(chunk)

            except Exception as e:
                print(f"Error saving file: {e}")


            corpus_entry, created = CorpusTable.objects.get_or_create(
            language_profeciency=language_proficiency,
            defaults={'corpus_id': str(next_corpus_id)} ,
            keyboard_id=keyboardId,
                keyboard_name=keyboardName,
                language_id=languageId,
                language_name=languageName,
                keyboard_filename=keyboard_filename
        )

        
        corpus_entry, created = CorpusTable.objects.get_or_create(
            language_profeciency=language_proficiency,
            defaults={'corpus_id': str(next_corpus_id)}
        )

        headers = [header.strip() for header in reader.fieldnames]

        file_import_entry = FileImport.objects.create(
            original_file_name=original_file_name, 
            generated_file_name=generated_file_name, 
            language_proficiency=language_proficiency,
            status='N',
            import_date=current_time 
        )
        job_entries = [] 

        for row in reader:
            row = {key.strip(): value for key, value in row.items()}
            source_data = row.get('source_data', None)

            if source_data is None:
                messages.error(request, f'Missing key in row: "source_data". Row data: {row}')
                error_occurred = True
                continue  

            try:
                job_entries.append(JobTable(
                    source_data=source_data,
                    batch_id=row.get('batch_id', ''),
                    major_job_id=row.get('major_job_id', ''),
                    corpus_id=corpus_entry.corpus_id,
                    priority=row.get('priority', ''),
                    t_flag='N',
                    r_flag='N',
                    t_assigned='N',
                    r_assigned='N',
                    file_number=file_import_entry.id,
                ))
                success_count += 1
            except Exception as e:
                messages.error(request, f'Error processing row: {row}. Error: {e}')
                error_occurred = True

        
        if job_entries:
            JobTable.objects.bulk_create(job_entries)

        messages.success(request, f'CSV file imported successfully! {success_count} entries added.')

        

        admin_name = request.session.get('admin_name')
        if admin_name:
            
            ist_timezone = pytz.timezone('Asia/Kolkata')
            ist_time = now().astimezone(ist_timezone)
            ist_now_naive = ist_time.replace(tzinfo=None)

        
            log_entry = ALogTable.objects.filter(admin_name=admin_name, logout__isnull=True).last()
            if log_entry:
                log_entry.import_file = csv_file.name
                log_entry.import_timestamp = ist_now_naive
                log_entry.save()

        
            

        return redirect('import_csv')

    return render(request, 'import_csv.html')


def custom_admin_login(request):
    if request.method == 'POST':
        admin_name = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin = AdminTable.objects.get(a_name=admin_name)
            if check_password(password, admin.a_password):
                
                text = request.GET.get('text', '')
                redirect_url = request.GET.get('redirect_url', 'default_redirect_url')  

                if text == 'importing':
                    return redirect('import_csv')  
                else:
                    return redirect(redirect_url)  

            else:
                messages.error(request, 'Invalid credentials')
        
        except AdminTable.DoesNotExist:
            messages.error(request, 'Admin does not exist')

    return render(request, 'custom_admin_login.html')




def unsupported_browser(request):
    return render(request, 'unsupported_browser.html')

def admin_logout(request):
    """
    Logs out the admin, updates the ALogTable with logout timestamp and log_duration (time difference only),
    and redirects to the admin login page.
    """
    admin_name = request.session.get('admin_name')
    if admin_name:
        # Get the current time in IST
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_time = now().astimezone(ist_timezone)
        ist_now_naive = ist_time.replace(tzinfo=None)

        # Fetch the latest log entry for the admin
        log_entry = ALogTable.objects.filter(admin_name=admin_name, logout__isnull=True).last()
        if log_entry:
            # Update logout timestamp
            log_entry.logout = ist_now_naive

            if log_entry.login:  # Ensure login timestamp exists
                # Calculate time difference (ignore date)
                time_diff = (log_entry.logout - log_entry.login).seconds  # Total seconds of duration
                duration_time = (datetime.min + timedelta(seconds=time_diff)).time()  # Convert to time object
                log_entry.log_duration = datetime.combine(log_entry.login.date(), duration_time)

            log_entry.save()

        # Clear the session
        request.session.flush()

    # Redirect to the admin login page
    return redirect('admin_login')



def download_biodata(request, email):
    user = get_object_or_404(Registration, email=email)
    pdf_data = user.org_details  
    print(pdf_data)
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="biodata.pdf"'
        return response
    else:
        return HttpResponse("No PDF found for this user.", status=404)

from django.views import View
from django.shortcuts import render
from .models import TranslatorTable, JobTable, ReviewerTable  # Make sure to import your models

class NotificationView(View):
    def get(self, request):
            # Fetching translators
            translators = TranslatorTable.objects.all()  # Fetch all translators
            translator_details = []

            for translator in translators:
                # Check if quit_flag is 'Y'
                if translator.quit_flag == 'Y':
                    # If quit_flag is 'Y', fetch the required fields
                    translator_details.append({
                        't_id': translator.t_id,
                        'email': translator.email,
                        'batch_range': translator.batch_range,
                        'quit_reason': translator.quit_reason,
                        't_review': None  # No review if quit_flag is 'Y'
                    })

            # Fetching reviewers
            reviewers = ReviewerTable.objects.all()  # Fetch all reviewers
            reviewer_details = []

            for reviewer in reviewers:
                # Check if quit_flag is 'Y'
                if reviewer.quit_flag == 'Y':
                    # If quit_flag is 'Y', fetch the required fields
                    reviewer_details.append({
                        'r_id': reviewer.r_id,
                        'email': reviewer.email,
                        'batch_range': reviewer.batch_range,
                        'quit_reason': reviewer.quit_reason,
                        'r_review': None  # No review if quit_flag is 'Y'
                    })

            # Prepare context data
            context = {
                'translators': translator_details,
                'reviewers': reviewer_details,
            }

            # Render the notifications template with the context
            return render(request, 'notifications.html', context)


   

def check_language_proficiency(request):
    lang_prof = request.GET.get('lang_prof', '')
    exists = CorpusTable.objects.filter(language_profeciency=lang_prof).exists()
    return JsonResponse({'exists': exists})