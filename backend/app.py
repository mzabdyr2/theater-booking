import stripe
from models import db, Event, Seat, Booking, BookedSeat
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import config first, before models
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# ============== LOGGING & MONITORING ==============
# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Azure Application Insights (jeśli skonfigurowane)
APPINSIGHTS_CONNECTION_STRING = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
if APPINSIGHTS_CONNECTION_STRING:
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.ext.azure.trace_exporter import AzureExporter
        from opencensus.ext.flask.flask_middleware import FlaskMiddleware
        from opencensus.trace.samplers import ProbabilitySampler
        
        # Dodaj Azure Log Handler
        logger.addHandler(AzureLogHandler(connection_string=APPINSIGHTS_CONNECTION_STRING))
        
        # Dodaj middleware do śledzenia requestów
        middleware = FlaskMiddleware(
            app,
            exporter=AzureExporter(connection_string=APPINSIGHTS_CONNECTION_STRING),
            sampler=ProbabilitySampler(rate=1.0),
        )
        logger.info("Azure Application Insights configured successfully")
    except ImportError as e:
        logger.warning(f"Could not configure Application Insights: {e}")
else:
    logger.info("Running without Application Insights (no connection string)")

# Initialize CORS - allow all origins for API
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Import and initialize database
db.init_app(app)

# Initialize Stripe
stripe.api_key = app.config.get('STRIPE_SECRET_KEY', '')


# ============== HEALTH CHECK ==============

@app.route('/')
def index():
    """Root endpoint - health check for Azure"""
    return jsonify({
        'status': 'healthy',
        'message': 'Theater Booking API is running',
        'version': '1.0.0'
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.route('/api/config')
def get_config():
    """Pobierz publiczną konfigurację (np. klucz Stripe)"""
    return jsonify({
        'stripe_publishable_key': app.config.get('STRIPE_PUBLISHABLE_KEY', '')
    })


# ============== API WYDARZEŃ ==============

@app.route('/api/events', methods=['GET'])
def get_events():
    """Pobierz listę wszystkich wydarzeń"""
    try:
        events = Event.query.filter(Event.date >= datetime.utcnow()).all()
        return jsonify([{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date': e.date.isoformat(),
            'venue': e.venue,
            'image_url': e.image_url
        } for e in events])
    except Exception as e:
        app.logger.error(f"Error fetching events: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Pobierz szczegóły wydarzenia"""
    try:
        event = Event.query.get(event_id)
        if event is None:
            return jsonify({'error': 'Event not found'}), 404
        return jsonify({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat(),
            'venue': event.venue,
            'image_url': event.image_url
        })
    except Exception as e:
        app.logger.error(f"Error fetching event {event_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ============== API MIEJSC ==============

@app.route('/api/events/<int:event_id>/seats', methods=['GET'])
def get_seats(event_id):
    """Pobierz mapę miejsc dla wydarzenia"""
    try:
        seats = Seat.query.filter_by(event_id=event_id).all()
        return jsonify([{
            'id': s.id,
            'row': s.row,
            'number': s.number,
            'category': s.category,
            'price': float(s.price) if s.price else 0,
            'is_available': s.is_available
        } for s in seats])
    except Exception as e:
        app.logger.error(f"Error fetching seats: {e}")
        return jsonify({'error': str(e)}), 500


# ============== API REZERWACJI ==============

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Utwórz nową rezerwację"""
    try:
        data = request.json

        # Walidacja danych
        required_fields = ['event_id', 'seat_ids',
                           'customer_name', 'customer_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Brakujące pole: {field}'}), 400

        # Sprawdź dostępność miejsc
        seats = Seat.query.filter(
            Seat.id.in_(data['seat_ids']),
            Seat.is_available == True
        ).all()

        if len(seats) != len(data['seat_ids']):
            return jsonify({'error': 'Niektóre miejsca są już zajęte'}), 400

        # Oblicz całkowitą kwotę
        total_amount = sum(float(seat.price) for seat in seats)

        # Utwórz rezerwację
        booking = Booking(
            booking_reference=str(uuid.uuid4())[:8].upper(),
            event_id=data['event_id'],
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            total_amount=total_amount,
            status='pending'
        )

        db.session.add(booking)
        db.session.flush()

        # Dodaj miejsca do rezerwacji i oznacz jako zajęte
        for seat in seats:
            booked_seat = BookedSeat(booking_id=booking.id, seat_id=seat.id)
            db.session.add(booked_seat)
            seat.is_available = False

        db.session.commit()

        return jsonify({
            'booking_id': booking.id,
            'booking_reference': booking.booking_reference,
            'total_amount': float(total_amount)
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating booking: {e}")
        return jsonify({'error': str(e)}), 500


# ============== API PŁATNOŚCI (Stripe) ==============

@app.route('/api/payments/create-intent', methods=['POST'])
def create_payment_intent():
    """Utwórz Stripe Payment Intent"""
    try:
        data = request.json
        booking_id = data.get('booking_id')

        booking = Booking.query.get_or_404(booking_id)

        intent = stripe.PaymentIntent.create(
            amount=int(float(booking.total_amount) * 100),
            currency='pln',
            metadata={'booking_id': booking_id}
        )

        return jsonify({
            'client_secret': intent.client_secret
        })
    except Exception as e:
        app.logger.error(f"Error creating payment intent: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/payments/confirm', methods=['POST'])
def confirm_payment():
    """Potwierdź płatność po stronie serwera"""
    try:
        data = request.json
        booking_id = data.get('booking_id')
        payment_intent_id = data.get('payment_intent_id')

        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'paid'
        booking.payment_id = payment_intent_id

        db.session.commit()

        return jsonify({
            'message': 'Płatność potwierdzona',
            'booking_reference': booking.booking_reference
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error confirming payment: {e}")
        return jsonify({'error': str(e)}), 500


# ============== INICJALIZACJA ==============

@app.route('/api/init-db', methods=['POST'])
def init_database():
    """Inicjalizacja bazy danych z przykładowymi danymi"""
    try:
        with app.app_context():
            db.create_all()

            # Sprawdź czy już są dane
            if Event.query.first():
                return jsonify({'message': 'Baza danych już zainicjalizowana'})

            # Przykładowe wydarzenie
            event = Event(
                title='Hamlet - William Shakespeare',
                description='Klasyczna tragedia w nowoczesnej inscenizacji',
                date=datetime(2026, 3, 15, 19, 0),
                venue='Teatr Narodowy, Warszawa'
            )
            db.session.add(event)
            db.session.flush()

            # Generuj miejsca
            categories = {
                'A': ('VIP', 150.00),
                'B': ('VIP', 150.00),
                'C': ('Standard', 100.00),
                'D': ('Standard', 100.00),
                'E': ('Standard', 100.00),
                'F': ('Economy', 70.00),
                'G': ('Economy', 70.00),
                'H': ('Economy', 70.00),
                'I': ('Economy', 50.00),
                'J': ('Economy', 50.00),
            }

            for row, (category, price) in categories.items():
                for num in range(1, 16):
                    seat = Seat(
                        event_id=event.id,
                        row=row,
                        number=num,
                        category=category,
                        price=price,
                        is_available=True
                    )
                    db.session.add(seat)

            db.session.commit()
            return jsonify({'message': 'Baza danych zainicjalizowana'})

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error initializing database: {e}")
        return jsonify({'error': str(e)}), 500


# ============== STARTUP ==============

# Create tables on startup (with error handling)
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.warning(f"Could not create database tables: {e}")


# Entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
