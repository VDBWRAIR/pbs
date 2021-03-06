#!/usr/bin/env python

# This script submits a PBS script, as with 'qsub script.sh'
# and adds the job to the pbs.JobDB job database

import pbs, sys

def main():
    if len(sys.argv) != 2:
        print "usage: psub PBS_SCRIPT"
        sys.exit()
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print "usage: psub PBS_SCRIPT"
        sys.exit()

    qsubstr=open(sys.argv[1],"r").read()
    job = pbs.Job( qsubstr=qsubstr )
    job.submit()
