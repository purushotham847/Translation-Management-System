from django.contrib import admin
from django.urls import path
from translation_app import views  # Import the views from the app
from .views import NotificationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # This makes the root URL render the home page
    path('home/', views.home, name='home'),  # Optionally, allow /home URL to render the home page
    path('logindashboard/', views.logindashboard, name='logindashboard'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('registrations/', views.registrations_view, name='registrations'),
    path('approve/<str:email>/', views.approve_user, name='approve_user'),
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('translatorlogin/', views.translator_login, name='translator_login'),
    path('reviewerlogin/', views.reviewer_login, name='reviewer_login'),
    path('adminregistration/', views.admin_registration, name='admin_registration'),
    path('adminreview/', views.adminreview_view, name='adminreview'),
    path('adminreview_view/', views.adminreview_view, name='adminreview_viewx`x '),
    path('assigned-jobs/', views.assigned_jobs, name='assigned_jobs'),
    path('assigned-jobs_r/', views.assigned_jobs_r, name='assigned_jobs_r'),
    path('allocate-job/', views.translations_view, name='allocate_job'),
    path('allocate-job_r/', views.adminreview_view, name='allocate_job_r'),
    path('translations/', views.translations_view, name='translations'),
    path('translations_view/', views.translations_view, name='translations_view'),
    path('fetch_available_batches/', views.fetch_available_batches, name='fetch_available_batches'),
    path('assign_batch/', views.assign_batch, name='assign_batch'),
    path('assign_batch_r/', views.assign_batch_r, name='assign_batch_r'),
    path('fetch_available_batches_r/', views.fetch_available_batches_r, name='fetch_available_batches_r'),
    path('translatordashboard/', views.translatordashboard, name='translatordashboard'),
    path('translatordashboard/t_user_view/<int:batch_id>/', views.t_user_view, name='t_user_view'),
    path('reviewerdashboard/', views.reviewerdashboard, name='reviewerdashboard'),
    path('reviewerdashboard/r_user_view/<int:batch_id>/', views.r_user_view, name='r_user_view'),
    path('api/job_counts_M/<int:major_id>/', views.job_counts_M, name='job_counts_M'),
    path('api/job_counts_MC/<int:major_id>/<int:corpus_id>/', views.job_counts_MC, name='job_counts_MC'),
    path('api/get_corpus_of_major/<int:major_id>/', views.get_corpus_of_major, name='get_corpus_of_major'),
    path('download_csv/<int:major_job_id>/<int:corpus_id>/<int:filenumber>', views.download_csv, name='download_csv'),
    path('custom_admin_login/', views.custom_admin_login, name='custom_admin_login'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('unsupported-browser/', views.unsupported_browser, name='unsupported_browser'),
    path('download-biodata/<str:email>/', views.download_biodata, name='download_biodata'),
    path('download_pdf/<str:user_id>/', views.download_pdf, name='download_pdf'),
    path('send_approval_email/<str:email>/<str:user_type>/<str:name>/<str:user_id>/', views.send_approval_email, name='send_approval_email'),
    path('api/job_counts_filenames/<int:fileNumber>/<str:fileName>/', views.job_counts_filenames, name='job_counts_filenames'),
    path('notifications/', NotificationView.as_view(), name='notifications'),  # Ensure this line is present
    path('check_language_proficiency/', views.check_language_proficiency, name='check_language_proficiency')
]