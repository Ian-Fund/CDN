#!/usr/bin/python

# This code is based on the sample code provided here: https://www.acmesystems.it/python_http
# You can create a random file with size of 5 MB in Linux or OS X using the following command:
# dd if=/dev/urandom of=file.bin bs=1024 count=5120

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import sys
import threading
import time
running = True
caching_style = 1
# intilize base routing table
my_links = []
global_routing_table = {"asia": [float('inf'), 'z'], "northamerica": [float('inf'), 'z'],
                 "southamerica": [float('inf'), 'z'],
                 "africa": [float('inf'), 'z'], "antartica": [float('inf'), 'z'], "europe": [float('inf'), 'z']}
# global_routing_table = {"texas": [float('inf'), 'z'], "florida": [float('inf'), 'z'],'mexico':[float('inf'),'z']}




# Takes links from another node
# Returns which node it's from
def get_guest_name(standardized_lists):
    # First get guest location
    for list in standardized_lists:
        if int(list[2]) == 0:
            guest_location = list[3]
            return guest_location

# Takes routing table and links from another node
# returns updated routing table
def dvr_Update(my_dvr,guest_links):
    guest_dvr = {"asia": [float('inf'), 'z'], "northamerica": [float('inf'), 'z'],
                     "southamerica": [float('inf'), 'z'],
                     "africa": [float('inf'), 'z'], "antartica": [float('inf'), 'z'], "europe": [float('inf'), 'z']}
    # guest_dvr = {"texas": [float('inf'), 'z'], "florida": [float('inf'), 'z'],'mexico':[float('inf'),'z']}
    for link in guest_links:
        guest_dvr[link[3]][0] = link[2]
    guest_location = get_guest_name(guest_links)
    my_Distance_guest = my_dvr[guest_location][0]
    for link in my_dvr:
        my_Distance_link = float(my_dvr[link][0])
        guest_distance_link = guest_dvr[link][0]
        if float(my_Distance_guest) + float(guest_distance_link) < float(my_Distance_link):
            my_dvr[link][0] = float(my_Distance_guest) + float(guest_distance_link)
            my_dvr[link][1] = guest_location
    return my_dvr


def do_ping(data ,my_links):

    while running:
        i = 0
        global  global_routing_table
        global logFile
        for link in data['links']:
            head = {'delay': int(data['links'][i]['link_delay'])}
            start_time = time.time()
            time.sleep(int(data['links'][i]['link_delay']))
            logFile.write(str(start_time) + "  " + data['links'][i]["geo_tag"] + " sent \n")
            try:
                r = requests.get("http://" + data['links'][i]['node_ip'] + ':' + data['links'][i]['node_port'] + "/ping"
                                 , headers=head)
                end_time = float(time.time() - start_time)
                logFile.write(str(time.time()) + '  ' + data['links'][i]["geo_tag"] + " received\n")
                i = i + 1
                #     Update table and dvr
                global_routing_table[data['links'][i]["geo_tag"]][0] = end_time  # Updates routing table with real delay

                for neighbor in my_links:  # Updates my_links with real delay
                    if neighbor == data['links'][i]["geo_tag"]:
                        my_links[neighbor][2] = end_time
                        break
                do_dvr(data,my_links)
            except:
                pass

def do_dvr(data,  my_links):
    i= 0
    global global_routing_table
    tryWorked = False
    for link in data['links']:
        try:  # issue might be here
            # here we want to post our table to each neighbor.
            jsondata = json.dumps(my_links)

            # this makes what I need to send
            dict_list = []
            for link in my_links:
                temp = {}
                temp['destination_ip'] = link[0]
                temp['destination_port'] = link[1]
                temp['link_delay'] = link[2]
                temp['geo_tag'] = link[3]
                dict_list.append(temp)

            logFile.write(str(time.time()) + "  " + data['links'][i]["geo_tag"] + " sent \n")
            r2 = requests.post(url='http://' + data['links'][i]['node_ip'] + ':' + data['links'][i]['node_port'],
                               # data= 'test')
                               json=dict_list)

            i = i + 1
            # This isn't right yet
            tryWorked = True

        except:
            pass

