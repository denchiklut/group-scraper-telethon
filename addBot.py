from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
import csv
import traceback
import time
import random

import config


api_id = config.api_id
api_hash = config.api_hash
phone = config.phone
client = TelegramClient(phone, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

input_file = sys.argv[1]
users = []

with open(input_file, newline='\n') as csvfile:
    rows = reader = csv.reader(csvfile)
    next(rows, None)
    for row in rows:
        user = {'username': row[0], 'name': row[1]}
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups=[]

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup:
            groups.append(chat)
    except:
        continue

print('Choose a group to add members:')

i = 0
for group in groups:
    print(str(i) + '- ' + group.title)
    i += 1

g_index = input("Enter a Number: ")
target_group = groups[int(g_index)]
target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

n = 0
for user in users:
    n += 1
    if n % 50 == 0:
        time.sleep(900)
    try:
        print("Adding {}".format(user['name']))
        if user['username'] == "":
            continue
        user_to_add = client.get_input_entity(user['username'])

        client(InviteToChannelRequest(target_group_entity, [user_to_add]))
        print("Waiting for 60-180 Seconds...")
        time.sleep(random.randrange(30, 60))
    except PeerFloodError:
        print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
    except UserPrivacyRestrictedError:
        print("The user's privacy settings do not allow you to do this. Skipping.")
    except UserNotMutualContactError:
        print("The provided user is not a mutual contact.")
    except:
        traceback.print_exc()
        print("Unexpected Error")
        continue
