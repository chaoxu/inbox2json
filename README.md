# inbox2sql
The logins to an inbox through imap,
output the mail into a sqlite database.
Move the mail that was read to a new folder.

## create the database

First create a database use the `dump.sql` file.

Create the config yaml file

```yaml
host: 'imap.fastmail.com'
port: 993
username: 'username' 
password: 'password'
inbox: 'Inbox' # name of the inbox folder
archive: 'Archive' # name of the Archive folder
move_to_archive: False # this determines the files gets archived
db: 'mail.db' # location of the db file
limit: 100 # the number of mails to process in each run
``` 