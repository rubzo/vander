#!/usr/bin/env python

import urwid, sys, subprocess, re

regex_number = re.compile("[^\d]*(\d+).*")

def get_value(output, n = 0):
	match = regex_number.match(output)
	if (match):
		# TODO: what if n is bad?
		return int(match.group(n+1))
	return None

def call(cmd):
	try:
		output = subprocess.check_output(cmd)
		return output.rstrip()
	except OSError:
		print("Couldn't execute command: " + " ".join(cmd))
		sys.exit(1)

def test(cmd):
	output = call(cmd)
	value = get_value(output)
	if (value == None):
		print("Couldn't find data in command's output.")
		sys.exit(1)

def usage():
	print("vander - live graphing of a command's output")
	print("vander [-t ...] [-c ...] <command>")
	print(" -t <n> : wait <n> seconds between each command. eg. 0.5, 3")
	print(" -c <color> : use <color> for the graph. eg. dark red, white")
	sys.exit(0)

update_period = 1
graph_color = "white"

# Build the command, and possibly read some flags.
command = []
read_flags = False
i = 1
while (i != len(sys.argv)):
	if (not read_flags) and sys.argv[i] == "-t":
		update_period = float(sys.argv[i+1])
		i += 2
		continue
	elif (not read_flags) and sys.argv[i] == "-c":
		graph_color = sys.argv[i+1]
		i += 2
		continue
	elif (not read_flags) and sys.argv[i] == "-h":
		usage()
	elif (not read_flags):
		read_flags = True
	command.append(sys.argv[i])
	i += 1

# Make sure the command actually returns an integer value somewhere.
test(command)

def add_data_point(data_points, data_point):
	data_points.pop(0)
	data_points.append((data_point, ))

def get_data_ceiling(data_points):
	maximum = 0
	for (i, ) in data_points:
		if (maximum < i):
			maximum = i
	return maximum

palette = [
    ("titlebar", "white", "black"),
    ("background", "white", "black"),
    ("graph_top", graph_color, graph_color),
    ("graph_fill", "white", "black")]

title_text = "Q quits. Graphing command: '" + " ".join(command) + "'"

header_text = urwid.Text(title_text)
header = urwid.AttrMap(header_text, "titlebar")

# TODO: Y axis values
graph_attrs = [("background", " "), ("graph_top", "#"), ("graph_fill", "&")]
graph = urwid.BarGraph(graph_attrs)

layout = urwid.Frame(header=header, body=graph)

# TODO: read from screen width somehow
max_data_points = 40

data_points = []
# Put in fake data points at the start, so the graphing comes
# in from the right...
for i in xrange(0, max_data_points):
	data_points.append((0, ))

def update_graph():
	global graph, command, data_points, header_text, title_text
	data_point = get_value(call(command))
	add_data_point(data_points, data_point)
	maximum = get_data_ceiling(data_points)
	graph.set_data(data_points, maximum)
	header_text.set_text("(L: %d M: %d) -- " % (data_point, maximum) + title_text)

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
