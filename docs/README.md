# SIREN Setup Instructions

## Download Linux dependencies
1. Recommend Ubuntu-based, raspbian is good
2. sudo apt-get install build-essential python-dev libmysqlclient-dev python-virtualenv python-pip
If some don’t resolve, install what Linux tells you to

## Clone repository
3. Git clone https://github.com/blaverick62/SIREN.git
### Change remote to your repository if using it for dev
## Setup VENV and install pip requirements
4. cd SIREN
5. . ./VENV/bin/activate
6. pip install -r requirements.txt
### If some pip dependencies don’t install, install what python tells you
7. sudo apt-get install libkrb5-dev
8. pip install python-gssapi
9. pip install paramiko

## To run SIREN
10. sudo ./sirenstart.sh

## Setup Snort on Pi
11.  sudo apt-get install flex bison build-essential checkinstall libpcap-dev libnet1-dev libpcre3-dev libmysqlclient15-dev libnetfilter-queue-dev iptables-dev libdumbnet-dev autoconf libtool libdaq-dev
12. snort setup: sudo apt-get install snort
13. set up home net and interface
14. add file siren.rules to /etc/snort/rules
15. add line alert tcp $HOME_NET any -> any any (msg:"Target file accessed!"; content:"malarkey"; sid:1000037;)
16. add line include $RULE_PATH/siren.rules to snort.conf near line 550 with other includes

## Mysql setup
### On SIREN_DB ubuntu server VM
17. sudo apt-get install mysql-server
18. mysql -u root -p
19. Enter root password
20. create user ‘sirenlocal’@’localhost’ identified by ‘sirenproj’;
21. grant all privileges on *.* to ‘sirenlocal’@’localhost’;
22. quit
23. mysql -u sirenlocal -p
24. sirenproj
25. create schema siren_db;
26. use siren_db;
27. quit
### On SIREN machine
28. cd /usr/src
29. sudo git clone github.com/firnsy/barnyard2 barnyard_src cd barnyard_src
30. cd barnyard_src
31. sudo autoreconf -fvi -I ./m4
32. sudo ln -s /usr/include/dumbnet.h /usr/include/dnet.h
33. sudo ldconfig
34. cd /usr/src/barnyard_src
35. ./configure --with-mysql --with-mysql-libraries=/usr/lib/YOUR-ARCH-HERE-linux-gnu
36. make
37. sudo make install
38. sudo cp etc/barnyard2.conf /etc/snort
39. sudo mkdir /var/log/barnyard2
40. sudo chown snort.snort /var/log/barnyard2
41. sudo touch /var/log/snort/barnyard2.bookmark
42. sudo chown snort.snort /var/log/snort/barnyard2.bookmark
43. scp /usr/src/barnyard_src/schemas/create_mysql to siren_db box
44. Change output format line for unified2 in /etc/snort.conf from snort.log to merged.log and remove nostamp option
### On SIREN_DB machine
45. mysql -u sirenlocal -p
46. enter password
47. create schema snort
48. quit
49. mysql -u sirenlocal -p snort </home/"username"/create_mysql
50. find sid-msg.map online, download and copy into /etc/snort
51. start snort with: sudo snort -q -c /etc/snort/snort.conf -i ens33
52. start barnyard2 with: sudo barnyard2 -c /etc/snort/barnyard2.conf -d /var/log/snort -f merged.log -w /var/log/snort/barnyard2.bookmark

## Web service setup
### On SIREN_DB ubuntu server VM
53. sudo apt-get install apache2
54. sudo service apache2 restart
55. sudo apt-get install php libapache2-mod-php
56. sudo nano /etc/apache2/apache2.conf
57. uncomment <directory /srv/> block
58. change /srv/ to path to /siren/Website/myapp/public
59. sudo nano /etc/apache2/sites-available/000-default.conf

