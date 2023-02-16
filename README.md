<!DOCTYPE html>
 <html lang="en-US">
<body>

<h1>StockTracker</h1>
<p>This page is the offical documentation for downloading and running the code in this code base</p>

<h2>How to Download and Run the entire code base</h2>
<ol>
	<li>Run <code>git clone <a href="https://github.com/key6oardWarrior/StockTracker">https://github.com/key6oardWarrior/StockTracker</a></code></li>
	<li><code>cd [dir that cloned StockTrader]</code></li>
	<li><code>py setup.py</code> This will install all the need python dependencies</li>
	<li>Go to the Dependencies folder and install the Mongo DB for your OS</li>
	<li>If your on linux run <code>cd [dir that you downloaded mongo db]</code></li>
	<li><code>sudo dpkg -i mongodb-org-server_6.0.4_amd64.deb</code></li>
	<li><code>sudo systemctl start mongod.service</code> This will start running Mongo DB</li>
	<li>To ensure that the service is running run: <code>sudo systemctl status mongod.service</code></li>
</ol>

<p>From here all the code can be unit tested. There currently is no system test to run an entire program</p>

 </body>
<html>
