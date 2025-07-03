import os
import csv

def save_user_data(km, kwh, meat_meals, inr, transport, energy, food, shopping):
    file_path = 'data/user_data.csv'
    os.makedirs('data', exist_ok=True)
    header = ['km', 'kwh', 'meat_meals_per_week', 'inr_spent', 'transport_emission', 'energy_emission', 'food_emission', 'shopping_emission']
    row = [km, kwh, meat_meals, inr, transport, energy, food, shopping]
    write_header = not os.path.exists(file_path)

    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)


def calculate_transport_emission(km):
    return km * 0.21

def calculate_energy_emission(kwh):
    return kwh * 0.85

def calculate_food_emission(meals_per_week):
    return meals_per_week * 4 * 2.5  # 4 weeks in a month

def calculate_shopping_emission(inr_spent):
    return inr_spent * 0.02

def main():
    print("🌍 Personal Carbon Footprint Calculator (Monthly Estimate)\n")

    km = float(input("Enter total km traveled by car this month: "))
    kwh = float(input("Enter electricity used in kWh this month: "))
    meat_meals = int(input("Enter meat-based meals per week: "))
    inr = float(input("Enter approx. ₹ spent on clothes/shopping this month: "))

    transport_emission = calculate_transport_emission(km)
    energy_emission = calculate_energy_emission(kwh)
    food_emission = calculate_food_emission(meat_meals)
    shopping_emission = calculate_shopping_emission(inr)

    total = transport_emission + energy_emission + food_emission + shopping_emission

    print("\n📊 Your Monthly CO₂ Emissions Breakdown (in kg):")
    print(f"🚗 Transport: {transport_emission:.2f}")
    print(f"⚡ Electricity: {energy_emission:.2f}")
    print(f"🍗 Food (Meat): {food_emission:.2f}")
    print(f"🛍️ Shopping: {shopping_emission:.2f}")
    print(f"\n🧮 Total Carbon Footprint: {total:.2f} kg CO₂/month")

    # Find highest contributor
    emissions = {
        "Transport": transport_emission,
        "Electricity": energy_emission,
        "Food": food_emission,
        "Shopping": shopping_emission
    }
    highest = max(emissions, key=emissions.get)
    print(f"\n📌 Highest impact area: {highest}")
    suggest_action(highest)
    
    save_user_data(km, kwh, meat_meals, inr,
                   transport_emission, energy_emission, food_emission, shopping_emission)

def suggest_action(area):
    print("💡 Suggested Action Plan:")
    if area == "Transport":
        print("- Try carpooling, cycling, or public transport more often.")
    elif area == "Electricity":
        print("- Switch to energy-efficient appliances and turn off unused devices.")
    elif area == "Food":
        print("- Reduce meat consumption; try plant-based meals once a day.")
    elif area == "Shopping":
        print("- Buy less, choose eco-friendly brands, or thrift.")

if __name__ == "__main__":
    main()
