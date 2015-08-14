#!/usr/bin/ruby

require 'droplet_kit'
require 'net/ssh'

snapshotname = 'departed'
servername = 'departedserver'

token=''
client = DropletKit::Client.new(access_token: token)
shot = '0'
images = client.images.all(public:false)
images.each do |image|
  if image.name == snapshotname
    shot = image.id
  end
end

droplist = client.droplets.all()
serverdrop = '0'
droplist.each do |drop|
  if drop.name == servername
    serverdrop = drop.id
  end
end


if ARGV[0] == 'start'
  if shot == '0'
    puts "snapshot not found"
    return
  end

  if serverdrop != '0'
    puts "server already running"
    return
  end

  puts "Starting server"
  droplet = DropletKit::Droplet.new(name: 'departed', region: 'sfo1', size: '2gb', image: shot)
  client.droplets.create(droplet)
elsif ARGV[0] == 'stop'
  if serverdrop == '0'
    puts "server not found"
    return
  end

  if shot != '0'
    client.images.delete(id: shot)
  end

  Net::SSH.start('games.butterknifeestates.com', 'bretspencer') do |session|
    session.exec "sudo poweroff"
  end
  
  sleep(30)
  puts "Saving snapshot"
  client.droplet_actions.snapshot(droplet_id: serverdrop, name: snapshotname)
  sleep(240)
  client.droplet_actions.power_off(droplet_id: serverdrop)
  sleep(90)
  client.droplets.delete(serverdrop)
else
  puts "Arguments: start|stop"
end
