import requests
from flask import Flask, jsonify

app = Flask(__name__)

NWS_API_URL = "https://api.weather.gov/alerts/active?area=MS"


@app.route("/")
def home():
  return "Grenada Weather Hotline Server is live!"


@app.route("/check-weather")
def check_weather():
  headers = {
      "User-Agent": "GrenadaMSWeatherHotline/1.0 (contact@yourdomain.com)",
      "Accept": "application/ld+json",
  }

  try:
    response = requests.get(NWS_API_URL, headers=headers, timeout=10)
    if response.status_code != 200:
      return (
          jsonify({
              "status": "error",
              "message": f"NWS API returned status {response.status_code}",
          }),
          500,
      )

    data = response.json()
    features = data.get("features", [])

    grenada_alerts = []
    has_tornado_warning = False

    for alert in features:
      props = alert.get("properties", {})
      area_desc = props.get("areaDesc", "")

      if "Grenada" in area_desc:
        event_name = props.get("event", "")
        # Check if it's a high-priority life safety alert
        is_tornado = "Tornado Warning" in event_name

        if is_tornado:
          has_tornado_warning = True

        grenada_alerts.append({
            "event": event_name,
            "headline": props.get("headline"),
            "description": props.get("description"),
            "severity": props.get("severity"),
            "effective": props.get("effective"),
            "expires": props.get("expires"),
            "priority": "HIGH" if is_tornado else "STANDARD",
        })

    return jsonify({
        "alert_active": len(grenada_alerts) > 0,
        "tornado_warning_active": has_tornado_warning,
        "count": len(grenada_alerts),
        "alerts": grenada_alerts,
    })

  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)