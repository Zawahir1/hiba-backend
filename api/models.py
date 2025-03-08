from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


class User(AbstractUser):
    ROLE_CHOICES = (
        ('therapist', 'Therapist'),
        ('user', 'User'),
    )
    phone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    therapist_expertise = models.CharField(max_length=300, null=True, blank=True)
    therapist_experience = models.IntegerField(null=True, blank=True)
    therapist_description = RichTextField()
    therapist_img = models.ImageField(upload_to="therapists/", null=True, blank=True)
    therapist_popUp = models.ImageField(upload_to="therapists/", null=True, blank=True)
    therapist_fee = models.IntegerField(null=True, blank=True)

class BlogsCategories(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    img = models.ImageField(upload_to="categories/", null=True, blank=True)

class Blogs(models.Model):
    category = models.ForeignKey(BlogsCategories, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
class BlogImages(models.Model):
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="blogs/")
    
class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Bookings(models.Model):
    CHOICE = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )
    PAYMENT_CHOICE = (
        ("online", "Online"),
        ("physical", "Physical"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient')
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapist')
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=CHOICE, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICE, default='physical')
    paid = models.BooleanField(default=False)
    receipt = models.ImageField(upload_to="receipts/", null=True, blank=True)
    

class Calculators(models.Model):
    name = models.CharField(max_length=500, unique=True)
    desc = models.CharField(max_length=1000)
    sub_desc = models.CharField(max_length=1000)
    caution = models.CharField(max_length=1000)
    scoring_name = models.CharField(max_length=100)
    leveling_name = models.CharField(max_length=100)
    calculation_para = models.TextField()
    result_line = models.CharField(max_length=100)
    img = models.ImageField(upload_to="calculators/", null=True, blank=True)
    
class CalculatorQuestions(models.Model):
    calculator = models.ForeignKey(Calculators, on_delete=models.CASCADE, related_name="calculator_questions")
    question = models.CharField(max_length=200, null=True, blank=True)
    option1 = models.CharField(max_length=200, null=True, blank=True)
    option2 = models.CharField(max_length=200, null=True, blank=True)
    option3 = models.CharField(max_length=200, null=True, blank=True)
    option4 = models.CharField(max_length=200, null=True, blank=True)

class CalculatorResults(models.Model):
    calculator = models.ForeignKey(Calculators, on_delete=models.CASCADE, related_name="calculator_results")
    min = models.IntegerField()
    max = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=200)
    
class CalculatorScores(models.Model):
    calculator = models.ForeignKey(Calculators, on_delete=models.CASCADE, related_name="user_calculator_score")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
