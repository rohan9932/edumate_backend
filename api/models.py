from django.db import models
from django.contrib.auth.models import AbstractUser
from django_softdelete.models import SoftDeleteModel
from api.choices import StatusChoices
import uuid

# Create your models here.
class LogDetailsModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AppUserModel(SoftDeleteModel, AbstractUser):
    email = models.EmailField(max_length=254, unique=False)
    phone_number = models.CharField(max_length=15)

    #added for bypassing checkerror in django
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                condition=models.Q(is_deleted=False),
                name='unique_active_email'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.username: # setting username if not set (unique)
            self.username = f"user_{uuid.uuid4()}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False # for jwt block of soft-deleted users
        super().delete(*args, **kwargs) # triggers soft_delete()

    def __str__(self): 
        return self.email


class AppUserProfileModel(SoftDeleteModel, LogDetailsModel):
    major = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    # will add image field later
    cgpa = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    total_sem = models.IntegerField(null=True, blank=True)
    curr_sem = models.IntegerField(null=True, blank=True)
    total_credits = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    app_user = models.ForeignKey(AppUserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.app_user.email


## Tasks
class TaskModel(SoftDeleteModel, LogDetailsModel):
    class TypeChoices(models.TextChoices):
        WORK = "Work"
        PERSONAL = "Personal"
        ACADEMIC = "Academic"

    class PriorityChoices(models.TextChoices):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
    
    name = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    type = models.CharField(choices=TypeChoices.choices, max_length=10)
    status = models.CharField(choices=StatusChoices.choices, max_length=15)
    priority = models.CharField(choices=PriorityChoices.choices, max_length=10)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class RoutineCellModel(SoftDeleteModel, LogDetailsModel):
    class DayChoices(models.TextChoices):
        SUNDAY = "SUN"
        MONDAY = "MON"
        TUESDAY = "TUE"
        WEDNESDAY = "WED"
        THURSDAY = "THU"

    day = models.CharField(choices=DayChoices.choices, max_length=3)
    time = models.TimeField()
    course_title = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.course_title} at {self.day} {self.time}"


## Course Elements
class CourseModel(SoftDeleteModel, LogDetailsModel):
    course_no = models.CharField(max_length=15)
    title = models.CharField(max_length=100)
    semester = models.IntegerField()
    faculty_name = models.CharField(max_length=100, blank=True, null=True)
    classroom_link = models.CharField(max_length=255, blank=True, null=True)
    credit = models.DecimalField(decimal_places=2, max_digits=3)

    def __str__(self):
        return self.course_no


class AssignmentModel(SoftDeleteModel, LogDetailsModel):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    status = models.TextField(choices=StatusChoices.choices)
    due_date = models.DateField(blank=True, null=True)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class DueStudyModel(SoftDeleteModel, LogDetailsModel):
    topic_name = models.CharField(max_length=255)
    due_date = models.DateField(blank=True, null=True)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.topic_name


class ExamModel(SoftDeleteModel, LogDetailsModel):
    name = models.CharField(max_length=20)
    syllabus = models.TextField(blank=True, null=True)
    date = models.DateField()
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.course.title}"


class ResourcesModel(SoftDeleteModel, LogDetailsModel):
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=255)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.course.title}"