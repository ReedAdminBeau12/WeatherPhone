import requests
from flask import Flask, jsonify

app = Flask(__name__)

# National Weather Service API for Mississippi alerts
NWS_API_URL = "https://api.weather.gov/alerts/active?area=MS"


@app.route("/")
def home():
  return (
      "Grenada Weather Hotline Server is live and connected to FlyNumber!"
  )


@app.route("/check-weather")
def check_weather():
  headers = {
      # NWS requires a User-Agent identifying your project/contact
      "User-Agent": (
          "GrenadaMSWeatherHotline/1.0 (contact@yourdomain.com)"
      ),
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
    for alert in features:
      props = alert.get("properties", {})
      area_desc = props.get("areaDesc", "")
      # Check if Grenada is mentioned in the affected area description
      if "Grenada" in area_desc:
        grenada_alerts.append({
            "event": props.get("event"),
            "headline": props.get("headline"),
            "description": props.get("description"),
            "severity": props.get("severity"),
            "effective": props.get("effective"),
            "expires": props.get("expires"),
        })

    if grenada_alerts:
      # Found active weather alerts for Grenada!
      return jsonify({
          "alert_active": True,
          "count": len(grenada_alerts),
          "alerts": grenada_alerts,
      })
    else:
      return jsonify({
          "alert_active": False,
          "message": (
              "No active weather alerts for Grenada, Mississippi right now."
          ),
      })

  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
