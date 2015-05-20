"""A package for submitting and managing PBS jobs"""
from job import *
from jobdb import *
from misc import *
from templates import *
from custom import *
__version__ = "VERSION_ID (git sha COMMIT_ID)"
__release__ = __version__ + '-dev'
__authors__ = 'Tyghe Vallard, Michael panciera'
__authoremails__ = 'vallardt@gmail.com, michael.panciera.work@gmail.com'
__description__ = 'PBS job submission in python'
__projectname__ = 'pbs'
__keywords__ = "pbs, torque, python"
__all__ = dir()
