// Konfiguracja
const API_URL =
	window.location.hostname === "localhost"
		? "http://localhost:8000/api"
		: "https://theater-booking-api.azurewebsites.net/api";

// Stripe będzie zainicjalizowany po pobraniu klucza z API
let stripe = null;
let cardElement = null;

// Stan aplikacji
let state = {
	currentEvent: null,
	selectedSeats: [],
	seats: [],
	booking: null,
	customerData: null,
};

// Inicjalizacja Stripe (pobierz klucz z backendu)
async function initStripe() {
	try {
		const response = await fetch(`${API_URL}/config`);
		const config = await response.json();
		if (config.stripe_publishable_key) {
			stripe = Stripe(config.stripe_publishable_key);
			console.log("Stripe initialized successfully");
		} else {
			console.warn("Stripe publishable key not configured");
		}
	} catch (error) {
		console.error("Failed to initialize Stripe:", error);
	}
}

// Wywołaj inicjalizację przy starcie
initStripe();

// ============== ŁADOWANIE WYDARZEŃ ==============

async function loadEvents() {
	const container = document.getElementById("events-list");
	container.innerHTML =
		'<p style="text-align: center;">Ładowanie wydarzeń...</p>';

	try {
		const response = await fetch(`${API_URL}/events`);

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const events = await response.json();

		if (events.length === 0) {
			container.innerHTML =
				'<p style="text-align: center;">Brak dostępnych wydarzeń</p>';
			return;
		}

		container.innerHTML = events
			.map(
				event => `
            <div class="event-card" data-event-id="${event.id}">
                <h3>${event.title}</h3>
                <p>${event.description || ""}</p>
                <p><strong>📅</strong> ${formatDate(event.date)}</p>
                <p><strong>📍</strong> ${event.venue}</p>
            </div>
        `,
			)
			.join("");

		// Dodaj event listenery
		document.querySelectorAll(".event-card").forEach(card => {
			card.addEventListener("click", () => {
				const eventId = card.dataset.eventId;
				selectEvent(parseInt(eventId));
			});
		});
	} catch (error) {
		console.error("Błąd ładowania wydarzeń:", error);
		container.innerHTML = `<p style="text-align: center; color: #ff6b6b;">Błąd ładowania wydarzeń: ${error.message}</p>`;
	}
}

function formatDate(dateString) {
	const date = new Date(dateString);
	return date.toLocaleDateString("pl-PL", {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	});
}

// ============== WYBÓR WYDARZENIA ==============

async function selectEvent(eventId) {
	console.log("Wybrano wydarzenie:", eventId);

	try {
		// Pobierz szczegóły wydarzenia
		const eventResponse = await fetch(`${API_URL}/events/${eventId}`);
		if (!eventResponse.ok) {
			throw new Error(`Błąd pobierania wydarzenia: ${eventResponse.status}`);
		}
		state.currentEvent = await eventResponse.json();
		console.log("Wydarzenie:", state.currentEvent);

		// Pobierz miejsca
		const seatsResponse = await fetch(`${API_URL}/events/${eventId}/seats`);
		if (!seatsResponse.ok) {
			throw new Error(`Błąd pobierania miejsc: ${seatsResponse.status}`);
		}
		state.seats = await seatsResponse.json();
		console.log("Miejsca:", state.seats);

		// Reset wybranych miejsc
		state.selectedSeats = [];

		// Wyświetl informacje o wydarzeniu
		document.getElementById("event-info").innerHTML = `
            <h3>${state.currentEvent.title}</h3>
            <p>${formatDate(state.currentEvent.date)} | ${state.currentEvent.venue}</p>
        `;

		// Renderuj mapę miejsc
		renderSeatMap();

		// Pokaż sekcję miejsc
		showSection("seats-section");
	} catch (error) {
		console.error("Błąd:", error);
		alert("Wystąpił błąd: " + error.message);
	}
}

// ============== MAPA MIEJSC ==============

function renderSeatMap() {
	const container = document.getElementById("seat-map");

	// Grupuj miejsca według rzędów
	const rows = {};
	state.seats.forEach(seat => {
		if (!rows[seat.row]) rows[seat.row] = [];
		rows[seat.row].push(seat);
	});

	// Sortuj miejsca w rzędach
	Object.values(rows).forEach(row => {
		row.sort((a, b) => a.number - b.number);
	});

	// Renderuj
	container.innerHTML = Object.entries(rows)
		.sort(([a], [b]) => a.localeCompare(b))
		.map(
			([rowLabel, seats]) => `
            <div class="seat-row">
                <span class="row-label">${rowLabel}</span>
                ${seats
									.map(
										seat => `
                    <div 
                        class="seat ${getSeatClass(seat)}"
                        data-seat-id="${seat.id}"
                        title="Rząd ${seat.row}, Miejsce ${seat.number} - ${seat.price} PLN"
                    >
                        ${seat.number}
                    </div>
                `,
									)
									.join("")}
                <span class="row-label">${rowLabel}</span>
            </div>
        `,
		)
		.join("");

	// Dodaj event listenery do miejsc
	document.querySelectorAll(".seat").forEach(seatEl => {
		seatEl.addEventListener("click", () => {
			const seatId = parseInt(seatEl.dataset.seatId);
			toggleSeat(seatId);
		});
	});

	// Zaktualizuj podsumowanie
	updateSeatSelection();
}

