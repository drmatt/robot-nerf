# Python G-Code simulator
#
# Copyright (C) 2011 Peter Rogers
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import absolute_import, division, print_function

import sys
import math
try:
    import numpy
except ImportError:
    print("ERROR - Cannot import NumPy module. Please visit http://www.numpy.org/\n")
    raise

###########
# Globals #
###########

OPERATIONS = {
    "*" : lambda a, b : a*b,
    "/" : lambda a, b : a/float(b),
    "+" : lambda a, b : a+b,
    "-" : lambda a, b : a-b,
}

# The rapid speed rate in mm/s
RAPID_SPEED_MM = 25.0

#############
# Functions #
#############

def parse_program(path):
    fd = open(path, "r")

    prog = Program()
    while 1:
        line = fd.readline()
        if (not line): 
            break
        line = line.strip()

        try:
            i = line.index("(")
        except ValueError:
            comment = ""
        else:
            comment = line[i:]
            line = line[:i].strip()

        args = line.split()

        statement = Statement()
        statement.command = line.strip() + " " + comment
        statement.lineNumber = len(prog.statements)
        if (line.startswith("#")):
            # Assignment statement
            if (len(args) != 3):
                print("bad line: %s" % repr(line))
                prog.invalidLines.append(line)
                continue

            name = args[0]
            op = args[1]
            exp = args[2]

            if (op != "="):
                print("bad line: %s" % repr(line))
                continue

            statement.code = op
            statement.args = (name, exp)

        elif (not line):
            pass

        else:
            code = args[0]
            args = args[1:]

            if (code.startswith("N")):
                # skip line numbers
                code = args[0]
                args = args[1:]
                

            if (code.startswith("G") or code.startswith("M")):
                # Format as a two digit number to make things standard (M2 -> M02)
                letter = code[0]
                try:
                    num = int(code[1:])
                except ValueError:
                    prog.invalidLines.append(line)
                    continue
                code = "%s%02d" % (letter, num)

            statement.code = code
            statement.args = args

            # Parse the arguments for this statement. Each parameter has a letter associated
            # with it, and there may or may not be a space between it and the value.
            n = 0
            while n < len(args):
                # Grab the next parameter
                arg = args[n]
                n += 1
                if (len(arg) == 1):
                    # The parameter and value are split up (eg "X" and "123.4")
                    key = arg
                    if (n < len(args)):
                        value = args[n]
                    else:
                        value = ""
                    n += 1
                else:
                    # The parameter and value come as a single token (eg "X123.4")
                    key = arg[0]
                    value = arg[1:]
                statement.params[key] = value

        statement.comment = comment
        prog.statements.append(statement)

    fd.close()
    return prog


###########
# Classes #
###########

class Program(object):
    statements = None
    invalidLines = None

    def __init__(this):
        this.statements = []
        this.invalidLines = []

    def start(this):
        return State(this)

class Statement(object):
    code = None
    args = None
    comment = None
    command = None
    params = None
    lineNumber = 0

    def __init__(this):
        this.code = ""
        this.params = {}

# A path plotting out by the cutting head
class Path(object):
    # Whether the spindle is on/off when tracing this path
    spindleOn = False
    # The statement that generated this path
    statement = None
    # The command that generated this path
    command = ""
    # The length of the path in machine units
    length = 0
    # The rate which we move along the path, in machine units
    feedRate = 1
    # When this path is traversed in the job timeline
    startTime = 0
    duration = 0

# A path between two points
class Line(Path):
    start = None
    end = None
    # Whether this represents a rapid movement command (G00), or 
    # a linear interpolation (G01)
    rapid = False

    def __init__(this, start, end, feedRate):
        this.start = start.copy()
        this.end = end.copy()
        this.feedRate = feedRate
        this.length = numpy.linalg.norm(this.end-this.start)
        this.duration = this.length/float(this.feedRate)

    def __repr__(this):
        template = '{0.__class__.__name__}({0.start}, {0.end}, {0.feedRate})'
        return template.format(this)

