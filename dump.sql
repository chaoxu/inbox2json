PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "mail" (
	"id"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	"source"	TEXT NOT NULL DEFAULT "",
	"receiver"	TEXT NOT NULL DEFAULT "",
	"subject"	TEXT NOT NULL DEFAULT "",
	"body"	TEXT NOT NULL DEFAULT "",
	"status"	TEXT NOT NULL DEFAULT "",
	"last_update"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
COMMIT;
