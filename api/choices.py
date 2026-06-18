from django.db import models

class StatusChoices(models.TextChoices):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"