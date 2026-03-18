import os
import sqlite3
import requests

def fix_4d_resolver(address):
    # 1. Check for Key
    api_key = os.getenv('SKYPIX_MAPS_KEY')
    if not api_key:
        print("!! DIAGNOSTIC: SKYPIX_MAPS_KEY is MISSING from this environment.")
        return

    print(f"--- 4D RESOLVER START ---")
    print(f"Target Address: {address}")
    
    # 2. Make the Request
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        
        # 3. Analyze Response
        status = data.get('status')
        print(f"Google API Status: {status}")
        
        if status == 'OK':
            results = data['results'][0]
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
            fmt_address = results['formatted_address']
            
            print(f"✓ Resolved: {fmt_address}")
            print(f"✓ Coordinates: {lat}, {lng}")
            
            # 4. Commit to Authority
            conn = sqlite3.connect("skypix_config.db")
            conn.execute("UPDATE setup_parameters SET user_address=?, default_lat=?, default_long=? WHERE id=1", (fmt_address, lat, lng))
            conn.commit()
            conn.close()
            print("✓ Database updated successfully.")
            
        elif status == 'REQUEST_DENIED':
            print(f"!! DENIED: {data.get('error_message', 'Check API restrictions or billing.')}")
        else:
            print(f"!! UNEXPECTED STATUS: {status}")
            
    except Exception as e:
        print(f"!! NETWORK ERROR: {e}")

if __name__ == "__main__":
    # USER: Replace with your actual test address
    fix_4d_resolver("1600 Amphitheatre Parkway, Mountain View, CA")