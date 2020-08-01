# quizbowl-practice-bot
A bot to handle certain aspects of quizbowl practice, namely:

	- keeping score
	- reading bonuses
	- running slowbowl (a particular format we like to play where tossups are read one clue at a time)

This bot is very much a mess of spaghetti code because I really don't know what I'm doing, but it seems to work fairly well. If anybody wants to take this and make an actually good version, that would be awesome.

Packets are uploaded by sending them attached to the "process" command, following which they are converted into a .txt file and the bot attempts to parse them. In order for this bot to be able to parse a packet, it has to meet some fairly strict formatting requirements, primarily being:

	- It must have at least 20 tossups and 20 bonuses
	- Questions must be separated from each other by at least one empty (whitespace permitted) line
	- All answers to tossups and bonuses must begin with "ANSWER:" (in all caps)
	- No non-whitespace text is permitted between the end of a tossup and the start of its answer
	- Bonus leadins must contain "for ten points each", "for 10 points each" or "ftpe"
	- Issues may occur when tossups after 20 exist and contain all those words
	- Bonus parts must begin with "[10]"
I'm sure it would be possible to parse these packets in a better way than I am doing, but this is the system I came up with.

Additional discord server settings required:

	- In order for the bot to accept packet uploads, they must be done by someone with a role called "trusted uploader"
	- The channels used for competitive slowbowl are by default "slowbowl-1" and "slowbowl-2"

