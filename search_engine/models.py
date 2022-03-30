from django.db import models
from django_celery_results.models import TaskResult
from django.contrib.auth.models import User
from datetime import datetime, date


class DdiFact(models.Model):
    id_fact = models.BigAutoField(primary_key=True)
    id_task = models.ForeignKey('Task', on_delete=models.CASCADE, db_column='id_task')
    id_doc = models.IntegerField()
    sentence_txt = models.TextField()
    parsing_txt = models.TextField()
    numb_sentence_in_doc = models.IntegerField()
    ddi_type = models.TextField()

    class Meta:
        managed = True
        db_table = 'ddi_fact'


class DdiResult(models.Model):
    id_fact = models.OneToOneField(DdiFact, on_delete=models.CASCADE, db_column='id_fact', primary_key=True)
    id_task = models.IntegerField()
    id_doc = models.IntegerField()
    sentence_txt = models.CharField(max_length=1024)
    parsing_txt = models.CharField(max_length=1024)
    numb_sentence_in_doc = models.IntegerField()
    ddi_type = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'ddi_result'


class DdiXFact(models.Model):
    id_fact = models.BigAutoField(primary_key=True)
    id_task = models.IntegerField()
    id_doc = models.IntegerField()
    sentence_txt = models.CharField(max_length=4096)
    parsing_txt = models.CharField(max_length=4096)
    numb_sentence_in_doc = models.IntegerField()
    ddi_type = models.CharField(max_length=45)

    class Meta:
        managed = True
        db_table = 'ddi_x_fact'


class DrugLink(models.Model):
    id_fact = models.OneToOneField('DdiFact', on_delete=models.CASCADE, db_column='id_fact', primary_key=True)
    drug_name = models.TextField()

    class Meta:
        managed = True
        db_table = 'drug_link'


class DrugXLink(models.Model):
    id_fact = models.IntegerField()
    drug_name = models.CharField(max_length=4096)

    class Meta:
        managed = True
        db_table = 'drug_x_link'


class DvaDdi(models.Model):
    id1 = models.BigAutoField(primary_key=True)
    id2 = models.IntegerField()
    ddi_text = models.TextField()
    pmid = models.IntegerField(db_column='PMID')
    sentencenumb = models.IntegerField(db_column='SentenceNumb')
    finddate = models.DateField(db_column='FindDate')

    class Meta:
        managed = True
        db_table = 'dva_ddi'


class DvaGisz(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    rus = models.TextField(blank=True, null=True)
    lat = models.TextField(blank=True, null=True)
    eng = models.TextField(blank=True, null=True)
    atx = models.TextField(blank=True, null=True)
    snomed = models.TextField(blank=True, null=True)
    gr = models.IntegerField(blank=True, null=True)
    mnn = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dva_gisz'


class DvaXGisz(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    rus = models.TextField(blank=True, null=True)
    lat = models.TextField(blank=True, null=True)
    eng = models.TextField(blank=True, null=True)
    atx = models.TextField(blank=True, null=True)
    snomed = models.TextField(blank=True, null=True)
    gr = models.IntegerField(blank=True, null=True)
    mnn = models.TextField(blank=True, null=True)
    query_time = models.DateTimeField(blank=True, null=True)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dva_x_gisz'


class ExportPkgDesc(models.Model):
    id = models.BigAutoField(primary_key=True)
    setid = models.TextField(db_column='SETID', blank=True, null=True)
    spl_version = models.IntegerField(db_column='SPL_VERSION', blank=True, null=True)
    product_name = models.TextField(db_column='PRODUCT_NAME', blank=True, null=True)
    product_code = models.TextField(db_column='PRODUCT_CODE', blank=True, null=True)
    ndc = models.TextField(db_column='NDC', blank=True, null=True)
    package_description = models.TextField(db_column='PACKAGE_DESCRIPTION', blank=True, null=True)
    form_code = models.TextField(db_column='FORM_CODE', blank=True, null=True)
    product_number = models.IntegerField(db_column='PRODUCT_NUMBER', blank=True, null=True)
    part_yn = models.TextField(db_column='PART_YN', blank=True, null=True)
    total_product_quantity = models.IntegerField(db_column='TOTAL_PRODUCT_QUANTITY', blank=True, null=True)
    strength = models.TextField(db_column='STRENGTH', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'export_pkg_desc'


class Rls(models.Model):
    regnumb = models.CharField(db_column='RegNumb', max_length=255, blank=True, null=True)
    regdate = models.CharField(db_column='RegDate', max_length=255, blank=True, null=True)
    enddata = models.CharField(db_column='EndData', max_length=255, blank=True, null=True)
    stopdate = models.CharField(db_column='StopDate', max_length=255, blank=True, null=True)
    company = models.CharField(db_column='Company', max_length=255, blank=True, null=True)
    country = models.CharField(db_column='Country', max_length=255, blank=True, null=True)
    torgname = models.CharField(db_column='TorgName', max_length=255, blank=True, null=True)
    chemname = models.CharField(db_column='ChemName', max_length=255, blank=True, null=True)
    forms = models.CharField(db_column='Forms', max_length=255, blank=True, null=True)
    enterprise = models.CharField(db_column='Enterprise', max_length=255, blank=True, null=True)
    scancode = models.CharField(db_column='ScanCode', max_length=255, blank=True, null=True)
    docum = models.CharField(db_column='Docum', max_length=255, blank=True, null=True)
    pharmgroup = models.CharField(db_column='PharmGroup', max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rls'


class Source(models.Model):
    source_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'source'


class Task(models.Model):
    id_task = models.BigAutoField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='username', null=True)
    task_back = models.CharField(max_length=150, blank=True, null=True)
    source_id = models.ForeignKey('Source', on_delete=models.CASCADE, db_column='source_id')
    query_text = models.CharField(max_length=45, blank=True, null=True)
    query_time = models.DateTimeField(blank=True, auto_now=True)
    date_start = models.DateField(blank=True)
    date_end = models.DateField(blank=True)

    class Meta:
        managed = True
        db_table = 'task'


