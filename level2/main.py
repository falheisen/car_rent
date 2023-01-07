###############################################################################################################
## 
## drivy_backend_challenge - level 1
## Author: Filipe Penna Ceravolo Soares
## Date: 07/01/2023
##
###############################################################################################################

### LIBRARIES

from datetime import datetime
import json
from operator import attrgetter
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

class Car:
    def __init__(self, id, price_per_day, price_per_km):
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

    def get_car(self):
        car = {'id':self.id,
               'price_per_day':self.price_per_day,
               'price_per_km':self.price_per_km}
        print('Car:', car)

class Rental:
    def __init__(self, id, car_id, start_date, end_date, distance):
        self.id = id    
        self.car_id = car_id    
        self.start_date = start_date
        self.end_date = end_date
        self.distance = distance
        self.duration_days = 1 + (datetime.strptime(self.end_date, '%Y-%m-%d') - datetime.strptime(self.start_date, '%Y-%m-%d')).days
        self.price = 0 

    def get_rental(self):
        rental = {'id':self.id,
                  'car_id':self.car_id,
                  'start_date':self.start_date, 
                  'end_date':self.end_date, 
                  'distance':self.distance,
                  'price':self.price}
        print('Rental:', rental)
    
    def set_price(self, price):
        self.price = price

###############################################################################################################
##
## Data extraction
##
###############################################################################################################

f = open('data/input.json')
data = json.load(f)

data_categories = {'cars','rentals'}
cars = []
rentals = []

print('Input:')

for categorie in data_categories:

    for instance in data[categorie]:
        # print(instance)

        if categorie == 'cars':
            cars.append(
                Car(id = instance['id'],
                    price_per_day = instance['price_per_day'],
                    price_per_km = instance['price_per_km']
                )
            )
            cars[-1].get_car()
        
        if categorie == 'rentals':
            rentals.append(
                Rental(id = instance['id'],
                       car_id = instance['car_id'],
                       start_date = instance['start_date'],
                       end_date = instance['end_date'],
                       distance = instance['distance']
                )
            )
            rentals[-1].get_rental()
            
f.close()

print('')

###############################################################################################################
##
## Find the right car to a given rental
##
###############################################################################################################

# sort objects by id
def sort_ids(array):   
    array.sort(key = attrgetter("id"))

# find right object (binary research)
def find_car(cars, rent):

    low = 0
    high = len(cars) - 1
    mid = 0

    id_target = rent.car_id
 
    while low <= high:
 
        mid = (high + low) // 2
 
        # If x is greater, ignore left half
        if cars[mid].id < id_target:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif cars[mid].id > id_target:
            high = mid - 1
 
        # means x is present at mid
        else:
            return cars[mid]
 
    # If we reach here, then the element was not present
    return -1

# get rental price from a rent
def get_price(car, rent):

    rental_days = rent.duration_days
    rental_price = [car.price_per_day] * rental_days
    for i, price in enumerate(rental_price):
        if i >= 10: 
            rental_price[i] = price * 0.5
        elif i >= 4:
            rental_price[i] = price * 0.7
        elif i >= 1:
            rental_price[i] = price * 0.9

    time_component = sum(rental_price)
    distance_component = car.price_per_km * rent.distance

    return int(time_component + distance_component)

# rental_days = 15
# car_price = 1000
# rental_price = [car_price] * rental_days
# for i, price in enumerate(rental_price):
#     if i >= 10: 
#         rental_price[i] = price * 0.5
#     elif i >= 4:
#         rental_price[i] = price * 0.7
#     elif i >= 1:
#         rental_price[i] = price * 0.9

# create json output
def export_output(rentals, filename):

    output_data = []
    for rental in rentals:

        output_data.append({'id': rental.id, 'price': rental.price})
    
    export_data = json.dumps({'rentals': output_data}, indent = 2)

    with open(filename, "w") as outfile:
        outfile.write(export_data)

###############################################################################################################
##
## Execute calculation and create output
##
###############################################################################################################

sort_ids(cars)
rental_info = []
print('Price calculation:')

for rental in rentals:

    right_car = find_car(cars, rental) # assuming that the id always exists
    price = get_price(right_car, rental)
    rental.set_price(price)
    rental.get_rental()

export_output(rentals, "data/output.json")


