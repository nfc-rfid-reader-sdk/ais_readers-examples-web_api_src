#!/usr/bin/env python

"""
@author: Vladan S
@version: 2.0.1.4 (build)  (lib:4.8.0)
 
"""



import MySQLdb as mdb

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
from constants import *
from dl_status import *
from ais_readers_list import *

import device_list

HND_LIST  = []    
devCount  = c_long()       
DEV_HND   = device_list .S_DEVICE()
log_t     = device_list .S_LOG()



def GetPlatformLib():       
            if sys.platform.startswith("win32"):
                return windll.LoadLibrary(os.getcwd() + LIB_PATH + WIN_PATH + LIB_WIN32)
            elif sys.platform.startswith("linux"):
                return cdll.LoadLibrary(os.getcwd() + LIB_PATH + LINUX_PATH + LIB_LINUX) #ARMHF_PATH + LIB_ARMHF (for BeagleBoneBlack)
            elif platform().lower().find('armv7l-with-debian') > -1:
                return cdll.LoadLibrary(os.getcwd() + LIB_PATH + LINUX_PATH + LIB_ARMHF) #CARM
    
    
def AISGetVersion():
        
        hardware_type    = c_int() 
        firmware_version = c_int()
        dev              = DEV_HND
        DL_STATUS = mySO.AIS_GetVersion(dev.hnd,byref(hardware_type),byref(firmware_version))                   
        res = "AIS_GetVersion() |>>hw = %d | fw = %d\n" % (hardware_type.value,firmware_version.value)    
        return res
    
    
def AISUpdateAndGetCount():          
        return mySO.AIS_List_UpdateAndGetCount()
    

    

      
        
         
def AISGetTime():
        
        dev      = DEV_HND       
        currTime = c_uint64()        
        timezone = c_int()
        DST      = c_int()
        offset   = c_int()        
      
        dev.status = mySO.AIS_GetTime(dev.hnd,byref(currTime),byref(timezone),byref(DST),byref(offset))                            
        res = "AIS_GetTime(dev= 0x%X)> {%d(%s):%s} = (tz= %d | dst= %d | offset= %d)  %d | %s\n" % (dev.hnd,dev.status,hex(dev.status),E_ERROR_CODES[dev.status],timezone.value,DST.value,offset.value,currTime.value, time.ctime(currTime.value)) 
                                                
        return res
        
    
def AISSetTime():
    
    currTime = c_uint64
    timez    = c_int
    DST      = c_int
    offset   = c_int 
    dev      = DEV_HND
       
    currTime = int(time.time())
    timez    = time.timezone
    DST      = time.daylight
    offset   = -3600
    
    ais_set_time = mySO.AIS_SetTime
    ais_set_time.argtypes = (c_void_p,c_char_p,c_uint64,c_int,c_int,c_int)
    ais_set_time.restype = c_int
    result = ais_set_time(dev.hnd,PASS,currTime,timez,DST,offset)
    
    res    = "AIS_SetTime(pass:%s)> timezone=%d | DST=%d |offset=%d {%d(%s)%s}|%s\n" % \
             (PASS,timez,DST,offset,result,hex(result),E_ERROR_CODES[result],time.ctime(currTime))
        
    return res
      
    
def AISGetDevicesForCheck():                    
        myStr = mySO.AIS_List_GetDevicesForCheck           
        myStr.restype = c_char_p
        print 'GetDevicesForCheck: %s' % myStr()                            
        return myStr()
        
    
def AISEraseAllDevicesForCheck():
        mySO.AIS_List_EraseAllDevicesForCheck()
        
   
def AISAddDeviceForCheck(devType,devId):            
        return mySO.AIS_List_AddDeviceForCheck(devType,devId)
    
                                

def blacklist_write(black_list_write):    
    dev        = DEV_HND
    dev.status = mySO.AIS_Blacklist_Write(dev.hnd,PASS,black_list_write)
    res        = 'AIS_Blacklist_Write(pass:%s):b_list= %s > %s\n' %  (PASS,black_list_write,dl_status2str(dev.status))
    return res

def whitelist_write(white_list_write):       
    dev        = DEV_HND
    dev.status = mySO.AIS_Whitelist_Write(dev.hnd,PASS,white_list_write)
    res = '\nAIS_Whitelist_Write(pass:%s):w_list= %s > %s\n' %  (PASS,white_list_write,dl_status2str(dev.status))
    return res
    




def print_percent_hdr():
        i = c_int
        sys.stdout.write("%")
        for i in range(0,101):            
            sys.stdout.write(str(i % 10))
        sys.stdout.write("\n%=")
  
def AISOpen():        
        dev      = DEV_HND
        for hnd in HND_LIST:
            aop  = mySO.AIS_Open(hnd)
            #res  = "AIS_Open():{%d(0x%X):%s} hnd[0x%X]" % (aop,aop,E_ERROR_CODES[aop],hnd)                                 
        dev.hnd  = HND_LIST[0]  #default           
        print "DEFAULT DEVICE hnd[0x%X] \n" % dev.hnd  

