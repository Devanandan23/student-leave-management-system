from django.shortcuts import render,redirect
from django.http import HttpResponse
from . import models
from django.contrib import messages
from .models import LeaveApplication
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
def index(request):
    return render(request,'index.html')

def registration(request):
    if request.method=='POST':
        username = request.POST.get("username")
        studentid = request.POST.get("studentid")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        department = request.POST.get("department")
        phone = request.POST.get("phone")
        semester = request.POST.get("semester")
        image = request.FILES.get("image")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("registration")



        if models.student.objects.filter(email=email).exists():
           return HttpResponse("<script> alert('email alredy existed');window.location.href='/registeration/';</script>")
                               
        else:
            user=models.student(username=username,studentid=studentid,email=email,password=password,department=department,phone=phone,semester=semester,image=image)
            user.save()
            return HttpResponse("<script> alert('Registered sucessfully');window.location.href='/login/';</script>")
    return render(request,'registration.html')  


def login(request):
    if request.method=='POST':
         email=request.POST.get("email")
         password=request.POST.get("password")
         try:
            user=models.student.objects.get(email=email)
            if user.password==password:
                request.session['email']=user.email
                return redirect('home')
            return HttpResponse('<script>alert("invalid password");window.history.back();</script>')
         except models.student.DoesNotExist:
            return HttpResponse('<script>alert("invalid email");window.history.back();</script>')
    return render(request,'login.html')


def profile(request):
    user=models.student.objects.get(email=request.session.get('email'))
    return render(request,'profile.html',{'user':user})

def logout(request):
    request.session.flush()
    return redirect('index')

from django.shortcuts import render, redirect
from django.db.models import Q
from . import models

from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils.timezone import now
from . import models

from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q
from . import models

from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q
from .models import student, LeaveApplication, Notifications


def home(request):
    if 'email' not in request.session:
        return redirect('login')

    email = request.session['email']

    try:
        user = student.objects.get(email=email)
    except student.DoesNotExist:
        # Clean up invalid session
        if 'email' in request.session:
            del request.session['email']
        return redirect('login')

    now = timezone.now()
    current_year = now.year

    # ── Unread notifications count (for badge + section) ──
    unread_count = Notifications.objects.filter(
        student=user,
        is_read=False
    ).count()

    # ── Personal leave quota logic (from leave_count field) ──
    if user.leave_count is None:
        personal_taken = 0
    else:
        if user.last_leave_year is None or user.last_leave_year != current_year:
            personal_taken = 0
        else:
            personal_taken = user.leave_count

    TOTAL_ALLOWED_PERSONAL = 10
    remaining_personal = max(TOTAL_ALLOWED_PERSONAL - personal_taken, 0)

    # ── Approved leaves this year breakdown (for display only) ──
    approved_this_year = LeaveApplication.objects.filter(
        student=user,
        approved=True,
        start_date__year=current_year
    )

    medical_taken   = approved_this_year.filter(leave_type__iexact="medical").count()
    emergency_taken = approved_this_year.filter(leave_type__iexact="emergency").count()
    other_taken     = approved_this_year.filter(leave_type__iexact="others").count()   # adjust if you use "Other" or "others"

    # Note: personal_taken is taken from leave_count, not from counting applications
    #       so we don't do approved_this_year.filter(leave_type__iexact="personal").count() here

    context = {
        'user': user,
        'unread_count': unread_count,
        'notifications': Notifications.objects.filter(student=user).order_by('-created_at')[:10],
        'personal_taken': personal_taken,
        'remaining_personal': remaining_personal,
        'medical_taken': medical_taken,
        'emergency_taken': emergency_taken,
        'other_taken': other_taken,
        'current_year': current_year,
        'total_allowed_personal': 10,
    }

    return render(request, 'home.html', context)
from django.http import JsonResponse
def mark_notification_read(request, notification_id):
    if 'email' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    try:
        student_obj = student.objects.get(email=request.session['email'])
        notification = get_object_or_404(Notifications, id=notification_id, student=student_obj)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except (student.DoesNotExist, Notifications.DoesNotExist):
        return JsonResponse({'error': 'Not found'}, status=404)
