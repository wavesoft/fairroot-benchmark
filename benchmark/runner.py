
import json
import copy
import time
import signal

from benchmark.monitor import TestMonitor
from benchmark.launcher import TestLauncher

def _recursive_macro_replace(val, macros):
	"""
	Iterate over the items of val and replace the macros with
	the properties of macros dictionary
	"""

	# Iterate over dicts
	if isinstance(val, dict):
		for k,v in val.iteritems():
			val[k] = _recursive_macro_replace(v, macros)
		return val

	# Iterate over lists
	elif isinstance(val, list):
		for i in range(0, len(val)):
			val[i] = _recursive_macro_replace(val[i], macros)
		return val

	# Replace only strings
	elif (type(val) is str) or (type(val) is unicode):
		if '%' in val:
			return val % macros
		return val

	# Everything else passes through
	else:
		return val


class TestRunner:

	def __init__(self, test_case):
		"""
		Initialize the runner for the specified test case
		"""

		# Reset properties
		self.lastError = ""
		self.testCase = test_case

		# Prepare launcher for monitor machine
		self.m_monitor = self.prepareLauncherConfig(
				test_case.local, test_case.remote, test_case.values
			)

		# Prepare launcher for assistant machines
		self.m_assist = []
		for m in test_case.remote:
			self.m_assist.append(
					self.prepareLauncherConfig(
							m, [test_case.local], test_case.values
						)
				)

	def prepareLauncherConfig(self, machine, remote_machines, values):
		"""
		Prepare launcher configuration for the specified machine and test-case
		"""

		# Collect information from various sources to build known macros
		km = machine.app['env'].copy()
		km.update( values )
		if 'globals' in self.testCase.config:
			km.update( self.testCase.config['globals'] )

		# Define local info
		km['local_ip'] = machine.ip
		km['local_name'] = machine.name

		# Define remote info
		for i in range(0, len(remote_machines)):
			# Unprefixed, is the last EP
			km['remote_ip'] = remote_machines[i].ip
			km['remote_name'] = remote_machines[i].name
			# But also include a list of EPs
			km['remote_%i_ip' % i] = remote_machines[i].ip
			km['remote_%i_name' % i] = remote_machines[i].name

		# Calculate some derrivatives (Allow 8 pending messages on the queue)
		km['rxtx_size_plus'] = int(km['rxtx_size']) * 8
		km['rxtx_size_minus'] = int(km['rxtx_size']) / 2

		############################
		# Compile environment
		############################

		# Start with empty
		l_env = {}

		# Iterate over environment variables
		for k,v in machine.app['env'].iteritems():
			# Replace macros in the value
			value = v
			if '%' in value:
				value = value % km
			# Update env variable AND the known macros
			l_env[k] = value
			km[k] = value

		############################
		# Compile Configuration
		############################

		# Recursively replace macros
		l_conf = copy.deepcopy( machine.app['config'] )
		_recursive_macro_replace( l_conf, km )

		############################
		# Compile command-line
		############################

		# Just clone the base command-line
		l_cmdline = list(machine.app['cmdline'])

		# Prepend the executable to run (if specified)
		if ('exec' in machine.app) and machine.app['exec']:
			l_cmdline.insert(0, machine.app['exec'])

		# Append configuration file flag
		l_cmdline.append( machine.app['config_arg'] )

		# Convert macros
		l_cmdline = _recursive_macro_replace( l_cmdline, km )

		print "DEBUG: Executing %s <config>" % " ".join(l_cmdline)
		print "DEBUG: Config:\n%s" % json.dumps(l_conf, indent=4, separators=(',', ': '))

		############################
		# Compile bootstrap script
		############################

		# Prepare script
		l_script = "\n".join([
			"#!/bin/bash",

			# Create a temporary were to keep the config
			"CONF=/tmp/fairmq-benchmark.json",

			# Write down the config
			"cat <<EOF > $CONF",
			json.dumps(l_conf, indent=4, separators=(',', ': ')),
			"EOF",

			# Prepare environment
			"\n".join(map(lambda kv: "export %s=%s" % kv, l_env.iteritems())),

			# Execute command-line
			"stdbuf -i0 -o0 -e0 " + " ".join(l_cmdline) + " $CONF"

		])

		############################
		# Prepare bootstrap command
		############################

		# Prepare command-line
		l_bootstrap = ["bash"]

		# In case of SSH, prefix with SSH
		if 'ssh' in machine.config:
			_ssh = machine.config['ssh']

			# Calculate ssh info to prepend
			ssh_cmdline = [ 'ssh', '-t' ]

			# Check for identity file
			if 'key' in _ssh:
				ssh_cmdline.append( "-i" )
				ssh_cmdline.append( _ssh['key'] )

			# Get host
			if 'host' in _ssh:
				host = _ssh['host']
			else:
				host = machine.ip

			# Get user
			if 'user' in _ssh:
				host = "%s@%s" % (_ssh['user'], host)

			# Finalize cmdline
			ssh_cmdline.append( host )
			ssh_cmdline.append( "--" )

			# Prepend to l_bootstrap
			ssh_cmdline.extend( l_bootstrap )
			l_bootstrap = ssh_cmdline

		# Return config
		return (machine.name, l_bootstrap, l_script)


	def run(self):
		"""
		Start the test and return the results, or None if an error occured
		"""
		print "--[ %s ]-----" % self.testCase.name

		# Create a test monitor
		monitor = TestMonitor( self.testCase )

		# Create launchers
		launchers = [ TestLauncher( *self.m_monitor, monitor=monitor ) ]
		for m in self.m_assist:
			launchers.append( TestLauncher( *m ) )

		# Start launchers
		monitor.start()
		for l in launchers:
			print "INFO: Starting app on %s" % l.name
			l.start()
			time.sleep(0.5)

		# Wait for head process to exit
		print "INFO: Waiting head worker to complete"
		launchers[0].join()

		# Wait 5 seconds for other threads to exit
		hasAlive = True
		timeout = time.time() + 5
		while (time.time() < timeout) and hasAlive:
			hasAlive = False
			for i in range(1,len(launchers)):
				if launchers[i].poll() is None:
					hasAlive = True
			time.sleep(0.5)

		# Kill incomplete threads
		if hasAlive:
			print "INFO: Forcefully stopping remaining workers"
			for i in range(1,len(launchers)):
				if launchers[i].poll() is None:
					launchers[i].interrupt()

		# Join all threads
		for i in range(1,len(launchers)):
			if launchers[i].poll() is None:
				launchers[i].join()

		# Collect monitor results
		monitor.close()
		return monitor.metrics()
