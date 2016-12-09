<?php
//setting header to json
header('Content-Type: application/json');

$servername = "localhost";
$username = "sirenlocal";
$password = "sirenproj";
$db_name = "siren_db";
print("helloworld");
// Create connection
$conn = new mysqli($servername, $username, $password, $db_name);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}


//query to get data from the table
$query = sprintf("SELECT username FROM AUTH");

//execute query
$result = $conn->query($query);

//loop through the returned data
$data = array();

while( $row = mysqli_fetch_array($result)){
    $data[] = $row; // Inside while loop

}

//free memory associated with result
mysqli_free_result($result);

//close connection
$conn->close();

//now print the data
print json_encode($data);

?>