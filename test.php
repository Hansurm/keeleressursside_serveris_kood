
<?php
setlocale(LC_ALL, 'et_EE.UTF-8');
$locale ='et_EE.UTF-8';
putenv('LC_ALL='.$locale);

function getResult($sona) {
    $paring = "PYTHONIOENCODING=utf-8:surrogateescape /usr/bin/python3 /home/veebid/psvchromeextension/estnltk14ver.py $sona";

    $python = utf8_encode(shell_exec($paring));
    return $python;
}
$vastus = "";
$s = "";
if ($_GET['word'] != '') {
    $s = trim(htmlspecialchars($_GET['word']));
    $vastus = getResult($s);
    //$vastus = stripslashes($vastus);
}
echo utf8_decode($vastus);
?>
