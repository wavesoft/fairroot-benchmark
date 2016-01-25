
import datetime

class TestReport:

	def __init__(self, filename):
		"""
		Initialize a new test report, keeping the data in the output specified
		"""
		self.filename = filename
		self.fd = None
		self.testID = 0
		self.activeTest = {}

	def start(self, config):
		"""
		Start test report, using the specified benchmark configuration specified
		"""

		# Reset properties
		self.testID = 0
		self.activeTest = {}
		self.columns = config.testConfig['metrics']

		# Open file descriptor
		self.fd = open(self.filename, "w")

		# Write title & Columns
		self.fd.write("Test Name,%s\n" % config.testConfig['title'])
		self.fd.write("Test Date,%s\n" % str(datetime.datetime.now()))
		self.fd.write("\n")
		self.fd.write("Num,Started,Ended,Status,Name,%s\n" % ( ",".join(self.columns) ) )

	def close(self):
		"""
		Close test report
		"""

		# Close file descriptor if open
		if self.fd:
			self.fd.close()
			self.fd = None

	def log_start(self, name, values=None):
		"""
		Log the start of a test
		"""

		# Prepare properties
		self.testID += 1
		self.activeTest = {
			'name': name,
			'values': values
		}

		# Log the beginning of test and starting date
		self.fd.write("%i,%s" % ( self.testID, str(datetime.datetime.now()) ) )

	def log_error(self, error):
		"""
		Log the failure of a test
		"""

		# Write end and values
		self.fd.write(",%s,Error,%s,%s\n" % ( str(datetime.datetime.now()), self.activeTest['name'], error ) )

	def log_end(self, metrics):
		"""
		Log the completion of a test
		"""

		# Make sure the metrics are arranged in column order
		vals = ""
		for col in self.columns:

			# Add commas
			if vals:
				vals += ","

			# Add dash or metric value
			if not col in metrics:
				vals += "-"
			else:
				vals += str(metrics[col])

		# Write end and values
		self.fd.write(",%s,OK,%s,%s\n" % ( str(datetime.datetime.now()), self.activeTest['name'], vals ) )

