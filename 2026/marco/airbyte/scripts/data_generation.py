import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

# Configurações
NUM_DRIVERS = 50
NUM_PASSENGERS = 200
NUM_TRIPS = 1000

def generate_drivers(num):
    print(f"Gerando {num} motoristas...")
    drivers = []
    categories = ['X', 'Black', 'Comfort']
    
    for i in range(1, num + 1):
        # Sujeira proposital: Nomes com espaços extras ou minúsculos
        name = fake.name()
        if random.random() < 0.1:
            name = name.lower()
            
        driver = {
            'driver_id': i,
            'name': name,
            'city': fake.city(),
            'vehicle_model': fake.license_plate() + " - " + random.choice(['Onix', 'HB20', 'Corolla', 'Civic']),
            'category': random.choice(categories),
            'joined_at': fake.date_between(start_date='-2y', end_date='-1y').isoformat()
        }
        drivers.append(driver)
    return drivers

def generate_passengers(num):
    print(f"Gerando {num} passageiros...")
    passengers = []
    for i in range(1, num + 1):
        passenger = {
            'passenger_id': i,
            'name': fake.name(),
            'email': fake.email(),
            # Passageiros VIPs têm nota alta
            'rating_avg': round(random.uniform(3.5, 5.0), 2)
        }
        passengers.append(passenger)
    return passengers

def generate_trips(num, driver_ids, passenger_ids):
    print(f"Gerando {num} corridas...")
    trips = []
    payment_methods = ['credit_card', 'cash', 'app_wallet']
    
    for i in range(1, num + 1):
        start_time = fake.date_time_between(start_date='-6m', end_date='now')
        
        # 15% de chance de cancelamento
        status_roll = random.random()
        if status_roll < 0.10:
            status = 'cancelled_by_driver'
        elif status_roll < 0.15:
            status = 'cancelled_by_passenger'
        else:
            status = 'completed'

        # Lógica de Duração e Distância
        if status == 'completed':
            duration_minutes = random.randint(5, 60)
            end_time = start_time + timedelta(minutes=duration_minutes)
            distance_km = round(duration_minutes * random.uniform(0.3, 0.8), 2) # Simula trânsito
            
            # Preço dinâmico simples
            base_fare = 5.00
            price = base_fare + (duration_minutes * 0.50) + (distance_km * 1.50)
            if random.random() < 0.2: price *= 1.5 # Tarifa dinâmica
            
            price = round(price, 2)
        else:
            # Canceladas
            end_time = '' # Vazio no CSV
            distance_km = 0
            price = 0
            if status == 'cancelled_by_passenger':
                price = 5.00 # Taxa de cancelamento

        trip = {
            'trip_id': i,
            'driver_id': random.choice(driver_ids),
            'passenger_id': random.choice(passenger_ids),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat() if end_time else '',
            'distance_km': distance_km,
            'amount': price,
            'status': status,
            'payment_method': random.choice(payment_methods)
        }
        trips.append(trip)
    return trips

def save_csv(filename, data):
    if not data: return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Salvo: {filename}")

# Execução
drivers = generate_drivers(NUM_DRIVERS)
passengers = generate_passengers(NUM_PASSENGERS)
trips = generate_trips(NUM_TRIPS, [d['driver_id'] for d in drivers], [p['passenger_id'] for p in passengers])

save_csv('datasets/raw_drivers.csv', drivers)
save_csv('datasets/raw_passengers.csv', passengers)
save_csv('datasets/raw_trips.csv', trips)