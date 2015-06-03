import tempfile
import subprocess
import os
from functools import partial
from itertools import starmap, ifilterfalse, chain
from operator import methodcaller
from func import compose,  typecheck, dictzip, _or
import job
import readline
from glob import glob

#TODO: properly segregate I/O
#TODO: put modules list in config.yaml?

static_modules_list =['bats',
'beagle-lib',
'beast/beast',
'beast/BEASTv1.8.0',
'bio_pieces',
'blast/blast-2.2.30+',
'bowtie/bowtie-2.2.5',
'bwa/bwa-0.7.12-r1044',
'cuda/cuda',
'cuda/cuda_6.5.14',
'igv/igv-2.3.37',
'igv/igv-2.3.52',
'mrsnbactpipeline',
'ngs_mapper/ngs_mapper-1.1',
'ngs_mapper/ngs_mapper-1.2',
'pathdiscov/pathdiscov-4.2',
'pypbs',
'usamriidPathDiscov',
'vdbstatus',
'ray/ray-2.3.1',
'roche/analysis',
'roche/analysis-v2.9',
'roche/gsprocessor-v2.9',
'samtools/samtools-1.1']

ngs_mapper_cmd = '''
cd $PBS_O_WORKDIR
mkdir -p $(pwd)/tmp
SAMPLEDIR=/media/VD_Research/NGSData/ReadsBySample/${SAMPLENAME}
TMPDIR=$(pwd)/tmp runsample.py $SAMPLEDIR {REFPATH} {SAMPLENAME} -od {SAMPLENAME}
'''
expand_path = compose(os.path.realpath, os.path.expanduser) 

''' Tab completion for directories ''' 
def glob_complete(text, state):
    expanded_text = expand_path(text)
    if os.path.isdir(expanded_text):
        expanded_text += '/'
    return (glob(expanded_text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(glob_complete)

prompt = compose(raw_input, "{0}>".format)
def getvar(varname):
    return os.environ.get(varname, None) or prompt(varname)

@typecheck(str)
def get_cmd_spec(module):
    if module.startswith('beast'):
        return {
            'inner_cmd' : 'cd \$TMPDIR\ncp {BEASTXML} input.xml\nbeast -{BEAGLE} input.xml 2>&1 | tee beast_out.txt',
            'vars' : ['BEASTXML', 'BEAGLE']
        }
    elif module.startswith("ngs_mapper"):
        return {
            'inner_cmd' : ngs_mapper_cmd,
            'vars' : ('SAMPLENAME', 'REFPATH')
        }

    elif module == "ngs_mapper_sheet":
         pass
    else:
        return {'inner_cmd' : edit(), 'vars' : []} #open vim

prologue = '''module load {0}'''
#epilogue = '''cp -R ./ \${PBS_O_WORKDIR}/\${PBS_JOBID}'''
epilogue = '''cp -R ./ \$PBS_O_WORKDIR/\$PBS_JOBID'''
wrap_cmd = (prologue + '\n{1}\n' + epilogue).format
#This will overwrite defaults with cfg settings
#sort of outer join
# user config should not have stuff like name, nodes, etc. really just email...
#pbs_defaults = merge_dicts(defaults, user_config)

pbs_defaults = {
    'name' : 'STDIN',
    'nodes' : 1,
    'ppn' : '1',
    'walltime' : "1:00:00",
    'pmem' : "3800mb",
    'queue' : 'batch',
    'exetime' : None,
    'message' : "a",
    'email' : None,
    'command' : None,
    'auto' : False
}

@typecheck(str)
def create_command(module_type):
    cmd_dict = get_cmd_spec(module_type)
    vars, inner_cmd = cmd_dict['vars'], cmd_dict['inner_cmd']
    cmd_opts = dictzip(vars, map(getvar, vars))
    if module_type != None:
          whole_cmd = wrap_cmd(module_type, inner_cmd)
          return whole_cmd.format(**cmd_opts)
    else:
          return inner_cmd

opts = ['name', 'nodes', 'ppn', 'walltime', 'pmem', 'message', 'exetime', 'email', 'auto', 'queue']
option_with_default = _or(getvar, pbs_defaults.__getitem__)

def make_job_dict():
    modules = get_available_modules() + ['Other']
    module_type = select_interactive_menu(modules)
    pbs_opts = dictzip(opts, map(option_with_default, opts))
    pbs_opts['command'] = create_command(module_type)
    return pbs_opts

def module_job():
     pbs_opts = make_job_dict()
     return job.Job(**pbs_opts)

run_and_create_job = compose(methodcaller('submit'), module_job)


#get_mods_cmd = "(modulecmd bash avail) 2>&1 |  grep -v ^---- | tr ' ' '\012' | sort | uniq | grep -v '^$'"

def get_available_modules():
    try:
        return get_modules_by_command()
    except OSError:
        return static_modules_list


is_header = methodcaller('__contains__', '---------')
raw_modules = partial(subprocess.check_output, args=['modulecmd', 'bash', 'avail'], stderr=subprocess.STDOUT)
def get_modules_by_command():
    res = raw_modules()
    inter = filter(bool, ifilterfalse(is_header, res.split('\n')))
    modules = list(chain(*map(str.split, inter)))
    return modules


@typecheck((list, tuple))
def select_interactive_menu(raw_choices):
    show_choice = '{0}. {1}'.format
    selections=dict(enumerate(raw_choices))
    display = '\n'.join(starmap(show_choice, selections.items()))
    print(display)
    _input = prompt('choose module: ')
    if not _input.isdigit() or not (int(_input) in selections):
        print "Error, please select by number."
        prompt("press enter")
        return select_interactive_menu(raw_choices)
    else:
        return selections[int(_input)]

def edit():
    print "Please enter the command in the editor."
    fdes = -1
    path = None
    fp = None
    try:
        fdes, path = tempfile.mkstemp(suffix='.txt', text=True)
        editor = (os.environ.get('VISUAL') or
                  os.environ.get('EDITOR') or
                  'vim')
        subprocess.check_call([editor, path])
        fp = open(path, 'r')
        return fp.read()
    finally:
        if fp is not None:
            fp.close()
        elif fdes >= 0:
            os.close(fdes)
        if path is not None:
            try:
                os.unlink(path)
            except OSError:
                pass



if __name__ == "__main__":
    run_and_create_job()
