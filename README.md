
# US Adoption System V1.0

#### Description

US Adoption System is an application provide a user registration and authentication system. Registered users will have the ability to post, edit and delete pet and shelter on the system. It also provides JSON to access API. 
 
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

###### Note: The authentication system is based on Google OAuth 2.0