function getSeatClass(seat) {
	if (!seat.is_available) return "taken";
	if (state.selectedSeats.includes(seat.id)) return "selected";
	if (seat.category === "VIP") return "available vip";
	return "available";
}

function toggleSeat(seatId) {
	console.log("Kliknięto miejsce:", seatId);

	const seat = state.seats.find(s => s.id === seatId);
	if (!seat) {
		console.log("Nie znaleziono miejsca");
		return;
	}

	if (!seat.is_available) {
		console.log("Miejsce niedostępne");
		return;
	}

	const index = state.selectedSeats.indexOf(seatId);
	if (index > -1) {
		state.selectedSeats.splice(index, 1);
		console.log("Odznaczono miejsce");
	} else {
		state.selectedSeats.push(seatId);
		console.log("Zaznaczono miejsce");
	}

	updateSeatSelection();
}

function updateSeatSelection() {
	// Aktualizuj wygląd miejsc
	document.querySelectorAll(".seat").forEach(el => {
		const seatId = parseInt(el.dataset.seatId);
		const seat = state.seats.find(s => s.id === seatId);
		if (seat) {
			el.className = `seat ${getSeatClass(seat)}`;
		}
	});

	// Aktualizuj podsumowanie
	const selectedSeatsInfo = state.selectedSeats.map(id => {
		const seat = state.seats.find(s => s.id === id);
		return `${seat.row}${seat.number}`;
	});

	const totalPrice = state.selectedSeats.reduce((sum, id) => {
		const seat = state.seats.find(s => s.id === id);
		return sum + (seat ? seat.price : 0);
	}, 0);

	document.getElementById("selected-seats").textContent =
		selectedSeatsInfo.length > 0 ? selectedSeatsInfo.join(", ") : "-";
	document.getElementById("total-price").textContent = totalPrice.toFixed(2);

	// Aktywuj/deaktywuj przycisk
	const proceedBtn = document.getElementById("proceed-btn");
	if (proceedBtn) {
		proceedBtn.disabled = state.selectedSeats.length === 0;
	}

	console.log("Wybrane miejsca:", state.selectedSeats);
}

// ============== DANE KLIENTA ==============

function proceedToCustomerForm() {
	if (state.selectedSeats.length === 0) {
		alert("Wybierz przynajmniej jedno miejsce!");
		return;
	}
	showSection("customer-section");
}

async function submitCustomerForm(e) {
	e.preventDefault();

	state.customerData = {
		name: document.getElementById("name").value,
		email: document.getElementById("email").value,
		phone: document.getElementById("phone").value || "",
	};

	// Utwórz rezerwację
	try {
		const response = await fetch(`${API_URL}/bookings`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				event_id: state.currentEvent.id,
				seat_ids: state.selectedSeats,
				customer_name: state.customerData.name,
				customer_email: state.customerData.email,
				customer_phone: state.customerData.phone,
			}),
		});

		if (!response.ok) {
			const error = await response.json();
			alert(error.error || "Błąd tworzenia rezerwacji");
			return;
		}

		state.booking = await response.json();
		console.log("Rezerwacja utworzona:", state.booking);

		// Przejdź do płatności
		setupPayment();
	} catch (error) {
		console.error("Błąd tworzenia rezerwacji:", error);
		alert("Błąd tworzenia rezerwacji: " + error.message);
	}
}

// ============== PŁATNOŚĆ ==============

async function setupPayment() {
	// Wyświetl podsumowanie
	const selectedSeatsInfo = state.selectedSeats.map(id => {
		const seat = state.seats.find(s => s.id === id);
		return `Rząd ${seat.row}, Miejsce ${seat.number} (${seat.price} PLN)`;
	});

	document.getElementById("booking-summary").innerHTML = `
        <h3>${state.currentEvent.title}</h3>
        <p>${formatDate(state.currentEvent.date)}</p>
        <hr>
        <p><strong>Miejsca:</strong></p>
        <ul>${selectedSeatsInfo.map(s => `<li>${s}</li>`).join("")}</ul>
        <hr>
        <p><strong>Dane:</strong> ${state.customerData.name}</p>
        <p><strong>Email:</strong> ${state.customerData.email}</p>
        <p><strong>Numer rezerwacji:</strong> ${state.booking.booking_reference}</p>
    `;

	document.getElementById("pay-amount").textContent =
		state.booking.total_amount.toFixed(2);

	// Inicjalizuj Stripe Elements
	const elements = stripe.elements({
		locale: "pl",
	});

	cardElement = elements.create("card", {
		style: {
			base: {
				fontSize: "16px",
				color: "#32325d",
				fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
				"::placeholder": {
					color: "#aab7c4",
				},
			},
			invalid: {
				color: "#fa755a",
				iconColor: "#fa755a",
			},
		},
	});

	// Wyczyść kontener i zamontuj element karty
	const cardElementContainer = document.getElementById("card-element");
	cardElementContainer.innerHTML = "";
	cardElement.mount("#card-element");

	// Obsługa błędów walidacji karty
	cardElement.on("change", event => {
		const displayError = document.getElementById("card-errors");
		if (event.error) {
			displayError.textContent = event.error.message;
		} else {
			displayError.textContent = "";
		}
	});

	showSection("payment-section");
}

