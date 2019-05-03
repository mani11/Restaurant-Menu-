# Restaurant-Menu-
This is a python and flask website for restaurant menu
It has the following features:
1. The user can login through facebook and google sign in.
2. Once the user is logged in, they can view the list of restaurants.
3. The user can click on any of the category to view the menu in that restaurant.
4. The user has an option to create,edit and delete a restaurant.
5. The user can add,edit,delete a menu in the restaurant
7. The user can logout of the website and can view the restaurant/menu. If a user is not logged in he/she will not have the      rights to create/update/delete a restaurant/menu


## Getting Started

Download the code with git clone https://github.com/mani11/Restaurant-Menu-.git

### Prerequisites

**You should have python3 installed.** 

_Download link_:https://www.python.org/downloads/

**You need VirtualBox tool to run VM.**

_Download Link_: https://www.virtualbox.org/wiki/Download_Old_Builds_5_2

**You need vagrant to configure the VM**

_Download Link_:https://www.vagrantup.com/downloads.html

Once you have the VMBox and vagrant you need to download the configuration for the VM

_Git link_: https://github.com/udacity/fullstack-nanodegree-vm

After the download,you will have a directory containing the VM files. Change to this directory in your terminal with cd. Inside, you will find another directory called vagrant. Change directory to the vagrant directory:

**Start Virtual Machine:**

From your terminal, inside the vagrant subdirectory, run the command _**vagrant up_**. This will cause Vagrant to download the Linux operating system and install it.

When vagrant up is finished running, you will get your shell prompt back. At this point, you can run _**vagrant ssh**_ to log in to your newly installed Linux VM!

**Running the database**

This project uses sqlite3 database.
Inside the vagrant folder run the database_setup.py file to create the database tables.
Run the command _**python database_setup.py**_


**Populate data**

Next, populate the database with some dummy data created in the lotsofmenus.py file
Run the command _**pythonlotsofmenus.py**_

**Run the website**

Next, run the application with _**python restaurant.py**_ command. This will start the server at port 5000.
Now from the browser visit _**localhost:5000/login**_ to land on the login page. To visit the home page visit _**localhost:5000/restaurant**_
or _**localhost:5000/**_


