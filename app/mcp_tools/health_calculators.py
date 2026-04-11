def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    Calculate Body Mass Index (BMI).
    Formula: weight (kg) / height (m)^2

    Returns BMI value and WHO classification.
    """
    if weight_kg <= 0 or height_cm <= 0:
        return {"error": "Weight and height must be positive numbers."}

    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        advice = "Consider consulting a doctor or nutritionist to reach a healthy weight."
    elif bmi < 25.0:
        category = "Normal weight"
        advice = "You are within the healthy BMI range. Maintain your current lifestyle."
    elif bmi < 30.0:
        category = "Overweight"
        advice = "Consider a balanced diet and regular exercise. Consult a doctor if needed."
    else:
        category = "Obese"
        advice = "Please consult a healthcare provider for a personalized weight management plan."

    return {
        "bmi":      bmi,
        "category": category,
        "advice":   advice,
        "formula":  f"{weight_kg}kg / ({height_cm/100}m)^2 = {bmi}"
    }


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age_years: int,
    gender: str,
    activity_level: str = "moderate"
) -> dict:
    """
    Calculate Basal Metabolic Rate (BMR) and daily calorie needs.
    Uses the Mifflin-St Jeor equation (most accurate for general population).

    activity_level options:
        sedentary   — little or no exercise
        light       — light exercise 1-3 days/week
        moderate    — moderate exercise 3-5 days/week
        active      — hard exercise 6-7 days/week
        very_active — very hard exercise + physical job
    """
    if weight_kg <= 0 or height_cm <= 0 or age_years <= 0:
        return {"error": "All values must be positive numbers."}

    gender = gender.lower()
    if gender not in ("male", "female"):
        return {"error": "Gender must be 'male' or 'female'."}

    # Mifflin-St Jeor formula
    if gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161

    activity_multipliers = {
        "sedentary":   1.2,
        "light":       1.375,
        "moderate":    1.55,
        "active":      1.725,
        "very_active": 1.9,
    }
    multiplier = activity_multipliers.get(activity_level, 1.55)
    tdee = round(bmr * multiplier)  # Total Daily Energy Expenditure

    return {
        "bmr":              round(bmr),
        "daily_calories":   tdee,
        "activity_level":   activity_level,
        "to_lose_weight":   tdee - 500,   # 500 kcal deficit = ~0.5kg/week loss
        "to_gain_weight":   tdee + 500,
        "unit":             "kcal/day"
    }


def calculate_ideal_weight(height_cm: float, gender: str) -> dict:
    """
    Calculate Ideal Body Weight using the Devine formula.
    Widely used in clinical settings for medication dosing.

    Devine formula:
        Male:   IBW = 50 + 2.3 * (height_inches - 60)
        Female: IBW = 45.5 + 2.3 * (height_inches - 60)
    """
    if height_cm <= 0:
        return {"error": "Height must be a positive number."}

    gender = gender.lower()
    if gender not in ("male", "female"):
        return {"error": "Gender must be 'male' or 'female'."}

    height_inches = height_cm / 2.54

    if height_inches < 60:
        return {"error": "Devine formula is only valid for height >= 152 cm (60 inches)."}

    if gender == "male":
        ibw = 50 + 2.3 * (height_inches - 60)
    else:
        ibw = 45.5 + 2.3 * (height_inches - 60)

    ibw = round(ibw, 1)

    return {
        "ideal_weight_kg": ibw,
        "ideal_weight_lbs": round(ibw * 2.205, 1),
        "formula": "Devine Formula",
        "note": "This is a general estimate. Healthy weight varies by body composition."
    }
