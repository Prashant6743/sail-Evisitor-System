from django.shortcuts import render, redirect
from .forms import StudentForm
from .models import Student


def list_students(request):
    students = Student.objects.all()
    return render(request, 'students_list.html', {'students': students})

def success(request):
    return render(request, 'success.html')

def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to a success page (you can customize this)
    else:
        form = StudentForm()
    return render(request, 'register_student.html', {'form': form})


#manually added 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegisterForm

from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save extra profile fields
            from .models import Profile
            Profile.objects.create(
                user=user,
                designation=form.cleaned_data['designation'],
                company_name=form.cleaned_data['company_name'],
                mobile=form.cleaned_data['mobile'],
                sex=form.cleaned_data['sex'],
                aadhar_no=form.cleaned_data['aadhar_no'],
                age=form.cleaned_data['age'],
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def home_view(request):
    return render(request, "home.html")

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "dashboard.html")

from .models import Profile, GatePass
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import openpyxl
from django.http import HttpResponse

def gatepass_form_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={
        'designation': '',
        'company_name': '',
        'mobile': '',
        'sex': '',
        'aadhar_no': '',
        'age': 0
    })
    if request.method == "POST":
        from django.utils import timezone
        from datetime import timedelta
        purpose = request.POST.get('purpose','')
        from_date = request.POST.get('from_date','')
        recent = GatePass.objects.filter(
            user=request.user,
            purpose=purpose,
            from_date=from_date,
            submitted_at__gte=timezone.now() - timedelta(minutes=1)
        ).first()
        if recent:
            return redirect('applications')
        GatePass.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name',''),
            last_name=request.POST.get('last_name',''),
            company_name=request.POST.get('company_name',''),
            designation=request.POST.get('designation',''),
            aadhar_no=request.POST.get('aadhar_no',''),
            mobile=request.POST.get('mobile',''),
            email=request.POST.get('email',''),
            purpose=purpose,
            employee_email=request.POST.get('employee_email',''),
            from_date=from_date,
            duration=request.POST.get('duration',''),
            vehicle_available=request.POST.get('vehicle_available',''),
            visiting_department=request.POST.get('visiting_department',''),
        )
        return redirect('applications')
    return render(request, "gatepass_form.html", {"user": request.user, "profile": profile})

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            request.session['is_admin_authenticated'] = True
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin_login.html')

def admin_logout_view(request):
    request.session.pop('is_admin_authenticated', None)
    return redirect('admin_login')

def admin_dashboard_view(request):
    if not request.session.get('is_admin_authenticated'):
        return redirect('admin_login')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    export = request.GET.get('export')
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)
    # Stats
    daily = GatePass.objects.filter(from_date=today).count()
    weekly = GatePass.objects.filter(from_date__gte=week_ago).count()
    monthly = GatePass.objects.filter(from_date__gte=month_ago).count()
    stats = {'daily': daily, 'weekly': weekly, 'monthly': monthly}
    # Filtering
    apps = GatePass.objects.all()
    if from_date and to_date:
        apps = apps.filter(from_date__gte=from_date, from_date__lte=to_date)
    apps = apps.order_by('-from_date')
    # Excel export
    if export == 'excel' and from_date and to_date:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['First Name', 'Last Name', 'Purpose', 'Date', 'Status'])
        for app in apps:
            ws.append([app.first_name, app.last_name, app.purpose, str(app.from_date), getattr(app, 'status', 'pending')])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=visitors_{from_date}_to_{to_date}.xlsx'
        wb.save(response)
        return response
    # Upcoming visitors: approved and from_date >= today
    upcoming_visitors = GatePass.objects.filter(status='approved', from_date__gte=today).order_by('from_date')
    # Pending visitors: pending and from_date >= today
    pending_visitors = GatePass.objects.filter(status='pending', from_date__gte=today).order_by('from_date')
    return render(request, "admin_dashboard.html", {
        'applications': apps,
        'stats': stats,
        'from_date': from_date,
        'to_date': to_date,
        'upcoming_visitors': upcoming_visitors,
        'pending_visitors': pending_visitors,
    })

def admin_approve_application(request, app_id):
    from django.shortcuts import get_object_or_404, redirect
    if not request.session.get('is_admin_authenticated'):
        return redirect('admin_login')
    if request.method == 'POST':
        app = get_object_or_404(GatePass, id=app_id)
        app.status = 'approved'
        app.save()
    return redirect('admin_dashboard')

def applications_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    applications = GatePass.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, "applications.html", {"applications": applications})
