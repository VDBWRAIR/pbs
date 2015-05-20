"""A package for submitting and managing PBS jobs"""
from job import *
from jobdb import *
from misc import *
from templates import *
from custom import *
__all__ = dir()

__version__ = '1.1.0'
__release__ = __version__ + '-dev'
__authors__ = 'Brian Puchala, Tyghe Vallard, Michael panciera'
__authoremails__ = 'bpuchala@umich.edu, vallardt@gmail.com, michael.panciera.work@gmail.com'
__description__ = 'PBS job submission and management',
__projectname__ = 'pbs'
__keywords__ = "pbs, job, submit, qstat, pstat"
