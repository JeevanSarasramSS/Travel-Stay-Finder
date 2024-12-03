import requests, math

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

location = input("Enter location: ")
user_lat = float(input("Enter latitude: ") or 0)
user_lon = float(input("Enter longitude: ") or 0)

params = {'q': location, 'format': 'json', 'limit': 1, 'addressdetails': 1}
response = requests.get("https://nominatim.openstreetmap.org/search", params=params)
results = response.json()

if results:
    latitude, longitude = float(results[0]['lat']), float(results[0]['lon'])
    print(f"Lat: {latitude}, Lon: {longitude}")
    overpass_query = f"""
    [out:json];
    node["tourism"="hotel"](around:50000,{latitude},{longitude});
    way["tourism"="hotel"](around:50000,{latitude},{longitude});
    relation["tourism"="hotel"](around:50000,{latitude},{longitude});
    out body;
    """
    response = requests.get("http://overpass-api.de/api/interpreter", params={'data': overpass_query})
    hotels = response.json()

    if hotels['elements']:
        for hotel in hotels['elements']:
            name = hotel.get('tags', {}).get('name', 'N/A')
            if name != 'N/A':
                hotel_lat, hotel_lon = hotel['lat'], hotel['lon']
                distance = calculate_distance(user_lat, user_lon, hotel_lat, hotel_lon)
                address = hotel.get('tags', {}).get('addr:full', 'Unavailable')
                print(f"Hotel: {name}, Address: {address}, Distance: {distance:.2f} km")
    else:
        print("No hotels found.")
