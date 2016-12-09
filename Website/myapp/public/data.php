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
$query = sprintf("SELECT username FROM AUTH;");

//execute query
$result = $conn->query($query);

//loop through the returned data
$data = array();
$uname_count = array();

while( $row = mysqli_fetch_array($result, MYSQLI_ASSOC)){
    $data[] = $row; // Inside while loop
}

foreach($data as $name){
    printf ("%s\n",$name["username"]);
    if (in_array($name.username, $uname_count, TRUE)){
        //$uname_count[$name.username] ++;
        printf ("TRUE\n");
    }
    elseif(!in_array($name.username, $uname_count, TRUE)){
    printf ("FALSE\n");
    $uname_count[] = $name;
    printf ("added %s to list\n", $uname_count["username"]);
    }
}


//free memory associated with result
mysqli_free_result($result);

//close connection
$conn->close();

//now print the data
print json_encode($data);

?>