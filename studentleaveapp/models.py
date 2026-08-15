from django.db import models

# Create your models here.


class student(models.Model):
    username=models.CharField(max_length=100,null=True,blank=True)
    studentid=models.IntegerField()
    email=models.EmailField(max_length=100)
    password=models.CharField(max_length=100,null=True,blank=True)
    dchoices=[
        ('Fashion Technology','Fashion Technology'),
        ('Software Development','Software Development'),
        ('MultiMedia','MultiMedia'),
        ('Accounting and Taxation','Accounting and taxation'),
         
    ]
    department=models.CharField(max_length=50,choices=dchoices,null=True,blank=True)
    phone=models.IntegerField()
    semchoices=[
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ]
    semester=models.CharField(max_length=1,choices=semchoices,null=True,blank=True)
    image=models.ImageField(upload_to="profile_image/",null=True,blank=True)
    leave_count=models.IntegerField(null=True,blank=True)
    last_leave_year=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.username

class LeaveApplication(models.Model):
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    approved=models.BooleanField(default=False)
    rejected=models.BooleanField(default=False)
    admin_remark = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    hide=models.BooleanField(default=False)
    leave_count=models.IntegerField(default=0)
    dept = models.CharField(max_length=50,null=True,blank=True)
    medsub = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.student.username} - {self.leave_type}"
class Notifications(models.Model):
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    leave = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)          # ← new
    is_read = models.BooleanField(default=False)    # ← useful for UI

    class Meta:
        ordering = ['-created_at']
class MedCerts(models.Model):
    leave=models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    certificate=models.FileField(upload_to="certificate/",null=True,blank=True)

