from flask import Flask, request, jsonify
from shapely.geometry import shape
from shapely.ops import transform
import pyproj
import random
from compliance import legal_risk_classifier, smart_recommendation_engine

app = Flask(__name__)


# ==============================
# Utility: Area Calculation
# ==============================

def calculate_area_in_meters(geojson):
    try:
        geom = shape(geojson)

        # Auto-detect correct UTM zone
        utm_crs = pyproj.database.query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=pyproj.aoi.AreaOfInterest(
                west_lon_degree=geom.bounds[0],
                south_lat_degree=geom.bounds[1],
                east_lon_degree=geom.bounds[2],
                north_lat_degree=geom.bounds[3],
            ),
        )[0].code

        project = pyproj.Transformer.from_crs(
            "EPSG:4326",
            pyproj.CRS.from_user_input(utm_crs),
            always_xy=True,
        ).transform

        projected = transform(project, geom)
        return projected.area

    except Exception as e:
        return None


# ==============================
# Routes
# ==============================

@app.route('/')
def home():
    return "THIS IS THE NEW VERSION"


@app.route("/detect-builtup", methods=["POST"])
def detect_builtup():
    try:
        data = request.json
        if not data or "boundary" not in data:
            return jsonify({"error": "Missing boundary GeoJSON"}), 400

        boundary = data["boundary"]
        total_area = calculate_area_in_meters(boundary)

        if total_area is None:
            return jsonify({"error": "Invalid GeoJSON"}), 400

        built_area = total_area * random.uniform(0.4, 0.9)

        return jsonify({
            "total_area_m2": round(total_area, 2),
            "built_up_area_m2": round(built_area, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detect-encroachment", methods=["POST"])
def detect_encroachment():
    try:
        data = request.json
        if not data or "boundary" not in data:
            return jsonify({"error": "Missing boundary GeoJSON"}), 400

        boundary = shape(data["boundary"])

        # Simulated encroachment
        encroach = boundary.buffer(0.0002)
        violation_area = encroach.difference(boundary)

        return jsonify({
            "encroachment_detected": not violation_area.is_empty,
            "encroachment_geojson": violation_area.__geo_interface__
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/compliance-score", methods=["POST"])
def compliance_score():
    try:
        data = request.json

        required_fields = ["total_area_m2", "built_up_area_m2", "encroachment"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        total_area = data["total_area_m2"]
        built_area = data["built_up_area_m2"]
        encroachment = data["encroachment"]
        unused_percentage = data.get("unused_percentage", 0)

        if total_area == 0:
            return jsonify({"error": "Total area cannot be zero"}), 400

        built_percentage = (built_area / total_area) * 100

        severity, risk_score = legal_risk_classifier(built_percentage)
        action, urgency = smart_recommendation_engine(severity, risk_score)

        # --- Enhanced Risk Score (0-100) ---
        score = 100
        if encroachment:
            score -= 40
        if unused_percentage > 20:
            score -= 30
        if 0 < unused_percentage <= 20 or (built_percentage > 70 and built_percentage <= 85):
            score -= 10  # minor deviation

        score = max(score, 0)

        return jsonify({
            "compliance_score": score,
            "built_percentage": round(built_percentage, 2),
            "unused_percentage": round(unused_percentage, 2),
            "severity": severity,
            "risk_score": risk_score,
            "recommended_action": action,
            "urgency": urgency
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/compare-boundaries", methods=["POST"])
def compare_boundaries():
    try:
        data = request.json

        reference = shape(data["reference"])
        current = shape(data["current"])
        tolerance_m2 = data.get("tolerance_m2", 25)

        def project_to_meters(geom):
            project = pyproj.Transformer.from_crs(
                "EPSG:4326",
                "EPSG:32644",  # UTM Zone for Chhattisgarh
                always_xy=True,
            ).transform
            return transform(project, geom)

        encroachment = current.difference(reference)
        unused = reference.difference(current)
        overlap = reference.intersection(current)

        # Project for area calculation
        enc_proj = project_to_meters(encroachment)
        unused_proj = project_to_meters(unused)
        overlap_proj = project_to_meters(overlap)
        ref_proj = project_to_meters(reference)

        enc_area = enc_proj.area
        unused_area = unused_proj.area
        total_ref_area = ref_proj.area

        # Tolerance threshold
        tolerance_applied = False
        if enc_area < tolerance_m2:
            enc_area = 0
            tolerance_applied = True
        if unused_area < tolerance_m2:
            unused_area = 0
            tolerance_applied = True

        # Unused percentage
        unused_percentage = (unused_area / total_ref_area * 100) if total_ref_area > 0 else 0

        return jsonify({
            "encroachment_geojson": encroachment.__geo_interface__,
            "unused_geojson": unused.__geo_interface__,
            "overlap_geojson": overlap.__geo_interface__,
            "encroachment_area": round(enc_area, 2),
            "unused_area": round(unused_area, 2),
            "overlap_area": round(overlap_proj.area, 2),
            "total_reference_area": round(total_ref_area, 2),
            "unused_percentage": round(unused_percentage, 2),
            "tolerance_m2": tolerance_m2,
            "tolerance_applied": tolerance_applied
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# Run Server
# ==============================

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)
