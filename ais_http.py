#!/usr/bin/env python

"""
@author: Vladan S
@copyright: D-Logic   http://www.d-logic.net/nfc-rfid-reader-sdk/
 
"""
__program_version = '4.0.4.2 (build)'

import os
import sys
import cgi
import threading
import time
import requests
import urllib2, urllib
from platform import platform
from urlparse import urlparse, parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from ctypes import *
from socket import *
import shutil
import signal



from shell.ais_shell import *
from constants import *
 
global edit_time


def AisHttpGetProgramVersion():
    return 'App name  : {0}  : {1}' . format(AIS_HTTP, __program_version)


def http_request(path, post_attrib, time_out=20):
    try:       
        req = urllib2.Request(path, post_attrib)        
        req.add_header("Content-type", "application/x-www-form-urlencoded")               
        page = urllib2.urlopen(req, timeout=time_out)        
        return page.read(), page.code
    except urllib2.URLError, urlExc:
        return '', urlExc.reason
    except urllib2.HTTPError, httpExc:
        return '', httpExc.code
        #if hasattr(e, 'reason'):
            #return '', e.reason       
        #elif hasattr(e, 'code'):
            #return '', e.code
                     
                    
class GetHandler(BaseHTTPRequestHandler):
   
    global url_query
    
    def do_GET(self):        
        try:            
            f = open(os.curdir + os.sep + "ais_readers.html")
            self.send_response(200)
            self.send_header("Content-type","text/html")
            self.end_headers()
            self.wfile.write(f.read())
            f.close()            
            return
        except IOError:
            self.send_error(404,"File Not Found: %s" % self.path)
        return    
    
    def do_POST(self):
        try:    
            global url_query, edit_list_choise
            dev = DEV_HND       
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                pq = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                pq = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)                
            else:
                pq = {}
                            
         
            f = ''.join(pq[FUNCTION])      
            # if pq[RTE] != None:        
            #     seconds = int(''.join(pq[RTE]))
            device = ''.join(pq[DEVICE])                    
        
            if GetBaseName() == AIS_MAIN:
                #log_dir = ''.join(pq[LOG_DIR])
                log_dir = 'debug_log' 
                read_deb_log = ''.join(pq[READ_DEBUG_LOG])
                save_deb_log = ''.join(pq[SAVE_DEBUG_LOG])
                if f == "SD":                  
                   # c = open(os.path.join(os.curdir, os.sep, log_dir, save_deb_log))
                    c = open(os.getcwd() + os.sep + log_dir + os.sep +  save_deb_log.strip())
                    self.send_response(200)
                    self.send_header("Content-type","text/json")
                    self.end_headers()
                    self.wfile.write(c.read())
                    c.close() 
                    self.wfile.close()                                       
                    return
                elif f == "D":               
                    self.send_response(200)
                    self.send_header("Content-type","text/html")
                    self.end_headers()                    
                    #c =  open(os.curdir + os.sep + BBB_DEBUG_LOG)
                    
                    c = open(os.getcwd() + os.sep + log_dir + os.sep +  read_deb_log.strip())
                    self.wfile.write("<html><head><title>Read Debug Log</title></head><body>")
                    for line in c:                    
                        l = line.encode("utf-8") 
                        self.wfile.write("<p>%s</p>" % l)                                   
                    c.close()
                    self.wfile.write("</body></html>")
                    self.wfile.close()
                    return                            
            
                               

            if pq[DEVICE_TYPE] != None:
                device_type = ''.join(pq[DEVICE_TYPE])

            if pq[DEVICE_ID] != None:
                device_id = ''.join(pq[DEVICE_ID])

            if pq[EDIT_LIST] != None:
                edit_list_choise = ''.join(pq[EDIT_LIST])


            if f == 'Q':                                
                if edit_list_choise == AVAILABLE_DEVICES :
                    self.wfile.write(edit_device_list(1))
                elif edit_list_choise == ACTUAL_LIST:                    
                    self.wfile.write(edit_device_list(2))
                elif edit_list_choise == CLEAR_LIST:
                    self.wfile.write(edit_device_list(3))
                elif edit_list_choise == ADD_DEVICE:
                    self.wfile.write("AIS_List_AddDevicesForCheck() ...\n")
                    if device_type == '' or device_id == '':
                        self.wfile.write("You must enter values in the relevant fields !")
                        return
                    else:                        
                        self.wfile.write(edit_device_list(4,"AIS_List_AddDeviceForCheck",int(device_type),int(device_id)))
                elif edit_list_choise == ERASE_DEVICE:
                    self.wfile.write("AIS_List_EraseDeviceForCheck()...\n")
                    self.wfile.write(edit_device_list(5,"AIS_List_EraseDeviceForCheck",int(device_type),int(device_id)))
                else:
                    self.wfile.write("") 
                                  
            if f == 'IP':
                from socket import gethostname, gethostbyname                
                from uuid import getnode
                import subprocess
                mac = getnode()
                macAddress = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))                               
                ip = gethostbyname(gethostname())        
                if sys.platform.startswith('linux'):                    
                    l = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
                    ipMac = 'IP address  :{0}MAC address :{1}' .format(l.communicate()[0], macAddress)
                    self.wfile.write(ipMac)
                else:                    
                    ipMac = "IP address  : %s\nMAC address : %s\n" % (ip, macAddress) 
                    self.wfile.write(ipMac)
                
                                                                                        
            if f == 'U':
                if pq[GIT_USERNAME] == None:
                    self.wfile.write('You must enter username !')
                    return                
                    if pq[GIT_PASS] == None:
                        self.wfile.write('You must enter password !')
                        return
                else:  
                    try:
                        gitUserName = ''.join(pq[GIT_USERNAME])
                        gitPassword = ''.join(pq[GIT_PASS])                                                              
                        gitRepo = "https://{0}:{1}@git.d-logic.net/sw-python/ais-readers-cross_platform_client.git" .format(gitUserName, gitPassword)
                        output = 'git pull %s' % gitRepo 
                        out = os.system(output)
                        if out == '' : out = 'Up To Date !'
                        self.wfile.write("GIT: %s" % out)
                      
                        #output = "git submodule update --remote --recursive " 
                        #output = 'git submodule update --init --recursive --remote -- "shell" %s' % gitRepo
                        #subOutput = os.system(output)
                        #if subOutput == '':subOutput = 'Up to date'
                        #self.wfile.write("\nSubmodule: %s" % subOutput) 
                        
                        #os.system('cd web_api/shell')
                        #out = os.system('output')                        
                        #self.wfile.write('Submodule: %s' % out)
                    except Exception as exc:
                        self.wfile.write("Exception: %s" % exc)
                                                    
            if f == 'R':
                import subprocess
                try:
                    if sys.platform.startswith('win'):
                        output = 'Cannot use reboot for Windows !\n'
                        return
                    command = 'sudo reboot '
                    out = os.system(command)
                    output = 'System Reboot NOW: %s' % out 
                except Exception as exc_shut:
                    output = 'System Reboot Error: %s ' % exc_shut
                finally:                             
                    self.wfile.write(output)
                    
                '''
                if len(HND_LIST) == 0:
                    self.wfile.write("\n>> NO DEVICES FOUND (or resource busy) \n " )
                    return
                                        
                if not device.isdigit():                 
                    dev.hnd = HND_LIST[0]
                elif int(device) > len(HND_LIST) or int(device) == 0:
                    self.wfile.write("dev[%s] : NO DEVICE FOUND (or resource busy)" % device)
                    return
                else:
                    dev.hnd = HND_LIST[int(device) -1]
                    #dev.hnd = DDEV_HND[dev.hnd][DEVHND]
                '''   
                                                                         
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

            
            if GetBaseName() == AIS_MAIN:
                from ais_readers_main_process import DoPOST
                self.wfile.write(DoPOST(f))            
            
            
            if f == 'q':                                          
                self.wfile.write(GetListInformation())
                
            
            if len(HND_LIST) == 0:
                self.wfile.write("\nNO DEVICES FOUND (or resource busy) \n " )
                return
            
                   
            if not device.isdigit():                 
                dev.hnd = HND_LIST[0]
            elif int(device) > len(HND_LIST) or int(device) == 0:
                self.wfile.write("dev[%s]NO DEVICE FOUND (or resource busy)" % device)
                return
            else:
                dev.hnd = HND_LIST[int(device) -1]    
                                                
                
            if f == 'o':                            
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
            
            elif f == 'r':
                pass
                rt = ''.join(pq[RTE])                                
                if rt.strip() == '':
                    self.wfile.write('Must enter value for seconds !')
                    return
                else:
                    try:                   
                        seconds = int(rt)
                        stop_time = c_uint64()
                        stop_time = time.time() + seconds #10
                        dev = DEV_HND
                        self.wfile.write("Wait for RTE for %d sec ...\n" % seconds)       
                        while (time.ctime(time.time()) < time.ctime(stop_time)) :
                            for hnd in HND_LIST:
                                dev.hnd = hnd            
                                r, rte = MainLoop()
                                if rte != None:                                                       
                                    self.wfile.write(rte)
                            time.sleep(THD_SLEEP)     
                        self.wfile.write ("End RTE listen") 
                    except Exception as vError:
                        self.wfile.write(vError)
                        return   
                
                  
            elif f == 'l':                         
                self.wfile.write(log_get(dev.hnd))
                
           
            elif f == 'n':                                                          
                self.wfile.write(log_by_index(int(start_index), int(end_index), dev.hnd))               
               
                
            elif f == 'N':                                                       
                self.wfile.write(log_by_time(int(start_time), int(end_time), dev.hnd))  
                
                
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
                global PASS
                self.wfile.write("Actual application password is :%s\n" % PASS)
                if  len(set_def_pass) == 0:
                    self.wfile.write("Patch - new pass = default pass\n")
                    set_def_pass = PASS
                PASS = set_def_pass                    
                self.wfile.write(password_set_default(set_def_pass)) 
                
            elif f == 'p':
                global PASS
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
                self.wfile.write(sys_get_timezone_info() + "\n")
       
           
            elif f == 'E':
                self.wfile.write(ee_lock())
            
            elif f == 'e':
                self.wfile.write(ee_unlock())
           
            elif f == 'F':              
                try:
                    if pq[BIN_FIRMWARE_NAME] != None:
                        firmw_name = ''.join(pq[BIN_FIRMWARE_NAME])
                        fwFile = ''.join(pq[BIN_FNAME])                                                                  
                        with open(firmw_name, 'wb') as out:
                            out.write(fwFile)                             
                        self.wfile.write(fw_update(fw_name=firmw_name))               
                    else:
                        self.wfile.write('NO FILE')
                except Exception as exc:
                    self.wfile.write("ERROR: %s" % exc)
                
            elif f == 's':
                try:
                    if pq[CONFIG_FILE_READ] != None:
                        conf_file_rd = ''.join(pq[CONFIG_FILE_READ])
                        self.wfile.write(config_file_rd(fname=conf_file_rd))
                        
                        from socket import gethostname, gethostbyname 
                        ip = gethostbyname(gethostname())
                         
                        with open(conf_file_rd + '.config' , 'wb') as out:                   
                            http_request(ip + ":" + str(HTTP_SERVER_PORT), out.write(conf_file_rd + '.config'))
                #ip + ":" + str(HTTP_SERVER_PORT)
                except Exception as exc:
                    self.wfile.write("ERROR: %s" % exc)
                
                
            elif f == 'S':               
                try:
                    if pq[CONFIG_FILE_WR_NAME] != None:
                        confFileNameWR = ''.join(pq[CONFIG_FILE_WR_NAME])
                        confFileWR = ''.join(pq[CONFIG_FILE_WRITE])                                                     
                        with open(confFileNameWR, 'wb') as out:
                            out.write(confFileWR)                                                                                                                   
                        self.wfile.write(config_file_wr(fname=confFileNameWR))  
                       
                    else:
                        self.wfile.write('NO FILE')
                except Exception as exc:
                    self.wfile.write("ERROR: %s" % exc)
            
            
                                                                         
            elif f == 'x':
                self.wfile.write("\nServer stopped !\nClose program !\n")            
                shut_event.set()                                            
                if sys.platform.startswith('linux'):
                    os.system('pkill -9 python')
                    os.kill(os.getpid(), signal.SIGINT)
                elif sys.platform.startswith('win'):                    
                    os._exit(0)                
            return
                                
        except (Exception) as error_mess: 
            #self.wfile.write("ERROR: NO DEVICE ???")                               
            self.wfile.write(error_mess.message)                               
           


        
def RunAll():   
    serv = threading.Thread(target=handler_server)   
    serv.start()       
    while True:
        try:                  
            if serv.isAlive():            
                serv.join(timeout = SERV_JOIN)                             
        except (KeyboardInterrupt, SystemExit, Exception) as e:
            httpd.server_close()
            print '\nServer stopped\nProgram close',e
            shut_event.set()
            if sys.platform.startswith('linux'):
                os.system('pkill -9 python')
            elif sys.platform.startswith('win'):            
                sys.exit(0)            
            break
            

def handler_server():
    global httpd
    while not shut_event.is_set():        
        my_lock.acquire()                                                         
        httpd.handle_request()
        my_lock.release()
        time.sleep(THD_SLEEP)

def init():   
    print AISGetLibraryVersionStr() 
    global httpd   
    #dev_list() 
    list_device()    
    httpd = HTTPServer((HTTP_SERVER_NAME,HTTP_SERVER_PORT),GetHandler) 
    httpd.socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) 
    RunAll() 



my_lock = threading.Lock()
shut_event = threading.Event()

if __name__ == '__main__': 
    global httpd     
    init()     
    
        
           
    
    
        
        
                    
 
