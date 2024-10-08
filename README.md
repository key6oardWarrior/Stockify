<!DOCTYPE html>
 <html lang="en-US">
<body>

<h1>StockTracker</h1>
<p>This page is the offical documentation for downloading and running the code in this code base.</p>
<h2>Update:</h2>
<p>This project is no longer in develoment. Attempting to build this project will fail because the required API keys are not present in this repo and the MongoDB servers are no longer active. See <a href="https://github.com/key6oardWarrior/No_Server_Stockify">No_Server_Stockify</a> to run the app. This project has been made public so others may learn from it's existence.</p>

<h2>Preview:</h2>
<img src="https://github.com/user-attachments/assets/24b37a28-4057-4dbe-8f36-b20d5560bd9b" alt="Image of the app working" />


<h2>Programming Conventions</h2>
<ol>
 <li>All code must use tabs over spaces</li>
 <li>One tab is equal to four spaces</li>
 <li>All lines of code must be 80 chars or else. The only exception to this rule is for layout array that are fed to the Window constructor</li>
 <li>Use camal case</li>
</ol>

<h2>Notes about the READMEs</h2>
<p>It is very important that you read all README.md files before attempting a system test, or a unit test of certain systems here is a list of all README files:</p>

<ol>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/README.md">/main/README.md</a> (the one your reading)</li>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/Helper/README.md">/main/Helper/helper.py/README.md</a> (used for fixing bugs in imported package)</li>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/UnitTest/Login/README.md">/main/UnitTest/Login/README.md</a> (used for unit testing)</li>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/UnitTest/Helper/README.md">/main/UnitTest/Helper/README.md</a> (used for unit testing)</li>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/Robinhood_API/README.md">/main/Robinhoon_API/README.md</a> (used for find robin_stocks docs)</li>
 <li><a href="https://github.com/key6oardWarrior/StockTracker/blob/main/UnitTest/Database/README.md">/main/UnitTest/Database/README.md</a> (used for fixing SSL cert error and set <code>connectionString</code>)</li>
</ol>

<h2>Setup Authorize.Net</h2>
<ol>
 <li>Create an Authrize.Net accout at: <a href="https://developer.authorize.net/hello_world/sandbox.html">developer.authorize.net</a></li>
 <li>Save the API key and the transaction key</li>
 <li>Login to your account</li>
 <li>Go to account settings</li>
 <li>Under Security Settings > General Security Settings > click Test Mode</li>
 <li>Set account to Test</li>
</ol>

<h2>How to Download and Setup</h2>
<ol>
	<li>Download <a href="https://www.python.org/downloads/release/python-3111/">Python v3.11.1</a></li>
	<li>Run <code>git clone <a href="https://github.com/key6oardWarrior/StockTracker">https://github.com/key6oardWarrior/StockTracker</a></code></li>
	<li><code>cd [dir that cloned StockTrader]</code></li>
	<li><code>python setup.py</code> This will install all the need python dependencies. If you have any more issue read the other README.md files</li>
</ol>

<p><b>***NOTE***:</b> MongoDB <b>MUST</b> be installed to do System test and any test that will use server side code</p>

<ol>
	<h3>MongoDB Windows Install</h3>
	<li>Download <a href="https://downloads.mongodb.com/compass/mongodb-compass-1.36.1-win32-x64.exe" target="blank">here</a></li>
</ol>

<ol>
	<h3>MongoDB Linux Install</h3>
	<li>Run <code>sudo dpkg -i mongodb-org-server_6.0.4_amd64.deb</code></li>
</ol>

<ol>
	<h3>Install macOS Install</h3>
	<li><a href="https://www.mongodb.com/try/download/compass" target="blank">Download link</a>. Ensure that you are downloading Mongo DB Compas</li>
	<li>Determin if your macOS is running on either ARM or Intel processor</li>
	<li>Click on the downloaded .tgz file, that is for your processor, in the StockTrader folder and follow the install instructions</li>
</ol>

<h2>Run MongoDB</h2>
<p><b>***NOTE***:</b> MongoDB <b>MUST</b> be run to do System test and any test that will use server side code</p>

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

<h2>Compile All Code</h2>
<p>Run: <code>py compile.py</code></p>
<p>When preforming any kind of test be sure to test both the .py and .pyc files. They both must pass before you can submit a PR. Please note that while running compile.py you may encounter an error that states, "Can't list [directory]." Please ignore this error message.</p>

<h1>Running the App</h1>
<p>After completing all the steps in this README and the other READMEs you can run this code. Go into the app directory and in the subdirectory UI click on Stockify.pyw. This will run the entire application for the user's perspective.</p>

 </body>
<html>
