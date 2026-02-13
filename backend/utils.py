def severity_heatmap(mask, risk_score):
    import cv2

    heatmap = cv2.applyColorMap(mask, cv2.COLORMAP_JET)

    if risk_score == 4:
        label = "CRITICAL ZONE"
    elif risk_score == 3:
        label = "HIGH RISK ZONE"
    elif risk_score == 2:
        label = "MEDIUM RISK ZONE"
    else:
        label = "LOW RISK ZONE"

    return heatmap, label
