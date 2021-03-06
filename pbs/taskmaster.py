#!/usr/bin/env python
import pbs, argparse, sys, subprocess

def main():
    parser = argparse.ArgumentParser(description='Automatically resubmit PBS jobs')
    parser.add_argument('-d','--delay', type=str, default="15:00", \
      help='How long to delay ("[[[DD:]HH:]MM:]SS") between executions.  Default is "15:00".')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--hold', action='store_true', help='Place a hold on the currently running taskmaster')
    group.add_argument('--release', action='store_true', help='Release the currently running taskmaster')
    group.add_argument('--kill', action='store_true', help='Kill the currently running taskmaster')

    args = parser.parse_args()

    if args.hold:
        jobid = pbs.job_id(name="taskmaster")
        if len(jobid) != 0:
            pbs.hold(jobid[-1])
    elif args.release:
        jobid = pbs.job_id(name="taskmaster")
        if len(jobid) != 0:
            pbs.release(jobid[-1])
    elif args.kill:
        jobid = pbs.job_id(name="taskmaster")
        if len(jobid) != 0:
            pbs.alter(jobid[-1], "-a " + pbs.exetime("10:00:00:00") )
            pbs.delete(jobid[-1])
    else:
        
        # check if taskmaster already running (besides this one)
        jobid = pbs.job_id(name="taskmaster")
        tmaster_status = pbs.job_status(jobid)
        for j in jobid:
            if j != pbs.job_id():
                if tmaster_status[j]["jobstatus"] != "C":
                    print "A taskmaster is already running. JobID:", j, "  Status:",  tmaster_status[j]["jobstatus"] 
                    sys.exit()
        
        # continue jobs
        db = pbs.JobDB()
        db.update()
        db.continue_all()
        db.close()
        
        # submit taskmaster
        print "submit taskmaster"
        j = pbs.PrismsDebugJob(nodes="1", ppn="1", name="taskmaster", \
            exetime=pbs.exetime(args.delay), auto=False, message=None, \
            command="taskmaster " + ' '.join(sys.argv[1:]))
        j.submit(add=False)
        
        #print "submit string:"
        #print j.qsub_string()
