#!/usr/bin/env python

import sys
from benchmark.config import BenchmarkConfig
from benchmark.runner import TestRunner
from benchmark.report import TestReport

# Check args
if len(sys.argv) < 2:
	print "Please specify the configuration file to use!"
	sys.exit(1)

# Load configuration 
config = BenchmarkConfig( sys.argv[1] )

# Load tests
tests = config.getTestCases()

# Start test report
report = TestReport( "report.csv" )
report.start( config )

# Run tests
for t in tests:

	# Create a test runner for this test case
	r = TestRunner(t)

	# Log the beginning of the test
	report.log_start( t.name, t.values )

	# Start test
	results = r.run()

	# Check for errors
	if results is None:
		report.log_error( r.lastError )
	else:
		report.log_end( results )
