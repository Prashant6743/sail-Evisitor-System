from django.shortcuts import render, redirect
from .forms import StudentForm
from .models import Student
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import openpyxl
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import openpyxl
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
import json
import base64
from PIL import Image
import io
import re


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
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import openpyxl
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse

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
    tracking_id = request.GET.get('tracking_id', '').strip()
    name = request.GET.get('name', '').strip()
    purpose = request.GET.get('purpose', '').strip()
    if tracking_id:
        apps = apps.filter(application_id__icontains=tracking_id)
    if name:
        name_parts = name.split()
        for part in name_parts:
            apps = apps.filter(
                models.Q(first_name__icontains=part) | models.Q(last_name__icontains=part)
            )
    if purpose:
        apps = apps.filter(purpose__icontains=purpose)
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
    # Rejected visitors: rejected and from_date >= today
    rejected_visitors = GatePass.objects.filter(status='rejected').order_by('-from_date')
    return render(request, "admin_dashboard.html", {
        'applications': apps,
        'stats': stats,
        'from_date': from_date,
        'to_date': to_date,
        'upcoming_visitors': upcoming_visitors,
        'pending_visitors': pending_visitors,
        'rejected_visitors': rejected_visitors,
    })

def verify_panel(request):
    return render(request, 'verify_panel.html')

@csrf_exempt
def verify_api(request):
    try:
        if request.method == 'POST':
            # Handle image upload
            try:
                data = json.loads(request.body)
                image_data = data.get('image')
                
                if not image_data:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No image data provided'
                    })

                # Extract base64 data
                if ',' in image_data:
                    image_data = image_data.split(',')[1]

                # Convert base64 to image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Here you would process the image with ZXing
                # For now, we'll just look for a pattern in the image name or metadata
                # You should replace this with actual QR code processing
                
                # Extract application ID from the filename or metadata
                application_id = None
                if 'name' in data:
                    match = re.search(r'(\d{4}[A-Z]{3}\d{3})', data['name'])
                    if match:
                        application_id = match.group(1)
                
                if not application_id:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Could not detect a valid QR code in the image'
                    })

            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON data'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error processing image: {str(e)}'
                })
        else:
            # Handle GET request (manual ID input or QR scan)
            application_id = request.GET.get('application_id')

        if not application_id:
            return JsonResponse({
                'status': 'error',
                'message': 'No application ID provided'
            })

        # Clean up the application ID
        application_id = application_id.strip().upper()
        
        # Validate application ID format (e.g., 2024BSL001)
        if not re.match(r'^\d{4}[A-Z]{3}\d{3}$', application_id):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid application ID format'
            })

        try:
            gatepass = GatePass.objects.get(application_id=application_id)
            
            # Check if the gate pass is approved and not expired
            valid_until = gatepass.from_date + timedelta(days=gatepass.duration)
            is_valid = (
                gatepass.status == 'approved' and 
                valid_until >= timezone.now().date()
            )
            
            if is_valid:
                return JsonResponse({
                    'status': 'success',
                    'gatepass': {
                        'first_name': gatepass.first_name,
                        'last_name': gatepass.last_name,
                        'application_id': gatepass.application_id,
                        'visiting_department': gatepass.visiting_department,
                        'from_date': gatepass.from_date.strftime('%Y-%m-%d'),
                        'valid_until': valid_until.strftime('%Y-%m-%d')
                    }
                })
            else:
                status_message = 'Gate pass is '
                if gatepass.status != 'approved':
                    status_message += 'not approved'
                elif valid_until < timezone.now().date():
                    status_message += 'expired'
                else:
                    status_message += 'invalid'
                
                return JsonResponse({
                    'status': 'error',
                    'message': status_message
                })
                
        except GatePass.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Gate pass not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error verifying gate pass: {str(e)}'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
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

def admin_reject_application(request, app_id):
    from django.shortcuts import get_object_or_404, redirect
    if not request.session.get('is_admin_authenticated'):
        return redirect('admin_login')
    if request.method == 'POST':
        app = get_object_or_404(GatePass, id=app_id)
        app.status = 'rejected'
        app.save()
    return redirect('admin_dashboard')

def applications_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    applications = GatePass.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, "applications.html", {"applications": applications})

def id_card_view(request, app_id):
    # Only allow if user owns the application and it's approved
    try:
        gatepass = GatePass.objects.get(id=app_id, user=request.user, status='approved')
    except GatePass.DoesNotExist:
        return HttpResponseForbidden('Not allowed')
    html = render_to_string('id_card.html', {'gatepass': gatepass})
    return HttpResponse(html)

