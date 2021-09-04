from inbox2sql import Mailbox, sql_insert, json_output
import sqlite3
import yaml
import sys
import argparse
from functools import partial

parser = argparse.ArgumentParser(description='Process some mail.')
parser.add_argument(dest='config_file', default='config.yml',
                    metavar='f', type=str,
                    help='path to the config file')
parser.add_argument('--dryrun', dest='dry_run', action='store_const',
                    const=True, default=False,
                    help='Is this a dry run? (does not change database, output json)')
args = parser.parse_args()
config_file = args.config_file
dry_run = args.dry_run
# load config
with open(config_file, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

db_file = config.get('db', 'mail.db')
limit = config.get('limit', 100000)

# dry run does not move mail around
if dry_run:
  config['archive'] = config['inbox']

m = Mailbox(host=config['host'],
        port=config['port'],
        username=config['username'],
        password=config['password'],
        inbox=config['inbox'],
        archive=config['archive'],
        move_to_archive=config['move_to_archive'])
print("Mailbox Setup")

if dry_run:
  # output json
  m.set_mail_processor(json_output)
else:
  print("Connect to Database")
  con = sqlite3.connect(db_file)
  m.set_mail_processor(partial(sql_insert, con))

print("Running")
m.run(limit)

if not dry_run:
  print("Close Database")
  con.close()