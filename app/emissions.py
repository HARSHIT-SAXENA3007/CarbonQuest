def calculate_transport_emission(km):
    return km * 0.21

def calculate_energy_emission(kwh):
    return kwh * 0.85

def calculate_food_emission(meals_per_week):
    return meals_per_week * 4 * 2.5

def calculate_shopping_emission(inr_spent):
    return inr_spent * 0.02

def calculate_emissions(data):
    km = data['km']
    kwh = data['kwh']
    meat_meals = data['meat_meals']
    inr = data['inr']

    transport = calculate_transport_emission(km)
    energy = calculate_energy_emission(kwh)
    food = calculate_food_emission(meat_meals)
    shopping = calculate_shopping_emission(inr)

    total = transport + energy + food + shopping
    emissions = {
        'Transport': transport,
        'Electricity': energy,
        'Food': food,
        'Shopping': shopping,
        'Total': total
    }

    highest = max(emissions, key=lambda x: emissions[x] if x != "Total" else -1)
    
    return emissions, highest
