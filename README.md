## CS50 Final Project
# WEAR WHERE
The result of my take on final project of CS50 course is the flask web app. 
It's main purpose is creating a selection of uploaded clothing items that fit current weather report.

## Table of content
1. [Requirements](#requirements)
2. [Built with](#built-with)
3. [Installation guide](#installation-guide)
4. [How does it work?](#how-does-it-work)
5. [Author](#author)
6. [License](#license)

## Requirements
* [Python3](https://www.python.org/downloads/)
* [requirements.txt](/requirements.txt)

## Built with
* Flask
* SQL
* Bootstrap 4
* jQuery
* PIL
* Werkzeug
* Flask-Session
* Open Weather API

## Installation guide
1. Clone repository https://github.com/MrsPeppermint/CS50-final.git:
    ```
    mkdir repo
    cd repo
    git clone git@github.com:MrsPeppermint/CS50-final.git
    cd CS50-final
    ```
2. Install required packages with pip: 
    ```
    $ pip install -r requirements.txt
    ```
    (or pip3 if you use pip3)

3. Acquire API KEY in order to get weather data:
    * visit [Openweathermap.org](https://openweathermap.org)
    * create free account
    * click on "My API Keys" in navigation menu and copy the api key
    * in terminal window execute:
    ```
    $ export API_KEY=[copied API key value]
    ```

4. run app from terminal:
    ```
    $ flask run
    ```

## How does it work?
The main web app idea is pretty straightforward. The user can create an account which allows him to upload photos of his clothing items into his online closet. 

#### Register and login
When registering for an account user must provide:
* Username - has to be unique
* Password - has to be 6-20 characters long and is saved into the database as a hash after successfully performed check

#### Add item
When creating a new item in online closet, user has to fill out a form in which he enters certain information about the clothing piece: 
* Type of clothing (6 categories: top, bottom, shoes, accessory, outerwear, underwear)
* Color of the item
* Photo of the item (*optional*)
* Description of the item (*optional*)
* Temperature at which the item is meant to be worn (5 categories: low - doesn't matter - high)
* Weather condition at which the item is meant to be worn (5 categories: rain - doesn't matter - sun)

#### Closet
After sucessfully submitting the form, the added clothing item can be found in user's online closet. If the photo was not provided by the user, the default image with dynamically changing background color is used when displaying the clothing item. The clothes are sorted into 6 categories based on the type of clothing. The remove item function is also available in the closet. 

#### Weather check and selection
The top of the homepage has a form that asks user for a city and then presents him with weather information about that city. The weather info is categorized to fit the weather categories in the aforementioned Add item form. The user is then presented with the selection of clothes that fit the current weather condition in the chosen city considering the data about the individual piece of clothing.

#### Change password and delete account
A registered user has an option to change his password and to delete his account. The latter function removes all the user's data including his closet.

#### Guest user function
The webpage also has limited funtionality for guest users - they can only retrieve information about the weather in a specific city.

#### Video Presentation
[Link](https://youtu.be/xXdwa72IAg0) to the video.

## Ideas for improvement
* Use current user's location acquired by his IP address
* Create outfit ideas based on the color matching
* Connect to bigger clothing stores' databases and allow user to choose items from those databases
* Add more profile info (connect to e-mail and add forgot password function)

## Author
Klara Žnideršič AKA [MrsPeppermint](https://github.com/MrsPeppermint)

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](/LICENSE.md)