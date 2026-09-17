from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Trek, Booking
from datetime import datetime
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('main.staff_dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('main.login'))
            
        if user.status == 'pending':
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('main.login'))
            
        if user.status == 'blacklisted':
            flash('Your account has been deactivated or blacklisted.', 'danger')
            return redirect(url_for('main.login'))
            
        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        name = request.form.get('name').strip()
        contact = request.form.get('contact').strip()
        role = request.form.get('role')
        
        if not username or not password or not name or not role:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('main.register'))
            
        if role not in ['trekker', 'staff']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('main.register'))
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username/Email is already registered.', 'danger')
            return redirect(url_for('main.register'))
            
        status = 'pending' if role == 'staff' else 'active'
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            name=name,
            contact_details=contact,
            status=status
        )
        db.session.add(new_user)
        db.session.commit()
        
        if role == 'staff':
            flash('Registration successful! Please wait for Admin approval before logging in.', 'success')
            return redirect(url_for('main.login'))
        else:
            login_user(new_user)
            flash('Registration successful! Welcome to the Trekking App.', 'success')
            return redirect(url_for('main.user_dashboard'))
            
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))

def require_role(role):
    if not current_user.is_authenticated or current_user.role != role:
        abort(403)

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    require_role('admin')
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(role='staff', status='pending').all()
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    
    trek_labels = []
    trek_booking_counts = []
    treks = Trek.query.all()
    for t in treks:
        booking_count = Booking.query.filter_by(trek_id=t.id).count()
        if booking_count > 0:
            trek_labels.append(t.name)
            trek_booking_counts.append(booking_count)
            
    difficulty_labels = ['Easy', 'Moderate', 'Hard']
    difficulty_counts = [
        Trek.query.filter_by(difficulty='Easy').count(),
        Trek.query.filter_by(difficulty='Moderate').count(),
        Trek.query.filter_by(difficulty='Hard').count()
    ]
    
    return render_template(
        'admin_dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings,
        pending_staff=pending_staff,
        all_bookings=all_bookings,
        trek_labels=trek_labels,
        trek_booking_counts=trek_booking_counts,
        difficulty_labels=difficulty_labels,
        difficulty_counts=difficulty_counts
    )

@main.route('/admin/staff/approve/<int:user_id>')
@login_required
def approve_staff(user_id):
    require_role('admin')
    staff = User.query.get_or_404(user_id)
    if staff.role == 'staff' and staff.status == 'pending':
        staff.status = 'approved'
        db.session.commit()
        flash(f'Staff {staff.name} approved successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    require_role('admin')
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        if search_query.isdigit():
            users = User.query.filter(
                or_(
                    User.id == int(search_query),
                    User.name.like(f'%{search_query}%'),
                    User.username.like(f'%{search_query}%')
                )
            ).all()
        else:
            users = User.query.filter(
                or_(
                    User.name.like(f'%{search_query}%'),
                    User.username.like(f'%{search_query}%')
                )
            ).all()
    else:
        users = User.query.all()
        
    return render_template('admin_users.html', users=users, search_query=search_query)

@main.route('/admin/user/toggle-status/<int:user_id>')
@login_required
def toggle_user_status(user_id):
    require_role('admin')
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot blacklist yourself!', 'danger')
        return redirect(url_for('main.admin_users'))
        
    if user.status in ['active', 'approved']:
        user.status = 'blacklisted'
        flash(f'User {user.name} has been blacklisted.', 'warning')
    else:
        user.status = 'approved' if user.role == 'staff' else 'active'
        flash(f'User {user.name} is now active.', 'success')
        
    db.session.commit()
    return redirect(url_for('main.admin_users'))

@main.route('/admin/treks', methods=['GET', 'POST'])
@login_required
def admin_treks():
    require_role('admin')
    
    if request.method == 'POST':
        name = request.form.get('name').strip()
        location = request.form.get('location').strip()
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        total_slots = int(request.form.get('total_slots'))
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        description = request.form.get('description').strip()
        price = float(request.form.get('price', 0))
        staff_id = request.form.get('staff_id')
        image_url = request.form.get('image_url', '').strip()


        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if start_date > end_date:
            flash('Start date cannot be after end date.', 'danger')
            return redirect(url_for('main.admin_treks'))
            
        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            total_slots=total_slots,
            available_slots=total_slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            price=price,
            image_url=image_url,
            status='Approved' if staff_id else 'Pending'
        )
        
        if staff_id:
            new_trek.staff_id = int(staff_id)
            
        db.session.add(new_trek)
        db.session.commit()
        flash('Trek route created successfully!', 'success')
        return redirect(url_for('main.admin_treks'))
        
    search_query = request.args.get('search', '').strip()
    if search_query:
        if search_query.isdigit():
            treks = Trek.query.filter(
                or_(
                    Trek.id == int(search_query),
                    Trek.name.like(f'%{search_query}%'),
                    Trek.location.like(f'%{search_query}%')
                )
            ).all()
        else:
            treks = Trek.query.filter(
                or_(
                    Trek.name.like(f'%{search_query}%'),
                    Trek.location.like(f'%{search_query}%')
                )
            ).all()
    else:
        treks = Trek.query.all()
        
    guides = User.query.filter_by(role='staff', status='approved').all()
    return render_template('admin_treks.html', treks=treks, guides=guides, search_query=search_query)

