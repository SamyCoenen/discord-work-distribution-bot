#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A discord bot which listens on different channels for incoming requests.
"""
__author__ = "Samy Coenen"
__email__ = "contact@samycoenen.be"
__status__ = "Development"
import discord
import asyncio
import string
import random
import sys, traceback
import logging
from fabric.api import *
import pymysql.cursors
import time

logging.basicConfig(level=logging.INFO)
client = discord.Client()
mysql_username = "root"
mysql_password = "th6k5gfdkgf54"
mysql_hostname = "db_inventory"
mysql_db_name = "inventory"
discord_pass = None
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    author = str(message.author)
    channel = str(message.channel)
    
    if channel == "admin" and message.author.bot is not True:
        if message.content.startswith('add'):
            server = message.content.split(" ")
            if add_server(server[1], server[2]):
                print("added server "+ server[1])
                await client.send_message(message.channel, 'Server was added.')
            else:
                print("failed to add server")
                await client.send_message(message.channel, 'Failed to add server.')
        elif message.content.startswith('delete'):
            server = message.content.split(" ")
            if delete_server(server[1]):
                print("deleted server "+ server[1])
                await client.send_message(message.channel, 'Server was deleted.')
            else:
                print("failed to delete server")
                await client.send_message(message.channel, 'Failed to deleted server.')
        elif message.content.startswith('confirm worker'):
            userID = message.content.split(" ")[2]
            user = message.server.get_member_named(userID)
            confirm_work_user(userID)
            print('user ' + str(user) + ' was confirmed.')
            await client.send_message(user, 'Hello ' + user.mention + ' your work has been confirmed by ' + message.author.mention)
            await client.send_message(message.channel, 'user ' + str(user) + ' was confirmed.')
        elif message.content.startswith('confirm server'): 
            serverIP = message.content.split(" ")[2]
            confirm_server(serverIP)
            print("server confirmed  "+ serverIP)
            await client.send_message(message.channel, 'Server '+ serverIP +' was confirmed.')

    if channel == "work":
        if message.content.startswith('available'):
            await start_job(message)
        elif message.content.startswith('stop') and channel == "work":
            await stop_job(message)
        elif message.author.bot is not True:
            await client.send_message(message.channel, "I'm sorry but I don't understand your command, please type 'available' to start working.")

    if channel == "ranked":
        start_ranked_job(message)

async def start_ranked_job(message):
    author = str(message.author)
    password = get_user_password(author)
    if worker_needs_payment(author):
        await client.send_message(message.channel, 'You have unconfirmed work, please wait until the administrator approves your previous work.')
    elif user_has_servers(author):
        await client.send_message(message.channel, 'You already have a session running, first close your previous session with "stop".')
    elif get_count_available_servers() >= 3:
        s = get_available_servers(3, author)
        if reset_passwords_servers(s, password):
            await client.send_message(message.channel, 'Hello there ' + message.author.mention + ', I am generating a private message for you now...')
            start_session(s, author)
            response = """Your connection details are: \n
                password: %s \n
                \n
                server 1: %s:%s\n
                server 2: %s:%s\n
                server 3: %s:%s\n
                """ % (password, s[0][0], s[0][1], s[1][0], s[1][1], s[2][0], s[2][1])
            await client.send_message(message.author, response)
        else:
            await client.send_message(message.author, "Apologies, the server couldn't be reached, please wait while it get's fixed")
            print("Server error, couldn't reset password", file=sys.stderr)
            await client.send_message(message.server.owner, "Server error, couldn't reset password")
    else: 
        print('no server available right now.', file=sys.stderr)
        await client.send_message(message.channel, 'Apologies, no server is available right now. Please wait while new accounts get created or other workers finish their work.')

async def start_job(message):
    author = str(message.author)
    password = get_user_password(author)
    if worker_needs_payment(author):
        await client.send_message(message.channel, 'You have unconfirmed work, please wait until the administrator approves your previous work.')
    elif user_has_servers(author):
        await client.send_message(message.channel, 'You already have a session running, first close your previous session with "stop".')
    elif get_count_available_servers() >= 3:
        #s = get_available_servers(3, author)
        s = get_available_servers(2, author)
        if reset_passwords_servers(s, password):
            await client.send_message(message.channel, 'Hello there ' + message.author.mention + ', I am generating a private message for you now...')
            #response = """Your connection details are: \n
            #    password: %s \n
            #    \n
            #    server 1: %s:%s\n
            #    server 2: %s:%s\n
           #     server 3: %s:%s\n
           #     """ % (password, s[0][0], s[0][1], s[1][0], s[1][1], s[2][0], s[2][1])
            response = """Your connection details are: \n
                password: %s \n
                \n
                server 1: %s:%s\n
                server 2: %s:%s\n
                """ % (password)
            current_server = 1
            for server in s:
                response += """server %s: %s:%s\n""" % (current_server, server[0], server[1])
                current_server += 1
            await client.send_message(message.author, response)
        else:
            await client.send_message(message.author, "Apologies, the server couldn't be reached, please wait while it get's fixed")
            print("Server error, couldn't reset password", file=sys.stderr)
            await client.send_message(message.server.owner, "Server error, couldn't reset password")
    else: 
        print('no server available right now.', file=sys.stderr)
        await client.send_message(message.channel, 'Apologies, no server is available right now. Please wait while new accounts get created or other workers finish their work.')

