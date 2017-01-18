<?php
//setting header to json
header('Content-Type: application/json');

$servername = "localhost";
$username = "sirenlocal";
$password = "sirenproj";
$db_name = "siren_db";
// Create connection
$conn = new mysqli($servername, $username, $password, $db_name);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}


//query to get data from the table
$queryuse = sprintf("SELECT username FROM AUTH;");
$data = array();
if ($result=mysqli_query($conn,$queryuse))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $data[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$querypass = sprintf("SELECT passwd FROM AUTH;");
$datapass = array();
if ($result=mysqli_query($conn,$querypass))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $datapass[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$querysucc = sprintf("SELECT success FROM AUTH;");
$datasucc = array();
if ($result=mysqli_query($conn,$querysucc))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $datasucc[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$queryip = sprintf("SELECT ip FROM SESSION;");
$dataip = array();
if ($result=mysqli_query($conn,$queryip))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $dataip[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$querycmd = sprintf("SELECT input FROM INPUT;");
$datacmd = array();
if ($result=mysqli_query($conn,$querycmd))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $datacmd[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$querylogstart = sprintf("SELECT  starttime FROM SESSION;");
$datalogstart = array();
if ($result=mysqli_query($conn,$querylogstart))
  {
  while($row=mysqli_fetch_row($result)){
	$datalogstart[] = $row[0];
  }
  mysqli_free_result($result);
}

//$querypass = sprintf("SELECT passwd FROM AUTH;");

//$resultpass = $conn->query($querypass);

$usernames = json_encode($data);
$passwords = json_encode($datapass);
$successes = json_encode($datasucc);
$ips =  json_encode($dataip);
$cmds = json_encode($datacmd);
$starttime = json_encode($datalogstart);

$dataout = array();
$dataout[0] = $usernames;
$dataout[1] = $passwords;
$dataout[2] = $successes;
$dataout[3] = $ips;
$dataout[4] = $cmds;
$dataout[5] = $starttime;

echo json_encode($dataout);

//free memory associated with result

//close connection
$conn->close();

//now print the data
?>
