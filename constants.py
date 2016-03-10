

from dl_status import E_ERROR_CODES
import ctypes

LIB_PATH     = '/shell/lib/testing/ver.4.8.0/'



WIN_PATH     = 'windows/x86/'
LINUX_PATH   = 'linux/x86/'
ARMHF_PATH   = 'linux/arm-hf/'

LIB_WIN32    = 'ais_readers-x86.dll'
LIB_LINUX    = 'libais_readers-x86_64.so'
LIB_ARM      = 'libais_readers-arm.so'
LIB_ARMHF    = 'libais_readers-armhf.so'

THD_SLEEP = .7
RTE_JOIN  = 1.0 #timeout 3.0
SERV_JOIN = 3.0 #timeout
#timers

UNREAD_LOG_TIMER = 100



#pass
PASS      = '1111'

#unread_log
RECORDS_TO_ACK      = 1

URL_ERROR_MESSAGE   = "INPUT ERROR IN URL QUERY STRING !"
NFC_UID_MAX_LEN = 10
SECONDS         = 10
DL_STATUS       = E_ERROR_CODES
 
#url_query_string
DEVICE           = 'device'
START_INDEX      = 'start_index'
END_INDEX        = 'end_index'
START_TIME       = 'start_time'
END_TIME         = 'end_time'
BLACK_LIST_WRITE = 'black_list_write'
WHITE_LIST_WRITE = 'white_list_write'
DEFAULT_APP_PASS = 'default_app_pass'
NEW_PASS         = 'new_pass'
UNREAD_LOG       = 'unread_log'
UNR_COUNT        = '1'
UNR_GET          = '2'
UNR_ACK          = '3'
RTE              = 'rte'
STOP_SERVER      = 'stop_server'
FUNCTION         = 'get_function'

#php 
EVENTS          = 'events.php'
GET_AISRBBB     = '/aisreadersbbb/aisreaderbbb.php'


#apache mysql
HTTP            = 'http://'
SERVER_NAME     = 'localhost'
USER_NAME       = 'root'
RTE_EVENTS      = '/aisreadersbbb//events.php' #mora ovako

#local mysql
SERVER_NAME      = 'localhost'
SERVER_USER_NAME = 'root'
SERVER_PASSWORD  = 'vladan' #dlogic654
DATABASE_NAME    = 'ais_readers_db' #AISReaders
TABLE_NAME       = 'rte'

LOG_INDEX        = 'log_index'
LOG_ACTION       = 'log_action'
LOG_READER_ID    = 'log_reader_id'
LOG_CARD_ID      = 'log_card_id'
LOG_SISTEM_ID    = 'log_system_id'
NFC_UID          = 'nfc_uid'
NFC_UID_LEN      = 'nfc_uid_len'
TIMESTAMP        = 'timestamp'
M_TIME           = 'm_time'

#http
HTTP_SERVER_NAME = ''
HTTP_SERVER_PORT = 8080 #8080