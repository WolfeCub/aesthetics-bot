run:
	python3 bot.py

install: hearthstone
	sudo pip3 install -r requirements.txt

hearthstone:
	curl -OL "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