async def stop_job(message):
    author = str(message.author)
    password = "examplePass"
    if (user_has_servers(author)):
        servers = servers_from_worker(author)
        items_created = 0
        if reset_passwords_servers(servers, password):
            items_created = stop_session(servers, author)
            remove_servers_from_user(author, True)
            await client.send_message(message.channel, 'You succesfully stopped your session. You created ' + items_created + ' items')
        else:
            await client.send_message(message.channel, 'The session is unable to stop due to a server error.')
        await client.send_message(message.server.owner, "These servers are currently in need of maintenance\n" + str(servers) + "\nThe worker that needs to be paid is " + author + ", created items: " + items_created)
    else:
        await client.send_message(message.channel, 'You have no started sessions currently.')

def start_session(servers, discord_id):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    data = None
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            total = 0
            # items is 2nd  (ip,port,items)
            items = 2
            for server in servers:
                total += server[items]
            total = total / len(servers)

            cursor.execute("""INSERT INTO sessions (
                worker_id, start_date, items_start
                ) 
                SELECT 
                    worker_id,
                    %s,
                    %s
                FROM 
                    workers 
                WHERE 
                    discord_id=%s LIMIT 1)""",(discord_id,time.strftime('%Y-%m-%d %H:%M:%S'), total))
            connection.commit()
            print("available servers is " + str(data))
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        connection.rollback()
        # disconnect from server
    finally:
        connection.close()
    return data

def stop_session(servers, discord_id):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    items_created = None
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            total = 0
            # items is 2nd  (ip,port,items)
            items = 2
            for server in servers:
                total += server[items]
            total = total / len(servers)
            cursor.execute("""SELECT session_id FROM sessions WHERE worker_id=IFNULL((SELECT worker_id FROM workers WHERE discord_id=%s),0) AND end_date IS NULL""", (discord_id))
            session_id, = cursor.fetchone()

            cursor.execute("""UPDATE sessions SET end_date=%s, items_end=%s
                WHERE 
                    session_id=%s""",(time.strftime('%Y-%m-%d %H:%M:%S'), total, session_id))
            connection.commit()

            cursor.execute("""SELECT items_start FROM sessions WHERE session_id=%s""", (session_id))
            # Fetch all the rows in a list of lists.
            items_start, = cursor.fetchone()
            items_created = total - items_start
            print("total production is " + str(data))
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        connection.rollback()
        # disconnect from server
    finally:
        connection.close()
    return items_created

def reset_passwords_servers(servers , password):
    env.user = 'samy'
    env.key_filename = '/root/.ssh/vultr'
    #k = paramiko.RSAKey.from_private_key_file("/root/.ssh/vultr")
    #c = paramiko.SSHClient()
    #c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #command = """ printf "%s\n%s\n\n" | /root/usr/bin/vncpasswd""" %(password,password )
    for s in servers:
        counter = 1
        ip = s[0]

        env.host_string = '172.17.0.1'
        #str(ip)
        
        port = s[1]
        #c.connect( hostname = ip, username = "root", pkey = k )
        if (port > 5900):
            counter = port - 5899
        command = """docker exec powerbot%s bash -c 'env TIGERVNC_VER=tigervnc-1.8.0.x86_64 printf "%s\n%s\n\n" | /root/$TIGERVNC_VER/usr/bin/vncpasswd'""" % (counter,password,password )
        with settings(warn_only=True):
            if not run(command):
                print("Problem resetting password with server " + ip + " port " + port)
                return False
        #print("Executing {}".format( command ))
        #stdin , stdout, stderr = c.exec_command(command)
        #print(stdout.read(), file=sys.stderr)
        #print( "Errors")
        #print(stderr.read(), file=sys.stderr)
        #c.close()
    return True

def username_exists(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT * FROM workers WHERE discord_id=%s""",(username))
            # Fetch all the rows in a list of lists.
            return cursor.fetchone() is not None
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return False

def worker_needs_payment(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT * FROM workers
            WHERE discord_id=%s AND needs_payment=true""",(username))
            # Fetch all the rows in a list of lists.
            return cursor.fetchone() is not None
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return False

