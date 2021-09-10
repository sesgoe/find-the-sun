from flask import Flask, request
import requests
import os
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class Weather:
    id: int
    main: str
    description: str


@dataclass
class City:
    name: str
    lat: float
    lon: float
    distance: float
    weather: Weather


@dataclass
class Location:
    lat: float
    lon: float


WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')


def angle_radians(degrees: float):
    return (math.pi / 180) * degrees


def distance(lat1: float, lon1: float, lat2: float, lon2: float):
    lat1_radians = angle_radians(lat1)
    lat2_radians = angle_radians(lat2)

    lon1_radians = angle_radians(lon1)
    lon2_radians = angle_radians(lon2)

    # pulled this great circle distance from: http://edwilliams.org/avform147.htm
    radians = math.acos(math.sin(lat1_radians)*math.sin(lat2_radians)+math.cos(lat1_radians)
                        * math.cos(lat2_radians)*math.cos(lon1_radians-lon2_radians))

    return radians * 3959  # earth radius in miles


def build_cities_list(citiesResponse, location: Location):
    cities: list[City] = []
    # unsure how to do this idiomatically in Python, probably a more efficient way (that also handles errors gracefully)
    for c in citiesResponse:
        name = c['name']
        lat = c['coord']['lat']
        lon = c['coord']['lon']
        weather_id = c['weather'][0]['id']
        weather_main = c['weather'][0]['main']
        weather_description = c['weather'][0]['description']
        d = distance(location.lat, location.lon, lat, lon)
        cities.append(City(name, lat, lon, d, Weather(
            weather_id, weather_main, weather_description)))
    return cities


# yay for Option[T] type hinting
def get_closest_sunny_city(cities: "list[City]") -> Optional[City]:
    # I find the `lambda <stuff>` syntax to be weird...who wants to type out `lambda` every time?
    cities.sort(key=lambda x: x.distance)
    for c in cities:
        if(c.weather.main == "Clear"):  # not a whole lot of API docs on the possible values for this -- from my basic testing, this gets the job done
            return c
    return None


def get_closest_sunny_city_for_location(loc: Location):
    count = 50  # pull max amount of cities to hopefully hit a positive result
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/find?lat={loc.lat}&lon={loc.lon}&count={count}&appid={WEATHER_API_KEY}&units=imperial")
    cities: list[City] = build_cities_list(
        response.json()['list'], loc)
    return get_closest_sunny_city(cities)


app = Flask(__name__)


# want this to be a simple POST with {lat: number, lon: number}
@app.route("/closest-sunny-city", methods=['POST'])
def closest_sunny_city():

    # probably an idiomatic way to do this that gracefully handles parsing errors
    closestCity = get_closest_sunny_city_for_location(Location(**request.json))

    if closestCity is not None:
        return {'result': 'success', 'data': closestCity}
    else:
        return {'result': 'failure'}
