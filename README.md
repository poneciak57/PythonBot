<style>
.center{
    text-align:center;
}

</style>

<h1 class="center"> My own discord music bot wrote in python </h1>
<p class="center" style="font-size:20px;">
This is my first bigger project in python and its not actually finished yet.
I really want to make other cogs and features for this bot
</p>

# Bot commands:
``` 
\connect
\disconnect
\play ${link:optional}
\clear
\queue
\pause
\next
\previous
\shuffle
\loop
```
| Syntax | Aliases | Description
| ----------- | ----------- |--------|
| connect | join| connect the bot to the channel where youre currently sitting|
| disconnect | leave| disconnect the bot if its connected|
| play | | resume paused track or queue up song from link|
| clear | stop| stop the music and clear the queue|
| queue | ls, list| show the queue|
| pause | | pause current track|
| next | skip| skip to the next track if exist|
| previous | prev| go to the previous track if exist|
| shuffle | | shuffle the queue |
| loop | | loop currently played track or unloop it|


# How you can run bot?
First what u need to do is to get openjdk (i recomend u to get the latest version) and lavalink.jar from official github page and copy it to openjdk bin folder.Then u need to follow along their tutorial how to run this up. </br>
When you get everything done u need to create virtual enviroment (or just use global...) and install requered dependencies by running this commands(make sure u have python and pip installed on your device)

```
pip install wavelink=0.9.4 //it wont work on different version!!!
```
```
pip install discord.py[voice] //i used version 1.7.3
```
```
pip install python-decouple
```
Now the last thing u need to do is to create ".env" file in main project folder
and type two variables in it
```
TOKEN=your discord bot token
LAVALINK_PASSWORD=your lavalink password
``` 
>Dont add any quotes and spaces in it

Now just open cmd and navigate to your project folder then type 
```
python launcher.py
```
