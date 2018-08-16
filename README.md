# account_api
API for Account System

This is still a work in progress but will eventually be used by the new account UI to create and manage your Underlight account.

In the root of the project you'll need to create a pw.txt file that contains the connection information for the running MySQL database containing the necessary UL databases. The format is as follows:

<pre>
DBHOST 10.20.18.1
DBPORT 3306
DBADMIN support@underlight.local
DBRETURNEMAIL support@underlight.local
DBKEY H16 90293311ALKWEVB
DBSALT 3A
ul_item root rooty
ul_player root rooty
ul_guild root rooty
ul_level root rooty
ul_server root rooty
ul_billing root rooty
</pre>