def dev_list():
    list_init = c_bool
    list_init = False
    if not list_init:
        ListDevices() #prepare device list
        list_init = True

    devCount = AISUpdateAndGetCount()
    res      = "AIS_List_UpdateAndGetCount()= [%d]\n" % devCount
    if devCount:
        GetListInformation()            
        AISOpen()                                            
    else:
        res = "NO DEVICE FOUND"
        print res
    return res 
 
 
# def PrintLOG():
       
        # logIndex     = c_int()
        # logAction    = c_int()
        # logReaderId  = c_int()
        # logCardId    = c_int()
        # logSystemId  = c_int()
        # logNfcUid       = (c_uint8 * NFC_UID_MAX_LEN)()
        # logNfcUidLen    = c_int()
        # logTimeStamp    = c_uint64() 
        # nfcuid       = str()
                   
        # dev = DEV_HND 
        # print rte_list_header[0],'\n', \
              # rte_list_header[1],'\n', \
              # rte_list_header[2]   
               
        # while True:            
            # dev.status =  mySO.AIS_ReadLog(dev.hnd,byref(logIndex),
                                               # byref(logAction),
                                               # byref(logReaderId),
                                               # byref(logCardId),
                                               # byref(logSystemId),
                                               # logNfcUid,
                                               # byref(logNfcUidLen),
                                               # byref(logTimeStamp)
                                          # )
                   
            # dev.log.log_index       = logIndex.value
            # dev.log.log_action      = logAction.value
            # dev.log.log_reader_id   = logReaderId.value
            # dev.log.log_card_id     = logCardId.value
            # dev.log.log_system_id   = logSystemId.value
            # dev.log.log_nfc_uid     = logNfcUid
            # dev.log.log_nfc_uid_len = logNfcUidLen.value
            # dev.log.log_timestamp   = logTimeStamp.value
            
            
            # if dev.status != 0:
                # break
            
            # nfcuid = '' 
            # for i in range(0,dev.log.log_nfc_uid_len):                
                # nfcuid += ":%02X" % (dev.log.log_nfc_uid[i])
            
            # uidNfcUidLen = '[' + str(dev.log.log_nfc_uid_len) + '] | ' + nfcuid  
          
            
            
            # print(log_format.format(dev.log.log_index,
                                    # #string_at(mySO.dbg_action2str(dev.log.log_action)).decode('utf-8'),
                                    # dbg_action2str(dev.log.log_action),
                                    # dev.log.log_reader_id,
                                    # dev.log.log_card_id,
                                    # dev.log.log_system_id,
                                    # uidNfcUidLen,                                    
                                    # dev.log.log_timestamp,
                                    # time.ctime(dev.log.log_timestamp)
                                   # )
                 # )
       
        # print rte_list_header[2]
        # print wr_status('AIS_GetLog()', dev.status)
 
    
def SendToMysql(logIndex,logAction,logReaderId,logCardId,logSystemId,nfcUID,nfcUIDLen,timestamp,mytime):
        
        part0 = "INSERT INTO " + TABLE_NAME + "(log_index,log_action,log_reader_id,log_card_id,log_system_id,nfc_uid,nfc_uid_len,timestamp,m_time)"
        part1 = "VALUES ('" + str(logIndex) + "','" \
                            + str(logAction)   + "','" \
                            + str(logReaderId) + "','" \
                            + str(logCardId) + "','" \
                            + str(logSystemId) + "','" \
                            + str(nfcUID)      + "','" \
                            + str(nfcUIDLen)   + "','" \
                            + str(timestamp)   + "','" \
                            + str(mytime)      + "')"  
        
        try:                
            con = mdb.connect(SERVER_NAME,SERVER_USER_NAME,SERVERPASSWORD,DATABASE_NAME)
            with con:               
                cur = con.cursor()
                cur.execute(part0 + part1)                        
            con.commit()                
        except mdb.Error,e:          
            print ("Error %d: %s" % (e.args[0],e.args[1]))            
        finally:                
            if con:
                con.close()   
                

def http_request(path, post_attrib):
    try:
        req = urllib2.Request(path, post_attrib)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        page = urllib2.urlopen(req).read()
    except Exception as e:
        print e



def http_post_to_mysql(logIndex,logAction,logReaderId,logCardId,logSystemId,nfcUID,nfcUIDLen,timestamp,mytime):
    
    rte = {LOG_INDEX    : logIndex,
           LOG_ACTION   : logAction,
           LOG_READER_ID: logReaderId,
           LOG_CARD_ID  : logCardId,
           LOG_SISTEM_ID: logSystemId,
           NFC_UID      : nfcUID,
           NFC_UID_LEN  : nfcUIDLen,
           TIMESTAMP    : timestamp,
           M_TIME       : mytime   
           }
    
    rte  = urllib.urlencode(rte)
    path = HTTP + SERVER_NAME + RTE_EVENTS    
    print path
    http_request(path, rte)
 
                             
    
            
            
