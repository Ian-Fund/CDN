#!/usr/bin/python

# This code is based on the sample code provided here: https://www.acmesystems.it/python_http
# You can create a random file with size of 5 MB in Linux or OS X using the following command:
# dd if=/dev/urandom of=file.bin bs=1024 count=5120

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import sys

proxy_port = int(sys.argv[1])
CDN_IP = (sys.argv[2])
CDN_port = int(sys.argv[3])

# HTTP_PORT = int(sys.argv[5])
# measure_address = str(sys.argv[3])
# measure_port = int(sys.argv[4])
# test_Image = str(sys.argv[6])
#

# This class handles any incoming request from the browser
class MeasurementServerRequestHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        # print('this is the address',(measure_address+':'+str(sys.argv[4])+'/'+test_Image))

        if self.path.endswith('.html'):
            file_path = str(self.path.split("http://"))
            file_path = file_path.strip("[")
            file_path = file_path.strip("'")
            file_path = file_path.strip("]")
            file_path2 = file_path[:-1]
            # print('http://' + sys.argv[4] + ':' + sys.argv[3] + '/' +str(file_path2))

            full_path = str('http://' + sys.argv[2] + ':' + sys.argv[3] + file_path2)

            r2 = requests.get(full_path)

            #print("Args", sys.argv[1], " ", sys.argv[2])

            self.send_response(200)
            self.send_header('Content-type', r2.headers['Content-type'])
            self.send_header('Content-length', r2.headers['Content-length'])
            self.end_headers()
            self.wfile.write(r2.content)











        else:
            # Send 404 (Not Found) status code for any other requests
            self.send_response(404)
        return


try:
    # Create HTTP server with customized class
    server = HTTPServer(('', proxy_port), MeasurementServerRequestHandler)
    print('Started httpserver on port', proxy_port)

    # Wait forever for incoming HTTP requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()