def user_has_servers(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    has_servers = False
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT COUNT(*) FROM worker_with_server WHERE worker_id=IFNULL((SELECT worker_id FROM workers WHERE discord_id=%s),0)""", (username))
            # Fetch all the rows in a list of lists.
            value, = cursor.fetchone()
            return value > 0
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return has_servers

def servers_from_worker(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""
            SELECT ip, port, items
            FROM servers JOIN worker_with_server
            ON servers.server_id=worker_with_server.server_id
            WHERE worker_with_server.worker_id=IFNULL((SELECT worker_id FROM workers WHERE discord_id=%s),0)""", (username))
            # Fetch all the rows in a list of lists.
            return cursor.fetchall()
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return None

def get_count_available_servers():
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT * FROM servers WHERE server_id not IN (SELECT server_id FROM worker_with_server) AND needs_preparing=false""")
            # Fetch all the rows in a list of lists.
            return cursor.rowcount 
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return 0

def get_available_servers(amount, username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    data = None
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""SELECT ip,port,items FROM servers WHERE server_id not IN (SELECT server_id FROM worker_with_server) AND needs_preparing=false LIMIT %s""",(amount))
            data = cursor.fetchmany(amount)
            cursor.execute("""INSERT INTO worker_with_server (worker_id, server_id) SELECT (SELECT worker_id FROM workers WHERE discord_id=%s LIMIT 1),server_id FROM servers WHERE server_id not IN (SELECT server_id FROM worker_with_server) LIMIT %s""",(username, amount))
            connection.commit()
            print("available servers is " + str(data))
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        connection.rollback()
        # disconnect from server
    finally:
        connection.close()
    return data

def get_used_servers(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    data = None
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT ip, port 
            FROM servers RIGHT JOIN worker_with_server
            ON servers.server_id=worker_with_server.server_id
            WHERE worker_with_server.worker_id=IFNULL(SELECT worker_id FROM workers WHERE discord_id=%s),0)""", (username))
            # Fetch all the rows in a list of lists.
            data = cursor.fetchall()
    except Exception as e:
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return data

def get_user_password(username):
    password = query_user_password(username)
    if password is None:
        password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        create_new_user(username, password)
    return password

def create_new_user(username, password):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""INSERT INTO workers(discord_id,password,needs_payment) VALUES(%s,%s, False)""",(username, password))
            connection.commit()
    except Exception as e:
        connection.rollback()
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()

def confirm_work_user(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""UPDATE workers set needs_payment=false WHERE discord_id=%s""", (username))            
            connection.commit()
    except Exception as e:
        connection.rollback()
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()

def confirm_server(ip):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""UPDATE servers set needs_preparing=false WHERE ip=%s""", (ip))
            connection.commit()
    except Exception as e:
        connection.rollback()
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()

def remove_servers_from_user(username, reusable):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            if not reusable:
                cursor.execute("""UPDATE servers set needs_preparing=true 
                WHERE server_id IN (SELECT server_id 
                FROM worker_with_server JOIN workers
                ON worker_with_server.worker_id = workers.worker_id
                WHERE workers.worker_id=
                    IFNULL((SELECT worker_id FROM workers WHERE discord_id=%s),0))""", (username))
            cursor.execute("""DELETE from worker_with_server WHERE worker_id=IFNULL((SELECT worker_id FROM workers WHERE discord_id=%s),0)""", (username))
            cursor.execute("""UPDATE workers set needs_payment=true WHERE discord_id=%s""", (username))
            connection.commit()
    except Exception as e:
        connection.rollback()
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()

def add_server(ip, port):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""INSERT INTO servers(ip,port,needs_preparing) 
            VALUES(%s,%s,False)""",(ip, port))
            connection.commit()
            return True
    except Exception as e:
        connection.rollback()
        traceback.print_exc(file=sys.stdout)
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        connection.rollback()
        return False
        # disconnect from server
    finally:
        connection.close()

def delete_server(ip):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            # Fetch all the rows in a list of lists.
            cursor.execute("""DELETE from servers WHERE ip=%s""",(ip))
            connection.commit()
            return True
    except Exception as e:
        connection.rollback()
        traceback.print_exc(file=sys.stdout)
        print ("Error: unable to fetch data " + repr(e), file=sys.stderr)
        connection.rollback()
        return False
        # disconnect from server
    finally:
        connection.close()


def query_user_password(username):
    # Open database connection
    connection = pymysql.connect(mysql_hostname,mysql_username,mysql_password,mysql_db_name )
    # Prepare SQL query to INSERT a record into the database.
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command
            cursor.execute("""SELECT password FROM workers WHERE discord_id=%s""", (username))
            # Fetch all the rows in a list of lists.
            value, = cursor.fetchone()
            return value
    except Exception as e:
        print ("Error: no worker exists with this discord_id yet " + repr(e), file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        # disconnect from server
    finally:
        connection.close()
    return None

client.run(discord_pass)