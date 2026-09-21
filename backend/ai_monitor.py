def analyze_transfer(file_size: int, access_hour: int = 12,
                     failed_login_attempts: int = 0) -> dict:
    # Simple educational risk heuristic.
    # Replace this function with the trained Isolation Forest model later.
    risk_points = 0

    if file_size > 25 * 1024 * 1024:
        risk_points += 2
    if access_hour < 6 or access_hour > 22:
        risk_points += 2
    if failed_login_attempts >= 3:
        risk_points += 2

    if risk_points >= 4:
        label = "Review required"
    elif risk_points >= 2:
        label = "Monitor"
    else:
        label = "No anomaly flagged"

    return {
        "risk_points": risk_points,
        "risk_label": label,
    }
