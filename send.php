<?php
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: kontakt.html');
    exit;
}

$thema    = trim($_POST['thema']    ?? '');
$name     = trim($_POST['name']     ?? '');
$email    = trim($_POST['email']    ?? '');
$telefon  = trim($_POST['telefon']  ?? '');
$nachricht = trim($_POST['nachricht'] ?? '');

if (!$thema || !$name || !$email || !$nachricht || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: kontakt.html?status=fehler');
    exit;
}

$to      = 'martin.buenger@t-online.de';
$subject = 'Neue Anfrage: ' . $thema;

$body  = "Thema: $thema\n";
$body .= "Name: $name\n";
$body .= "E-Mail: $email\n";
if ($telefon) $body .= "Telefon: $telefon\n";
$body .= "\nNachricht:\n$nachricht\n";

$headers  = "From: no-reply@martin-buenger-architekt.de\r\n";
$headers .= "Reply-To: $email\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

if (mail($to, $subject, $body, $headers)) {
    header('Location: danke.html');
} else {
    header('Location: kontakt.html?status=fehler');
}
exit;