# An arc segment
class Arc(Path):
    clockwise = True
    center = None
    start = None
    end = None
    radius = 0

    def __init__(this, start, end, center, feedRate, clockwise=True):
        this.start = start.copy()
        this.end = end.copy()
        this.center = center.copy()
        this.feedRate = feedRate
        this.clockwise = clockwise

        u = this.start - this.center
        v = this.end - this.center

        this.radius = numpy.linalg.norm(u)

        this.angle1 = math.atan2(u[1], u[0])
        this.angle2 = math.atan2(v[1], v[0])

        if (this.angle1 < 0): this.angle1 += 2*math.pi
        if (this.angle2 < 0): this.angle2 += 2*math.pi

        diff = abs(this.angle1-this.angle2)
        if (diff > math.pi): 
            diff = 2*math.pi - diff
        this.length = this.radius * diff
        this.duration = this.length/float(this.feedRate)

    def __repr__(this):
        template = ('{0.__class__.__name__}({0.start}, {0.end}, {0.center}, '
                    '{0.feedRate}, {0.clockwise})')
        return template.format(this)

class ToolChange(Path):
    length = 0
    duration = 0
    def __repr__(this):
        return this.__class__.__name__ + '()'

class Dwell(Path):
    duration = 0
    def __repr__(this):
        return this.__class__.__name__ + '()'