async function processPayment() {
	const payBtn = document.getElementById("pay-btn");
	payBtn.disabled = true;
	payBtn.textContent = "Przetwarzanie...";

	try {
		// Utwórz Payment Intent na serwerze
		const intentResponse = await fetch(`${API_URL}/payments/create-intent`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ booking_id: state.booking.booking_id }),
		});

		if (!intentResponse.ok) {
			const error = await intentResponse.json();
			throw new Error(error.error || "Błąd tworzenia płatności");
		}

		const { client_secret } = await intentResponse.json();
		console.log("Payment Intent utworzony");

		// Potwierdź płatność przez Stripe
		const { error, paymentIntent } = await stripe.confirmCardPayment(
			client_secret,
			{
				payment_method: {
					card: cardElement,
					billing_details: {
						name: state.customerData.name,
						email: state.customerData.email,
					},
				},
			},
		);

		if (error) {
			console.error("Błąd Stripe:", error);
			document.getElementById("card-errors").textContent = error.message;
			payBtn.disabled = false;
			payBtn.textContent = `Zapłać ${state.booking.total_amount.toFixed(2)} PLN`;
			return;
		}

		console.log("Płatność potwierdzona przez Stripe:", paymentIntent.id);

		// Potwierdź płatność na serwerze
		const confirmResponse = await fetch(`${API_URL}/payments/confirm`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				booking_id: state.booking.booking_id,
				payment_intent_id: paymentIntent.id,
			}),
		});

		if (!confirmResponse.ok) {
			throw new Error("Błąd potwierdzenia płatności na serwerze");
		}

		// Pokaż potwierdzenie
		showConfirmation();
	} catch (error) {
		console.error("Błąd płatności:", error);
		document.getElementById("card-errors").textContent = error.message;
		payBtn.disabled = false;
		payBtn.textContent = `Zapłać ${state.booking.total_amount.toFixed(2)} PLN`;
	}
}

function showConfirmation() {
	document.getElementById("confirmation-details").innerHTML = `
        <h3>Dziękujemy za zakup!</h3>
        <p><strong>Numer rezerwacji:</strong> ${state.booking.booking_reference}</p>
        <p><strong>Wydarzenie:</strong> ${state.currentEvent.title}</p>
        <p><strong>Data:</strong> ${formatDate(state.currentEvent.date)}</p>
        <p><strong>Miejsca:</strong> ${state.selectedSeats
					.map(id => {
						const seat = state.seats.find(s => s.id === id);
						return `${seat.row}${seat.number}`;
					})
					.join(", ")}</p>
        <hr>
        <p>Potwierdzenie zostanie wysłane na: <strong>${state.customerData.email}</strong></p>
        <br>
        <button class="btn btn-primary" onclick="location.reload()">Powrót do strony głównej</button>
    `;

	showSection("confirmation-section");
}

// ============== NAWIGACJA ==============

function showSection(sectionId) {
	document.querySelectorAll(".section").forEach(section => {
		section.classList.add("hidden");
	});
	document.getElementById(sectionId).classList.remove("hidden");
	window.scrollTo({ top: 0, behavior: "smooth" });
}

// ============== INICJALIZACJA ==============

document.addEventListener("DOMContentLoaded", () => {
	console.log("Aplikacja uruchomiona");
	console.log("API URL:", API_URL);

	// Przycisk "Przejdź do danych"
	const proceedBtn = document.getElementById("proceed-btn");
	if (proceedBtn) {
		proceedBtn.addEventListener("click", proceedToCustomerForm);
	}

	// Formularz danych klienta
	const customerForm = document.getElementById("customer-form");
	if (customerForm) {
		customerForm.addEventListener("submit", submitCustomerForm);
	}

	// Przycisk płatności
	const payBtn = document.getElementById("pay-btn");
	if (payBtn) {
		payBtn.addEventListener("click", processPayment);
	}

	// Załaduj wydarzenia
	loadEvents();
});
