from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from datetime import datetime
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#   --------  JSON FILE START--------


@app.route('/shelters/JSON')
def shelterListJSON():
    allshelter = session.query(Shelter).all()
    return jsonify(JSONShelter=[i.serialize for i in allshelter])


@app.route('/shelters/<int:shelter_id>/petlist/JSON')
def petListJSON(shelter_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    puppies = session.query(Puppy).filter_by(shelter_id=shelter_id).all()
    return jsonify(JSONPetList=[i.serialize for i in puppies])


@app.route('/shelters/<int:shelter_id>/petlist/<int:pet_id>/JSON')
def eachPetJSON(shelter_id, pet_id):
    puppies = session.query(Puppy).filter_by(id=pet_id).one()
    return jsonify(JSONPet=puppies.serialize)

#   --------  JSON FILE END--------

# Shelter List
@app.route('/')
@app.route('/shelters/')
def allShelterList():
    allshelter = session.query(Shelter).order_by(asc(Shelter.name))
    return render_template('allshelterlist.html', allshelter=allshelter)

# Add a new Shelter
@app.route('/shelters/new/', methods=['GET', 'POST'])
def newShelter():
    if request.method == 'POST':
        newShelter = Shelter(
            name=request.form['name'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zipCode=request.form['zipcode'],
            website=request.form['website'],
        )
        session.add(newShelter)
        session.commit()
        return redirect(url_for('allShelterList'))
    else:
        return render_template('newshelter.html')

# Edit shelter
@app.route('/shelters/<int:shelter_id>/edit', methods=['GET','POST'])
def editShelter(shelter_id):
    editedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedShelter.name = request.form['name']
        if request.form['address']:
            editedShelter.address = request.form['address']
        if request.form['city']:
            editedShelter.city =  request.form['city']
        if request.form['state']:
            editedShelter.state =  request.form['state']
        if request.form['zipcode']:
            editedShelter.zipCode = request.form['zipcode']
        if request.form['website']:
            editedShelter.website = request.form['website']
        session.add(editedShelter)
        session.commit()
        flash("Shelter has been edited")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template(
            'editshelter.html',
            shelter_id=shelter_id,
            i=editedShelter)

#   Delete shelter
@app.route('/shelters/<int:shelter_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteShelter(shelter_id): 
    deletedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if request.method == 'POST':
        session.delete(deletedShelter)
        session.commit()
        flash("pet has been deleted")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('deleteshelter.html', i=deletedShelter)

@app.route('/shelters/<int:shelter_id>/list')
def shelterList(shelter_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    puppies = session.query(Puppy).filter_by(shelter_id=shelter.id)
    return render_template('home.html', shelter=shelter, puppies=puppies)


#   Add a new pet
@app.route('/shelters/<int:shelter_id>/new/', methods=['GET', 'POST'])
def newPet(shelter_id):
    if request.method == 'POST':
        addnew = Puppy(
            name=request.form['name'],
            dateOfBirth=datetime.strptime(
                request.form['dateofbirth'],
                "%Y-%m-%d"),
            gender=request.form['gender'],
            weight=request.form['weight'],
            picture=request.form['picture'],
            shelter_id=shelter_id)
        session.add(addnew)
        session.commit()
        flash("New Pet created")
        # redirect url_for(function: shelter)
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('newpet.html', shelter_id=shelter_id)


#   Edit a new pet

@app.route(
    '/shelters/<int:shelter_id>/<int:pet_id>/edit',
    methods=[
        'GET',
        'POST'])
def editPet(shelter_id, pet_id):
    editedPet = session.query(Puppy).filter_by(id=pet_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedPet.name = request.form['name']
        if request.form['gender']:
            editedPet.gender = request.form['gender']
        if request.form['dateofbirth']:
            editedPet.dateOfBirth = datetime.strptime(
                request.form['dateofbirth'], "%Y-%m-%d")
        if request.form['weight']:
            editedPet.weight = request.form['weight']
        if request.form['picture']:
            editedPet.picture = request.form['picture']
        session.add(editedPet)
        session.commit()
        flash("Pet has been edited")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template(
            'editpet.html',
            shelter_id=shelter_id,
            pet_id=pet_id,
            i=editedPet)

#   Delete pet
@app.route(
    '/shelters/<int:shelter_id>/<int:pet_id>/delete/',methods=['GET','POST'])
def deletePet(shelter_id, pet_id): 
    deletedPet = session.query(Puppy).filter_by(id=pet_id).one()
    if request.method == 'POST':
        session.delete(deletedPet)
        session.commit()
        flash("pet has been deleted")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('deletepet.html', i=deletedPet)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
