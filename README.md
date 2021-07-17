## My code for [this API exercise][link] from Postman

[link]:https://documenter.getpostman.com/view/8411283/SVfMSqA3?version=latest

Written in Django and Django REST Framework. I tried to follow the requirments as close as possible.
## Installation

0. Install Python3

2. Clone this repo in a folder
```
>>> git clone https://github.com/sam-val/mini_wallet_exercise.git
```
2. Outside of folder **mini_wallet_excercise**, create an virtual enviroment:
```
>>> python3 -m venv venv
```

3. Activate it
-  On Linux/Mac
```
>>> source venv/bin/activate
```
- On Windows (using cmd) 
```
>>> venv\Scripts\activate.bat
```
4. Install the projects' dependencies:
```
>>> pip install -r requirements.txt
```
5. Navigate into project root (folder with file **manage.py**) and run:
```
>>> python manage.py migrate
>>> python manage.py runserver
``` 
<br>

That's it! The Server is running at localhost:8000

## Testing
Using *Postman* or command line tool like *curl* or whatever, you can access these endpoints (as specified in the exercise)

* `POST http://localhost:8000/api/v1/init`
* `GET 'http://localhost:8000/api/v1/wallet'`
* `POST 'http://localhost:8000/api/v1/wallet'`
* `PATCH 'http://localhost:8000/api/v1/wallet'`
* `POST http://localhost:8000/api/v1/wallet/deposits`
* `POST http://localhost:8000/api/v1/wallet/withdrawals`

For details, read [the exercise][link] from Postman itself.





