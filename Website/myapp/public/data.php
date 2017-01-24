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

$querycmdid = sprintf("SELECT session_id FROM INPUT;");
$datacmdid = array();
if ($result=mysqli_query($conn,$querycmdid))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $datacmdid[] = $row[0];
    }
  // Free result set
    mysqli_free_result($result);
}

$querycmdtimes = sprintf("SELECT timestmp FROM INPUT;");
$datacmdtimes = array();
if ($result=mysqli_query($conn,$querycmdtimes))
    {
  // Fetch one and one row
    while ($row=mysqli_fetch_row($result)){
        $datacmdtimes[] = $row[0];
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

$querysessionid = sprintf("SELECT session_id FROM SESSION;");
$datasessionid = array();
if ($result=mysqli_query($conn,$querysessionid))
  {
  while($row=mysqli_fetch_row($result)){
	$datasessionid[] = $row[0];
  }
  mysqli_free_result($result);
}

$querylogend = sprintf("SELECT endtime FROM SESSION;");
$datalogend = array();
if ($result=mysqli_query($conn,$querylogend))
  {
  while($row=mysqli_fetch_row($result)){
	$datalogend[] = $row[0];
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
$cmdids = json_encode($datacmdid);
$cmdtimes = json_encode($datacmdtimes);
$sessionids = json_encode($datasessionid);
$starttime = json_encode($datalogstart);
$endtime = json_encode($datalogend);

$dataout = array();
$dataout[0] = $usernames;
$dataout[1] = $passwords;
$dataout[2] = $successes;
$dataout[3] = $ips;
$dataout[4] = $cmds;
$dataout[5] = $starttime;
$dataout[6] = $cmdids;
$dataout[7] = $cmdtimes;
$dataout[8] = $sessionids;
$dataout[9] = $endtime;

echo json_encode($dataout);

//free memory associated with result

//close connection
$conn->close();

?>
