<!DOCTYPE html>
 <html lang="en-US">
  <body>

<h1>Requirements for Running</h1>

<ol>
 <li>Create a creds.py file in the Helper directory because creds.py has been placed in the git ignore. In the creds.py file type: <br /> <code>apiLoginId: str = "[API Key Here]"</code><br /><code>transactionKey: str = "[Transaction Key Here]"</code><br />Don't include the brackets</li>

 <li>There is an imported Python package that has an error in one of the files. To fix this:
  <ol>
   <li>Put a break point on line 11 of Helper/helper.py.</li>
   <li>Create a launch.json for python</li>
   <li>Change line 13 from: <code>"justMyCode": true,</code> to: <code>"justMyCode": false,</code>
   <li>Then run Helper/helper.py in debug mode</li>
   <li>Once the break point is hit click continue</li>
   <li>Once the error message comes up change line 807 in content.py from: <code>class _PluralBinding (collections.MutableSequence):</code> to: <code>class _PluralBinding (collections.abc.MutableSequence):</code></li>
  </ol>
 </li>
</ol>

<h1>Fix Error From Authorize.Net's Package's Deprecated Dependencies</h1>

<ol>
 <li>Navigate to: Python\Python311\Lib\site-packages in your computer's directory</li>
 <li>Make a copy of the lxml directory</li>
 <li>Make a src directoy</li>
 <li>Place coped lxml directory in the src directory</li>
</ol>

<h1>Authorize.Net Docs</h1>
<ol>
 <li><a href="https://developer.authorize.net/api/reference/features/errorandresponsecodes.html">Responce Codes</a></li>
 <li><a href="https://developer.authorize.net/hello_world/testing_guide.html">Hello World</a></li>
 <li><a href="https://developer.authorize.net/api/reference/index.html">Code Docs</a></li>

 </body>
</html>