def AIS_GetLog_Set():
    dev       = DEV_HND
    DL_STATUS = mySO.AIS_GetLog_Set(dev.hnd, PASS)
    res       = DL_STATUS,hex( DL_STATUS),E_ERROR_CODES[ DL_STATUS]
    return res     

        
             
def GetInfoAndDeviceCount():            
        print  AISUpdateAndGetCount()
         
def GetTime():                
        print  AISGetTime()
     

    
def ListDevices():
            
        deviceType = E_KNOWN_DEVICE_TYPES['DL_BASE_HD']        
        AISEraseAllDevicesForCheck()        
        
        deviceId = 1        
        DL_STATUS =  AISAddDeviceForCheck(deviceType, deviceId) 
       
        deviceId = 3        
        DL_STATUS =  AISAddDeviceForCheck(deviceType, deviceId) 
        
        
def GetListInformation():
        hnd            = c_void_p()
        devSerial      = c_char_p()
        devType        = c_int()
        devID          = c_int()
        devFW_VER      = c_int()
        devCommSpeed   = c_int()
        devFTDI_Serial = c_char_p()
        devOpened      = c_int()
        devStatus      = c_int()
        systemStatus   = c_int()    
        dev            = DEV_HND
        
        print format_grid[0],'\n',format_grid[1],'\n',format_grid[2]
      
        devCount =  AISUpdateAndGetCount()
        
        for i in range(0,devCount):                             
            DL_STATUS =  mySO.AIS_List_GetInformation(byref(hnd),
                                                     byref(devSerial),
                                                     byref(devType),
                                                     byref(devID),
                                                     byref(devFW_VER),
                                                     byref(devCommSpeed),
                                                     byref(devFTDI_Serial),
                                                     byref(devOpened),
                                                     byref(devStatus),
                                                     byref(systemStatus)
                                                    )
            HND_LIST.append(hnd.value)
            
            print(mojFormat.format(i+1,
                                   hnd.value,
                                   devSerial.value.decode("utf-8"),
                                   devType.value,
                                   devID.value,
                                   devFW_VER.value,
                                   devCommSpeed.value,
                                   devFTDI_Serial.value.decode("utf-8"),
                                   devOpened.value,
                                   devStatus.value,
                                   systemStatus.value
                                   )
                 )
                  
            print format_grid[0],'\n'
    
    

    
def TestLights(choise):
        
        green_master = False
        red_master   = False
        green_slave  = False
        red_slave    = False
        dev          = DEV_HND
        
        
        
        
        if choise == 'g':
                green_master = not green_master
        elif choise == 'r':
                red_master = not red_master
        elif choise == 'G':
                green_slave = not green_slave
        elif choise == 'R':
                red_slave = not red_slave            
            
        DL_STATUS = mySO.AIS_LightControl(dev.hnd,green_master,red_master,green_slave,red_slave)
        res = "AIS_LightControl(green= %d | red= %d || slave:green= %d | red= %d) > %s\n" % (green_master,red_master,green_slave,red_slave,E_ERROR_CODES[ DL_STATUS])                                                                                            
        return res
    

    
    
    
