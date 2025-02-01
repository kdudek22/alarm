import threading, logging
import pygame, time, flask, json
from datetime import datetime


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AlarmPlayer:
    instance = None

    def __init__(self):
        self.is_playing: bool = False
        self.should_play: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)

        return cls.instance

    def play(self):
        print(self)
        if self.is_playing:
            logger.log("Tried to play, but is already playing")
            return

        self.should_play = True
        threading.Thread(target=self._play).start()

    def _play(self, file_name="alarm.mp3"):
        self.is_playing = True
        logger.debug(f"Alarm player started, playing {file_name}")
        pygame.mixer.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play(-1)

        while self.should_play:
            time.sleep(1)

        logger.debug("Alarm player stopped")
        self.is_playing = False

    def stop(self):
        self.is_playing = False

app = flask.Flask(__name__)

PLAY_SOUND = False

def check_for_events():
    global PLAY_SOUND
    player = AlarmPlayer()

    logger.debug("Started event checking")

    with open("events.json") as f:
        events = json.load(f)

    for event in events:
        event_time = datetime.strptime(event, "%Y-%m-%d %H:%M:%S")
        while datetime.now() < event_time:
            logger.debug("Checking for event, next check in 10 seconds")
            time.sleep(10)

        logger.debug(f"Starting player, event: {event}")
        PLAY_SOUND = True
        player.play()

        while PLAY_SOUND:
            time.sleep(1)

        player.stop()


@app.route("/stop", methods=["GET"])
def stop():
    global PLAY_SOUND
    PLAY_SOUND = False
    return "Success", 200


if __name__ == "__main__":
    threading.Thread(target=check_for_events).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