@main.route('/admin/trek/edit/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_trek(trek_id):
    require_role('admin')
    trek = Trek.query.get_or_404(trek_id)
    
    if request.method == 'POST':
        trek.name = request.form.get('name').strip()
        trek.location = request.form.get('location').strip()
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        
        old_total = trek.total_slots
        new_total = int(request.form.get('total_slots'))
        diff = new_total - old_total
        
        if trek.available_slots + diff < 0:
            flash('Cannot reduce total slots below currently booked slots.', 'danger')
            return redirect(url_for('main.admin_edit_trek', trek_id=trek.id))
            
        trek.total_slots = new_total
        trek.available_slots += diff
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        trek.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if trek.start_date > trek.end_date:
            flash('Start date cannot be after end date.', 'danger')
            return redirect(url_for('main.admin_edit_trek', trek_id=trek.id))
            
        trek.description = request.form.get('description').strip()
        trek.price = float(request.form.get('price', 0))
        
        staff_id = request.form.get('staff_id')
        if staff_id:
            trek.staff_id = int(staff_id)
            if trek.status == 'Pending':
                trek.status = 'Approved'
        else:
            trek.staff_id = None
            trek.status = 'Pending'
            
        db.session.commit()
        flash('Trek updated successfully!', 'success')
        return redirect(url_for('main.admin_treks'))
        
    guides = User.query.filter_by(role='staff', status='approved').all()
    return render_template('admin_edit_trek.html', trek=trek, guides=guides)

@main.route('/admin/trek/delete/<int:trek_id>')
@login_required
def admin_delete_trek(trek_id):
    require_role('admin')
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted successfully.', 'info')
    return redirect(url_for('main.admin_treks'))

@main.route('/admin/bookings')
@login_required
def admin_bookings():
    require_role('admin')
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin_bookings.html', bookings=bookings)

@main.route('/staff/dashboard')
@login_required
def staff_dashboard():
    require_role('staff')
    assigned_treks = Trek.query.filter_by(staff_id=current_user.id).all()
    
    trek_stats = []
    for trek in assigned_treks:
        reg_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_stats.append({
            'trek': trek,
            'registered_users': reg_count
        })
        
    return render_template('staff_dashboard.html', trek_stats=trek_stats)

@main.route('/staff/trek/edit-slots/<int:trek_id>', methods=['POST'])
@login_required
def staff_edit_slots(trek_id):
    require_role('staff')
    trek = Trek.query.get_or_404(trek_id)
    
    if trek.staff_id != current_user.id:
        abort(403)
        
    new_total = int(request.form.get('total_slots'))
    old_total = trek.total_slots
    diff = new_total - old_total
    
    if trek.available_slots + diff < 0:
        flash('Cannot reduce total slots below booked slots.', 'danger')
    else:
        trek.total_slots = new_total
        trek.available_slots += diff
        db.session.commit()
        flash('Slots updated successfully!', 'success')
        
    return redirect(url_for('main.staff_dashboard'))

@main.route('/staff/trek/update-status/<int:trek_id>', methods=['POST'])
@login_required
def staff_update_status(trek_id):
    require_role('staff')
    trek = Trek.query.get_or_404(trek_id)
    
    if trek.staff_id != current_user.id:
        abort(403)
        
    new_status = request.form.get('status')
    if new_status in ['Open', 'Closed', 'Completed', 'Started']:
        trek.status = new_status
        db.session.commit()
        flash(f'Trek status updated to {new_status}!', 'success')
    else:
        flash('Invalid status transition.', 'danger')
        
    return redirect(url_for('main.staff_dashboard'))

@main.route('/staff/trek/participants/<int:trek_id>')
@login_required
def staff_participants(trek_id):
    require_role('staff')
    trek = Trek.query.get_or_404(trek_id)
    
    if trek.staff_id != current_user.id:
        abort(403)
        
    bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
    return render_template('staff_participants.html', trek=trek, bookings=bookings)

@main.route('/dashboard')
@login_required
def user_dashboard():
    require_role('trekker')
    difficulty = request.args.get('difficulty')
    location = request.args.get('location', '').strip()
    search = request.args.get('search', '').strip()
    
    query = Trek.query.filter(Trek.status == 'Open')
    
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.like(f'%{location}%'))
    if search:
        query = query.filter(Trek.name.like(f'%{search}%'))
        
    available_treks = query.all()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    locations = db.session.query(Trek.location).distinct().all()
    locations_list = [loc[0] for loc in locations if loc[0]]
    
    return render_template(
        'user_dashboard.html',
        available_treks=available_treks,
        my_bookings=my_bookings,
        locations=locations_list,
        selected_difficulty=difficulty,
        selected_location=location,
        search_query=search
    )

