#!/usr/bin/python

import digitalocean
import sys
import paramiko

snapshotName = "departed-2"
serverName = "departedserver"

token=''
manager = digitalocean.Manager(token=myToken)
all_droplets = manager.get_all_droplets()
all_images = manager.get_my_images()

shot = 0
for image in all_images:
    if image.name == snapshotName:
        shot = image.id
        break

drop = 0
for droplet in all_droplets:
    if droplet.name == serverName:
        drop = droplet.id
        break

if len(sys.argv) < 2:
    print('Arguements: start|stop')
elif sys.argv[1] == 'start':
    if shot == 0:
        print('Snapshot not found')
        sys.exit

    if drop != 0:
        print('Server already running')
        sys.exit
    else:
        print('Starting server')
        droplet = digitalocean.Droplet(token=myToken, name=serverName, region='sfo1', image=shot, size_slug='2gb')
        droplet.create()
        droplet.load()
        print(droplet.ip_address)

elif sys.argv[1] == 'stop':
    if drop == 0:
        print('Server not found')
        sys.exit
    elif shot != 0:
        manager.get_image(image_id=shot).destroy()

    print('Shutting down server')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('games.butterknifeestates.com', username='bretspencer')
    client.exec_command('sudo poweroff')
    client.close()
    
    print('Saving snapshot')
    newdrop = manager.get_droplet(drop)
    newdrop.load()
    if newdrop.status != 'off':
        action = newdrop.power_off(return_dict=False)
        action.wait()
    action = newdrop.take_snapshot(snapshot_name=snapshotName, power_off=False, return_dict=False)
    action.wait()
    action = newdrop.power_off(return_dict=False)
    action.wait()
    print('Destroying droplet')
    newdrop.destroy()
else:
    print('Arguments: start|stop')
    
