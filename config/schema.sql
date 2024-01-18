CREATE TABLE IF NOT EXISTS owners (
  id bigint unsigned NOT NULL,
  level smallint unsigned NOT NULL,

  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS guilds (
  id bigint unsigned NOT NULL,
  -- TODO: add basic guild stats such as bot join timestamp and last active command run

  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS antispam ( -- 0 False, 1 True
  guild bigint unsigned NOT NULL,
  strict boolean NOT NULL DEFAULT 0,
  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS antinuke (
  guild bigint unsigned NOT NULL,
  action_limit tinyint unsigned NOT NULL DEFAULT 10,
  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS panic (
  guild bigint unsigned NOT NULL,
  message_limit bigint unsigned NOT NULL DEFAULT 200,
  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prefixes (
  guild bigint unsigned NOT NULL,
  prefix varchar(255) NOT NULL,

  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS logging (
  guild bigint unsigned NOT NULL,
  webhook_url varchar(255) DEFAULT NULL,

  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS welcome (
  guild bigint unsigned NOT NULL,
  channel bigint unsigned, -- should default to the channel the command was first ran in.
  message varchar(255) NOT NULL DEFAULT "Welcome {{user}}!",
  embed boolean NOT NULL DEFAULT 0,

  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS antialt (
  guild bigint unsigned NOT NULL,
  age_threshold int unsigned NOT NULL DEFAULT 7,

  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS autorole (
  guild bigint unsigned NOT NULL,
  role_id bigint unsigned NOT NULL,

  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reactionrole (
  guild bigint unsigned NOT NULL,
  message_id bigint unsigned NOT NULL,
  emoji_id bigint unsigned NOT NULL,

  role_id bigint unsigned NOT NULL,
  enabled boolean NOT NULL DEFAULT 0,

  PRIMARY KEY (guild, message_id, emoji_id),
  FOREIGN KEY (guild) REFERENCES guilds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS premium (
  user_id bigint unsigned NOT NULL,
  expires_timestamp bigint NOT NULL,
  level tinyint unsigned NOT NULL,

  PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS premium_points (
  user_id bigint unsigned NOT NULL,
  points bigint unsigned NOT NULL DEFAULT 0,

  PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS oauth_identification (
  user_id bigint unsigned NOT NULL,
  access_token varchar(255) NOT NULL,

  PRIMARY KEY (access_token)
);

CREATE TABLE IF NOT EXISTS oauth_refresh (
  user_id bigint unsigned NOT NULL,
  refresh_token varchar(255) NOT NULL,

  PRIMARY KEY (user_id)
);