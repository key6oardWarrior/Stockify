<!DOCTYPE html>
 <html lang="en-US">
<body>

<h1>StockTracker</h1>
<p>This page is the offical documentation for downloading and running the code in this code base</p>

<h2>How to Download and Setup the entire code base</h2>
<ol>
	<li>Run <code>git clone <a href="https://github.com/key6oardWarrior/StockTracker">https://github.com/key6oardWarrior/StockTracker</a></code></li>
	<li><code>cd [dir that cloned StockTrader]</code></li>
	<li><code>python setup.py</code> This will install all the need python dependencies</li>
</ol>

<ol>
	<h3>MongoDB Windows Install</h3>
	<li>Click on the downloaded .msi file in the StockTrader folder and follow the install instructions</li>
</ol>

<ol>
	<h3>MongoDB Linux Install</h3>
	<li>Run <code>sudo dpkg -i mongodb-org-server_6.0.4_amd64.deb</code></li>
</ol>

<ol>
	<h3>Install macOS Install</h3>
	<li>Determin if your macOS is running on either ARM or Intel processor</li>
	<li>Click on the downloaded .tgz file, that is for your processor, in the StockTrader folder and follow the install instructions</li>
</ol>

<h2>Run MongoDB</h2>
<ol>
	<h3>Windows</h3>
	<li>Click on the MongoDBCompass app</li>
	<li>Click the big green "Connect" button. The server should start running</li>
</ol>

<ol>
	<h3>Linux</h3>
	<li>Run <code>sudo systemctl start mongod.service</code> This will start running Mongo DB</li>
	<li>To ensure that the service is running run: <code>sudo systemctl status mongod.service</code></li>
</ol>

<ol>
	<h3>macOS</h3>
	<li>Click on the MongoDBCompass app</li>
	<li>Click the big green "Connect" button. The server should start running</li>
</ol>

<h2>System Testing</h2>
<p>From here all the code can be unit tested. There currently is no system test to run an entire program</p>

 </body>
<html>
