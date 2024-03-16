<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Lana AntiRaid" /> 

  &#xa0;
</div>

<h1 align="center">Lana Anti-Raid</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/Serbirial/lana-py?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/Serbirial/lana-py?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/Serbirial/lana-py?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/Serbirial/lana-py?color=56BEB8">

  <img alt="Github issues" src="https://img.shields.io/github/issues/Serbirial/lana-py?color=56BEB8" />

  <img alt="Github forks" src="https://img.shields.io/github/forks/Serbirial/lana-py?color=56BEB8" />

  <img alt="Github stars" src="https://img.shields.io/github/stars/Serbirial/lana-py?color=56BEB8" />
</p>

<h4 align="center"> 
	🚧 Under construction...  🚧
</h4> 

<hr>

<p align="center">
  <a href="#about">About</a> &#xa0; | &#xa0; 
  <a href="#features">Features</a> &#xa0; | &#xa0;
  <a href="#stack">Stack</a> &#xa0; | &#xa0;
  <a href="#requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#starting">Starting</a> &#xa0; | &#xa0;
  <a href="#license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/Serbirial" target="_blank">Author</a>
</p>

<br>

## About ##

Lana is a new and innovative discord security bot, taking on the challenge of never failing or lagging behind during raids or spam, no matter how large.<br/>

## Features ##

:heavy_check_mark: 90% Open source;\
:heavy_check_mark: Made in Python;\
:heavy_check_mark: Made with security and optimization as a priority;\
:heavy_check_mark: Under active development;

## Stack ##

The following tools were used in this project:

- [Python 3.11+](https://python.org)
- [Sanic 23.3](https://sanic.dev)
- [Redis 6.0.16+](https://github.com/redis/redis)
- [MariaDB 10.11.3](https://downloads.mariadb.org/mariadb/10.11.3/)
- [Discommand dev branch](https://github.com/Serbirial/DisCommand)
- [Discord.py Latest](https://github.com/Rapptz/discord.py)
- [PM2 Latest](https://pm2.keymetrics.io)
  
##  Requirements ##

Before starting, you need to have [Git](https://git-scm.com) and [Python](https://python.org/) installed, along with [Node](https://nodejs.org/en) and [PM2](https://pm2.keymetrics.io).

## Starting ##

```bash
# Clone this project
$ git clone https://github.com/Serbirial/lana-py

# Access
$ cd lana-py

# Clone my discord.py wrapper and rename it for the bot to use (CANT SKIP) 
$ git clone -b dev https://github.com/Serbirial/DisCommand && mv discommand dis_command

# Install dependencies
$ pip install -r requirements.txt

# Run the project
$ pm2 start

# Make sure to configure the bot, including Redis and mariaDB!
```


Make sure you setup the database (MariaDB) with the schema files in the [Schema](https://github.com/Serbirial/lana-py/blob/main/config/schema.sql) file.

If you need any help, or have questions, or just want to join and chat, feel free to join Lana's community discord https://discord.gg/Ae8sH5qYVX

## License ##

This project is under the (license in progress). For more details, see the [LICENSE](LICENSE.md) file.

## :memo: ##

README made by <a href="https://github.com/babymu5k" target="_blank">Babymusk</a> and edited by <a href="https://github.com/Serbirial" target="_blank">Me</a>.

&#xa0;

## Disclaimer!! ##
The main branch of Lana AR will be considered a rolling release until an official release is put in the releases section.
After the first stable release; the main branch will go back to being a mostly-stable release of the bot, and a dev branch will be made in its place.
We say Lana is 90% open source because we keep certain features entirely private code-wise to prevent both code theft and attackers from knowing very intricately how the bot's internals works.
This includes: 
	Any/All Auto-Mod/Events: antispam, welcoming, logging, anything of the sorts. (Will slowly trickle viable features in)
	The antilock code to entirely prevent raids/spam from disrupting/DDoSing the bot (relatively simple should you want to implement it yourself and are intermediate at python, just go from what you see left in the bot)
	Any/All code that enables or adds payment processing/monitization to the bot.
I will provide limited support with how to implement some of these features yourself.

<a href="#top">Back to top</a>
