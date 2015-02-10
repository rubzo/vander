#!/usr/bin/env python

import urwid, sys, subprocess, re

import os
SCREEN_rows, SCREEN_columns = os.popen('stty size', 'r').read().split()
SCREEN_rows = int(SCREEN_rows)
SCREEN_columns = int(SCREEN_columns)

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

def get_unique_points(data_points):
	uniques = []
	for (i, ) in data_points:
		if i not in uniques and (i != 0):
			uniques.append(i)
	return sorted(uniques)[:-1]

palette = [
    ("titlebar", "white", "black"),
    ("background", "white", "black"),
    ("graph_top", graph_color, graph_color),
    ("line", "white", "white"),
    ("graph_fill", "white", "black")]

title_text = "Q quits. Graphing command: '" + " ".join(command) + "'"

header_text = urwid.Text(title_text)
header = urwid.AttrMap(header_text, "titlebar")

title_rows = header_text.rows((SCREEN_columns, ))

graph_attrs = [("background", " "), ("graph_top", "#"), ("graph_fill", "&")]
graph = urwid.BarGraph(graph_attrs)

y_axis_size = 10

y_axis_text = urwid.Text("MAXIMUM", align="right")
y_axis = urwid.AttrMap(y_axis_text, "titlebar")
columns = urwid.Columns([(y_axis_size, y_axis), ("weight", 1, urwid.LineBox(urwid.BoxAdapter(graph, SCREEN_rows - (2 + title_rows))))])

layout = urwid.Frame(header=header, body=urwid.Filler(columns))

max_data_points = SCREEN_columns - y_axis_size - 2

data_points = []
# Put in fake data points at the start, so the graphing comes
# in from the right...
for i in xrange(0, max_data_points):
	data_points.append((0, ))

def update_y_axis(maximum, data_points):
	if maximum == 0:
		return

	global y_axis_text, title_rows

	uniques = get_unique_points(data_points)

	graph_height = SCREEN_rows - (title_rows)

	if len(uniques) > 5:
		new_uniques = []
		factor = len(uniques) / 5
		i = 0
		while (i < len(uniques)):
			new_uniques.append(uniques[i])
			i += factor
		uniques = new_uniques

	placements = []
	for unique in uniques:
		placement = graph_height - int((float(unique) / maximum) * graph_height)
		if (placement > graph_height):
			placement = graph_height
		placements.append((placement, unique))

	final = ["\n"] * (graph_height)
	final[0] = str(maximum) + "\n"
	final[-1] = "0" + "\n"
	for (placement, unique) in placements:
		if (placement > 0) and (placement < (graph_height-1)):
			final[placement] = str(unique) + "\n"

	new_text = "".join(final)
	y_axis_text.set_text(new_text)

def update_graph():
	global graph, command, data_points, header_text, title_text
	data_point = get_value(call(command))
	add_data_point(data_points, data_point)
	maximum = get_data_ceiling(data_points)
	graph.set_data(data_points, maximum)
	#header_text.set_text("(L: %d M: %d) -- " % (data_point, maximum) + title_text)
	update_y_axis(maximum, data_points)

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
