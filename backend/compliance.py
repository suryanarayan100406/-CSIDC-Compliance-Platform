def legal_risk_classifier(built_percentage):
    """
    Classifies legal severity based on built-up percentage.
    """

    if built_percentage > 85:
        severity = "Critical Encroachment"
        risk_score = 4
    elif built_percentage > 70:
        severity = "Major Violation"
        risk_score = 3
    elif built_percentage > 40:
        severity = "Moderate Deviation"
        risk_score = 2
    elif built_percentage > 20:
        severity = "Minor Deviation"
        risk_score = 1
    else:
        severity = "Underutilized / Partial Construction"
        risk_score = 2

    return severity, risk_score


def smart_recommendation_engine(severity, risk_score):

    if risk_score == 4:
        action = "Immediate Legal Notice & Drone Verification"
        urgency = "Within 7 Days"

    elif risk_score == 3:
        action = "Issue Show-Cause Notice & Schedule Inspection"
        urgency = "Within 15 Days"

    elif risk_score == 2:
        action = "Review Allotment Compliance & Conduct Field Visit"
        urgency = "Within 30 Days"

    else:
        action = "Continue Monitoring"
        urgency = "Quarterly Review"

    return action, urgency