class GetHandler(BaseHTTPRequestHandler):
    
    def GetListDevices(self):
        hnd            = c_void_p()
        devSerial      = c_char_p()
        devType        = c_int()
        devID          = c_int()
        devFW_VER      = c_int()
        devCommSpeed   = c_int()
        devFTDI_Serial = c_char_p()
        devOpened      = c_int()
        devStatus      = c_int()
        systemStatus   = c_int()    
        dev            = DEV_HND
        
        devCount =  AISUpdateAndGetCount()
        
        self.wfile.write("AISUpdateAndGetCount()= %d\n" %devCount)
        self.wfile.write(format_grid[0] + '\n')
        self.wfile.write(format_grid[1] + '\n')
        self.wfile.write(format_grid[2] + '\n')

        
        del HND_LIST[:]
        
        for i in range(0,devCount):                             
            DL_STATUS =  mySO.AIS_List_GetInformation(byref(hnd),
                                             byref(devSerial),
                                             byref(devType),
                                             byref(devID),
                                             byref(devFW_VER),
                                             byref(devCommSpeed),
                                             byref(devFTDI_Serial),
                                             byref(devOpened),
                                             byref(devStatus),
                                             byref(systemStatus)
                                            )
            HND_LIST.append(hnd.value)
            
            self.wfile.write(mojFormat.format(i+1,
                                hnd.value,
                                devSerial.value.decode("utf-8"),
                                devType.value,
                                devID.value,
                                devFW_VER.value,
                                devCommSpeed.value,
                                devFTDI_Serial.value.decode("utf-8"),
                                devOpened.value,
                                devStatus.value,
                                systemStatus.value
                                )
                            )                  
            self.wfile.write('\n' + format_grid[0] + '\n')
    
    def AISOpen(self):
        dev = DEV_HND
        for hnd in HND_LIST:
            aop     = mySO.AIS_Open(hnd)            
            dev.hnd = hnd
            self.wfile.write("AIS_Open(0x%X):{ %d(%s):%s} hnd[0x%X]\n" % (dev.hnd,aop,hex(aop),E_ERROR_CODES[aop],hnd))         
            if aop == 0:
                self.wfile.write(AISGetTime())
                self.wfile.write(sys_get_timezone_info()+ "\n")
        
        dev.hnd  = HND_LIST[0]
        self.wfile.write("ACTIVE DEVICE HND >> [0x%X]\n" % dev.hnd)
 
    def AISClose(self):
        for hnd in HND_LIST:
            acl = mySO.AIS_Close(hnd)
            res = "AIS_Close():{ %d(%s):%s} hnd[0x%X]\n" % (acl,hex(acl),E_ERROR_CODES[acl],hnd)
            self.wfile.write(res)    
    
    def log_get(self):
           
        dev        = DEV_HND
        dev.status = mySO.AIS_GetLog_Set(dev.hnd, PASS)
        self.wfile.write(wr_status('AIS_GetLog_Set()',dev.status))
        if dev.status != 0:
            return   
        self.DoCmd()
        self.PrintLOG() 

    def log_by_index(self,start_index,end_index):        
        dev         = DEV_HND
        dev.status  = mySO.AIS_GetLogByIndex(dev.hnd,PASS,start_index,end_index)        
        self.wfile.write('AIS_GetLogByIndex:(pass: %s [ %d - %d ] >> %s\n)' % (PASS,start_index,end_index,E_ERROR_CODES[dev.status]))        
        if dev.status != 0:
            return
        self.DoCmd()    
        self.PrintLOG()    
    
    def log_by_time(self,start_time,end_time):
        start_time = c_uint64(start_time)
        end_time   = c_uint64(end_time)    
        dev        = DEV_HND
        dev.status = mySO.AIS_GetLogByTime(dev.hnd,PASS,start_time,end_time)
        self.wfile.write('AIS_GetLogByTime:(pass: %s [ %10d - %10d ] >> %s)\n' % (PASS,start_time.value,end_time.value,E_ERROR_CODES[dev.status]))        
        if dev.status !=0:
            return
        self.DoCmd()    
        self.PrintLOG()     
    
    def whitelist_read(self):    
        white_list_size = c_int()
        white_list      = c_char_p()    
        dev             = DEV_HND              
        dev.status      = mySO.AIS_Whitelist_Read(dev.hnd,PASS,byref(white_list))    
        if white_list.value:
            white_list_size = len(white_list.value)
        else:
            white_list_size = 0
        self.wfile.write ("AIS_Whitelist_Read(pass:%s): size= %d >%s\n" % (PASS,white_list_size,dl_status2str(dev.status)) )                 
        self.wfile.write(white_list.value)
    
    def blacklist_read(self):   
        black_list_size = c_int()   
        dev             = DEV_HND       
        dev.status      = mySO.AIS_Blacklist_GetSize(dev.hnd,PASS, byref(black_list_size))    
        black_list      = (c_char * black_list_size.value)()   
        res             =  "AIS_Blacklist_GetSize(pass:%s): size= %d > %s\n" % (PASS,black_list_size.value,dl_status2str(dev.status))        
        if dev.status and  black_list_size.value <= 0:        
            self.wfile.write(res)
        dev.status =  mySO.AIS_Blacklist_Read(dev.hnd, black_list);
        l          = list(black_list)    
        self.wfile.write(res)
        self.wfile.write(''.join(l))
        
    def change_password(self,new_pass):
        self.wfile.write("=- Change password -=\n")
        global PASS    
        dev = DEV_HND     
        if  len(new_pass) == 0:
            self.wfile.write("Patch - new pass = default pass")
            new_pass = PASS
        
        self.wfile.write("old pass = %s\nnew pass = %s\n" % (PASS,new_pass))
        dev.status = mySO. AIS_ChangePassword(dev.hnd,PASS,new_pass)
        self.wfile.write("AIS_ChangePassword (old pass= %s new pass= %s |%s\n"%(PASS,new_pass,dl_status2str(dev.status)))
        if dev.status == 0:
            PASS = new_pass
            self.wfile.write("New default application password = %s\n" % PASS)    
        
    def set_default_password(self,default_app_pass):
        global PASS
        self.wfile.write("=- Set default password -=\n")
        self.wfile.write("Actual application password is :%s\n" % PASS)    
        if  len(default_app_pass) == 0:
            self.wfile.write("Patch - new pass = default pass")
            default_app_pass = PASS    
        PASS = default_app_pass
        self.wfile.write("New default application password = %s\n" % PASS)
    
    
    
    
    def RTEListen(self):
        stop_time = c_uint64()
        stop_time = time.time() + 10 #10
        dev       = DEV_HND
        self.wfile.write("Wait for RTE for %d...\n" % SECONDS )      
        while (time.ctime(time.time()) < time.ctime(stop_time)) :
            for hnd in HND_LIST:
                dev.hnd = hnd            
                self.MainLoop()                       
                time.sleep(THD_SLEEP)     
        self.wfile.write("\nEnd RTE listen" )
    
    
    
    
    
    def DoCmd(self):    
        dev = DEV_HND
        dev.print_percent_hdr = True    
        while True:
            if not self.MainLoop():
                break        
            if dev.cmdResponses !=0:
                break
    
    def PrintRTE(self):
  
        logIndex     = c_int()
        logAction    = c_int()
        logReaderId  = c_int()
        logCardId    = c_int()
        logSystemId  = c_int()
        nfcUid       = (c_uint8 * NFC_UID_MAX_LEN)()
        nfcUidLen    = c_int()
        timeStamp    = c_uint64() 
        nfcUid       = str()
        rteCount     = c_int
        dev          = DEV_HND
        rte_count    =  mySO.AIS_ReadRTE_Count(dev.hnd)
        
        self.wfile.write("AIS_ReadRTE_Count = %d\n" % rte_count)
        self.wfile.write("= RTE Real Time Events = \n")       
        self.wfile.write(rte_list_header[0] + "\n")
        self.wfile.write(rte_list_header[1] + "\n")
        self.wfile.write(rte_list_header[2] + "\n")
                
        while True:                
            DL_STATUS =  mySO.AIS_ReadRTE(dev.hnd,
                                           byref(logIndex),
                                           byref(logAction),
                                           byref(logReaderId),
                                           byref(logCardId),
                                           byref(logSystemId),
                                           nfcUid,
                                           byref(nfcUidLen),
                                           byref(timeStamp)
                                         )
            
            
            dev.log.log_index       = logIndex.value
            dev.log.log_action      = logAction.value
            dev.log.log_reader_id   = logReaderId.value
            dev.log.log_card_id     = logCardId.value
            dev.log.log_system_id   = logSystemId.value
            dev.log.log_nfc_uid     = nfcUid
            dev.log.log_nfc_uid_len = nfcUidLen.value
            dev.log.log_timestamp   = timeStamp.value
          
            if  DL_STATUS != 0:
                break  
            nfcuid = ''    
            for i in range(0,dev.log.log_nfc_uid_len):                
                nfcuid += ":%02X" % dev.log.log_nfc_uid[i]
            
            uid_uid_len = '[' + str(dev.log.log_nfc_uid_len) + '] | ' + nfcuid 
            self.wfile.write(rte_format.format (dev.log.log_index,                                     
                                     dbg_action2str(dev.log.log_action),
                                     dev.log.log_reader_id,
                                     dev.log.log_card_id,
                                     dev.log.log_system_id,
                                     uid_uid_len,#nfc_uid + nfc_uid_len                                    
                                     dev.log.log_timestamp,
                                     time.ctime(dev.log.log_timestamp)
                                    )
                            )            
            self.wfile.write("\n" + rte_list_header[2] + "\n")
            
            
            
            
