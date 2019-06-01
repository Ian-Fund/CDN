#!/usr/bin/python

# This code is based on the sample code provided here: https://www.acmesystems.it/python_http
# You can create a random file with size of 5 MB in Linux or OS X using the following command:
# dd if=/dev/urandom of=file.bin bs=1024 count=5120

from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
import os
import shutil


HTTP_PORT =  int(sys.argv[1])
server_name = str(sys.argv[3])


# Make class to parse header from https://stackoverflow.com/questions/4685217/parse-raw-http-headers/5955949

# This class handles any incoming request from the browser
class MeasurementServerRequestHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):

        #elif os.path.isfile('./' + self.path):
        if self.path.endswith(".jpg"):


            print(" ")

        elif self.path.endswith('.html'):
            geo_request = self.headers['return']
            try_server = False

            try:
                file_path = str(self.path.split("http://"))
                file_path = file_path.strip("[")
                file_path = file_path.strip("'")
                file_path = file_path.strip("]")
                file_path2 = file_path[:-1]
                file_path2 = file_path2.strip("/")
                # full_path = '/home/mathbot/Documents/Fall 2018/Computer Networks/project/'\
                #             +geo_request+'/cache/'+file_path2
                full_path = '/home/y2018/fall/cs6377/1/cosc3393/project/' \
                            + geo_request + '/cache/' + file_path2
                myfile = open(full_path,'r')
                mytxt = myfile.read()
                myfile.close()

                if (self.headers['caching_style'] == '2' and self.headers['needs_caching'] == 'True'):
                    self.send_response(202)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Content-length', str(os.stat(full_path).st_size))
                    self.end_headers()
                    self.wfile.write(mytxt.encode('utf-8'))
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Content-length', str(os.stat(full_path).st_size))
                    self.end_headers()
                    self.wfile.write(mytxt.encode('utf-8'))
            except:
                try_server= True
            if try_server:
                if self.headers['caching_style'] == '2' and  self.headers['needs_caching'] == 'True':

                        # self.headers['needs_caching'] = 'False'
                        print(self.headers)
                try:
                    file_path = str(self.path.split("http://"))
                    file_path = file_path.strip("[")
                    file_path = file_path.strip("'")
                    file_path = file_path.strip("]")
                    file_path2 = file_path[:-1]
                    file_path2 = file_path2.strip("/")
                    # full_path = '/home/mathbot/Documents/Fall 2018/Computer Networks/project/' \
                    #             + geo_request + '/server/' + file_path2
                    full_path = '/home/y2018/fall/cs6377/1/cosc3393/project/' \
                                + geo_request + '/server/' + file_path2
                    myfile = open(full_path,'r')
                    mytxt = myfile.read()
                    myfile.close()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('needs_caching', 'False')
                    self.send_header('Content-length', str(os.stat(full_path).st_size))



                    self.end_headers()
                    self.wfile.write(mytxt.encode('utf-8'))


                except:
                    self.send_response(405)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()




        else:
            # Send 404 (Not Found) status code for any other requests
            self.send_response(404)
        return




#  Added feature: Preload into cache when starting server
# cache_path = '/home/mathbot/Documents/Fall 2018/Computer Networks/project/'+server_name+'/cache/'
# path_to_file = '/home/mathbot/Documents/Fall 2018/Computer Networks/project/'+server_name+'/server/'+server_name+'.html'

cache_path = '/home/y2018/fall/cs6377/1/cosc3393/project/'+server_name+'/cache/'
path_to_file = '/home/y2018/fall/cs6377/1/cosc3393/project/'+server_name+'/server/'+server_name+'.html'

# Delete contents of cache first
for the_file in os.listdir(cache_path):
    file_path =  os.path.join(cache_path,the_file)
    try:
        if os.path.isfile(cache_path):
            os.unlink(file_path)
    except:
        pass

cache_path = cache_path +server_name+'.html'
myfile = open(path_to_file, 'r')
file_content = myfile.read()
myfile.close()
myfile = open(cache_path,'w')
myfile.write(file_content)
myfile.close()

try:
    # Create HTTP server with customized class
    server = HTTPServer(('', HTTP_PORT), MeasurementServerRequestHandler)
    print('Started httpserver on port', HTTP_PORT)

    # Wait forever for incoming HTTP requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()