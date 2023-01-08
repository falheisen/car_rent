###############################################################################################################
## 
## drivy_backend_challenge - level 5
## Author: Filipe Penna Ceravolo Soares
## Date: 08/01/2023
##
###############################################################################################################

### LIBRARIES

from datetime import datetime
import json
from operator import attrgetter
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

### CLASSES

class Car:

    def __init__(self, id, price_per_day, price_per_km):

        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

    # print object's attributes
    def display_car(self):

        car = {
            'id':self.id,
            'price_per_day': self.price_per_day,
            'price_per_km': self.price_per_km
        }
        print('Car:', car)

class Option:

    def __init__(self, id, rental_id, type):

        self.id = id
        self.rental_id = rental_id
        self.type = type

    # print object's attributes
    def display_option(self):

        option = {
            'id':self.id,
            'rental_id':self.rental_id,
            'type':self.type
        }
        print('Option:', option)

class Rental:

    def __init__(self, id, car_id, start_date, end_date, distance):

        self.id = id    
        self.car_id = car_id    
        self.start_date = start_date
        self.end_date = end_date
        self.distance = distance
        self.duration_days = 1 + (datetime.strptime(self.end_date, '%Y-%m-%d') - datetime.strptime(self.start_date, '%Y-%m-%d')).days
        self.driver_total_price = 0
        self.profit = 0
        self.commission_insurance = 0
        self.commission_assistance = 0
        self.commission_drivy = 0
        self.options = []

    # print object's attributes
    def display_rental(self):

        rental = {
            'id': self.id,
            'car_id': self.car_id,
            'start_date': self.start_date, 
            'end_date': self.end_date, 
            'distance': self.distance,
            'driver_total_price': self.driver_total_price,
            "profit": self.profit,
            "commission_insurance": self.commission_insurance,
            "commission_assistance": self.commission_assistance,
            "commission_drivy": self.commission_drivy
        }

        print('Rental:', rental)

    # set the money related values to the chosen options
    def set_options(self, Option):

        option_type = Option.type

        self.options.append(option_type)

        if option_type == 'gps':

            additional_cost = 500 * self.duration_days
            self.profit += additional_cost
            self.driver_total_price += additional_cost

        elif option_type == 'baby_seat':

            additional_cost = 200 * self.duration_days
            self.profit += additional_cost
            self.driver_total_price += additional_cost

        elif option_type == 'additional_insurance':

            additional_cost = 1000 * self.duration_days
            self.commission_drivy += additional_cost
            self.driver_total_price += additional_cost

    # set all money related final parameters
    def set_price(self, Car):
        
        """
            define :
            - total price to driver (must be executed after set options),
            - profit 
            - assistance commission 
            - insurance commission
            - drivy commission

        """
 
        rental_price = [Car.price_per_day] * self.duration_days
        for i, price in enumerate(rental_price):
            if i >= 10: 
                rental_price[i] = price * 0.5
            elif i >= 4:
                rental_price[i] = price * 0.7
            elif i >= 1:
                rental_price[i] = price * 0.9

        time_component = sum(rental_price)
        distance_component = Car.price_per_km * self.distance
        driver_base_price = time_component + distance_component

        total_comission = 0.3 * driver_base_price
        insurance_fee =  0.5 * total_comission
        assistance_fee = 100 * self.duration_days
        drivy_fee = total_comission - insurance_fee - assistance_fee
        profit = driver_base_price - total_comission

        self.profit += profit
        self.driver_total_price += driver_base_price 
        self.commission_assistance = assistance_fee
        self.commission_insurance = insurance_fee
        self.commission_drivy += drivy_fee

###############################################################################################################
##
## Data extraction
##
###############################################################################################################

f = open('data/input.json')
data = json.load(f)

data_categories = {'cars','rentals','options'}
cars = []
rentals = []
options = []

print('Input:')

for categorie in data_categories:

    for instance in data[categorie]:

        if categorie == 'cars':

            cars.append(
                Car(
                    id = instance['id'],
                    price_per_day = instance['price_per_day'],
                    price_per_km = instance['price_per_km']
                )
            )

            cars[-1].display_car()
        
        if categorie == 'rentals':

            rentals.append(
                Rental(
                    id = instance['id'],
                    car_id = instance['car_id'],
                    start_date = instance['start_date'],
                    end_date = instance['end_date'],
                    distance = instance['distance']
                )
            )

            rentals[-1].display_rental()

        if categorie == 'options':

            options.append(
                Option(
                    id = instance['id'],
                    rental_id = instance['rental_id'],
                    type = instance['type']
                )
            )

            options[-1].display_option()
            
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

# find target object from its id (binary research)
def find_object(object_list, query_id):

    low = 0
    high = len(object_list) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
 
        # If x is greater, ignore left half
        if object_list[mid].id < query_id:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif object_list[mid].id > query_id:
            high = mid - 1
 
        # means x is present at mid
        else:
            return object_list[mid]
 
    # If we reach here, then the element was not present
    return -1

# create json output
def export_output(rentals, filename):

    output_data = []
    for rental in rentals:

        output_data.append(
            {
                'id': rental.id, 
                'options': rental.options,
                'actions': [
                    {
                        "who": "driver",
                        "type": "debit",
                        "amount": round(rental.driver_total_price)
                    },
                    {
                        "who": "owner",
                        "type": "credit",
                        "amount": round(rental.profit)
                    },
                    {
                        "who": "insurance",
                        "type": "credit",
                        "amount": round(rental.commission_insurance)
                    },
                    {
                        "who": "assistance",
                        "type": "credit",
                        "amount": round(rental.commission_assistance)
                    },
                    {
                        "who": "drivy",
                        "type": "credit",
                        "amount": round(rental.commission_drivy)
                    }
                ]
            }
        )    

    export_data = json.dumps({'rentals': output_data}, indent = 2)

    with open(filename, "w") as outfile:
        outfile.write(export_data)

###############################################################################################################
##
## Execute calculation and create output
##
###############################################################################################################

sort_ids(cars)
sort_ids(rentals)
sort_ids(options)
print('Price calculation:')

for option in options:

    right_rental = find_object(rentals, option.rental_id)
    right_rental.set_options(option)
    right_rental.display_rental()

for rental in rentals:

    right_car = find_object(cars, rental.car_id) # assuming that the id always exists
    rental.set_price(right_car)
    rental.display_rental()

export_output(rentals, "data/output.json")


