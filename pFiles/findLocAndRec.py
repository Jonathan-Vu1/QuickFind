import geocoder
from googleplaces import GooglePlaces, types, lang
from geopy.geocoders import Nominatim
import time
import pandas as pd
from pprint import pprint
from csv import reader
from collabRec import makeCollab
from contentRec import makeContent, recommend

# the below code uses an ip address, somewhat inaccurate
# g = geocoder.ip('me')
# print(g.latlng)

API_KEY = ''
google_places = GooglePlaces(API_KEY)
# below are adjustable parameters
#it should be noted that currently the number for MOE is arbitrary,
#but may have to be lowered
def get_address_by_location(latitude, longitude, language="en"):
    app = Nominatim(user_agent="tutorial")
    """This function returns an address as raw from a location
    will repeat until success"""
    # build coordinates string to pass to reverse() function
    coordinates = f"{latitude}, {longitude}" # string format of lat and ling
    try:
        return app.reverse(coordinates, language=language).raw
    except:
        return get_address_by_location(latitude, longitude)

def sameLatLong(lat1, long1, lat2, long2, MOE): 
    return True if abs(lat1 - lat2) < MOE and abs(long1 - long2) < MOE else False

def searchLocationsRec(inputLat, inputLong, myRadius, 
numOfSug, myCity, myState, userID, collabAttribute, contentAttributes, marginOfError = 0.03):
    # startTime = time.process_time()
    print(f'Starting searchLocationsRec')
    # print(f'Type: {typeList}')
    query_result = google_places.nearby_search( # searches nearby places, takes a type of location
		lat_lng= {'lat': inputLat, 'lng': inputLong}, #Madison, Wisconscin
		#lat_lng ={'lat': g.lat, 'lng': g.lng},
		radius = myRadius, #radius in meters
		type = collabAttribute) # this should NOT be types

    if query_result.has_attributions:
        print(query_result.html_attributions)
    placeNames = []
    # app = Nominatim(user_agent="tutorial")
    placeCoords = [] # stores place coords, tuples of lat and lng
    # placeAddresses= []
    for place in query_result.places:
        #print(place)
        # print(place.name)
        placeNames.append(place.name)
        placeCoords.append((place.geo_location['lat'], place.geo_location['lng']))
        #print("Latitude", place.geo_location['lat'])
        #print("Longitude", place.geo_location['lng'])
        # address = get_address_by_location(place.geo_location['lat'],place.geo_location['lng'])['display_name']
        # placeAddresses.append(address)
        #print()
    # print(placeNames)
    # print(place
    # Iterate over the search results, prints lat, lng, and address
    realPlaces = []
    realCoords = []
    realAddresses= []
    businessIds = []
    with open(f'../csvFiles/b{myCity.lower()[:3]}_{myState.lower()[:3]}.csv', 'r', encoding="utf-8") as file:
        data = list(reader(file))[1:]
        print('l')
        for i, v in enumerate(data):
            if v[1][1:-1] in placeNames and v[1][1:-1] not in realPlaces:
                if sameLatLong(float(v[5]), float(v[6]), 
                inputLat, inputLong, marginOfError):
                    realPlaces.append(v[1][1:-1])
                    myI = realPlaces.index(v[1][1:-1])
                    realCoords.append((float(placeCoords[myI][0]), float(placeCoords[myI][1])))
                    realAddresses.append(v[2]) # add stuff
                    businessIds.append(v[0])
    # print(realPlaces)
    # print(placeNames)
    # print(realCoords)
    # print(businessIds)
    # currently, the next goal is to try to filter the review data so it
    collabResults = [] 
    algo = makeCollab(myCity=myCity, myState=myState)
    print(contentAttributes)
    ds, results = makeContent(myCity=myCity, myState=myState, categories=contentAttributes)
    # only uses the places in Madison
    for i, v in enumerate(businessIds):
        prediction = algo.predict(userID, v)
        collabResults.append((realPlaces[i], realAddresses[i][1:-1], prediction.est))
        # print(f'Collab: {realPlaces[i]} - {prediction.est}')
    contentResults = recommend(ds, results, "addedCategory", numOfSug)
    # print(collabResults)
    # print(contentResults)
    return collabResults, contentResults
    # print(f'findandrec done in {time.process_time()-startTime:.3}s')

# searchLocationsRec(inputLat=43.0848679, inputLong=-89.376, myRadius=5000, 
# marginOfError=0.03, contentAttributes=['Ice Cream & Frozen Yogurt'], numOfSug=10,
# myCity="Madison", myState="Wisconsin", userID ='KoY4KGxev8gdg5qQpyDlZA', typeList=types.TYPE_GAS_STATION)
# algo = makeCollab(myCity='Madison', myState='Wisconsin')
