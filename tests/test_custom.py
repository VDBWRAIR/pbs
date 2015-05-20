import unittest
import mock
#from pbs import custom
from custom import make_job_dict, create_command, select_interactive_menu, module_job
envs = ('bxml', 'beagle_GPU')
choices = ['2', 'Aname', '3', '', '', '', '', '', 'user@email', '', '', 'bxml', 'beagle_GPU']

def Raise():
     raise OSError('foo')


class TestCustomJobSystem(unittest.TestCase):
    def setUp(self):
        self.expected_beast = '''module load beast/beast
cd \$TMPDIR
cp bxml input.xml
beast -beagle_GPU input.xml 2>&1 | tee beast_out.txt
cp -R ./ \$PBS_O_WORKDIR/\$PBS_JOBID'''

    @mock.patch("custom.os.environ.get")#, side_effect=envs)
    def test_beast_env_job_command_text(self, mget):
        #mget.return_value = 'bxml'
        mget.side_effect = envs
        actual =  create_command('beast/beast')
        self.assertMultiLineEqual(self.expected_beast, actual)


    @mock.patch("custom.getvar")#, side_effect=envs)
    def test_beast_job_command_text_rawinput(self, minput):
        minput.side_effect = envs
        #j = module_job()
        actual =  create_command('beast/beast')
        #actual = j.command
        self.assertMultiLineEqual(self.expected_beast, actual)

    @mock.patch("custom.raw_modules", side_effect=Raise)
    @mock.patch("custom.prompt", side_effect=choices)
    def test_full_job_command_dict_rawinput(self, _, __):
        expected = {
        'name' : 'Aname',
        'nodes' : '3',
        'ppn' : '1',
        'pmem' : "3800mb",
        'walltime' : "1:00:00",
        'exetime' : None,
        'message' : "a",
        'email' : 'user@email',
        'queue' : 'batch',
        'command' : self.expected_beast,
        'auto' : False
    }
        #with mock.patch('__builtin__.raw_input', side_effect=choices()):
        actual = make_job_dict()
        self.assertEquals(expected, actual)

    @mock.patch("custom.raw_modules", side_effect=Raise)
    @mock.patch("custom.prompt", side_effect=choices)
    def test_full_job_command_job_created(self, _, __):
        #with mock.patch('__builtin__.raw_input', side_effect=choices()):
        job = module_job()
        self.assertEquals('Aname', job.name)
        self.assertEquals(self.expected_beast, job.command)


    def test_interactive_menu(self):
        with mock.patch('custom.prompt', return_value='1'):
            choices = ['a', 'b', 'c']
            result = select_interactive_menu(choices)
            self.assertEquals('b', result)

    def test_interactive_menu_with_failures(self):
        with mock.patch('custom.prompt', side_effect=['a', 'do', '2']):
            choices = ['a', 'b', 'c']
            result = select_interactive_menu(choices)
            self.assertEquals('c', result)

