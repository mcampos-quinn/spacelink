from datetime import datetime
import logging
from pathlib import Path
from zoneinfo import ZoneInfo

# this should be set in config
my_timezone = ZoneInfo("America/Los_Angeles")
today = datetime.now(tz=my_timezone).strftime("%Y-%m-%d")

class LinkLog():
	"""class to make a logging utility"""
	def __init__(self):
		self.today = today
		self.log_path = Path(".","log",f"link-log_{today}.log")
		self.logger = None

		self.check_log_exists(self.today)

	def check_log_exists(self,today):
		if self.log_path.is_file():
			self.config_log()
			return True
		else:
			self.make_log(self.today)

	def config_log(self):
		logging.basicConfig(
			filename=self.log_path,
			format='%(asctime)s | %(levelname)s: %(message)s',
			datefmt='%Y-%m-%d %I:%M:%S %p',
			filemode="a",
			level=logging.WARNING)
		self.logger = logging.getLogger("link_log")

	def make_log(self,today):
		self.config_log()
		logging.info(f"\n*** ***\n\nLOGGING THE SPACELINK FOR {today}\n\n*** ***")
