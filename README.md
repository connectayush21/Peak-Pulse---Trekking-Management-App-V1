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

<img width="2481" height="1299" alt="Blank diagram - Page 1" src="https://github.com/user-attachments/assets/f65b8470-d491-4d6f-9800-19c1abb2d53c" />


## Main Website Sections



