#!/usr/bin/env python 

import enforce
import logging
import os
import sys

INFO = logging.INFO
DEBUG = logging.DEBUG
WARNING = logging.WARNING

enforce.config({'enabled': False})  # Turn off runtime type-checking, for speed

if __name__== '__main__':            
    #set up logging
    logging.basicConfig()
    
    logging.getLogger('master').setLevel(INFO) #INFO, DEBUG
    
    #set help message
    help = """
Usage: run_1 MAX_DAYS OUTPUT_DIR 

 MAX_DAYS -- float -- # days to simulate
 OUTPUT_DIR -- string -- output directory for csv file & state db files.
 """

    #got the right number of args?  If not, output help
    num_args = len(sys.argv) - 1
    num_args_needed = [2]
    if num_args not in num_args_needed:
        print(help)
        if num_args > 0:
            print("Got %d argument(s), need %s.\n" % (num_args, num_args_needed))
        sys.exit(0)
    
    #extract inputs
    max_days = eval(sys.argv[1])
    output_dir = sys.argv[2]

    print("Arguments: MAX_DAYS=%s, OUTPUT_DIR=%s\n" % (max_days, output_dir))

    #handle corner cases
    if os.path.exists(output_dir):
        print("\nOutput path '%s' already exists.  Exiting.\n" % output_dir)
        sys.exit(0)

    # make directory
    os.mkdir(output_dir)

    from engine.SimEngine import SimEngine
    from engine.SimStrategy import SimStrategy
    from util import constants
    
    ss = SimStrategy()
    ss.setMaxTicks(max_days * constants.S_PER_DAY / ss.time_step + 1)
    
    assert hasattr(ss, 'save_interval')
    ss.save_interval = constants.S_PER_DAY
                
    #go
    master = SimEngine(ss, output_dir)
    master.run()
