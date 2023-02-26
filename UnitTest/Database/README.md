<!DOCTYPE html>
 <html>
  <body>

<h1>Fix "SSL: CERTIFICATE_VERIFY_FAILED" Error</h1>
<p>Only do this if you run into this error</p>
<ol>
 <li>Download <a href="https://letsencrypt.org/certs/lets-encrypt-r3.der">this</a>. It is the cert that Python needs to connect to MongoDB</li>
 <li>Follow instructions to install</li>
</ol>

<h1>Add varable to creds.py</h1>
<ol>
 <li>Add a line to (or create the file if it does not exist) /Helper/creds.py</li>
 <li>Type <code>connectionString = "mongodb://localhost:27017/"</code></li>
 <li>If you need to do sandbox test on an actual database get <code>connectionString</code> from key6oardWarrior</li>
</ol>

 </body>
</html>