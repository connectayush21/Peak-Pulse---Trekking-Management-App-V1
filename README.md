# Peak-Pulse---Trekking-Management-App-V1

Peak Pulse is a Flask-based trekking management web application built for organizing and managing trekking expeditions, bookings, staff assignments, and user registrations. It supports different roles, including trekkers, staff members, and administrators, making it suitable for an adventure travel or tourism business.

## Overview

This project provides a complete workflow for a trekking company:

- Tourists can sign up and browse available treks
- Trekkers can view trek details and make bookings
- Staff can be assigned to treks and manage participant lists
- Admins can approve staff, manage users, update trek information, and view bookings
- Booking and trekking data are stored in a SQLite database using SQLAlchemy

The app is structured around a role-based dashboard system, with a clean frontend built with Flask templates and Bootstrap styling.

## Site Preview 

1. Admin Dashboard 
<img width="2628" height="3412" alt="Screenshot_21-9-2026_3542_127 0 0 1" src="https://github.com/user-attachments/assets/bf3c4d0f-b2f9-4dec-bbde-7fdd40783dc1" />

2. Admin Trek Manager
<img width="2628" height="2550" alt="Screenshot_21-9-2026_360_127 0 0 1" src="https://github.com/user-attachments/assets/3e368b06-d471-43b1-9127-8930974b8b35" >

3. Staff(Guide) Dashboard
<img width="2628" height="1565" alt="Screenshot_21-9-2026_328_127 0 0 1" src="https://github.com/user-attachments/assets/f90ed3a7-ab6d-43f1-9801-fe4d4f621c3a" />

4. User Dashboard 
<img width="2628" height="3149" alt="Screenshot_21-9-2026_338_127 0 0 1" src="https://github.com/user-attachments/assets/0542fd2b-caf3-4546-ba00-9f2cf99019ba" />

5. User Booking 
<img width="1763" height="1456" alt="Screenshot_16-7-2026_195833_127 0 0 1" src="https://github.com/user-attachments/assets/3c851eee-6ab1-4016-99d8-4f979c22f5b3" />

## Key Features

### User Side
- User registration and login
- Trek discovery by search and filters
- Trek details page with route and pricing information
- Booking creation and cancellation
- User dashboard showing active bookings and trekking history
- Profile management

### Staff Side
- Staff dashboard overview
- Trek assignment and participant management
- Review of bookings tied to assigned treks
- Tracking trek participation and trip logistics

### Admin Side
- Admin dashboard statistics
- Staff approval workflow
- User and staff management
- Trek creation, editing, and deletion
- Booking log and operational monitoring
- Search and filtering tools for users and treks

## Technology Stack

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5
- Jinja2 Templates

## Project Structure
'''
Peak-Pulse---Trekking-Management-App-V1/
├── app.py
├── routes.py
├── models.py
├── database.db
├── requirements.txt
├── test_app.py
├── static/
│   ├── css/
├── templates/
│   ├── admin_bookings.html
│   ├── admin_dashboard.html
│   ├── admin_edit_trek.html
│   ├── admin_treks.html
│   ├── admin_users.html
│   ├── base.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   ├── staff_dashboard.html
│   ├── staff_participants.html
│   ├── user_dashboard.html
│   └── view_trek.html
└── README.md
'''
## Roles in the App

### Trekkers
Users can:
- register as a trekker
- browse all available treks
- view details before booking
- manage their profiles and trip history

### Staff
Staff members can:
- access a staff dashboard
- view assigned trekking activities
- manage trek participants
- support trip operations

### Admin
Admins can:
- approve staff accounts
- manage all user activity and statuses
- add or edit trekking routes
- monitor bookings and trip performance

## Database Model / ER Diagram

<img width="2520" height="1368" alt="Blank diagram - Page 1" src="https://github.com/user-attachments/assets/3f029f97-13f6-4137-894d-c5d520184e4c" />

