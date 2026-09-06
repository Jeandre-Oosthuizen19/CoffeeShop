
import googlemaps
import sys
import os


API_KEY = os.environ.get ("GOOGLE_MAPS_API_KEY", "")
SEARCH_RADIUS_METERS = 2500
MAX_RESULTS_TO_SHOW = 10


def get_coordinates(gmaps_client, place_name):
    result = gmaps_client.geocode(place_name)
    if not result:
        return None, None
    location = result[0]["geometry"]["location"]
    formatted_address = result[0]["formatted_address"]
    return (location["lat"], location["lng"]), formatted_address


def find_coffee_shops(gmaps_client, lat_lng, radius=SEARCH_RADIUS_METERS):
    response = gmaps_client.places_nearby(
        location=lat_lng,
        radius=radius,
        type="cafe",
        keyword="coffee"
    )
    results = response.get("results", [])


    while "next_page_token" in response:
        import time
        time.sleep(2)  # required delay before token becomes valid
        response = gmaps_client.places_nearby(
            page_token=response["next_page_token"]
        )
        results.extend(response.get("results", []))

    return results


def display_results(shops):

    if not shops:
        print("\nNo coffee shops found nearby. Try a different suburb or wider radius.")
        return


    shops_sorted = sorted(
        shops,
        key=lambda s: s.get("rating", 0),
        reverse=True
    )

    print(f"\nFound {len(shops_sorted)} coffee shop(s):\n")
    for i, shop in enumerate(shops_sorted[:MAX_RESULTS_TO_SHOW], start=1):
        name = shop.get("name", "Unknown")
        address = shop.get("vicinity", "Address not available")
        rating = shop.get("rating", "N/A")
        total_ratings = shop.get("user_ratings_total", 0)
        open_now = shop.get("opening_hours", {}).get("open_now")

        status = ""
        if open_now is True:
            status = " (Open now)"
        elif open_now is False:
            status = " (Closed now)"

        print(f"{i}. {name}{status}")
        print(f"   {address}")
        print(f"   Rating: {rating} ({total_ratings} reviews)")
        print()


def main():
    if not API_KEY:
        print("ERROR: No API key found.")
        print("Set the GOOGLE_MAPS_API_KEY environment variable, or edit API_KEY in this script.")
        sys.exit(1)

    gmaps_client = googlemaps.Client(key=API_KEY)

    suburb = input("Enter a suburb, city, or address: ").strip()
    if not suburb:
        print("No location entered. Exiting.")
        sys.exit(1)

    coords, formatted_address = get_coordinates(gmaps_client, suburb)
    if coords is None:
        print(f"Could not find a location matching '{suburb}'. Try being more specific.")
        sys.exit(1)

    print(f"\nSearching for coffee shops near: {formatted_address}")
    print(f"(lat: {coords[0]:.5f}, lng: {coords[1]:.5f})")

    shops = find_coffee_shops(gmaps_client, coords)
    display_results(shops)


if __name__ == "__main__":
    main()