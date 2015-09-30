This directory should contain all test scripts.

All test scripts should be named like test_*.py, where * describes which
parts of the ReportLab toolkit are being tested (see sample test scripts).

Most tests can be executed individually, or all can be run with 'runAll.py'.
Some tests are functional rather than unit-tests and do things like
generating the manuals, which assumes that you have the normal source
distribution layout and other directories in the correct locations.

The file runAll.py begins by deleting any files with extension ".pdf" or
".log" in the test directory, so you can't confuse old and current
test output.  It then loops over all test scripts following the 
aforementioned pattern and executes them.

Any PDF or log files written should be examined, at least before
major releases.  If you are writing tests, ensure that you only
leave behind files which you intend a human to check.
