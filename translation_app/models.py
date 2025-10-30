
from django.db import models


class AdminTable(models.Model):
    a_id = models.CharField(primary_key=True, max_length=20)
    a_email = models.CharField(unique=True, max_length=254)
    a_name = models.CharField(unique=True, max_length=100)
    a_password = models.CharField(max_length=128)

    class Meta:

        db_table = 'admin_table'


class CorpusTable(models.Model):
    language_profeciency = models.CharField(max_length=255)
    corpus_id = models.TextField(primary_key=True)
    keyboard_id = models.TextField(blank=True, null=True)
    keyboard_name = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.TextField(blank=True, null=True)
    language_name = models.CharField(max_length=255, blank=True, null=True)
    keyboard_filename = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'corpus_table'




class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:

        db_table = 'custom_django_session'


class JobTable(models.Model):
    sen_id = models.AutoField(primary_key=True)
    source_data = models.CharField(max_length=255)
    t_target_data = models.CharField(blank=True, null=True, max_length=255)
    r_target_data = models.CharField(blank=True, null=True, max_length=255)
    batch_id = models.IntegerField()
    minor_job_id = models.IntegerField(blank=True, null=True)
    major_job_id = models.IntegerField()
    t_flag = models.CharField(max_length=1)
    r_flag = models.CharField(max_length=1)
    corpus_id = models.TextField()
    priority = models.CharField(max_length=50)
    t_assigned = models.CharField(max_length=1)
    r_assigned = models.CharField(max_length=1)
    t_rating = models.IntegerField(blank=True, null=True)
    t_reviews = models.CharField(blank=True, null=True, max_length=255)
    r_reviews = models.CharField(blank=True, null=True, max_length=255)
    file_number = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'job_table'

    class Meta:

        db_table = 'job_table'


class MajorTable(models.Model):
    major_id = models.IntegerField(primary_key=True)
    language = models.CharField()

    class Meta:

        db_table = 'major_table'


class RLogTable(models.Model):
    slno = models.AutoField(primary_key=True)
    r = models.ForeignKey('ReviewerTable', on_delete=models.DO_NOTHING, blank=True, null=True)
    batch_range = models.CharField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    login = models.DateTimeField(blank=True, null=True)
    logout = models.DateTimeField(blank=True, null=True)
    log_duration = models.DateTimeField(blank=True, null=True)
    module_access_timestamp = models.DateTimeField(blank=True, null=True)
    module_submission_timestamp = models.DateTimeField(blank=True, null=True)
    batch_id = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'r_log_table'


class RegistrationTable(models.Model):
    id =  models.CharField(blank=True, null=True)
    user_name = models.CharField(max_length=255) 
    email = models.CharField(primary_key=True, max_length=255)
    password = models.CharField(max_length=255)  
    user_type = models.CharField(max_length=50) 
    language_profeciency = models.TextField()  
    org_details = models.BinaryField(null=True, blank=True) 
    flag = models.CharField(max_length=1)

    class Meta:

        db_table = 'registration_table'

class ReviewerTable(models.Model):
    r_id = models.CharField(primary_key=True)
    r_name = models.CharField()
    password = models.CharField()
    email = models.CharField()
    language_profeciency = models.CharField()
    major_job_id = models.IntegerField(blank=True, null=True)
    minor_job_id = models.IntegerField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    batch_range = models.CharField(blank=True, null=True)
    corpus_id = models.TextField(blank=True, null=True)
    job_assigned = models.CharField(max_length=1)
    completed_batches = models.CharField(blank=True, null=True)
    file_assigned = models.TextField()
    quit_flag = models.CharField(max_length=1)
    quit_reason = models.TextField(blank=True)
   

    class Meta:

        db_table = 'reviewer_table'


class TLogTable(models.Model):
    slno = models.AutoField(primary_key=True)
    t_id = models.CharField(blank=True, null=True)
    batch_range = models.CharField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    login = models.DateTimeField(blank=True, null=True)
    logout = models.DateTimeField(blank=True, null=True)
    log_duration = models.DateTimeField(blank=True, null=True)
    module_access_timestamp = models.DateTimeField(blank=True, null=True)
    module_submission_timestamp = models.DateTimeField(blank=True, null=True)
    batch_id = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 't_log_table'


class TranslatorTable(models.Model):
    t_id = models.CharField(primary_key=True)
    t_name = models.CharField()
    password = models.CharField()
    email = models.CharField()
    language_profeciency = models.CharField()
    major_job_id = models.IntegerField(blank=True, null=True)
    minor_job_id = models.IntegerField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    batch_range = models.CharField(blank=True, null=True)
    t_review = models.CharField(blank=True, null=True)
    corpus_id = models.TextField(blank=True, )
    job_assigned = models.CharField(max_length=1)
    completed_batches = models.CharField(blank=True, null=True)
    file_assigned = models.TextField()
    quit_flag = models.CharField(max_length=1)
    quit_reason = models.TextField(blank=True)


    class Meta:

        db_table = 'translator_table'


class ALogTable(models.Model):
    slno = models.AutoField(primary_key=True)
    admin_name = models.CharField(blank=True, null=True)
    login = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(blank=True, null=True)
    user_type = models.CharField(blank=True, null=True)
    minor_job_id = models.IntegerField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    import_file = models.TextField(blank=True, null=True)
    import_timestamp = models.DateTimeField(blank=True, null=True)
    export_file = models.TextField(blank=True, null=True)
    export_timestamp = models.DateTimeField(blank=True, null=True)
    logout = models.DateTimeField(blank=True, null=True)
    log_duration = models.DateTimeField(blank=True, null=True)

    class Meta:

        db_table = 'a_log_table'


class FileImport(models.Model):
    id = models.AutoField(primary_key=True)
    original_file_name = models.CharField()
    generated_file_name = models.CharField()
    language_proficiency =models.CharField() 
    import_date = models.DateTimeField()  
    status =  models.CharField() 
    
    class Meta:

        db_table = 'file_import'