class State(object):
    variables = None
    lineno = 0
    finished = False
    program = None
    # In units per second
    feedRate = 1
    time = 0
    minPos = None
    maxPos = None
    pos = None
    spindleOn = True
    # The paths cut by the laser
    paths = None
    # The units are inches by default
    units = "in"
    rapidSpeed = RAPID_SPEED_MM/25.4
    # The list of not-implemented codes in this program
    unknownCodes = None

    # The output GCode
    output = []
    previousG = None

    def __init__(this, program):
        this.variables = {}
        this.program = program
        this.paths = []
        # Note it is important to pass floats to make this a float array (otherwise it uses ints)
        this.pos = numpy.array([0.0, 0.0, 0.0])
        this.unknownCodes = []

    # Returns the length of the job
    def get_run_length(this):
        total = 0
        for path in this.paths:
            total += path.duration
        return total

    def eval_expression(this, exp):
        if (exp.startswith("[")):
            # Calculated value
            exp = exp[1:-1]

        if (not exp): 
            return 0

        for op in ("*", "/", "+", "-"):
            try:
                i = exp.index(op)
            except ValueError:
                pass
            else:
                (left, right) = (exp[:i], exp[i+1:])
                left = this.eval_expression(left)
                right = this.eval_expression(right)
                func = OPERATIONS[op]
                return func(left, right)

        if (exp.startswith("#")):
            return this.variables[exp]

        return float(exp)

    def eval_coords(this, args):
        lst = {}
        for arg in args:
            lst[arg[0]] = this.eval_expression(arg[1:])
        return lst

    def eval_params(this, params):
        lst = {}
        for key in params:
            lst[key] = this.eval_expression(params[key])
        return lst

    def handle_statement(this, st):
        if (st.code == ""):
            # Noop
            pass

        elif (st.code == "%"):
            pass

        elif (st.code == "="):
            # Variable assignment
            (name, exp) = st.args
            this.variables[name] = this.eval_expression(exp)

        elif (st.code.startswith("X") or st.code.startswith("Y") or st.code.startswith("Z")):
            # next pass of previous G command
            # need to do the same thing in previous command G00 or G01
            pass 

        elif (st.code == "G01" or st.code == "G00"):
            # Linear interpolation / rapid positioning
            params = this.eval_params(st.params)
            try:
                # The feed rate is supplied per minute
                this.feedRate = params["F"]/60.0
            except KeyError:
                pass

            if (this.pos is None):
                # Use this move to define the starting position
                this.pos = numpy.array([params["X"], params["Y"]])
                return

            if ("X" in params or "Y" in params):
                newpos = this.pos.copy()
                try:
                    newpos[0] = params["X"]
                except KeyError:
                    pass
                try:
                    newpos[1] = params["Y"]
                except KeyError:
                    pass

                if (this.spindleOn):
                    # The spindle is on, move at the feed rate
                    feedRate = this.feedRate
                else:
                    # Otherwise move at the jog rate
                    feedRate = this.rapidSpeed

                # Create a line connecting our position to the target position
                line = Line(this.pos, newpos, feedRate)
                line.startTime = this.time
                line.spindleOn = this.spindleOn
                line.rapid = (st.code == "G00")
                try:
                    line.cmd = (params["X"], params["Y"])
                except KeyError:
                    pass
                line.statement = st
                this.paths.append(line)
                # Advance the timeline
                this.time += line.duration
                # Jump to the end position
                this.pos = newpos.copy()

        elif (st.code == "G02" or st.code == "G03"):
            # Circle interpolation, clockwise or couter-clockwise
            params = this.eval_params(st.params)

            try:
                # The feed rate is supplied per minute
                this.feedRate = params["F"]/60.0
            except KeyError:
                pass
            
            
            newpos = this.pos.copy()
            try:
                newpos[0] = params["X"]
            except KeyError:
                pass
            try:
                newpos[1] = params["Y"]
            except KeyError:
                pass

            end = newpos

            if (this.spindleOn):
                try:
                    center = this.pos + numpy.array([params["I"], params["J"]])
                    arc = Arc(this.pos, end, center, this.feedRate, clockwise=(st.code=="G02"))
                    arc.startTime = this.time
                    arc.spindleOn = this.spindleOn
                    arc.statement = st
                    this.paths.append(arc)
                    # Advance the timeline
                    this.time += arc.duration
                except:
                    print( "failed ", st.code, st.params)
                    
            this.pos = end.copy()

        elif (st.code == "M02"):
            # End of program
            this.finished = True

        elif (st.code == "M03"):
            this.spindleOn = True

        elif (st.code == "M05"):
            this.spindleOn = False

        elif (st.code == "G96"):
            # Constant surface speed
            pass

        elif (st.code == "G21"):
            # Programming in mm
            this.units = "mm"
            this.rapidSpeed = RAPID_SPEED_MM

        elif (st.code == "G90"):
            print("G90: absolute distance mode")

        elif (st.code == "G17"):
            # Define the XY plane
            pass

        elif (st.code.startswith("F")):
            # Feed rate definition
            rate = this.eval_expression(st.code[1:])
            this.feedRate = float(rate)

        

        elif (st.code == "M06"):
            # Tool change operation
            change = ToolChange()
            change.duration = 3
            change.startTime = this.time
            change.statement = st
            this.paths.append(change)
            this.time += change.duration

        elif (st.code.startswith("T")):
            # Tool selection operation
            pass

        elif (st.code.startswith("N")):
            # line number
            pass

        elif (st.code == "G04"):
            # Dwell operation
            params = this.eval_params(st.params)
            dwell = Dwell()
            dwell.startTime = this.time
            dwell.statement = st
            dwell.duration = params.get("P", 0)
            this.paths.append(dwell)
            this.time += dwell.duration

        else:
            # print("Unknown code: %s" % st.code)
            if (not st.code in this.unknownCodes): 
                this.unknownCodes.append(st.code)

    def gen_command( this, code, p ):
        q = inverse_kinematics(p)
        return code + " X" + str(q[0]) + " Y" + str(q[2])+ " Z-" + str(q[1]) + " F100"

    def process_g(this,st):

        statements = [st]

        
        # Linear interpolation / rapid positioning
      
        params = this.eval_params(st.params)
        try:
            # The feed rate is supplied per minute
            this.feedRate = params["F"]/60.0
        except KeyError:
            pass

        try:
            x = params["X"]
        except KeyError:
            x = None

        try:
            y = params["Y"]
        except KeyError:
            y = None

        try:
            z = params["Z"]
        except KeyError:
            z = None
        
        # if this.pos is None:
        #     # Use this move to define the starting position
        #     if x is None:
        #         x = 0.0
            
        #     if y is None:
        #         y = 0.0
            
        #     if z is None:
        #         z = 0.0

        #     this.pos = numpy.array([x, y, z ])
        #     return

       
        newpos = this.pos.copy()

        if x is not None: 
            newpos[0] = x

        if y is not None: 
            newpos[1] = y

        if z is not None: 
            newpos[2] = z

        
        
        if (this.spindleOn):
            # The spindle is on, move at the feed rate
            feedRate = this.feedRate
        else:
            # Otherwise move at the jog rate
            feedRate = this.rapidSpeed

        # line = Line(this.pos, newpos, feedRate)


        max_segment_length = 0.1
        
        distance = numpy.linalg.norm( newpos - this.pos )

        print( "==", this.pos, newpos, distance, st.command)

        statements = []

        if distance>max_segment_length and  st.code != "G00": # ignore rapids
            

            start = numpy.array(this.pos)
            end = numpy.array(newpos)

            num_segments = math.ceil( distance / max_segment_length )
            
            n = 1
            
            while n<num_segments:
                f = n /num_segments
                p = start + f* ( end - start )
                statement = Statement()
                statement.command = this.gen_command( st.code, p) # "G01 X" + str(p[0]) + " Y" + str(p[1]) + " Z-" + str(p[2])
                statements.append( statement )

                n += 1 
            
            statement = Statement()
            statement.command =  this.gen_command( st.code, end) # "G01 X" + str(end[0]) + " Y" + str(end[1]) + " Z-" + str([2])
            statements.append( statement )
        else:
            statement = Statement()
            statement.command =  this.gen_command( st.code, numpy.array(newpos))
            statements.append( statement )

            
        this.pos = newpos.copy()

        return statements
    
    def process_statement(this,st):

        statements = [st]

        if (st.code.startswith("X")):
            st.params["X"] = st.code[1:]
            st.code = this.previousG
            statements = this.process_g(st)
            pass 

        # elif (st.code.startswith("Y")):
        #     st.params["Y"] = st.code[1:]
        #     st.code = this.previousG
        #     statements = this.process_g(st)
        #     pass 

        # elif (st.code.startswith("Z")):
        #     st.params["Z"] = st.code[1:]
        #     st.code = this.previousG
        #     statements = this.process_g(st)
        #     pass 

        elif (st.code == "G01" or st.code == "G00"):
            this.previousG = st.code
            statements = this.process_g(st)

        return statements

    def step(this):
        # Execute the current statement
        st = this.program.statements[this.lineno]
        

        for s in this.process_statement(st):
            print(s.command)
            if s.command != None:
                this.output.append( s.command )



        # Increment to the next statement
        this.lineno += 1
        # Check if the program is finished
        if (this.lineno >= len(this.program.statements)):
            this.finished = True

        if (this.pos is None):
            return

        # Update the minimum pos
        if (this.minPos is None):
            this.minPos = this.pos.copy()
        else:
            this.minPos[0] = min(this.pos[0], this.minPos[0])
            this.minPos[1] = min(this.pos[1], this.minPos[1])
        # Update the max position too
        if (this.maxPos is None):
            this.maxPos = this.pos.copy()
        else:
            this.maxPos[0] = max(this.pos[0], this.maxPos[0])
            this.maxPos[1] = max(this.pos[1], this.maxPos[1])


