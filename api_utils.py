import concurrent.futures
import queue
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

class APIHandler:
	"""
	handler for a single API endpoint
	"""
	def __init__(self,endpoint):
		self.endpoint = endpoint
		self.url_queue = queue.Queue()
		self.session = requests.Session()
		self.retry = Retry(other=0,backoff_factor=1)
		self.adapter = HTTPAdapter(max_retries=self.retry)
		self.session.mount('http://', self.adapter)
		self.session.mount('https://', self.adapter)
		self.futures = {}

	def feed_me(self,chunk_id,url,auth,data,header):
		self.url_queue.put([url,auth,data,chunk_id,header])

	def clean_me(self):
		self.futures = {}

	def run_me(self):
		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
			# process_futures = {0:executor.submit(self.dummy_future())}
			process_futures = {}
			while not self.url_queue.empty():
				[url,auth,data,chunk_id,header] = self.url_queue.get()
				# print("HELLO FROM THE API RUNNER")
				# print((chunk_id,[url,auth,data]))
				process_futures[executor.submit(self.worker, url, auth=auth, data=data, header=header)] = (url,chunk_id)
				self.url_queue.task_done()
			for future in concurrent.futures.as_completed(process_futures):
				url = process_futures[future][0]
				chunk_id = process_futures[future][1]
				self.futures[future] = chunk_id
				# print(future.result().content[:50])
		print(self.futures)
		return self.futures

	def worker(self,url,auth=None,data=None,header=None):
		while True:
			try:
				r = self.session.get(url,auth=auth,data=data,headers=header)
				r.raise_for_status()
				break
			except Exception as e:
				print(e)
				time.sleep(.1)
		# print(r.content)

		return(r)
