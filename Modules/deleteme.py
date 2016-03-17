def get_net_devices():
	"""Return list of network devices."""
	with open('/proc/net/dev', 'r') as fhandle:
		lines = [line.lstrip() for line in fhandle.readlines()]

	return [line.split(':', 1)[0] for line in lines
		if not (line.startswith('face') or line.startswith('Inter-'))]

print get_net_devices()
