import django
from django.conf import settings
django.setup()
from collector.models import PuzzlePiece
from urllib.parse import urlparse
import hashlib
import requests
import getopt
import sys

def hash_my_data(url):
        url = url.encode("utf-8")
        hash_object = hashlib.sha256(url)
        hex_dig = hash_object.hexdigest()
        return hex_dig

def main():
	inputfile = "images.txt"
	priority = 0
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:p:",["ifile=","priority="])
	except getopt.GetoptError:
		print ('bulk_loader.py -i <inputfile> -p <priority as integer>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('bulk_loader.py -i <inputfile> -p <priority as integer>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = str(arg)
		elif opt in ("-p", "--priority"):
			priority = int(arg)
	
	with open(inputfile, "r") as infile:
		data = infile.readlines()

	for line in data:
		try:
			line = line.rstrip()
			if not line:
				continue
			if len(line) > 200:
				raise ValueError('URL too long to fit')
			print(line)
			host = urlparse(line).hostname 
			if host in ["tjl.co","gamerdvr.com","dropbox.com","www.gamerdvr.com","www.dropbox.com"]:
				raise ValueError('We cannot accept images from gamerdvr or dropbox or tjl.co - try another host please, Discord works great!')
			# Check this can be reached
			request = requests.head(line)
			if request.status_code != 200:
				raise ValueError('That URL does not seem to exist. Please verify and try again.')
			i = PuzzlePiece()
			i.url = line
			i.hash = hash_my_data(line)
			i.ip_address = "127.0.0.1"
			i.approved = True
			i.priority = priority
			i.save()
		except KeyError as ex:
			print ("There was an issue with your request.")
		except ValueError as ex:
			print (str(ex))
		except Exception as ex:
			if "unique" in str(ex).lower() or "duplicate" in str(ex).lower():
				print("Looks like that puzzle piece image has already been submitted. Thanks for submitting!")
			else:
				print ("Something went wrong..." + str(ex))

if __name__ == "__main__":
	main()