def get_destination(url_path):
    file_path = str(url_path.split("http://"))
    file_path = file_path.strip("[")
    file_path = file_path.strip("'")
    file_path = file_path.strip("]")
    file_path2 = file_path[:-1]
    return file_path2

server_port = int(sys.argv[1])
server_address = str(sys.argv[2])
geo = str(sys.argv[3]) + 'Config'

f = open(geo, 'r')
if f.mode == 'r':
    node_data = f.read()
geo_tag = str(sys.argv[3])
#  Use data from config file to make routing table
data = json.loads(node_data)
logFile = open(data['log_file'], 'w')
CDN_Port = int(data['node_port'])
CDN_address = data['node_ip']

# This class handles any incoming request from the browser
class MeasurementServerRequestHandler(BaseHTTPRequestHandler):

    #  Don't know what to put in here to make it work
    def do_POST(self):  #Copied from https://pymotw.com/2/BaseHTTPServer/
        try:
            self.send_response(201)
            self.send_header('Content-type', 'json/application')
            content_len = int(self.headers.get('content-length', 0))
            self.end_headers()
            post_body = self.rfile.read(content_len)
            self.wfile.write(post_body)
            global global_routing_table
            post_body_str = str(post_body)
            post_body_str = post_body_str[2:]
            post_body_str = post_body_str[:-1]
            jdata = json.loads(post_body_str)

            # Makes my_links from new POSTED info
            your_links = []
            for dictionary in jdata:
                temp = []
                temp.append(dictionary['destination_ip'])
                temp.append(int(dictionary['destination_port']))
                temp.append(int(dictionary['link_delay']))
                temp.append(dictionary['geo_tag'])
                your_links.append(temp)
            global_routing_table = dvr_Update(global_routing_table,your_links)
        except:
            pass




    def do_GET(self):
        if self.path.endswith('.html'):
            test_time = time.time()
            # Get file name
            destination = get_destination(self.path)
            global logFile
            global  global_routing_table

            # Have path from browser at this point ex: /africa.html
            full_path =  str('http://' +str(server_address )+ ':' + str(server_port) + destination)
            # Check if the server has the file
            return_address = get_guest_name(my_links)
            head = {'file_path': destination, 'return':return_address,'needs_caching':'True','caching_style':str(caching_style)}

            log_dest = destination.strip('.html')
            log_dest = log_dest.strip('/')
            start_time = time.time()
            logFile.write(str(start_time) + "  " + log_dest +" sent \n")
            time.sleep(global_routing_table[log_dest][0])
            r2 = requests.get(full_path, headers = head)
            logFile.write(str(time.time() -start_time) + "  " + destination + " received \n")



            if int(r2.status_code) == 405:
                destination = destination.strip('.html')
                destination = destination.strip('/')
                i = 0
                for link in my_links:
                    if link[2] == 0 or link[2] == '0':
                        # cache_path = '/home/mathbot/Documents/Fall 2018/Computer Networks/project/' \
                        #              + geo_tag + '/cache/'
                        cache_path = '/home/y2018/fall/cs6377/1/cosc3393/project/'+geo_tag+'/cache/'
                        break

                for entry in global_routing_table:
                    if destination == entry:
                        next_hop = global_routing_table[entry][1]
                        for link in my_links:
                            if next_hop == link[3]:
                                full_path = 'http://' + str(link[0]) + ':' + str(
                                    link[1]) + '/' + destination + '.html'
                                break
                    i = i + 1

                head = {'return_to': return_address}
                if caching_style == 1:
                    head['cache_style'] = '1'
                    logFile.write(str(start_time) + "  " + log_dest + " sent \n")
                    time.sleep(global_routing_table[log_dest][0])
                    r3 = requests.get(full_path,headers = head)
                    logFile.write(str(time.time() - start_time) + "  " + destination + " received \n")
                    myfile = open(cache_path+destination+'.html', 'w')
                    myfile.write(r3.text)
                    # mytxt = myfile.read()
                    myfile.close()
                    self.send_response(200)
                    self.send_header('Content-type', r3.headers['Content-type'])
                    self.send_header('Content-length', r3.headers['Content-length'])
                    self.end_headers()
                    self.wfile.write(r3.content)

                if caching_style == 2:
                    head['caching_style'] = '2'
                    head['needs_caching'] = 'True'
                    logFile.write(str(start_time) + "  " + log_dest + " sent \n")
                    time.sleep(global_routing_table[log_dest][0])
                    r3 = requests.get(full_path, headers=head)
                    logFile.write(str(time.time() - start_time) + "  " + destination + " received \n")
                    if r3.status_code == 202:
                        myfile = open(cache_path + destination + '.html', 'w')
                        myfile.write(r3.text)
                        myfile.close()

                    self.send_response(200)
                    self.send_header('Content-type', r3.headers['Content-type'])
                    self.send_header('Content-length', r3.headers['Content-length'])
                    self.end_headers()
                    self.wfile.write(r3.content)

                # make request for it and save it
                # get info by making routing table global?.
                # get geo tag by stripping path
                # use get tag in my_links to find address for request
                # how to make sure it's tracing the same route instead of shortest path each time? maybe that's my feature
            elif r2.status_code == int(202):

                try:

                     # myfile = open('/home/mathbot/Documents/Fall 2018/Computer Networks/project/' \
                     #               + self.headers['return_to'] + '/cache/' + destination, 'w')
                     myfile = open('/home/y2018/fall/cs6377/1/cosc3393/project/' \
                                   + self.headers['return_to'] + '/cache/' + destination, 'w')
                     myfile.write(r2.text)
                     myfile.close()
                except:
                    pass
                self.send_response(200)
                self.send_header('Content-type', r2.headers['Content-type'])
                self.send_header('Content-length', r2.headers['Content-length'])
                self.end_headers()
                self.wfile.write(r2.content)
                # myfile = open('/home/mathbot/Documents/Fall 2018/Computer Networks/project/' \
                #                      + self.headers['return_to'] + '/cache/' + destination , 'w')
                # myfile.write(r2.text)
                # myfile.close()
            else:
                self.send_response(200)
                self.send_header('Content-type', r2.headers['Content-type'])
                self.send_header('Content-length', r2.headers['Content-length'])
                self.end_headers()
                self.wfile.write(r2.content)

        elif self.path.endswith("ping"):

            time.sleep(int(self.headers['delay']))
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Content-length', 4)
            self.end_headers()
            self.wfile.write("pong".encode('utf-8'))



        else:
            # Send 404 (Not Found) status code for any other requests
            self.send_response(404)
        return

try:
    # Create HTTP server with customized class
    server = HTTPServer(('', CDN_Port), MeasurementServerRequestHandler)
    print('Started httpserver on port', CDN_Port)

    dvr = {}

    i = 0
    for link in data['links']:
        temp_list =[]
        temp_list.append(data['links'][i]['node_ip'])
        temp_list.append(data['links'][i]['node_port'])
        temp_list.append(data['links'][i]['link_delay'])
        temp_list.append(data['links'][i]['geo_tag'])
        my_links.append(temp_list)
        dvr[data['links'][i]['geo_tag']] = int(data['links'][i]['link_delay'])
        i = i + 1
    temp_list = [CDN_address,CDN_Port,0,geo_tag]
    my_links.append(temp_list)
    #  Now I have the list that will get shared


    # update routing table based on which node it is
    global_routing_table[geo_tag][0] = 0
    global_routing_table[geo_tag][1] = geo_tag
    for key in dvr:
        global_routing_table[key][0] = dvr[key]
        global_routing_table[key][1] = key



    # Wait forever for incoming HTTP requests

    threading.Timer(10, do_ping, args=(data, my_links)).start()
    threading.Timer(5,do_dvr, args=(data,my_links)).start()

    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    running = False
    server.socket.close()
except:
    running = False

