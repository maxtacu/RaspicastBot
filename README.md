# RaspicastBot

Telegram bot that controls your Raspicast device.
This bot was created to make it easier to share connection to the Raspicast device without sharing ssh credentials.

## Requirements

Before starting this bot on your device, you should configure raspberry Pi as a Chromecast device.  
You can follow the guide here: https://pimylifeup.com/raspberry-pi-chromecast

*OPTIONAL*  
You can also configure it as a Spotify Connect client.  
Check the tutorial here: https://github.com/dtcooper/raspotify

After you configured and tested your Raspicast, you are ready to go.

![Screenshot from 2019-04-11 01-19-35](https://user-images.githubusercontent.com/17516391/55922399-d7ad8100-5bf8-11e9-969f-223a8da2650a.png)

Above is an example of the bot response when someone is sending a link to play.

-------

## Running the Bot

Please be sure that you have Python 3 installed.  

I preffer to run the bot inside of the virtualenv. But you can do as you want and skip this section. 

```
python3 -m venv .venv
```
This will create virtualenv inside **.venv** folder.  
```
source .venv/bin/activate
```  
Install all dependencies: 
```
pip3 install -r requirements.txt
```
Create **apiKey.txt** file in the same folder as **raspicast_bot.py** script.  
Insert in the **apiKey.txt** the bot API key which you retrieved from BotFather when you created a bot in telegram.

Now you are ready to start the bot.
```
python raspicast_bot.py
```
-----
## Some features/commands of the bot

![Webp net-resizeimage](https://user-images.githubusercontent.com/17516391/56228362-8e818500-606f-11e9-960d-9851ea819a57.jpg)  
RaspicastBot has aditionally a User Management support to restrict access to the bot. Use **/admin** command to add/remove/list users by their telegram username.

Please update the [Admins list line](https://github.com/tmxak/RaspicastBot/blob/44949e9482a5022170d1dd41423952c85cc8d5da/raspicast_bot.py#L36) with your telegram username to get access to the admin (user-management) functions. 