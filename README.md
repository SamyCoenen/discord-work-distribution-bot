# Discord work distribution bot

## Use Case

You have a server or servers which stream apps or are remote desktops, the amount of servers that you have may or may not be limited.

In a dedicated (work) channel someone can ask the bot to be a assigned a server, the bot will select an available server and pm the connection details to the user. In this repo the connection details are for a vnc server and the bot automatically changes the tigervnc-server password before sending the ip and password to the user.

In some cases the work that a user has done needs to be checked before he can continue working, which is why there is a confirm worker function.
In some cases the server needs to be prepared before a new worker can work again, which is why there is a confirm server function.

## Administration

You can add or remove users and servers from the database using the chat instead of manually querying.

First you need to create an Admin channel, then you use the following commands:

    add $server
    delete $server
    confirm worker $worker_id
    conform server $server_id

This bot is programmed with Python and the library to access the api is discord.py

## External bot API

There is a second container which contains flask-api, this provides endpoints as an API that you can design yourself which also has access to the same database as the discord bot.


