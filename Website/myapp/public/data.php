<?php
header('Content-Type: application/json');

define('DB_HOST', 'localhost');
define('DB_USERNAME', 'sirenlocal');
define('DB_PASSWORD', 'sirenproj');
define('DB_NAME', 'siren_db');


$mysqli = new mysqli(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);

if ($mysqli) {
    die("Connection failed: " . $mysqli->connect_error);
}
echo "Connected successfully";

$query = sprintf("select * from AUTH");

$result = $mysqli->query($query);

$data = array();
foreach ($result as $row){
    $data[] = $row;
}

$result->close();

print json_encode($data);



?>