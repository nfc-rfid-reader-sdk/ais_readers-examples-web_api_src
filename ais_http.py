#!/usr/bin/env python

"""
@author: Vladan S
@version: 2.0.1.8 (build)  (lib:4.9.4)
 
"""

import os
import sys
import cgi
import threading
import time
import traceback
import requests
import urllib2,urllib
from platform import platform
from urlparse import urlparse, parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from ctypes import *
from socket import *


from shell.ais_shell import *
from constants import *




def http_request(path, post_attrib):
    try:
        req = urllib2.Request(path, post_attrib)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        page = urllib2.urlopen(req).read()
    except Exception as e:
        print e

class GetHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        pass
        return
    
    
    def do_POST(self):
        pass                
        dev              = DEV_HND       
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            pq = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            pq = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            pq = {}
      
        try:  
           
            f             = ''.join(pq[FUNCTION])             
            seconds       = int(''.join(pq[RTE]))
            device        = ''.join(pq[DEVICE])
                     
            if device == None or device == '':
                dev.hnd  = HND_LIST[0]
                device   = dev.hnd          
            else:
                dev.hnd  = HND_LIST[int(device) - 1]
          
          
           
            if pq[START_INDEX] != None or pq[END_INDEX] != None:
               start_index = (''.join(pq[START_INDEX]))
               end_index   = (''.join(pq[END_INDEX]))
              
            
            if pq[START_TIME] != None or pq[END_TIME] != None:
               start_time = (''.join(pq[START_TIME]))        
               end_time   = (''.join(pq[END_TIME]))
             
               
            if pq[WHITE_LIST_WRITE] != None:            
                white_list_write = ''.join(pq[WHITE_LIST_WRITE])
               
            
            if pq[BLACK_LIST_WRITE]!= None:
                black_list_write = ''.join(pq[BLACK_LIST_WRITE])  
            
            if pq[DEFAULT_APP_PASS] != None:
                set_def_pass = ''.join(pq[DEFAULT_APP_PASS])
                
            if pq[NEW_PASS] != None:
                new_pass  = ''.join(pq[NEW_PASS])
                       
            if pq[UNREAD_LOG] != None:                 
                get_unread_log = (''.join(pq[UNREAD_LOG]))
            
            if pq[LIGHTS] != None:
                lights_choise = ''.join(pq[LIGHTS])   
                               
            if pq[EDIT_LIST] != None:
                edit_list_choise = ''.join(pq[EDIT_LIST])
               
                      
            if pq[DEVICE_TYPE] != None:
                device_type = ''.join(pq[DEVICE_TYPE])
            
            if pq[DEVICE_ID] != None:
                device_id  = ''.join(pq[DEVICE_ID])
            
           
            
            if f == 'q':                
                self.wfile.write(GetListInformation())
                
            elif f == 'o':
                #self.AISOpen() #self.wfile.write("<h1>" + str(list_res([0][0])) + "</h1>")              
                pass                
                self.wfile.write(AISOpen())                
                    
            elif f == 'c':
                self.wfile.write(AISClose())
            
            if f == 'd':                             
                self.wfile.write('GET DEVICES COUNT > %s\n' % AISUpdateAndGetCount())                        
        
            elif f == 't': 
                self.wfile.write(active_device()) 
                self.wfile.write(AISGetTime())       
            
            elif f == 'T':             
                self.wfile.write(sys_get_timezone_info()+ "\n")
                self.wfile.write(AISSetTime())
            
            elif f == 'E':
                pass                
                stop_time = c_uint64()
                stop_time = time.time() + seconds #10
                dev       = DEV_HND
                self.wfile.write("Wait for RTE for %d sec ...\n" % seconds)       
                while (time.ctime(time.time()) < time.ctime(stop_time)) :
                    for hnd in HND_LIST:
                        dev.hnd = hnd            
                        r,rte = MainLoop()                       
                        self.wfile.write(rte)
                    time.sleep(THD_SLEEP)     
                self.wfile.write ("End RTE listen")    
                
                  
            elif f == 'l':                
                self.wfile.write(log_get()) 
           
            elif f == 'n':                                             
                self.wfile.write(log_by_index(int(start_index),int(end_index)))               
            
            elif f == 'N':                                          
                self.wfile.write(log_by_time(int(start_time),int(end_time)))  

            elif f == 'u':                
                get_unread_log = int(get_unread_log)                                
                self.wfile.write(get_unread_log_one(get_unread_log))
           
            elif f == 'v':            
                self.wfile.write("AIS_GetDLLVersion() >> %s\n" % AISGetLibraryVersionStr())
                      
            elif f == 'w':               
                self.wfile.write(whitelist_read())
                
            elif f == 'b':                
                self.wfile.write(blacklist_read())

            elif f == 'W':                                    
                self.wfile.write(whitelist_write(white_list_write))                                  

            elif f == 'B':                                                
                self.wfile.write(blacklist_write(black_list_write))                                 

            elif f == 'L':                          
                self.wfile.write(TestLights(lights_choise))
                
            elif f == 'g':               
                self.wfile.write(get_io_state())
            elif f == 'G':               
                self.wfile.write(lock_open())
            elif f == 'y':               
                self.wfile.write(relay_toogle())
          
            elif f == 'P':                               
                self.wfile.write("Actual application password is :%s\n" % PASS)
                if  len(set_def_pass) == 0:
                    self.wfile.write("Patch - new pass = default pass\n")
                    set_def_pass = PASS
                PASS = set_def_pass                    
                self.wfile.write(password_set_default(set_def_pass)) 
                
            elif f == 'p':
                self.wfile.write("Old password is actual application password: %s\n" % PASS)           
                self.wfile.write("New password for units ( and application ): %s\n" % new_pass)
                if  len(new_pass) == 0:
                    self.wfile.write ("Patch - new pass = default pass\n")
                    new_pass = PASS 
                self.wfile.write("Try set new password for units= %s\n" % (new_pass))
                self.wfile.write(password_change(new_pass))                       

            elif f == 'd':
                self.wfile.write(AISGetDevicesForCheck()) 
          
            elif f == 'f':               
                self.wfile.write(AISGetVersion())
            
            elif f == 'i':              
                self.wfile.write(AISGetVersion())
                self.wfile.write(AISGetTime())
                self.wfile.write(sys_get_timezone_info()+ "\n")
           
            elif f == 'Q':             
                if edit_list_choise == AVAILABLE_DEVICES :            
                    self.wfile.write(edit_device_list(1))
                elif edit_list_choise == ACTUAL_LIST:
                    self.wfile.write(edit_device_list(2))
                elif edit_list_choise == CLEAR_LIST:
                    self.wfile.write(edit_device_list(3))
                elif edit_list_choise == ADD_DEVICE:
                    self.wfile.write("AIS_List_AddDevicesForCheck() ...\n")
                    self.wfile.write(edit_device_list(4,"AIS_List_AddDeviceForCheck",int(device_type),int(device_id)))
                elif edit_list_choise == ERASE_DEVICE:
                    self.wfile.write("AIS_List_EraseDeviceForCheck()...\n")
                    self.wfile.write(edit_device_list(5,"AIS_List_EraseDeviceForCheck",int(device_type),int(device_id)))
             
                else:
                    self.wfile.write("")
           
            elif f == 'x':
                self.wfile.write("\nServer stopped !\nClose program !\n")            
                shut_event.set()
                httpd.server_close()                
                if sys.platform.startswith('linux'):
                    os.system('pkill -9 python')
                elif sys.platform.startswith('win'):                    
                    sys.exit(0)
                
        except (Exception) as error_mess:
                self.wfile.write(error_mess)
                self.wfile.write(traceback.print_exc())
        return
        
def RunAll():   
    serv = threading.Thread(target=handler_server)   
    serv.start()       
    while True:
        try:          
        
            if serv.isAlive():            
                serv.join(timeout = SERV_JOIN)                     
        
        except (KeyboardInterrupt,SystemExit,Exception) as e:
            httpd.server_close()
            print '\nServer stopped\nProgram close',e
            shut_event.set()
            if sys.platform.startswith('linux'):
                os.system('pkill -9 python')
            elif sys.platform.startswith('win'):            
                sys.exit(0)            
            break
            

def handler_server():
    while not shut_event.is_set():        
        my_lock.acquire()                                                         
        httpd.handle_request()
        my_lock.release()
        time.sleep(THD_SLEEP)

def init():   
    print AISGetLibraryVersionStr() 
    global httpd   
    dev_list()     
    httpd = HTTPServer((HTTP_SERVER_NAME,HTTP_SERVER_PORT),GetHandler) 
    httpd.socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) 
    RunAll() 



my_lock = threading.Lock()
shut_event = threading.Event()

if __name__ == '__main__': 
    global httpd 
    
    # global mySO
    # mySO = GetPlatformLib() 
    init()     
    
        
           
    
    
        
        
                    
 
