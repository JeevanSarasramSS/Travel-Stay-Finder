from flask import Flask, request, jsonify, render_template
import requests, math

app = Flask(__name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route('/')
def index(): return render_template('index.html')

@app.route('/search')
def search_location():
    location = request.args.get('location')
    params = {'q': location, 'format': 'json', 'limit': 1, 'addressdetails': 1}
    response = requests.get("https://nominatim.openstreetmap.org/search", params=params)
    results = response.json()

    if results:
        latitude, longitude = results[0]['lat'], results[0]['lon']
        overpass_query = f"""
        [out:json];
        (
          node["tourism"="hotel"](around:50000,{latitude},{longitude});
          way["tourism"="hotel"](around:50000,{latitude},{longitude});
          relation["tourism"="hotel"](around:50000,{latitude},{longitude});
        );
        out body;
        """
        response = requests.get("http://overpass-api.de/api/interpreter", params={'data': overpass_query})
        hotels = response.json()
        hotel_list = []

        if hotels['elements']:
            for hotel in hotels['elements']:
                name = hotel.get('tags', {}).get('name', 'N/A')
                if name != 'N/A':
                    address = hotel.get('tags', {}).get('addr:full', hotel.get('tags', {}).get('addr:street', 'N/A'))
                    hotel_list.append({'name': name, 'address': address if address != 'N/A' else 'Unavailable'})
            return jsonify(hotels=hotel_list)
    return jsonify(hotels=[])

if __name__ == '__main__':
    app.run(debug=True)
