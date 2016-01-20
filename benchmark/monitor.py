
import re

RE_RATE = re.compile(r".*out: [0-9\.\+e]+ msg \(([0-9\.\+e]+).*")


class TestMonitor:

	def __init__(self, test_case):
		"""
		Test monitor monitors the applications output according
		to test specifications and extracts the metrics.
		"""
		
		# Keep local properties
		self.testCase = test_case

		# Extract some info from config
		self.maxSamples = 0
		if 'max-samples' in test_case.config:
			self.maxSamples = int(test_case.config['max-samples'])

		# Counters
		self.v_min = 0
		self.v_max = 0
		self.v_samples = 0
		self.v_sum = 0
		self.m_samples = []

		# Flags
		self.exitFlag = False

	def start(self):
		"""
		Reset counters and prepare for capture
		"""
		self.v_min = 0
		self.v_max = 0
		self.v_samples = 0
		self.v_sum = 0
		self.m_samples = []
		self.exitFlag = False

	def process(self, line):
		"""
		Process a line from stdin
		"""
		print line

		# Handle
		if 'data-out[0]:' in line:
			m = RE_RATE.match( line )
			if m:
				mbps = float(m.group(1))
				print ">> Found %f MB/s" % mbps

				# Summarize anda verage
				if self.v_samples == 0:
					self.v_min = mbps
					self.v_max = mbps
				else:
					if mbps < self.v_min:
						self.v_min = mbps
					if mbps > self.v_max:
						self.v_max = mbps

				# Collect for average and statistics
				self.v_samples += 1
				self.v_sum += mbps
				self.m_samples.append( mbps )

				# If we have more than maximum samples, we are good
				if (self.maxSamples > 0) and (self.v_samples >= self.maxSamples):
					self.exitFlag = True

		elif 'RUNNING state finished' in line:
			self.exitFlag = True

	def close(self):
		"""
		Finalize reading
		"""
		if self.v_samples == 0:
			self.v_average = 0
		else:
			self.v_average = self.v_sum / self.v_samples


	def metrics(self):
		"""
		Return monitor metrics
		"""
		return {
			'min': self.v_min,
			'max': self.v_max,
			'average': self.v_average
		}