def dump_parse():
    """Command line function to print G-code from a file."""
    import re
    import os
    import sys
    from pprint import pprint

    if len(sys.argv) != 2:
        print('Please give path to G-code file.')
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print('File does not exist.')
        sys.exit(1)

    prog = parse_program(path)
    state = prog.start()

    while not state.finished:
        state.step()

    for command in state.output:
        print(command)

    # max_segment_length = 0.1

    # for path in state.paths:
    #     if (isinstance(path,Line)):
    #         if (path.rapid or path.length<max_segment_length):
    #             print( path )
    #         else:
    #             print( "split", path)
    #             start = numpy.array(path.start)
    #             end = numpy.array(path.end)
    #             num_segments = math.ceil( path.length / max_segment_length )
    #             print( "G01 X", start[0], " Y", start[1] )
                
    #             n = 1
                
    #             while n<num_segments:
    #                 f = n * path.length/num_segments
    #                 p = start * (1-f) + end * f
    #                 print( "G01 X", p[0], " Y",p[1] )
    #                 n += 1 
    #             print()
           
    

def inverse_kinematics(p):
    
    x = p[0]
    y = p[1]
    z = p[2]

    a1 = 200
    a2 = 99 
    q2 = numpy.arccos( (x*x+y*y-a1*a1-a2*a2) / (2*a1*a2) )
    q1 = numpy.arctan(y/x) - numpy.arctan( (a2*numpy.sin(q2)) / (a1 + a2*numpy.cos(q2)) )
    
    
    return [ numpy.rad2deg(q1), numpy.rad2deg(q2), z]

if __name__ == '__main__':
    dump_parse()
