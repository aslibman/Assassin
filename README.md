Assassin
========
By David Dvorkin, Victor Gaitour, Kyler Chase, Julian Kalogerakis, Alex Libman  

Gunicorn: http://104.236.123.216 <br>
Demo Video: https://www.youtube.com/watch?v=w98Tqa_cDVY <br>

## What It Does
Assassin is a multiplayer "manhunt" game. Players register an account on the site, and can then either join a game off of another user or host their own game. After the game is started, players in the game will be randomly matched to a target, who is another player in the game. Their job is to try to "assassinate" their target by taking and uploading a clear image of the person, while trying to avoid being assassinated themselves. After a target is assassinated, the assassin inherits their target. The overall winner is the last man standing in the game. Images are automatically compared with the Kairos facial recognition API to allow for instant confirmation of a kill, but if that fails there is an option for manual confirmation by the target. A geolocation system is also in place to help lead assassins to the general location of their targets. 

## Installation
1. Clone the repository: `git clone git@github.com:kingalex11235/Assassin.git`
2. Install PIP: `sudo apt-get install python-pip`
3. (Optional) Install and use virtualenv `sudo apt-get install python-virtualenv`
4. Install MongoDB
5. Install the flask module: `pip install flask`
6. Install the pymongo module: `pip install pymongo`
7. Configure your server to deploy app.py

## Roles
* Alex: Backend, General Management
* Victor: Facial Recognition
* Julian: Geolocation
* David: Flask
* Kyler: Frontend

## Timeline
### 12/21/14
* Basic account and login system
* Start front end work

### 12/28/14
* Better website look
* Randomly pair assassins to targets
* Be able to upload images
* Be able to change status of people if they are confirmed assassinated

### 1/3/15
* Allow for a host user to create their own local game
* Geolocation
* Implement login with Facebook?
* Implement face recognition confirmation for assassinations?
* Finalize website look and javascript interactions

### 1/11/15
* Implement login with Facebook
* Implement face recognition confirmation for assassinations
* Optimize site for mobile view

### Afterwards
* Miscellaneous features