#            try:                
#                 SendToMysql(dev.log.log_index,                           
#                             dbg_action2str(dev.log.log_action),
#                             dev.log.log_reader_id,
#                             dev.log.log_card_id,
#                             dev.log.log_system_id,
#                             nfcuid, #nfc_uid
#                             dev.log.log_nfc_uid_len,
#                             dev.log.log_timestamp,
#                             time.ctime(dev.log.log_timestamp)
#                            )
                   
                # http_post_to_mysql(dev.log.log_index,                           
                             # dbg_action2str(dev.log.log_action),
                             # dev.log.log_reader_id,
                             # dev.log.log_card_id,
                             # dev.log.log_system_id,
                             # nfcuid, #nfc_uid
                             # dev.log.log_nfc_uid_len,
                             # dev.log.log_timestamp,
                             # time.ctime(dev.log.log_timestamp)
                            # ) 
             
            # except Exception as error_mess:
                # self.wfile.write(error_mess + "\n")
        
        #self.wfile.write("LOG unread (incremental) = %d" % dev.UnreadLog)                
        self.wfile.write(wr_status('AIS_ReadRTE()', DL_STATUS))
    
    
    def MainLoop(self):
        pass            
        real_time_events  = c_int()
        log_available     = c_int()
        cmd_responses     = c_int()
        unread_log        = c_int()        
        cmd_percent       = c_int()
        device_status     = c_int()
        time_out_occurred = c_int()
        _status           = c_int()
        dev               =  DEV_HND  
       
        dev.status        =  mySO.AIS_MainLoop(dev.hnd,
                                                    byref(real_time_events),
                                                    byref(log_available),
                                                    byref(unread_log),
                                                    byref(cmd_responses),                                                 
                                                    byref(cmd_percent),
                                                    byref(device_status),
                                                    byref(time_out_occurred),
                                                    byref(_status)
                                                 ) 
                 
        dev.RealTimeEvents  = real_time_events.value
        dev.LogAvailable    = log_available.value
        dev.UnreadLog       = unread_log.value
        dev.cmdResponses    = cmd_responses.value                                                 
        dev.cmdPercent      = cmd_percent.value
        dev.DeviceStatus    = device_status.value
        dev.TimeoutOccurred = time_out_occurred.value
        dev.Status          = _status.value
         
        if dev.status:                            
            return False           
        
        if dev.RealTimeEvents:                 
            self.PrintRTE()
        
        if dev.LogAvailable:
            self.wfile.write ("LOG= %d\n" % dev.LogAvailable)
            self.PrintLOG()
        
        if dev.UnreadLog_last != dev.UnreadLog:
            dev.UnreadLog_last = dev.UnreadLog
        
        if dev.TimeoutOccurred:
            self.wfile.write("TimeoutOccurred= %d\n" % dev.TimeoutOccurred)  
            
            
        if dev.cmdPercent:
            if dev.print_percent_hdr:
                #print_percent_hdr()
                dev.percent_old = -1
                dev.print_percent_hdr = False
            
            while (dev.percent_old != dev.cmdPercent):
                if dev.percent_old < 100:
                    #sys.stdout.write(".")                    
                    dev.percent_old +=1
        
        if dev.cmdResponses:            
            self.wfile.write("\n-- COMMAND FINISH !\n")
               
        return True 
    
      
    def u_log_info(self): 
        log_available = c_uint32()
        r_log         = c_int   
        dev           = DEV_HND
        
        r_log = mySO.AIS_ReadLog_Count(dev.hnd)    
        if r_log:
            self.wfile.write("AIS_ReadLog_Count() %d\n" % r_log)        
        r_log = mySO.AIS_ReadRTE_Count(dev.hnd)
        if r_log:
            self.wfile.write("AIS_ReadRTE_Count() %d\n" % r_log)
        
    def u_log_count(self):
    
    #===if dll_less 4.8.0
    # dev.status = mySO.AIS_UnreadLOG_Count(dev.hnd,byref(log_available))
    # if dev.status:
    # print wr_status("AIS_UnreadLOG_Count()",dev.status)
    # return
        dev           = DEV_HND
        self.MainLoop()    
        self.wfile.write("LOG unread (incremental) = %d\n" % dev.UnreadLog)    
        self.u_log_info()
        return dev.UnreadLog
    
    def u_log_get(self):
        dev           = DEV_HND
        logIndex     = c_int()
        logAction    = c_int()
        logReaderId  = c_int()
        logCardId    = c_int()
        logSystemId  = c_int()
        nfcUid       = (c_uint8 * NFC_UID_MAX_LEN)()
        nfcUidLen    = c_int()
        timeStamp    = c_uint64() 
        nfcUid       = str()
        
        self.wfile.write(rte_list_header[0] + '\n')
        self.wfile.write(rte_list_header[1] + '\n')
        self.wfile.write(rte_list_header[2] + '\n')
        
        dev.status = mySO.AIS_UnreadLOG_Get(dev.hnd,
                                            byref(logIndex),
                                            byref(logAction),
                                            byref(logReaderId),
                                            byref(logCardId),
                                            byref(logSystemId),
                                            nfcUid,
                                            byref(nfcUidLen),
                                            byref(timeStamp)
                                           )
        if dev.status:            
            return 
        nfcuid = ''    
        for i in range(0,nfcUidLen.value):                
            nfcuid += ":%02X" % nfcUid[i]
            
        uid_uid_len = '[' + str(nfcUidLen.value) + '] | ' + nfcuid 
        self.wfile.write(rte_format.format (logIndex.value,                                     
                                 dbg_action2str(logAction.value),
                                 logReaderId.value,
                                 logCardId.value,
                                 logSystemId.value,
                                 #uidUidLen,#nfc_uid + nfc_uid_len                                    
                                 uid_uid_len,
                                 timeStamp.value,
                                 time.ctime(timeStamp.value)
                                    ) 
                         )                   
                                            
        self.wfile.write('\n' + rte_list_header[0] + '\n')                                                  
        self.wfile.write(wr_status("AIS_UnreadLOG_Get()",dev.status))        
        self.u_log_info()
    
    def u_log_ack(self):
        dev           = DEV_HND
        rec_to_ack = c_uint32()
        rec_to_ack = RECORDS_TO_ACK
        dev.status = mySO.AIS_UnreadLOG_Ack(dev.hnd,rec_to_ack)
        self.wfile.write(wr_status("AIS_UnreadLOG_Ack()",dev.status))
        if dev.status:
            return
        self.u_log_info()
    
    
    
    def PrintLOG(self):
       
        logIndex     = c_int()
        logAction    = c_int()
        logReaderId  = c_int()
        logCardId    = c_int()
        logSystemId  = c_int()
        logNfcUid    = (c_uint8 * NFC_UID_MAX_LEN)()
        logNfcUidLen = c_int()
        logTimeStamp = c_uint64() 
        nfcuid       = str()
                   
        dev          = DEV_HND 
        self.wfile.write(rte_list_header[0] + '\n')
        self.wfile.write(rte_list_header[1] + '\n')
        self.wfile.write(rte_list_header[2] + '\n')
               
        while True:            
            dev.status =  mySO.AIS_ReadLog(dev.hnd,byref(logIndex),
                                               byref(logAction),
                                               byref(logReaderId),
                                               byref(logCardId),
                                               byref(logSystemId),
                                               logNfcUid,
                                               byref(logNfcUidLen),
                                               byref(logTimeStamp)
                                          )
                   
            dev.log.log_index       = logIndex.value
            dev.log.log_action      = logAction.value
            dev.log.log_reader_id   = logReaderId.value
            dev.log.log_card_id     = logCardId.value
            dev.log.log_system_id   = logSystemId.value
            dev.log.log_nfc_uid     = logNfcUid
            dev.log.log_nfc_uid_len = logNfcUidLen.value
            dev.log.log_timestamp   = logTimeStamp.value
            
            
            if dev.status != 0:
                break
            
            nfcuid = '' 
            for i in range(0,dev.log.log_nfc_uid_len):                
                nfcuid += ":%02X" % (dev.log.log_nfc_uid[i])
            
            uidNfcUidLen = '[' + str(dev.log.log_nfc_uid_len) + '] | ' + nfcuid  
          
            
            
            self.wfile.write (log_format.format(dev.log.log_index,
                                    #string_at(mySO.dbg_action2str(dev.log.log_action)).decode('utf-8'),
                                    dbg_action2str(dev.log.log_action),
                                    dev.log.log_reader_id,
                                    dev.log.log_card_id,
                                    dev.log.log_system_id,
                                    uidNfcUidLen,                                    
                                    dev.log.log_timestamp,
                                    time.ctime(dev.log.log_timestamp)
                                   )
                 )
       
            self.wfile.write('\n' + rte_list_header[0] + '\n')
        self.wfile.write(wr_status('AIS_GetLog()', dev.status))
    
    def do_GET(self):
        pass
        return
       
    def do_POST(self):
        pass
                
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            pq = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            pq = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            pq = {}
      
        try:
            dev         = DEV_HND                                 
            f           = ''.join(pq["function"])
            
            
            device     = ''.join(pq[DEVICE])
            if device == None:
                device = dev.hnd
            else:
                dev.hnd     = HND_LIST[int(device) - 1]
           


                    
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
            
            
            if f == 'q':
                self.GetListDevices()
                
            elif f == 'o':
                self.AISOpen()     #self.wfile.write("<h1>" + str(list_res([0][0])) + "</h1>")              
                   
            elif f == 'c':
                self.AISClose()
            
            if f == 'd':                             
                self.wfile.write('GET DEVICES COUNT > %s\n' % AISUpdateAndGetCount())                        
        
            elif f == 't':  
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(AISGetTime())       
            
            elif f == 'T':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(sys_get_timezone_info()+ "\n")
                self.wfile.write(AISSetTime())
            
            elif f == 'E':
                self.RTEListen()
                  
            elif f == 'l': 
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(self.log_get()) 
           
            elif f == 'n':                 
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)                
                self.log_by_index(int(start_index),int(end_index))               
            
            elif f == 'N':                           
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.log_by_time(int(start_time),int(end_time))  

            elif f == 'u':
                get_unread_log = int(get_unread_log)
                if get_unread_log == 1:
                    self.u_log_count()
                if get_unread_log == 2:
                    self.u_log_get()
                if get_unread_log == 3:
                    self.u_log_ack()
                    
           
            elif f == 'v':            
                self.wfile.write("AIS_GetDLLVersion() >> %s\n" % GetDLLVersion())
                      
            elif f == 'w':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(self.whitelist_read())
                
            elif f == 'b':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(self.blacklist_read())            

            elif f == 'W':                     
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(whitelist_write(white_list_write))                                  

            elif f == 'B':            #black_list_write                      
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(blacklist_write(black_list_write))                                 

            elif f == 'r':  
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(TestLights(f))
            
            elif f == 'g': 
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(TestLights(f))
            
            elif f == 'G': 
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(TestLights(f))
            
            elif f == 'R':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(TestLights(f))         
           
            elif f == 'P':                
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write("input pass: %s\n" % set_def_pass)
                self.wfile.write(self.set_default_password(set_def_pass)) 
                
            elif f == 'p': 
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write("input pass: %s\n" % new_pass)
                self.wfile.write(self.change_password(new_pass))                       

            elif f == 'd':
                self.wfile.write(AISGetDevicesForCheck()) 
          
            elif f == 'f':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(AISGetVersion())
            
            elif f == 'i':
                self.wfile.write("Device hnd[0x%X]\n" % dev.hnd)
                self.wfile.write(AISGetVersion())
                self.wfile.write(AISGetTime())
                self.wfile.write(sys_get_timezone_info()+ "\n")
           
           
            elif f == 'x':
                self.wfile.write("\nClose server !\nClose program !\n")            
                shut_event.set()
                httpd.server_close()
                httpd.shutdown()
                os.system('pkill -9 python')
                sys.exit()
                
        except (Exception) as error_mess:
                self.wfile.write(error_mess)
                self.wfile.write(traceback.print_exc())
        
        """
        self.send_response(200)  # OK
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        """
       
        return

           
