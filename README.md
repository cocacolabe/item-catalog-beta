
# Item Catalog - Udacity Project

#### Description

Developed a content management system using the Flask framework in Python. Authentication is provided via OAuth and all data is stored within a PostgreSQL database.
 
#### How to open the file? 
######  (Example below will be using **vagrant**)
1. Install Vagrant and VirtualBox
2. Clone the app to the folder name **vagrant**.
3. Open the terminal and then go directly to the location where you store the file
4. Before running the command line, please Launch the Vagrant VM with `vagrant up`. Then log into it with `vagrant ssh`
5.  After you saw something like **vagrant@vagrant**, type code below and hit enter.
```
$ cd /vagrant/item_catalog_beta
```
6. Run the command line below
```
$ python database_setup.py
$ python puppypopulator.py
$ python project.py
```
7. Access and test your application by visiting http://localhost:8000 locally



#### Display US Adoption System V1.0 sample here (Video):

[![US Adoption System V1.0](https://img.youtube.com/vi/I9CA57E_hq4/maxresdefault.jpg)](https://youtu.be/I9CA57E_hq4 "US Adoption System V1.0")


###### Note: The authentication system is based on Google OAuth 2.0