def editprofile(request):
    if 'email' in request.session:
        user=models.student.objects.get(email=request.session.get('email'))
        if request.method=='POST':
            user.username = request.POST.get("username")
            user.studentid = request.POST.get("studentid")
            user.email = request.POST.get("email")
            user.password = request.POST.get("password")
            user.department = request.POST.get("department")
            user.phone = request.POST.get("phone")
            user.semester = request.POST.get("semester")
            if 'image' in request.FILES:
                user.image = request.FILES.get("image")
            user.save()
            return redirect('profile')
        return render(request,'editprofile.html',{'user':user})
    return redirect('login')


def adminlogin(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username=='admin' and password=='admin':
            return redirect('adminhome2')
        return HttpResponse('<script>alert("invalid username or password");window.location.href="/adminlogin/";</script>')
    return render(request,'adminlogin.html')

def adminhome2(request):
    return render(request,'adminhome2.html')

from django.db.models import Q
from django.shortcuts import render
from . import models

def adminhome_software_dev(request):

    # Get all students from Software Development department
    software_students = models.student.objects.filter(
        department='Software Development'
    )

    # Pending leave count
    pending_count = models.LeaveApplication.objects.filter(
        approved=False,
        rejected=False,
        student__in=software_students
    ).count()

    # Approved leave count
    approved_count = models.LeaveApplication.objects.filter(
        approved=True,
        student__in=software_students
    ).count()

    # Rejected leave count
    rejected_count = models.LeaveApplication.objects.filter(
        rejected=True,
        student__in=software_students
    ).count()

    context = {
        "count": pending_count,   # badge
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
    }

    return render(request, 'adminhome_software_dev.html', context)

def adminhome_multimedia(request):

    # Get all students from Software Development department
    software_students = models.student.objects.filter(
        department='MultiMedia'
    )

    # Pending leave count
    pending_count = models.LeaveApplication.objects.filter(
        approved=False,
        rejected=False,
        student__in=software_students
    ).count()

    # Approved leave count
    approved_count = models.LeaveApplication.objects.filter(
        approved=True,
        student__in=software_students
    ).count()

    # Rejected leave count
    rejected_count = models.LeaveApplication.objects.filter(
        rejected=True,
        student__in=software_students
    ).count()

    context = {
        "count": pending_count,   # badge
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
    }

    return render(request, 'adminhome_mm.html', context)

def adminhome_ft(request):

    # Get all students from Software Development department
    software_students = models.student.objects.filter(
        department='Fashion Technology'
    )

    # Pending leave count
    pending_count = models.LeaveApplication.objects.filter(
        approved=False,
        rejected=False,
        student__in=software_students
    ).count()

    # Approved leave count
    approved_count = models.LeaveApplication.objects.filter(
        approved=True,
        student__in=software_students
    ).count()

    # Rejected leave count
    rejected_count = models.LeaveApplication.objects.filter(
        rejected=True,
        student__in=software_students
    ).count()

    context = {
        "count": pending_count,   # badge
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
    }

    return render(request, 'adminhome_ft.html', context)

def adminhome_at(request):

    # Get all students from Software Development department
    software_students = models.student.objects.filter(
        department='Accounting and Taxation'
    )

    # Pending leave count
    pending_count = models.LeaveApplication.objects.filter(
        approved=False,
        rejected=False,
        student__in=software_students
    ).count()

    # Approved leave count
    approved_count = models.LeaveApplication.objects.filter(
        approved=True,
        student__in=software_students
    ).count()

    # Rejected leave count
    rejected_count = models.LeaveApplication.objects.filter(
        rejected=True,
        student__in=software_students
    ).count()

    context = {
        "count": pending_count,   # badge
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
    }

    return render(request, 'adminhome_at.html', context)



def userlist(request):
    users=models.student.objects.all()
    return render(request,'userlist.html',{'users':users})

def userlist_sd(request):
    users=models.student.objects.filter(department='Software Development')
    return render(request,'userlist_sd.html',{'users':users})

def userlist_mm(request):
    users=models.student.objects.filter(department='MultiMedia')
    return render(request,'userlist_mm.html',{'users':users})

def userlist_ft(request):
    users=models.student.objects.filter(department='Fashion Technology')
    return render(request,'userlist_ft.html',{'users':users})

def userlist_at(request):
    users=models.student.objects.filter(department='Accounting and Taxation')
    return render(request,'userlist_at.html',{'users':users})



def leavelist(request):
    leave=LeaveApplication.objects.all()
    return render(request,'leavelist.html',{'leave':leave})


def leavelist_ft(request):
    leaves = LeaveApplication.objects.filter(student__department="Fashion Technology")
    return render(request, "leavelist_ft.html", {"leaves": leaves})

def leavelist_sd(request):
    leaves = LeaveApplication.objects.filter(student__department="Software Development")
    return render(request, "leavelist_sd.html", {"leaves": leaves})

def leavelist_mm(request):
    leaves = LeaveApplication.objects.filter(student__department="MultiMedia")
    return render(request, "leavelist_mm.html", {"leaves": leaves})

def leavelist_at(request):
    leaves = LeaveApplication.objects.filter(student__department="Accounting and Taxation")
    return render(request, "leavelist_at.html", {"leaves": leaves})












def deleteuser(request, id):
    users = models.student.objects.get(id=id)
    users.delete()
    return redirect('userlist')

from django.shortcuts import render, redirect
from django.utils import timezone
from . import models
from .models import LeaveApplication

from django.utils import timezone
from .models import LeaveApplication, student

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime
from .models import student, LeaveApplication


def apply_leave(request):
    if request.method == "POST":
        username = request.POST.get("username")          # actually not used — kept for form compatibility
        leave_type = request.POST.get("leave_type")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")
        reason = request.POST.get("reason")

        # Get the actual student from session (more secure)
        try:
            student_obj = student.objects.get(email=request.session.get('email'))
        except student.DoesNotExist:
            return render(request, "apply_leave.html", {
                "error": "Student account not found. Please login again.",
                "user": None
            })

        now = timezone.now()

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return render(request, "apply_leave.html", {
                "error": "Invalid date format.",
                "user": student_obj
            })

        if end_date < start_date:
            return render(request, "apply_leave.html", {
                "error": "End date cannot be before start date.",
                "user": student_obj
            })

        # ── Only personal leave has yearly limit ──
        if leave_type.lower() == "personal":
            # Initialize if somehow None
            if student_obj.leave_count is None:
                student_obj.leave_count = 0
            if student_obj.last_leave_year is None:
                student_obj.last_leave_year = now.year

            # Reset for new year
            if student_obj.last_leave_year != now.year:
                student_obj.leave_count = 0
                student_obj.last_leave_year = now.year

            # Enforce limit
            if student_obj.leave_count >= 10:
                return render(request, "apply_leave.html", {
                    "error": "You have reached the maximum personal leave limit (10) for this year.",
                    "user": student_obj
                })

            # Count it
            student_obj.leave_count += 1
            student_obj.save()

        # ── All other types (Emergency, Medical, Others) → no limit check, no count increment ──

        # Create the leave application
        LeaveApplication.objects.create(
            student=student_obj,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            dept=student_obj.department,
            # approved = False   ← already default, no need to set
        )

        return redirect("home")

    # ── GET request ──
    try:
        user = student.objects.get(email=request.session.get("email"))
    except student.DoesNotExist:
        return render(request, "apply_leave.html", {
            "error": "Please login to apply for leave.",
            "user": None
        })

    return render(request, "apply_leave.html", {"user": user})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import LeaveApplication, student

def cancel_leave(request, leave_id):
    if request.method != "POST":
        # Optional: you can render a confirmation page on GET
        # For simplicity here we'll handle via POST only (safer for deletion)
        messages.error(request, "Invalid request method.")
        return redirect("home")  # or wherever you list leaves

    # Get the leave application
    leave = get_object_or_404(LeaveApplication, id=leave_id)

    # Security: only allow the student to cancel their own leave
    try:
        current_student = student.objects.get(email=request.session.get('email'))
    except student.DoesNotExist:
        messages.error(request, "Session expired. Please login again.")
        return redirect("login")  # adjust to your login name

    if leave.student != current_student:
        messages.error(request, "You are not authorized to cancel this leave.")
        return redirect("home")


    now = timezone.now()

    # If it was a Personal leave → restore the count
    if leave.leave_type.lower() == "personal":
        student_obj = leave.student
        
        # Make sure counters are initialized
        if student_obj.leave_count is None:
            student_obj.leave_count = 0
        if student_obj.last_leave_year is None:
            student_obj.last_leave_year = now.year

        # Only decrease if the leave was counted in current year
        if student_obj.last_leave_year == now.year and student_obj.leave_count > 0:
            student_obj.leave_count -= 1
            student_obj.save()
            messages.info(request, "Personal leave count restored (+1).")
        else:
            # Edge case: leave was from previous year or count already 0
            messages.info(request, "No personal leave count was deducted (different year or already zero).")

    # Delete the leave application
    leave.delete()

    messages.success(request, "Your leave application has been successfully cancelled.")
    return redirect("home")  # or better: redirect to a "my leaves" page
def leavelist(request):
    leaves = LeaveApplication.objects.all().order_by('student__department', '-applied_on')
    return render(request, "leavelist.html", {
        "leaves": leaves
    })


def deleteleave(request, id):
    leave = models.LeaveApplication.objects.get(id=id)
    leave.delete()
    return redirect('userlist') 


from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import LeaveApplication, Notifications

def approve(request, id):
    leave = get_object_or_404(LeaveApplication, pk=id)

    # Prevent double approval / race condition
    if leave.approved or leave.rejected:
        return redirect('leavelist')

    leave.approved = True
    leave.rejected = False
    leave.save()

    # Create notification
    Notifications.objects.create(
        student=leave.student,
        leave=leave,
        message=(
            f"Your {leave.leave_type} leave request "
            f"({leave.start_date.strftime('%d %b')} – {leave.end_date.strftime('%d %b %Y')}) "
            f"has been approved."
        )
    )

    return redirect('leavelist')


def rejected(request, id):
    leave = get_object_or_404(LeaveApplication, pk=id)

    if leave.approved or leave.rejected:
        return redirect('leavelist')

    now = timezone.now()

    # Restore personal leave count ONLY if applicable
    if leave.leave_type.lower() == "personal":
        student_obj = leave.student

        # Safety initialization
        if student_obj.leave_count is None:
            student_obj.leave_count = 0
        if student_obj.last_leave_year is None:
            student_obj.last_leave_year = now.year

        # Only restore if it was counted this year
        if student_obj.last_leave_year == now.year and student_obj.leave_count > 0:
            student_obj.leave_count -= 1
            student_obj.save()

    leave.approved = False
    leave.rejected = True
    leave.save()

    # Create notification
    Notifications.objects.create(
        student=leave.student,
        leave=leave,
        message=(
            f"Your {leave.leave_type} leave request "
            f"({leave.start_date.strftime('%d %b')} – {leave.end_date.strftime('%d %b %Y')}) "
            f"has been rejected."
        )
    )

    return redirect('leavelist')
def userleave(request):
    email=request.session['email']
    user=models.student.objects.get(email=email)
    leaves=models.LeaveApplication.objects.filter(student=user)
    return render(request,'userleavelist.html', {
        "leaves": leaves
    })

def admin_remark(request, leave_id):
    leave = get_object_or_404(LeaveApplication, id=leave_id)

    if request.method == "POST":
        remark = request.POST.get("admin_remark")
        leave.admin_remark = remark
        leave.save()
        return redirect('leavelist')  # change to your leave list URL name

    return render(request, 'admin_remark.html', {'leave': leave})


from django.shortcuts import render, redirect
from django.http import HttpResponse

def submitcertificate(request, id):
    # Fetch the specific leave application
    leave = models.LeaveApplication.objects.get(id=id)
    
    if request.method == "POST":
        certificate = request.FILES.get("certificate")
        if certificate:
            # Create the record in MedCerts
            models.MedCerts.objects.create(leave=leave, certificate=certificate)
            leave.medsub = True
            leave.save()
            return HttpResponse("<script>alert('Submitted successfully'); window.location.href='/userleave/';</script>")
        else:
            return HttpResponse("<script>alert('Please select a file'); window.history.back();</script>")

    return render(request, 'submitcertificate.html', {'leave': leave})


def medlist(request):
    users=models.MedCerts.objects.all()
    return render(request,'medlist.html',{'users':users})

def medlist_ft(request):
    users = models.MedCerts.objects.filter(leave__student__department="Fashion Technology")
    return render(request, "medlist_ft.html", {"users": users})

def medlist_sd(request):
    users = models.MedCerts.objects.filter(leave__student__department="Software Development")
    return render(request, "medlist_sd.html", {"users": users})

def medlist_mm(request):
    users = models.MedCerts.objects.filter(leave__student__department="MultiMedia")
    return render(request, "medlist_mm.html", {"users": users})

def medlist_at(request):
    users = models.MedCerts.objects.filter(leave__student__department="Accounting and Taxation")
    return render(request, "medlist_at.html", {"users": users})

from django.shortcuts import render
from .models import LeaveApplication

from django.shortcuts import render
from django.utils.timezone import now
from .models import LeaveApplication

def user_leave_summary(request):
    if 'email' in request.session:
        user=models.student.objects.get(email=request.session.get('email'))
        student = user   # adjust if your relation is different
        current_year = now().year

    # Approved leaves for this year only
    leaves = LeaveApplication.objects.filter(
        student=student,
        approved=True,
        start_date__year=current_year
    )

    total_taken = leaves.count()

    medical_taken = leaves.filter(medsub=True).count()
    other_taken = leaves.filter(medsub=False).count()

    TOTAL_ALLOWED = 10
    remaining = max(TOTAL_ALLOWED - total_taken, 0)

    context = {
        "year": current_year,
        "total_taken": total_taken,
        "remaining": remaining,
        "medical_taken": medical_taken,
        "other_taken": other_taken,
        "total_allowed": TOTAL_ALLOWED,
    }

    return render(request, "summary.html", context)

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import student
import uuid

# Temporary token storage (for demo)
reset_tokens = {}

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = student.objects.get(email=email)
            token = str(uuid.uuid4())
            reset_tokens[token] = user.email

            reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"

            send_mail(
                "Password Reset",
                f"Click this link to reset your password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
            )

            return render(request, "email_sent.html")

        except student.DoesNotExist:
            return render(request, "forgot_password.html", {"error": "Email not found"})

    return render(request, "forgot_password.html")


def reset_password(request, token):
    if token not in reset_tokens:
        return render(request, "invalid_token.html")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            email = reset_tokens[token]
            user = student.objects.get(email=email)

            user.password = password   # ⚠️ Not secure (see note below)
            user.save()

            del reset_tokens[token]
            return redirect("login")

        else:
            return render(request, "reset_password.html", {"error": "Passwords do not match"})

    return render(request, "reset_password.html")



# views.py
from django.http import HttpResponse
from datetime import datetime
from .ai_report import generate_leave_report_pdf

from datetime import datetime
from django.http import HttpResponse
from .generate_leave_report_pdf import generate_leave_report_pdf

def my_leave_report_pdf_view(request):
    email = request.session.get("email")
    if not email:
        return HttpResponse("You must be logged in as a student.", status=403)

    start = request.GET.get("start")
    end   = request.GET.get("end")

    try:
        if start:
            start = datetime.strptime(start, "%Y-%m-%d").date()
        else:
            start = None
        if end:
            end = datetime.strptime(end, "%Y-%m-%d").date()
        else:
            end = None
    except ValueError:
        return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)

    pdf_buf = generate_leave_report_pdf(email, start, end)
    response = HttpResponse(pdf_buf.read(), content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=leave_report_{email}.pdf"
    return response