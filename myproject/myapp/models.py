from django.db import models
from django.contrib.auth.models import User

# Create your models here.
import uuid
from django.db import models

class GatePass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    aadhar_no = models.CharField(max_length=12)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    purpose = models.CharField(max_length=200)
    employee_email = models.EmailField()
    from_date = models.DateField()
    duration = models.PositiveIntegerField()
    vehicle_available = models.CharField(max_length=10)
    visiting_department = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved')],
        default='pending'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.purpose} ({self.submitted_at:%Y-%m-%d})"
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    sex = models.CharField(max_length=10)
    aadhar_no = models.CharField(max_length=12)
    age = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    regno = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.regno})"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "regno": self.regno,
            "location": self.location,
            "college": self.college,
            "city": self.city,
            "email": self.email,
            "mobile": self.mobile,
        }
