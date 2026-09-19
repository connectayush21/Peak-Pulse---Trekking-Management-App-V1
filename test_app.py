import unittest
import os
from datetime import date
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, Trek, Booking

class TrekkingAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_database.db')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.seed_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def seed_test_data(self):
        admin = User(
            username='test_admin@trek.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            name='Test Admin',
            status='active'
        )
        staff_approved = User(
            username='test_guide1@trek.com',
            password_hash=generate_password_hash('staff123'),
            role='staff',
            name='Approved Guide',
            status='approved'
        )
        staff_pending = User(
            username='test_guide2@trek.com',
            password_hash=generate_password_hash('staff123'),
            role='staff',
            name='Pending Guide',
            status='pending'
        )
        trekker = User(
            username='test_trekker@gmail.com',
            password_hash=generate_password_hash('user123'),
            role='trekker',
            name='Test Trekker',
            status='active'
        )
        db.session.add_all([admin, staff_approved, staff_pending, trekker])
        db.session.commit()

        self.trek_open = Trek(
            name='Open Trail',
            location='Nepal',
            difficulty='Moderate',
            duration=5,
            total_slots=10,
            available_slots=10,
            staff_id=staff_approved.id,
            status='Open',
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 6),
            price=200.0
        )
        self.trek_closed = Trek(
            name='Closed Trail',
            location='Bhutan',
            difficulty='Hard',
            duration=8,
            total_slots=5,
            available_slots=5,
            staff_id=staff_approved.id,
            status='Closed',
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 9),
            price=400.0
        )
        db.session.add_all([self.trek_open, self.trek_closed])
        db.session.commit()

    def login_client(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_database_initialization(self):
        with self.app.app_context():
            admin = User.query.filter_by(username='test_admin@trek.com').first()
            self.assertIsNotNone(admin)
            self.assertEqual(admin.role, 'admin')
            trek = Trek.query.filter_by(name='Open Trail').first()
            self.assertIsNotNone(trek)
            self.assertEqual(trek.status, 'Open')

    def test_pending_guide_cannot_login(self):
        response = self.login_client('test_guide2@trek.com', 'staff123')
        self.assertIn(b'Your account is pending admin approval.', response.data)

    def test_approved_guide_can_login(self):
        response = self.login_client('test_guide1@trek.com', 'staff123')
        self.assertIn(b'Welcome back, Approved Guide!', response.data)
        dash_response = self.client.get('/staff/dashboard')
        self.assertEqual(dash_response.status_code, 200)
        self.assertIn(b'Guide Dashboard', dash_response.data)

    def test_trekker_booking_flow(self):
        self.login_client('test_trekker@gmail.com', 'user123')
        with self.app.app_context():
            trek = Trek.query.filter_by(name='Open Trail').first()
            trek_id = trek.id
            
        book_response = self.client.post(f'/trek/{trek_id}/book', follow_redirects=True)
        self.assertIn(b'Successfully booked trek', book_response.data)
        
        with self.app.app_context():
            trek = db.session.get(Trek, trek_id)
            self.assertEqual(trek.available_slots, 9)
            booking = Booking.query.filter_by(trek_id=trek_id).first()
            self.assertIsNotNone(booking)
            self.assertEqual(booking.status, 'Booked')

    def test_booking_closed_trek_fails(self):
        self.login_client('test_trekker@gmail.com', 'user123')
        with self.app.app_context():
            trek = Trek.query.filter_by(name='Closed Trail').first()
            trek_id = trek.id
            
        book_response = self.client.post(f'/trek/{trek_id}/book', follow_redirects=True)
        self.assertIn(b'This trek is currently closed for bookings.', book_response.data)

    def test_overbooking_prevention(self):
        self.login_client('test_trekker@gmail.com', 'user123')
        with self.app.app_context():
            trek = Trek.query.filter_by(name='Open Trail').first()
            trek.available_slots = 0
            db.session.commit()
            trek_id = trek.id
            
        book_response = self.client.post(f'/trek/{trek_id}/book', follow_redirects=True)
        self.assertIn(b'Sorry, this trek is fully booked!', book_response.data)

    def test_blacklisted_user_login_fails(self):
        self.login_client('test_admin@trek.com', 'admin123')
        with self.app.app_context():
            trekker = User.query.filter_by(username='test_trekker@gmail.com').first()
            trekker_id = trekker.id
            
        self.client.get(f'/admin/user/toggle-status/{trekker_id}')
        self.client.get('/logout')
        response = self.login_client('test_trekker@gmail.com', 'user123')
        self.assertIn(b'Your account has been deactivated or blacklisted.', response.data)

if __name__ == '__main__':
    unittest.main()
