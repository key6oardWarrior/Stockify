<!DOCTYPE html>
 <html lang="en-US">
  <body>

<h1>Requirements for Unit Testing</h1>

<ol>
 <li>Create a creds.py file in the Helper directory because creds.py has been placed in the git ignore. In the creds.py file type: <br /> <code>apiLoginId: str = "[API Key Here]"<br />transactionKey: str = "[Transaction Key Here]"</code></li>

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

 </body>
</html>