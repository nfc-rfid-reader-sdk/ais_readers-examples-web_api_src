<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>eventi</title>
</head>
<body>
<h3>unos u bazu</h3>

<?php
  $LogIndex        = $_POST['log_index'];
  $LogAction      = $_POST['log_action'];
  $LogReaderId = $_POST['log_reader_id'];
  $LogCardId      = $_POST['log_card_id'];
  $LogSystemId = $_POST['log_system_id'];
  $NfcUID	            = $_POST['nfc_uid'];
  $NfcUIDLen     = $_POST['nfc_uid_len'];
  $Timestamp     = $_POST['timestamp'];
  $M_Time           = $_POST['m_time'];
  
  
  if (!get_magic_quotes_gpc())
  {
  	$LogIndex        = addslashes($LogIndex);
  	$LogAction      = addslashes($LogAction);
  	$LogReaderId = addslashes($LogReaderId);
  	$LogCardId      = addslashes($LogCardId);
  	$LogSystemId = addslashes($LogSystemId);
  	$NfcUID	         = addslashes($NfcUID);
  	$NfcUIDLen    = addslashes($NfcUIDLen);
  	$Timestamp     = addslashes($Timestamp);
  	$M_Time           = addslashes($M_Time);
  }
  $server_name   = 'localhost';
  $user_name      = 'root';
  $server_pass	 = '';
  $db_name		     = 'AISReaders'; #ais_readers_db
  $table_name    = 'rte';
  
  $conn = new mysqli($server_name,$user_name,$server_pass,$db_name);
 
  if ($conn->connect_error)
  {
  	die('Ne mogu se konektovati na bazu podataka!');
  	Exit;
  }
  
  $insert_query = "INSERT INTO $table_name(log_index,log_action,log_reader_id,
  										   log_card_id,log_system_id,nfc_uid,nfc_uid_len,
  										   timestamp,m_time)VALUES
  				   (
  				    '".$LogIndex."',
  				    '".$LogAction."',
  				    '".$LogReaderId."',
  				    '".$LogCardId."',
  				    '".$LogSystemId."',
  				    '".$NfcUID."',
  				    '".$NfcUIDLen."',
  				    '".$Timestamp."',
  				    '".$M_Time."'
  				   )";
  				  
  $result = $conn->query($insert_query);
  if (!$result)
  
  	die($conn->error);
  	//Exit;  
 
?>
</body>
</head>
</html>