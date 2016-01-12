
class TestCase:

	def __init__(self, properties, localMachine, remoteMachines):
		"""
		Initialize the test case
		"""

		# The test properties (vary between tests)
		self.properties = properties

		# Local and remote machines
		self.localMachine = localMachine
		self.remoteMachines = remoteMachines