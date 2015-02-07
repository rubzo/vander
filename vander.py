#!/usr/bin/env python

import urwid, sys, subprocess, re

regex_number = re.compile("[^\d]*(\d+).*")

def call(cmd):
	try:
		output = subprocess.check_output(cmd)
		return output.rstrip()
	except OSError:
		print("Couldn't execute command: " + " ".join(cmd))
		sys.exit(1)

def get_value(output, n = 0):
	match = regex_number.match(output)
	if (match):
		# TODO: what if n is bad?
		return int(match.group(n+1))
	return None

def test(cmd):
	output = call(cmd)
	value = get_value(output)
	if (value == None):
		print("Couldn't find data in command's output.")
		sys.exit(1)

command = []
for i in xrange(1, len(sys.argv)):
	command.append(sys.argv[i])

test(command)

# TODO: read from screen width
max_data_points = 40
update_period = 0.5

data_points = []
for i in xrange(0, max_data_points):
	data_points.append((0, ))

def add_data_point(data_points, data_point):
	data_points.pop(0)
	data_points.append((data_point, ))

def get_data_ceiling(data_points):
	maximum = 0
	for (i, ) in data_points:
		if (maximum < i):
			maximum = i
	return maximum

def get_average(data_points):
	total = 0
	for (i, ) in data_points:
		total += i
	return (float(total) / len(data_points))

palette = [
    ('titlebar', 'white', 'black'),
    ('graph_bg', 'white', 'black'),
    ('graph_top', 'white', 'white'),
    ('graph_fill', 'white', 'black')]

title_text = "Q quits. Graphing command: '" + " ".join(command) + "'"

header_text = urwid.Text(title_text)
header = urwid.AttrMap(header_text, 'titlebar')

# TODO: Y axis values
graph_attrs = [('graph_bg', " "), ('graph_top', "#"), ('graph_fill', "&")]
graph = urwid.BarGraph(graph_attrs)
layout = urwid.Frame(header=header, body=graph)

def update_graph():
	global graph, command, data_points, header_text, title_text
	data_point = get_value(call(command))
	add_data_point(data_points, data_point)
	maximum = get_data_ceiling(data_points)
	average = get_average(data_points)
	graph.set_data(data_points, maximum)
	header_text.set_text("(L: %d M: %d RA: %.3f) -- " % (data_point, maximum, average) + title_text)

def handle_input(key):
    if key == 'Q' or key == 'q':
        raise urwid.ExitMainLoop()

def periodic(main_loop, user_data):
	global update_period
	update_graph()
	main_loop.set_alarm_in(update_period, periodic)

main_loop = urwid.MainLoop(layout, palette, unhandled_input=handle_input)
periodic(main_loop, None)
main_loop.run()
