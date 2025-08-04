import requests
import json

linka = '521'

def get_bus_data():
    # The API endpoint (you'll need to provide the actual URL)
    url = "https://mapa.idsbk.sk/navigation/vehicles/nearby?lat=48.286053338636776&lng=17.27099569931395&radius=5.5867589135097853&cityID=-1"  # Replace with your actual API URL

    try:
        # Make the GET request
        response = requests.get(url)

        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            for vehicle in data['vehicles']:
                print(vehicle['timeTableTrip']['timeTableLine']['line'])
                if vehicle['timeTableTrip']['timeTableLine']['line'] != linka:
                    break
                print(f'{linka} meska {vehicle["delayMinutes"]}')


            return data
        else:
            print(f"Error: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    bus_data = get_bus_data()