def RunAll():
    global serv   
    serv = threading.Thread(target=handler_server)   
    serv.start()       
    while True:
        try:          
            if serv.isAlive():            
                serv.join(timeout = SERV_JOIN)                     
        except (KeyboardInterrupt,SystemExit,Exception) as e:
            httpd.server_close()
            print '\nServer close\nProgram close',e
            shut_event.set()
            os.system('pkill -9 python')
            break
            

def handler_server():
    while not shut_event.is_set():        
        my_lock.acquire()                                                         
        httpd.handle_request()
        my_lock.release()
        time.sleep(THD_SLEEP)

def init():   
    print GetDLLVersion() 
    global httpd   
    dev_list()  
    
    
    httpd = HTTPServer((HTTP_SERVER_NAME,HTTP_SERVER_PORT),GetHandler) 
    httpd.socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) 
    RunAll() 


def GetDLLVersion():
    dll_ver = mySO.AIS_GetDLLVersion
    dll_ver.restype = c_char_p
    return dll_ver()
 
 #=========================== helper functions ======================= 
def wr_status(funct_name,dl_status):
    res = funct_name + ': {%d(%s): %s}\n' % (dl_status,hex(dl_status),E_ERROR_CODES[dl_status])
    return res
        
# def dbg_action2str(action_value):    
    # res = '[%d(%s):%s]' % (action_value,hex(action_value),E_CARD_ACTION[action_value])
    # return res
   
