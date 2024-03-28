from PredictionFunction.PredictionFiles.LosTacos.bergen import location_function as bergen_function
from PredictionFunction.PredictionFiles.LosTacos.fredrikstad import location_function as fredrikstad_function
from PredictionFunction.PredictionFiles.LosTacos.karl_johan import location_function as karl_johan_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_city import location_function as oslo_city_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_lokka import location_function as oslo_lokka_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_smestad import location_function as oslo_smestad_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_steenstrom import location_function as oslo_steenstrom_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_storo import location_function as oslo_storo_function
from PredictionFunction.PredictionFiles.LosTacos.oslo_torggata import location_function as oslo_torggata_function
from PredictionFunction.PredictionFiles.LosTacos.sandnes import location_function as sandnes_function
from PredictionFunction.PredictionFiles.LosTacos.stavanger import location_function as stavanger_function


# This is a datatable showing which city each restaurant locations is in
data = [
   {"Restaurant": "Oslo Storo", "City": "Oslo", "Company": "Los Tacos"},
    {"Restaurant": "Oslo City", "City": "Oslo", "Company": "Los Tacos"},
     {"Restaurant": "Oslo Torggata", "City": "Oslo", "Company": "Los Tacos"},
     {"Restaurant": "Karl Johan", "City": "Oslo", "Company": "Los Tacos"},
   {"Restaurant": "Fredrikstad", "City": "Fredrikstad", "Company": "Los Tacos"},
   {"Restaurant": "Oslo Lokka", "City": "Oslo", "Company": "Los Tacos"},
    {"Restaurant": "Stavanger", "City": "Stavanger", "Company": "Los Tacos"},
    {"Restaurant": "Bergen", "City": "Bergen", "Company": "Los Tacos"},
   {"Restaurant": "Oslo Steen_Strom", "City": "Oslo", "Company": "Los Tacos"},
    {"Restaurant": "Oslo Smestad", "City": "Oslo", "Company": "Los Tacos"},
    {"Restaurant": "Sandnes", "City": "Stavanger", "Company": "Los Tacos"},

]
location_specific_dictionary = {
    "Stavanger": stavanger_function,
    "Bergen": bergen_function,
    "Fredrikstad": fredrikstad_function,
    "Oslo Lokka": oslo_lokka_function,
    "Oslo Smestad": oslo_smestad_function,
    "Oslo Torggata": oslo_torggata_function,
    "Oslo Storo": oslo_storo_function,
    "Oslo City": oslo_city_function,
    "Oslo Steen_Strom": oslo_steenstrom_function,
    "Karl Johan": karl_johan_function,
    "Sandnes": sandnes_function,
}
# OBS! for Drammen and Fredrikstad i had trouble finding good weather data, so used Oslo
weather_locations = {
    "Stavanger": {"source_id": "SN44560", "lat": "58.969976", "lon": "5.733107"},
    "Bergen": {"source_id": "SN50540", "lat": "60.391263", "lon": "5.322054"},
    "Fredrikstad": {"source_id": "SN18700", "lat": "59.913868", "lon": "10.752245"},
    "Drammen": {"source_id": "SN18700", "lat": "59.913868", "lon": "10.752245"},
    "Oslo": {"source_id": "SN18700", "lat": "59.913868", "lon": "10.752245"},
}