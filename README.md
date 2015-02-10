# vander

Run a command, and live-graph the first integer in its output, right in your terminal.

## Usage

`vander [-t <how often command should run>] [-c <color>] command`

How often the command should run can be either an integer or a float, e.g., 3 and 0.7 are both valid. See the standard foreground/background colors [here](http://urwid.org/manual/displayattributes.html) for the valid arguments for the color.

## Examples

* `vander.py cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq`
* `vander.py python -c "import random; print random.randint(0, 100)"`

## Todo

* Nothing?
