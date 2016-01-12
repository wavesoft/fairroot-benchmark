
import signal
from threading import Thread
from subprocess import Popen, PIPE

class TestLauncher(Thread):

	def __init__(self, name, cmdline, stdin, monitor=None, *args, **kwargs):
		"""
		Initialize a test launcher
		"""
		# Initialize thread
		Thread.__init__(self, *args, **kwargs)

		# Prepare properties
		self.cmdline = cmdline
		self.stdin = stdin
		self.name = name

		# Specify monitor
		self.monitor = monitor
		self.proc = None

	def interrupt(self):
		"""
		Interrupt the subprocess
		"""

		# First gracefully kill the sub-process
		if self.proc:
			self.proc.send_signal(signal.SIGINT)

	def poll(self):
		"""
		Forward poll request
		"""
		if self.proc:
			return self.proc.poll()
		return -1

	def run(self):
		"""
		Main run function
		"""

		# Open process
		self.proc = proc = Popen( self.cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE )
		sentSIGINT = False

		# Send stdin
		proc.stdin.write( self.stdin )
		proc.stdin.close()
		
		# Read output
		if self.monitor is None:
			proc.stdout.read()
			proc.stdout.close()
		else:
			for line in iter(proc.stdout.readline, b''):
				self.monitor.process( line.strip() )

				# If we have enough data, kill process
				if self.monitor.enoughData and not sentSIGINT:
					proc.send_signal(signal.SIGINT)
					sentSIGINT = True

			proc.stdout.close()

		# Drain standard error
		stderr = proc.stderr.read()
		proc.stderr.close()

		# Wait for completion
		proc.wait()
		ret = proc.returncode
		print "INFO: Exited with %r" % ret

		# Check for errors
		if ret != 0:
			print "~~~~~~~~~~~~~~~~~~~~~~~~"
			print stderr
			print "~~~~~~~~~~~~~~~~~~~~~~~~"

		# Return exit code
		return ret