# def dl_status2str(status):
    # res = '[%d(%s):%s]' % (status,hex(status),E_ERROR_CODES[status])
    # return res

def dbg_action2str(action_value):
    dbg_a = mySO.dbg_action2str
    dbg_a.argtype = c_int
    dbg_a.restype = c_char_p    
    return dbg_a(action_value)

def dl_status2str(status):
    dl_s = mySO.dl_status2str
    dl_s.argtype = DL_STATUS
    dl_s.restype = c_char_p    
    return dl_s(status)
    
def sys_get_timezone():
    s_tz = mySO.sys_get_timezone
    s_tz.restype = c_long
    return s_tz()

def sys_get_daylight():
    s_dl  = mySO.sys_get_daylight
    s_dl.restype = c_int
    return s_dl()    

def sys_get_dstbias():
    s_dstb = mySO.sys_get_dstbias
    s_dstb.restype = c_long
    return s_dstb()  

def sys_get_timezone_info():
    s_tzinfo = mySO.sys_get_timezone_info
    s_tzinfo.restype = c_char_p
    return s_tzinfo()

#====================================================================== 




mojFormat      = "| {0:3d} | {1:016X} | {2} | {3:7d}  | {4:2d}  | {5}  | {6:7d} | {7:10s} | {8:5d}  | {9:8d}  | {10:9d} |"    

format_grid = ["--------------------------------------------------------------------------------------------------------------------",
               "| indx|  Reader HANDLE   | SerialNm | Type h/d | ID  | FW   | speed   | FTDI: sn   | opened | DevStatus | SysStatus |",
               "--------------------------------------------------------------------------------------------------------------------"
              ]    


rte_list_header=["-----------------------------------------------------------------------------------------------------------------------------------------",
                 "| Idx   |              ACTION              | RD ID | Card ID | JobNr |    NFC [length] : UID    | Time-stamp |       Date - Time        |",
                 "----------------------------------------------------------------------------------------------------------------------------------------"
                ]


rte_format = "| {0:5d} | {1:28s} | {2:5d} | {3:7d} | {4:5d} | {5:24s} | {6:10d} | {7:s} | "

log_format = "| {0:5d} | {1:32s} | {2:5d} | {3:7d} | {4:5d} | {5:24s} | {6:#10d} | {7:s} | "




my_lock = threading.Lock()
shut_event = threading.Event()

if __name__ == '__main__': 
    global httpd 
    global mySO
    mySO = GetPlatformLib() 
    init()     
    
        
           
    
    
        
        
                    
 
