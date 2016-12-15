# This function is just for debugging output; you can safely ignore it.
def finishexample(name):
    print("\nThis is the content of the file 'output.txt' after the example for " + name + ":\n")
    with open('output.txt', 'r') as f:
        print(f.read())

Programming Code segment to read and write to files on disk.

#!/bin/python3
import thisexample

########## Writing a text file ##########

with open('output.txt', 'w') as f:
    f.write('This is being written to a file.\n')
    f.write('And this is the second line of the file!\n')

#####
# Writing a file is very similar to reading a file. Simply pass in a 'w' for
# write mode instead of 'r' for read mode. Then, call f.write with whatever text
# you want to write to the file.
#
# Note that 'w' mode will create a new file if the file does not exist. If the
# file does exist, its old contents will be deleted.
####
thisexample.finishexample("writing a text file with 'w' mode")


########## Appending to a text file ##########

with open('output.txt', 'a') as f:
    f.write('This line is appended to the file.\n')

#####
# You can open a file in append mode by passing an 'a' as the second parameter.
#
# Append mode behaves almost exactly like write mode from above. If the file
# does not exist, it will be created.
#
# The only difference is that if the file does exist, append mode will start
# writing to the file at the end of the file instead of deleting any previous
# contents. Thus, anything you write is appended to the end of the file.
#
# Because the file 'output.txt' exists from the first example, the code above
# simply adds on one line to the file.
#####
thisexample.finishexample("appending to a text file with 'a' mode")


########## Exclusive creation of a text file ##########
print("Exclusive creation of the text file throws an exception:")

with open('output.txt', 'x') as f:
    print('This is never reached.')

#####
# You can open a file in exclusive creation mode by passing an 'x' as the second
# parameter.
#
# Exclusive creation mode behaves almost exactly like write mode from above. If
# the file does not exist, it will be created.
#
# The only difference is that if the file does exist, exclusive creation mode
# will throw a FileExistsError exception. Therefore, if exclusive creation does
# not create the text file itself, opening the file will fail.
#
# Because the file 'output.txt' exists from the first two examples, the code
# above throws an exception.
#
# Note that this mode is not available in Python 2.
#####

