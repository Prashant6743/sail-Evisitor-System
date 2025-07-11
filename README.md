# Django Visitor Pass & ID Card System

## Overview
This project is a Django-based Visitor Pass Management System with the following features:
- Visitor gate pass application and approval workflow
- Admin dashboard for managing applications
- Unique ID card generation for each approved visitor
- Downloadable and verifiable digital ID cards with QR code authentication
- User authentication and role-based access

## Features
- **User Registration & Login**: Users can register, log in, and apply for a visitor pass.
- **Admin Panel**: Admin can view, approve, or reject applications and see visitor details.
- **ID Card Generation**: Upon approval, a digital visitor ID card is generated.
- **QR Code Verification**: Each ID card contains a QR code with a verification URL encoding the visitor's name and unique ID.
- **Downloadable ID Card**: Users can view and download their ID card as an image.

## Quick Start
1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run migrations**
   ```bash
   python manage.py migrate
   ```
4. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```
5. **Start the server**
   ```bash
   python manage.py runserver
   ```
6. **Access the site**
   - User: Register and log in to submit applications
   - Admin: Log in at `/dashboard/admin/` (default: username `admin`, password `admin`)

## User & Visitor ID Structure
- **User**: Primary key is Django's default user ID.
- **Visitor**: Primary key is `application_id` in the format `YEARBSL###` (e.g., `2025BSL001`).

## QR Code Functionality
- Each ID card has a QR code that encodes a verification URL:
  ```
  /verify/?name=<first>_<last>&id=<application_id>
  ```
- Scanning the QR can be used to implement visitor authentication/verification.

## File Structure
- `myproject/myapp/models.py` — Models for users and visitor passes
- `myproject/myapp/views.py` — Views for user, admin, and ID card logic
- `myproject/templates/` — HTML templates for all pages, including `id_card.html`
- `requirements.txt` — Python dependencies

## Default Credentials
- **Admin**: `admin` / `admin`
- **Test User**: `root` / `root`, `test2` / `root2`

## License
MIT

---
For help, contact the project maintainer.
