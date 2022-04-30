# How to set up the environment for testing the code?
System used: Windows 8.1, 4gb RAM, i3 core  
Language : Python version 3.7.3  
Web Framework : Flask  
Database: MongoDB Community Server version 3.6.23 (https://www.mongodb.com/try/download/community)

![mongo_dnld](https://user-images.githubusercontent.com/43542022/147854654-61253631-9ad4-45ff-99ef-ffe491bc653c.png)

Mongo version 3.6.23 are not for Windows 8.1  
MongoDB Compass: GUI for MongoDB   
Make a db folder in the location "C:\data\db". For higher versions of MongoDB this will be automatically get created.  
Using Mongo Compass ,create database named "TunedIn" and add three collections named "Credentials","Users","Invitations"
![image](https://user-images.githubusercontent.com/43542022/147854794-91c97ab5-2169-4fe2-bde6-f51c3d1679f1.png)

Open cmd in mongodb folder at location "C:\Program Files\MongoDB\Server\3.6\bin" and run the mongod.exe file. This file must run at all times in order for our queries to database to work.
![ghgh](https://user-images.githubusercontent.com/43542022/147854833-1bd82016-0b12-46e5-8416-dfbf07515f86.png)

I have used postman for API testing and Visual Studio Code, code editor  

On command prompt, we need to install flask,flask-session and pymongo. Assuming pip already installed.

```sh
pip install Flask
pip install Flask-Session
pip install pymongo
```
![image](https://user-images.githubusercontent.com/43542022/147854785-9cf2418b-84aa-48de-9331-be25b2ed9a1e.png)  
In the folder TunedIn, where we have the app.py file, open cmd and run the flask app. 

![image](https://user-images.githubusercontent.com/43542022/147855117-3c35220a-f750-4613-8ae2-58c918165919.png)


Now we are ready to test the API's
