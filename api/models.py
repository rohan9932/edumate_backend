from django.db import models
from django.contrib.auth.models import AbstractUser
from django_softdelete.models import SoftDeleteModel
import uuid

# Create your models here.
class AppUser(SoftDeleteModel, AbstractUser):
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
        if not self.username:
            self.username = f"user_{uuid.uuid4()}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False # for jwt block of soft-deleted users
        super().delete(*args, **kwargs) # triggers soft_delete()

    def __str__(self): 
        return self.email
