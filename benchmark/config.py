
import json
import itertools
from benchmark.testcase import TestCase
from collections import OrderedDict

class TestCaseConfig:

	def __init__(self, test_config, test_name, values, local, remote):
		"""
		A test-case contains the machine and the a
		"""

		# Keep test properties
		self.config = test_config
		self.name = test_name

		# Keep test values
		self.values = values
		self.local = local
		self.remote = remote

class MachineConfig:

	def __init__(self, name="", ip="", app={}):
		"""
		Machine configuration
		"""

		# Application configuration
		self._app = app
		# Machine name
		self.name = name
		# Machine IP
		self.ip = ip

	def env(self, test_case=None):
		"""
		Compile and return environment variables, with macros applied
		"""

		# Prepare response
		ans = {}

		# Update known macros with test-case values
		km = self._env.copy()
		if not test_case is None:
			km.update( test_case.values )

		# Iterate over environment variables
		for k,v in self._env.iteritems():
			# Replace macros in the value
			value = v
			if '%' in value:
				value = value % km
			# Update env variable AND the known macros
			ans[k] = value
			km[k] = value

		# Return response
		return ans

class BenchmarkConfig:

	def __init__(self):
		"""
		Initialize the benchmark configuration case
		"""

		# Reset properties
		self.application = None
		self.localMachine = None
		self.remoteMachines = []
		self.testCases = []

	def parseMachineConfig(self, machine_conf):
		"""
		Parse specified machine configuration and return a machine instance
		"""

		# Prepare local copy of the config
		app = self.application.copy()

		# Prepare application variables
		if 'application' in machine_conf:
			_app = machine_conf['application']

			# Check for special cases
			for k,v in _app:

				# Handle merge cases
				if k == "env":
					app['env'].update( v )
				elif k == "config":
					app['config'].update( v )

				# Handle append cases
				elif k == "cmdline_append":
					# Check for appendable command-line information
					app['cmdline'].extend( v )

				# Everything else is replace
				else:
					app[k] = v


		# Create a return a MachineConfig instance
		return MachineConfig(
				name=conf['name'],
				ip=conf['ip'],
				app=app
			)

	def load(self, filename):
		"""
		Load configuration from the specified JSON file
		"""

		# Load configuration from file to raw dict
		# (We are using OrderedDict to perserve the order in the configuration)
		with open(filename, "r") as f:
			raw = json.loads( f.read(), object_pairs_hook=OrderedDict )

		##############################
		# Parse test cases config
		##############################

		# Reset test cases
		self.testCases = []

		# Parse configuration
		values = []
		keys = []
		_test = raw['test']
		for k,v in _test['cases'].iteritems():
			keys.append(v)
			values.append(v)

		# Generate test cases as product of combinations
		for v in itertools.product(*values):
			self.testCases.append( dict(zip( keys, v)) )

		##############################
		# Parse application config
		##############################

		# Reset application config
		self.application = {
			"cmdline": ["/bin/false"],
			"env": {},
			"config_arg": "--config-json-file",
			"config": {}
		}

		# Update application config
		_app = raw['application']
		if 'cmdline' in _app:
			self.application['cmdline'] = _app['cmdline']
		if 'config_arg' in _app:
			self.application['config_arg'] = _app['config_arg']
		if 'config' in _app:
			self.application['config'] = _app['config']
		if 'env' in _app:
			self.application['env'] = _app['env']

		##############################
		# Parse machine configuration
		##############################

		# Parse local machine configuration
		self.localMachine = self.parseMachineConfig(raw['machines']['local'])

		# Parse remote machine configuration
		for m in raw['machines']['remote']:
			self.remoteMachines.append( self.parseMachineConfig(m) )


	def getTestCases(self):
		"""
		Compile and return the test cases
		"""
		ans = []

		# Iterate over test case values and create
		# test cases with the appropriate config
		for case in self.testCases:

			# Calculate a name for this test
			name = "%s-%s" % (_test['name'], "-".join(map(str,case.values())))

			# Create a test-case config
			ans.append( TestCaseConfig(
				test_config=_test, test_name=name,
				values=case, local=self.localMachine, 
				remote=self.remoteMachines) 
			)

		# Return test cases
		return ans

