import requests
import json


def get_bus_data():
    # The API endpoint (you'll need to provide the actual URL)
    url = "https://mapa.idsbk.sk/navigation/vehicles/get_real?tripID=806089902&firmaID=806&line=527&tripNumber=223"  # Replace with your actual API URL

    try:
        # Make the GET request
        response = requests.get(url)

        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Print the data
            print("Status:", data.get('status'))
            print("Vehicle ID:", data['vehicle'].get('vehicleID'))
            print("Delay Minutes:", data['vehicle'].get('delayMinutes'))
            print("Latitude:", data['vehicle'].get('latitude'))
            print("Longitude:", data['vehicle'].get('longitude'))
            print("License Number:", data['vehicle'].get('licenseNumber'))
            print("Last Communication:", data['vehicle'].get('lastCommunication'))
            print("Last Stop Order:", data['vehicle'].get('lastStopOrder'))
            print("Is On Stop:", data['vehicle'].get('isOnStop'))

            return data
        else:
            print(f"Error: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    bus_data = get_bus_data()