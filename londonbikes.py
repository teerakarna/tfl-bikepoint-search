#!/usr/bin/env python3

from math import radians, cos, sin, asin, sqrt
import os
import re
import requests
import sys

# bikepoint_url = os.environ['BIKEPOINT_URL']
# tfl_app_id = os.environ['TFL_APP_ID']
# tfl_app_key = os.environ['TFL_APP_KEY']
bikepoint_url = 'https://api.tfl.gov.uk/BikePoint'
tfl_app_id = ''
tfl_app_key = ''
tfl_creds = {'app_id': tfl_app_id, 'app_key': tfl_app_key}


# Haversine formula to calculate distance between two latitude/longitude
# coordinates on the surface of a sphere (Earth)
def haversine(lat1, lon1, lat2, lon2):
	lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
	archav = 2 * asin(sqrt(
		sin((lat2 - lat1)/2)**2 + 
		cos(lat1) * cos(lat2) * 
		sin((lon2 - lon1)/2)**2))
	earth_radius = 6371 * 1000
	return archav * earth_radius


# Dynamically generates a list of the max widths of each index (column) in
# a nested list; for use with .format() method
def col_width(my_lists):
	max_width = [0] * len(my_lists[0])
	col_width = ""
	for r in my_lists:
		for e in r:
			position = r.index(e)
			length = len(e)
			if max_width[position] < length:
				max_width[position] = length
	for i in range(len(max_width)):
		col_width += '{:' + str(max_width[i] + 4) + '}'
	return col_width


# Prints the help message
def print_help():
	print(
'''
Usage: 
	londonbikes search <search_string> 
	londonbikes search <latitude> <longitude> <radius_in_metres> 
	londonbikes id <bike_point_id>
'''
		)
	sys.exit(1)


if len(sys.argv) > 1:
	# Handles the search argument
	if sys.argv[1] == 'search':
		# Make sure GET yields a 200 HTTP response and store the payload as a
		# dictionary, otherwise print response code and exit
		bikepoints = requests.get(bikepoint_url, tfl_creds)
		if bikepoints.status_code == 200:
			bikepoints_json = bikepoints.json()
		else:
			print(bikepoints)
			sys.exit(1)
		# If no argument after search, print message and exit
		if len(sys.argv) == 2:
			print('Please specify a search term')
			sys.exit(10)
		# Conditional for a single argument after search
		elif len(sys.argv) == 3:
			search_term = sys.argv[2]
			# Create the nested list stub with the column headers
			search_name = [['ID', 'Name', 'Latitude', 'Longitude']]
			for bikepoint in bikepoints_json:
				# Match search term (case insensitive) with commonName field
				if re.search(search_term, bikepoint['commonName'], re.IGNORECASE):
					# Append list of components as strings to the nested list
					search_name.append(
						[bikepoint['id'],
						bikepoint['commonName'],
						str(bikepoint['lat']),
						str(bikepoint['lon'])])
			# Loop through each line of the completed nested list and print
			# formatted by col_width function
			for i in range(len(search_name)):
				print(col_width(search_name).format(
					search_name[i][0],
					search_name[i][1],
					search_name[i][2],
					search_name[i][3]))
		# Condition to handle search for bike point within an area defined by
		# a given distance from a geographic co-ordinate
		elif len(sys.argv) == 5:
			# Test that arguments can be converted to float
			try:
				my_lat = float(sys.argv[2])
				my_lon = float(sys.argv[3])
				my_dis = float(sys.argv[4])
			except:
				print('The search request is invalid')
				sys.exit(11)
			# Similar routine as before with search_term, but with different
			# components in nested list and using the haversine function to
			# calculate conditional based on distance
			search_distance = [['ID', 'Name', 'Latitude,Longitude', 'Distance (m)']]
			for bikepoint in bikepoints_json:
				location_name = bikepoint['commonName']
				bp_lat = bikepoint['lat']
				bp_lon = bikepoint['lon']
				distance = haversine(my_lat, my_lon, bp_lat, bp_lon)
				if distance <= my_dis:
					search_distance.append(
						[bikepoint['id'],
						bikepoint['commonName'],
						str(bikepoint['lat']) + "," + str(bikepoint['lon']),
						str(round(distance,1))])
			for i in range(len(search_distance)):
				print(col_width(search_distance).format(
					search_distance[i][0],
					search_distance[i][1],
					search_distance[i][2],
					search_distance[i][3]))
		# Anything else after search will print this message and exit
		else:
			print('The search request is invalid')
			sys.exit(11)
	# Handles id argument
	elif sys.argv[1] == 'id':
		# If no argument after id, print message and exit
		if len(sys.argv) == 2:
			print('Please specify a bike point ID')
			sys.exit(12)
		elif len(sys.argv) == 3:
			bpid = sys.argv[2]
			# Construct URL from input argument
			bikepoint_id_url = "{}/{}".format(bikepoint_url, bpid)
			bikepoint_id = requests.get(bikepoint_id_url, tfl_creds)
			# Test HTTP response from GET
			if bikepoint_id.status_code == 404:
				print('Bike point ID ' + bpid + ' not recognised')
				sys.exit(13)
			elif bikepoint_id.status_code == 200:
				bikepoint_id_json = bikepoint_id.json()
			else:
				print(bikepoint_id)
				sys.exit(1)
			# Same routine as in previous search conditions
			search_id = [['Name', 'Latitude', 'Longitude', 'Bikes', 'Empty Docks']]
			for property in bikepoint_id_json['additionalProperties']:
				if property['key'] == "NbBikes":
					bikes = property['value']
				elif property['key'] == "NbEmptyDocks":
					empty_docks = property['value']
			search_id.append(
				[bikepoint_id_json['commonName'],
				str(bikepoint_id_json['lat']),
				str(bikepoint_id_json['lon']),
				str(bikes),
				str(empty_docks)])
			for i in range(len(search_id)):
				print(col_width(search_id).format(
					search_id[i][0],
					search_id[i][1],
					search_id[i][2],
					search_id[i][3],
					search_id[i][4]))
		else:
			print_help()
	else:
		print_help()
else:
	print_help()
