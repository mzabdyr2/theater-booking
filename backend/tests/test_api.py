# ============================================
# Pytest Configuration
# ============================================

from datetime import datetime, timedelta
from models import Event, Seat, Booking, BookedSeat
from app import app, db
import pytest
import sys
import os

# Dodaj ścieżkę do backendu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def client():
    """Tworzy testowego klienta Flask"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def sample_event(client):
    """Tworzy przykładowe wydarzenie w bazie"""
    with app.app_context():
        event = Event(
            title='Test Event',
            description='Test Description',
            date=datetime.utcnow() + timedelta(days=30),
            venue='Test Venue'
        )
        db.session.add(event)
        db.session.commit()

        # Dodaj miejsca
        for row in ['A', 'B']:
            for num in range(1, 6):
                seat = Seat(
                    event_id=event.id,
                    row=row,
                    number=num,
                    category='Standard',
                    price=100.00,
                    is_available=True
                )
                db.session.add(seat)
        db.session.commit()

        return event.id


class TestHealthEndpoints:
    """Testy endpointów health check"""

    def test_root_endpoint(self, client):
        """Test głównego endpointu"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_health_check(self, client):
        """Test endpointu /api/health"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'


class TestEventsAPI:
    """Testy API wydarzeń"""

    def test_get_events_empty(self, client):
        """Test pobierania pustej listy wydarzeń"""
        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_events_with_data(self, client, sample_event):
        """Test pobierania listy wydarzeń z danymi"""
        response = client.get('/api/events')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        assert data[0]['title'] == 'Test Event'

    def test_get_single_event(self, client, sample_event):
        """Test pobierania pojedynczego wydarzenia"""
        response = client.get(f'/api/events/{sample_event}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Event'
        assert data['venue'] == 'Test Venue'

    def test_get_nonexistent_event(self, client):
        """Test pobierania nieistniejącego wydarzenia"""
        response = client.get('/api/events/99999')
        assert response.status_code == 404


class TestSeatsAPI:
    """Testy API miejsc"""

    def test_get_seats(self, client, sample_event):
        """Test pobierania miejsc dla wydarzenia"""
        response = client.get(f'/api/events/{sample_event}/seats')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 10  # 2 rzędy x 5 miejsc

    def test_seat_structure(self, client, sample_event):
        """Test struktury danych miejsca"""
        response = client.get(f'/api/events/{sample_event}/seats')
        data = response.get_json()
        seat = data[0]

        assert 'id' in seat
        assert 'row' in seat
        assert 'number' in seat
        assert 'category' in seat
        assert 'price' in seat
        assert 'is_available' in seat


class TestBookingsAPI:
    """Testy API rezerwacji"""

    def test_create_booking(self, client, sample_event):
        """Test tworzenia rezerwacji"""
        # Pobierz dostępne miejsca
        seats_response = client.get(f'/api/events/{sample_event}/seats')
        seats = seats_response.get_json()
        seat_ids = [seats[0]['id'], seats[1]['id']]

        # Utwórz rezerwację
        booking_data = {
            'event_id': sample_event,
            'seat_ids': seat_ids,
            'customer_name': 'Jan Kowalski',
            'customer_email': 'jan@example.com',
            'customer_phone': '+48123456789'
        }

        response = client.post('/api/bookings',
                               json=booking_data,
                               content_type='application/json')

        assert response.status_code == 201
        data = response.get_json()
        assert 'booking_id' in data
        assert 'booking_reference' in data
        assert data['total_amount'] == 200.00  # 2 miejsca x 100 PLN

    def test_create_booking_missing_fields(self, client, sample_event):
        """Test tworzenia rezerwacji bez wymaganych pól"""
        booking_data = {
            'event_id': sample_event,
            # Brak seat_ids, customer_name, customer_email
        }

        response = client.post('/api/bookings',
                               json=booking_data,
                               content_type='application/json')

        assert response.status_code == 400

    def test_create_booking_unavailable_seats(self, client, sample_event):
        """Test rezerwacji zajętych miejsc"""
        # Pobierz miejsca
        seats_response = client.get(f'/api/events/{sample_event}/seats')
        seats = seats_response.get_json()
        seat_ids = [seats[0]['id']]

        # Pierwsza rezerwacja
        booking_data = {
            'event_id': sample_event,
            'seat_ids': seat_ids,
            'customer_name': 'Jan Kowalski',
            'customer_email': 'jan@example.com'
        }

        response1 = client.post('/api/bookings',
                                json=booking_data,
                                content_type='application/json')
        assert response1.status_code == 201

        # Próba drugiej rezerwacji na te same miejsca
        booking_data2 = {
            'event_id': sample_event,
            'seat_ids': seat_ids,
            'customer_name': 'Anna Nowak',
            'customer_email': 'anna@example.com'
        }

        response2 = client.post('/api/bookings',
                                json=booking_data2,
                                content_type='application/json')
        assert response2.status_code == 400


class TestInitDB:
    """Testy inicjalizacji bazy danych"""

    def test_init_database(self, client):
        """Test endpointu inicjalizacji bazy"""
        response = client.post('/api/init-db')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

    def test_init_database_twice(self, client):
        """Test podwójnej inicjalizacji"""
        # Pierwsza inicjalizacja
        response1 = client.post('/api/init-db')
        assert response1.status_code == 200

        # Druga inicjalizacja - powinna zwrócić info że już istnieje
        response2 = client.post('/api/init-db')
        assert response2.status_code == 200
        data = response2.get_json()
        assert 'już zainicjalizowana' in data['message']
