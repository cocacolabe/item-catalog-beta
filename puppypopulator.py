from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from database_setup import Base, Shelter, Puppy, User
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random


engine = create_engine('sqlite:///petshelterwithuser.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

#Add Shelters
shelter1 = Shelter(user_id =1, name = "Oakland Animal Services", address = "1101 29th Ave", city = "Oakland", state = "California", zipCode = "94601", website = "oaklandanimalservices.org")
session.add(shelter1)

shelter2 = Shelter(user_id =1, name = "San Francisco SPCA Mission Adoption Center", address="250 Florida St", city="San Francisco", state="California", zipCode = "94103", website = "sfspca.org")
session.add(shelter2)

shelter3 = Shelter(user_id =1, name = "Wonder Dog Rescue", address= "2926 16th Street", city = "San Francisco", state = "California" , zipCode = "94103", website = "http://wonderdogrescue.org")
session.add(shelter3)

shelter4 = Shelter(user_id =1, name = "Humane Society of Alameda", address = "PO Box 1571" ,city = "Alameda" ,state = "California", zipCode = "94501", website = "hsalameda.org")
session.add(shelter4)

shelter5 = Shelter(user_id =1, name = "Palo Alto Humane Society" ,address = "1149 Chestnut St." ,city = "Menlo Park", state = "California" ,zipCode = "94025", website = "paloaltohumane.org")
session.add(shelter5)


#Add Puppies

male_names = ["Bailey", "Max", "Charlie", "Buddy","Rocky","Jake", "Jack", "Toby", "Cody", "Buster", "Duke", "Cooper", "Riley", "Harley", "Bear", "Tucker", "Murphy", "Lucky", "Oliver", "Sam", "Oscar", "Teddy", "Winston", "Sammy", "Rusty", "Shadow", "Gizmo", "Bentley", "Zeus", "Jackson", "Baxter", "Bandit", "Gus", "Samson", "Milo", "Rudy", "Louie", "Hunter", "Casey", "Rocco", "Sparky", "Joey", "Bruno", "Beau", "Dakota", "Maximus", "Romeo", "Boomer", "Luke", "Henry"]

female_names = ['Bella', 'Lucy', 'Molly', 'Daisy', 'Maggie', 'Sophie', 'Sadie', 'Chloe', 'Bailey', 'Lola', 'Zoe', 'Abby', 'Ginger', 'Roxy', 'Gracie', 'Coco', 'Sasha', 'Lily', 'Angel', 'Princess','Emma', 'Annie', 'Rosie', 'Ruby', 'Lady', 'Missy', 'Lilly', 'Mia', 'Katie', 'Zoey', 'Madison', 'Stella', 'Penny', 'Belle', 'Casey', 'Samantha', 'Holly', 'Lexi', 'Lulu', 'Brandy', 'Jasmine', 'Shelby', 'Sandy', 'Roxie', 'Pepper', 'Heidi', 'Luna', 'Dixie', 'Honey', 'Dakota']

puppy_images = ["https://goo.gl/TPw8w8", "https://goo.gl/WhXhQP","https://goo.gl/y8dexz","https://goo.gl/q1iRWH","https://goo.gl/NQwtjN","https://goo.gl/VpzxkJ","https://goo.gl/2MdKbG","https://goo.gl/f1EBdY","https://goo.gl/mhakwE","https://goo.gl/Sqaf6j"]
#This method will make a random age for each puppy between 0-18 months(approx.) old from the day the algorithm was run.
def CreateRandomAge():
	today = datetime.date.today()
	days_old = randint(0,540)
	birthday = today - datetime.timedelta(days = days_old)
	return birthday

#This method will create a random weight between 1.0-40.0 pounds (or whatever unit of measure you prefer)
def CreateRandomWeight():
	return random.uniform(1.0, 15.0)

for i,x in enumerate(male_names):
	new_puppy = Puppy(name = x, gender = "male", dateOfBirth = CreateRandomAge(),picture=random.choice(puppy_images) ,shelter_id=randint(1,5), weight= CreateRandomWeight())
	session.add(new_puppy)
	session.commit()

for i,x in enumerate(female_names):
	new_puppy = Puppy(name = x, gender = "female", dateOfBirth = CreateRandomAge(),picture=random.choice(puppy_images),shelter_id=randint(1,5), weight= CreateRandomWeight())
	session.add(new_puppy)
	session.commit()