@main.route('/trek/<int:trek_id>')
@login_required
def view_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    
    if current_user.role == 'trekker' and trek.status not in ['Open', 'Closed', 'Completed', 'Approved']:
        abort(403)
    elif current_user.role == 'staff' and trek.staff_id != current_user.id:
        abort(403)
        
    already_booked = False
    if current_user.role == 'trekker':
        already_booked = Booking.query.filter_by(
            user_id=current_user.id,
            trek_id=trek.id,
            status='Booked'
        ).first() is not None
        
    return render_template('view_trek.html', trek=trek, already_booked=already_booked)

@main.route('/trek/<int:trek_id>/book', methods=['POST'])
@login_required
def book_trek(trek_id):
    require_role('trekker')
    trek = Trek.query.get_or_404(trek_id)
    
    if trek.status != 'Open':
        flash('This trek is currently closed for bookings.', 'danger')
        return redirect(url_for('main.view_trek', trek_id=trek.id))
        
    if trek.available_slots <= 0:
        flash('Sorry, this trek is fully booked!', 'danger')
        return redirect(url_for('main.view_trek', trek_id=trek.id))
        
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    ).first()
    if existing_booking:
        flash('You have already booked this trek!', 'warning')
        return redirect(url_for('main.user_dashboard'))
        
    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    
    flash(f'Successfully booked trek: {trek.name}!', 'success')
    return redirect(url_for('main.user_dashboard'))

@main.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if current_user.role != 'admin' and booking.user_id != current_user.id:
        abort(403)
        
    if booking.status != 'Booked':
        flash('Booking cannot be cancelled in its current state.', 'danger')
        return redirect(url_for('main.index'))
        
    booking.status = 'Cancelled'
    trek = Trek.query.get(booking.trek_id)
    trek.available_slots += 1
    db.session.commit()
    
    flash('Booking cancelled successfully.', 'success')
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_bookings'))
    return redirect(url_for('main.user_dashboard'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        contact = request.form.get('contact').strip()
        password = request.form.get('password')
        
        if not name:
            flash('Name cannot be empty.', 'danger')
            return redirect(url_for('main.edit_profile'))
            
        current_user.name = name
        current_user.contact_details = contact
        
        if password:
            current_user.password_hash = generate_password_hash(password)
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('profile.html')


@main.route('/api/treks', methods=['GET'])
def api_treks():
    treks = Trek.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'difficulty': t.difficulty,
        'duration': t.duration,
        'total_slots': t.total_slots,
        'available_slots': t.available_slots,
        'status': t.status,
        'start_date': t.start_date.isoformat(),
        'end_date': t.end_date.isoformat(),
        'price': t.price,
        'image_url': t.image_url if t.image_url else None
    } for t in treks])

@main.route('/api/bookings', methods=['GET'])
def api_bookings():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user.role == 'admin':
        bookings = Booking.query.all()
    elif current_user.role == 'staff':
        bookings = Booking.query.join(Trek).filter(Trek.staff_id == current_user.id).all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        
    return jsonify([{
        'id': b.id,
        'user_id': b.user_id,
        'trek_id': b.trek_id,
        'booking_date': b.booking_date.isoformat(),
        'status': b.status
    } for b in bookings])

@main.route('/api/users', methods=['GET'])
def api_users():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
        
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'role': u.role,
        'name': u.name,
        'contact_details': u.contact_details,
        'status': u.status
    } for u in users])
