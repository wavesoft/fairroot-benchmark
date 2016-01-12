
# Import thread
from threading import Thread
from subprocess import Popen, PIPE

def run_app(workdir, cmdline, outqueue, config):
	"""
	Dump the configuration JSON from the config parameter into the 'benchmark-temp.json'
	and then run the application specified in the command line (an array of arguments).

	When interesting information are crawled from the command-line, they should be pushed
	to the output queue. (This queue object is thread-safe, so you can pass it as argument
	to thread functions).

	This function should return when the test has completed.
	"""

	# Open configuration JSON (the 'with' statement will close the file upon
	# exiting the code block)
	with open("%s/benchmark-temp.json" % workdir, "w") as f:
		# Write JSON-Encoded contents of the configuration
		f.write( json.dumps(config) )

	# TODO: Launch Process

	# TODO: Start processing thread

	# TODO: Parse output and send feedback to outqueue

	# TODO: Kill process when ready

	# TODO: Return

