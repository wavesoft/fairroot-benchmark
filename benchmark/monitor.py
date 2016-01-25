
import re

RE_RATE = re.compile(r".*out: [0-9\.\+e]+ msg \(([0-9\.\+e]+).*")
RE_STATS = re.compile (r"\s+")
RE_PID_SPLIT = re.compile (r".*PS_INFO:\s+root (\d+).*")


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

		# PID stats counters

		self.uss_min=0
		self.uss_max=0
		self.uss_avg=0
		self.mem_samples=0

		self.pss_min=0
		self.pss_max=0
		self.pss_avg=0

		self.rss_min=0
		self.rss_max=0
		self.rss_avg=0

		self.uss_sum=0
		self.pss_sum=0
		self.rss_sum=0

		self.prev_ntwrk_rx=0
		self.prev_ntwrk_tx=0
		self.network_stats_tx=0
		self.network_stats_rx=0
		self.cur_ntwrk_tx=0
		self.cur_ntwrk_rx=0
		self.total_rx=0
		self.total_tx=0

		self.cpu_avg=0
		self.cpu_samples=0
		self.cpu_sum=0
		self.cpu_percent=0

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
		self.mem_sum = 0
		self.m_samples = []
		self.exitFlag = False
		
		self.uss_min=0
		self.uss_max=0
		self.uss_avg=0
		self.mem_samples=0

		self.pss_min=0
		self.pss_max=0
		self.pss_avg=0

		self.rss_min=0
		self.rss_max=0
		self.rss_avg=0
		
		self.uss_sum=0
		self.pss_sum=0
		self.rss_sum=0
		
		self.prev_ntwrk_rx=0
		self.prev_ntwrk_tx=0
		self.network_stats_tx=0
		self.network_stats_rx=0
		self.cur_ntwrk_tx=0
		self.cur_ntwrk_rx=0
		self.total_rx=0
		self.total_tx=0
		
		self.cpu_avg=0
		self.cpu_samples=0
		self.cpu_sum=0
		self.cpu_percent=0

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
				
		if 'PS_INFO:' in line:
			pid = RE_PID_SPLIT.match( line )

			if pid:
				procid = int(pid.group(1))
				print ">> PID-------> = %s" % procid	

	#	if 'STAT_INFO:' in line:
	#		stats=RE_STATS.split( line )
	#		
	#		if stats:		

				#pidinfo = int(stats[1])
				#print ">> Stats PID________>> %d" % int(stats[2])	
				#print ">> Stats PID________>> %d" % int(stats[3])
				

	#			self.vsize=int(stats[23])	
	#			self.rss =int(stats[24]) 
	#			self.nswap =int(stats[36])
	#			self.cnswap =int(stats[37])
	#			self.num_threads =int(stats[20])
	#			
	#			print "CURRENT MEM = %d" % self.vsize
	#			if self.mem_samples == 0:
	#				self.mem_min = 0
	#				self.mem_max = 0
	#			else:
	#				if self.vsize < self.mem_min:
	#					self.mem_min = self.vsize
	#					print "HAVE MIN MEM = %d" % self.vsize
	#				if self.vsize > self.mem_max:
	#					self.mem_max = self.vsize
	#					print "HAVE MAX MEM = %d" % self.vsize
#
#				# Collect for average and statistics
#				self.mem_samples += 1
#				self.mem_sum += self.vsize
#				#self.m_samples.append( mbps )



		if line.startswith("STAT_INFO:"):
			stats = line[10:].strip()
			if stats:
				stats = RE_STATS.split(stats)
				self.uss = int(stats[-3])
				self.pss = int(stats[-2])
				self.rss = int(stats[-1])
				print ">>>>>>>>>>>USS %s" % self.uss
				
				if self.mem_samples == 0:
					self.uss_min = 0
					self.uss_max = 0
					self.pss_min = 0
					self.pss_max = 0
					self.rss_min = 0
					self.rss_max = 0
				else:
					if self.uss < self.uss_min:
						self.uss_min = self.uss
						print "HAVE MIN USS = %d" % self.uss
					if self.uss > self.uss_max:
						self.uss_max = self.uss
						print "HAVE MAX USS = %d" % self.uss
					if self.pss < self.pss_min:
						self.pss_min = self.pss
						print "HAVE MIN PSS = %d" % self.pss
					if self.pss > self.pss_max:
						self.pss_max = self.pss
						print "HAVE MAX PSS = %d" % self.pss
					if self.rss < self.rss_min:
						self.rss_min = self.rss
						print "HAVE MIN RSS = %d" % self.rss
					if self.rss > self.rss_max:
						self.rss_max = self.rss
						print "HAVE MAX RSS = %d" % self.rss

				self.mem_samples += 1
				self.uss_sum +=self.uss
				self.pss_sum +=self.pss
				self.rss_sum +=self.rss

		if 'CPU:' in line:
			stats=RE_STATS.split( line )
			if stats:
				self.cpu_percent = float(stats[4])
				self.cpu_samples += 1
				self.cpu_sum +=self.cpu_percent
				print "CPU LOAD %1f %%" % self.cpu_percent
				

		if 'NTSTAT_RX:' in line:
			stats=RE_STATS.split( line )
			if stats:
				self.network_stats_rx = int(stats[1])
				self.total_rx +=self.network_stats_rx
				self.cur_ntwrk_rx = self.network_stats_rx-self.prev_ntwrk_rx
				self.prev_ntwrk_rx = self.network_stats_rx

				print "NETWORK %d bytes" % self.cur_ntwrk_rx


		if 'NTSTAT_TX:' in line:
			stats=RE_STATS.split( line )
			if stats:
				self.network_stats_tx = int(stats[1])
				self.total_tx +=self.network_stats_tx
				self.cur_ntwrk_tx = self.network_stats_tx-self.prev_ntwrk_tx
				self.prev_ntwrk_tx = self.network_stats_tx

				print "NETWORK %d bytes" % self.cur_ntwrk_tx

	def close(self):
		"""
		Finalize reading
		"""
		if self.v_samples == 0:
			self.v_average = 0
		else:
			self.v_average = self.v_sum / self.v_samples

		if self.mem_samples == 0:
			self.uss_avg = 0
			self.pss_avg = 0
			self.rss_avg = 0
		else:
			self.uss_avg = self.uss_sum / self.mem_samples
			self.pss_avg = self.pss_sum / self.mem_samples
			self.rss_avg = self.rss_sum / self.mem_samples

		if self.cpu_samples ==0:
			self.cpu_avg = 0
		else:
			self.cpu_avg=self.cpu_sum / self.cpu_samples
			
			


	def metrics(self):
		"""
		Return monitor metrics
		"""
		return {
			'min': self.v_min,
			'max': self.v_max,
			'average' : self.v_average,
			'uss_min' : self.uss_min,
			'uss_max' : self.uss_max,
			'uss_avg' : self.uss_avg,
			'pss_min' : self.pss_min,
			'pss_max' : self.pss_max,
			'pss_avg' : self.pss_avg,
			'rss_min' : self.rss_min,
			'rss_max' : self.rss_max,
			'rss_avg' : self.rss_avg,
			'rx_bytes': self.total_rx,
			'tx_bytes': self.total_tx,
			#'cpu_load': self.cpu_percent
			'cpu_average' : self.cpu_avg,
			
			
		}

