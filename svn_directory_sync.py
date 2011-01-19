#!/usr/bin/env python

import os
import optparse
import shlex
import shutil
import subprocess

def run_command(working_directory, command):
    """ Runs command in working directory and returns the output """
    process = subprocess.Popen(shlex.split(command),
                            cwd=working_directory,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT,
                            close_fds = True
                            )
    output = process.stdout.readlines()
    process.stdout.close()
    
    return output

def move_modified_or_added_svn_files(svn_dir, output_dir, revision_1, revision_2, \
                                     verbose):
    """ Moves files in Subversion directory that have been modified or added
    between revision 1 and revision 2 to output directory """
    
    # Run command
    output = run_command(svn_dir, 'svn diff -r %s:%s --summarize' % (revision_1, \
                                                                      revision_2))
    
    # Parse command output and act accordingly
    for line in output:
        # Store related output into variables
        svn_code = line[0]
        relative_location = line[2:].strip()
        
        if svn_code == 'M' or svn_code =='A':
            # File has been modified or added, copy over
            
            # Setup directories for moving files
            origin_location = os.path.join(svn_dir,relative_location)
            destination_location = os.path.join(output_dir, relative_location)
            destination_directory = os.path.dirname(destination_location)
            
            # Make sure origin location exists
            if not os.path.exists(origin_location):
                raise IOError('Unable to access origin file,  \
                              check svn diff output')
            
            # Create directory if it doesnt exist
            if not os.path.exists(destination_directory):
                if verbose:
                    print "Creating directory %s" % (destination_directory)
                os.makedirs(destination_directory)
            
            # If the file is a directory, it's already been created
            if os.path.isdir(origin_location):
                continue
            
            # Output message and copy over
            if verbose:
                print 'Copying %s to %s' % (origin_location,destination_location)
                
            # Copy file over
            shutil.copy(origin_location, destination_location)

if __name__ == '__main__':
    # Collect command line arguments and send them to function
    
    # Collect and parse command line arguments
    parser = optparse.OptionParser()
    parser.add_option("-s", "--svn_dir", dest="svn_dir",
                      help="Subversion directory", metavar="DIRECTORY")
    parser.add_option("-o", "--output_dir", dest="output_dir",
                      help="Output directory", metavar="DIRECTORY")
    parser.add_option("-r", "--revision_1", dest="revision_1",
                      help="Revision 1", metavar="REVISION")
    parser.add_option("-t", "--revision_2", dest="revision_2",
                      help="Revision 2", metavar="REVISION", default="HEAD")
    parser.add_option("-v", action="store_true", dest="verbose",
                      help="Verbose Mode", default=True)
    parser.add_option("-q", action="store_false", dest="verbose",
                      help="Quiet Mode")
    (options, args) = parser.parse_args()
    
    # Force required options as optparse does not support this
    required_options = ('svn_dir', 'output_dir', 'revision_1', 'revision_2')
    for required_option in required_options:
        if getattr(options, required_option) == None:
            parser.error('Required option %s missing' % (required_option))
    
    # Send parsed options to function
    move_modified_or_added_svn_files(options.svn_dir, options.output_dir, \
                                     options.revision_1, options.revision_2, \
                                     options.verbose)