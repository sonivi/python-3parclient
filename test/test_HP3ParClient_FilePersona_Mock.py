# (c) Copyright 2015 Hewlett Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Test class of 3Par Client handling File Persona API."""

import mock
import pprint

from testconfig import config
import HP3ParClient_base as hp3parbase

from hp3parclient import exceptions
from hp3parclient import file_client
from hp3parclient import ssh


class HP3ParFilePersonaClientMockTestCase(hp3parbase.HP3ParClientBaseTestCase):

    interfaces = None
    DEBUG = config['TEST']['debug'].lower() == 'true'

    def debug_print(self, obj, **kwargs):
        if self.DEBUG:
            print pprint.pformat(obj, **kwargs)

    def setUp(self, **kwargs):
        version = (file_client.HP3ParFilePersonaClient
                   .HP3PAR_WS_MIN_BUILD_VERSION)
        mock_version = mock.Mock()
        mock_version.return_value = {'build': version}
        with mock.patch('hp3parclient.client.HP3ParClient.getWsApiVersion',
                        mock_version):
            self.cl = file_client.HP3ParFilePersonaClient('anyurl')
            self.cl.ssh = mock.Mock()
            self.cl.http = mock.Mock()
            self.cl.ssh.run = mock.Mock()
            self.cl.ssh.run.return_value = 'anystring'

    def tearDown(self):
        pass

    class ArgMatcher(object):
        """Test args vs. expected. Options order can vary."""

        def __init__(self, f, cmd, options, specifiers):
            self.assertEqual = f
            self.cmd = cmd
            self.options = options
            self.specifiers = specifiers

        def __eq__(self, actual):

            # Command has to be first. Allow string or list ['doit','nfs'].
            if isinstance(self.cmd, str):
                self.cmd = [self.cmd]
            for c in self.cmd:
                self.assertEqual(c, actual[0])
                del actual[0]

            # Specifiers have to be last.
            if self.specifiers:
                num_specs = len(self.specifiers)
                self.assertEqual(self.specifiers, actual[-num_specs:])
                actual = actual[0:-num_specs]

            # Options can be in any order. Some are flags. Some are pairs.
            if self.options:
                for option in self.options:
                    if isinstance(option, str):
                        actual.remove(option)
                    else:
                        first = actual.index(option[0])
                        self.assertEqual(option[1], actual[first + 1])
                        del actual[first + 1]
                        del actual[first]

                self.assertEqual(actual, [])

            else:
                # No options should match and empty actual.
                self.assertEqual(self.options, actual)

            return True

    def test_cli_from_sig_varargs(self):
        """Use mock and removefpg to test cli_from sig with varargs and
        kwargs."""
        self.cl.removefpg()
        self.cl.ssh.run.assert_called_with(['removefpg', '-f'],
                                           multi_line_stripper=True)
        self.cl.removefpg("foo")
        self.cl.ssh.run.assert_called_with(['removefpg', '-f', 'foo'],
                                           multi_line_stripper=True)
        self.cl.removefpg("foo", "bar")
        self.cl.ssh.run.assert_called_with(['removefpg', '-f',
                                            'foo', 'bar'],
                                           multi_line_stripper=True)
        self.cl.removefpg("foo", "bar", d=True)
        self.cl.ssh.run.assert_called_with(['removefpg', '-f', '-d',
                                            'foo', 'bar'],
                                           multi_line_stripper=True)
        self.cl.removefpg("foo", "bar", forget="4gotten", wait=True)
        self.cl.ssh.run.assert_called_with(['removefpg', '-f',
                                            '-forget', '4gotten',
                                            '-wait',
                                            'foo', 'bar'],
                                           multi_line_stripper=True)
        # what if string 'True' is used.  That is not a boolean!
        self.cl.removefpg("foo", "bar", forget='True', wait=True)
        self.cl.ssh.run.assert_called_with(['removefpg', '-f',
                                            '-forget', 'True',
                                            '-wait',
                                            'foo', 'bar'],
                                           multi_line_stripper=True)
        # keyword=None is skipped
        # keyword=False (boolean) is skipped
        self.cl.removefpg("foo", "bar", forget=None, wait=False)
        self.cl.ssh.run.assert_called_with(['removefpg', '-f',
                                            'foo', 'bar'],
                                           multi_line_stripper=True)

    def test_removefpg_mock(self):
        """Use mock to test removefpg -f."""
        self.cl.removefpg()
        self.cl.ssh.run.assert_called_with(
            ['removefpg', '-f'], multi_line_stripper=True)
        self.cl.removefpg('testfpg')
        self.cl.ssh.run.assert_called_with(
            ['removefpg', '-f', 'testfpg'], multi_line_stripper=True)

    def test_createfstore_mock(self):
        """Use mock to test createfstore."""
        self.assertRaises(TypeError, self.cl.createfstore)
        self.cl.createfstore('testvfs', 'testfstore')
        self.cl.ssh.run.assert_called_with(['createfstore',
                                            'testvfs', 'testfstore'],
                                           multi_line_stripper=True)
        self.cl.createfstore('testvfs', 'testfstore', fpg='testfpg',
                             comment='test comment')
        self.cl.ssh.run.assert_called_with(['createfstore',
                                            '-comment',
                                            '"test comment"',
                                            '-fpg', 'testfpg',
                                            'testvfs', 'testfstore'],
                                           multi_line_stripper=True)

    def test_createfshare_mock(self):
        """Use mock to test createfshare with protocol first."""
        self.assertRaises(TypeError, self.cl.createfshare)
        self.cl.createfshare('nfs', 'testvfs', 'testfshare')
        self.cl.ssh.run.assert_called_with(['createfshare', 'nfs',
                                            'testvfs', 'testfshare'],
                                           multi_line_stripper=True)
        self.cl.createfshare('smb', 'testvfs', 'testfshare')
        self.cl.ssh.run.assert_called_with(['createfshare', 'smb',
                                            'testvfs', 'testfshare'],
                                           multi_line_stripper=True)
        self.cl.createfshare('nfs', 'testvfs', 'testfstore', fpg='testfpg',
                             fstore='testfstore', sharedir='testsharedir',
                             comment='test comment')
        self.cl.ssh.run.assert_called_with(self.ArgMatcher(
            self.assertEqual,
            ['createfshare', 'nfs'],
            [('-fpg', 'testfpg'),
             ('-fstore', 'testfstore'),
             ('-sharedir', 'testsharedir'),
             ('-comment', '"test comment"')],  # Comments get quoted
            ['testvfs', 'testfstore']), multi_line_stripper=True)

    def test_strip_input_from_output(self):
        cmd = [
            'createvfs',
            '-fpg',
            u'marktestfpg',
            '-wait',
            '127.0.0.2',
            '255.255.255.0',
            'UT5_VFS_150651'
        ]
        out = [
            'setclienv csvtable 1',
            'createvfs -fpg marktestfpg -wait 127.0.0.2 255.255.255.0 '
            'UT5_VFS_150651',
            'exit',
            'CSIM-EOS08_1611165 cli% setclienv csvtable 1\r',
            'CSIM-EOS08_1611165 cli% createvfs -fpg marktestfpg -wait '
            '127.0.0.2 255.255.255.\r',
            '0 UT5_VFS_150651\r',
            'VFS UT5_VFS_150651 already exists within FPG marktestfpg\r',
            'CSIM-EOS08_1611165 cli% exit\r',
            ''
        ]
        expected = [
            'VFS UT5_VFS_150651 already exists within FPG marktestfpg\r']

        actual = ssh.HP3PARSSHClient.strip_input_from_output(cmd, out)
        self.assertEqual(expected, actual)

    def test_strip_input_from_output_no_exit(self):
        cmd = [
            'createvfs',
            '-fpg',
            u'marktestfpg',
            '-wait',
            '127.0.0.2',
            '255.255.255.0',
            'UT5_VFS_150651'
        ]
        out = [
            'setclienv csvtable 1',
            'createvfs -fpg marktestfpg -wait 127.0.0.2 255.255.255.0 '
            'UT5_VFS_150651',
            'XXXt',  # Don't match
            'CSIM-EOS08_1611165 cli% setclienv csvtable 1\r',
            'CSIM-EOS08_1611165 cli% createvfs -fpg marktestfpg -wait '
            '127.0.0.2 255.255.255.\r',
            '0 UT5_VFS_150651\r',
            'VFS UT5_VFS_150651 already exists within FPG marktestfpg\r',
            'CSIM-EOS08_1611165 cli% exit\r',
            ''
        ]
        self.assertRaises(exceptions.SSHException,
                          ssh.HP3PARSSHClient.strip_input_from_output,
                          cmd, out)

    def test_strip_input_from_output_no_setclienv(self):
        cmd = [
            'createvfs',
            '-fpg',
            u'marktestfpg',
            '-wait',
            '127.0.0.2',
            '255.255.255.0',
            'UT5_VFS_150651'
        ]
        out = [
            'setclienv csvtable 1',
            'createvfs -fpg marktestfpg -wait 127.0.0.2 255.255.255.0 '
            'UT5_VFS_150651',
            'exit',
            'CSIM-EOS08_1611165 cli% setcliXXX csvtable 1\r',  # Don't match
            'CSIM-EOS08_1611165 cli% createvfs -fpg marktestfpg -wait '
            '127.0.0.2 255.255.255.\r',
            '0 UT5_VFS_150651\r',
            'VFS UT5_VFS_150651 already exists within FPG marktestfpg\r',
            'CSIM-EOS08_1611165 cli% exit\r',
            ''
        ]
        self.assertRaises(exceptions.SSHException,
                          ssh.HP3PARSSHClient.strip_input_from_output,
                          cmd, out)

    def test_strip_input_from_output_no_cmd_match(self):
        cmd = [
            'createvfs',
            '-fpg',
            u'marktestfpg',
            '-wait',
            '127.0.0.2',
            '255.255.255.0',
            'UT5_VFS_150651'
        ]
        out = [
            'setclienv csvtable 1',
            'createvfs -fpg marktestfpg -wait 127.0.0.2 255.255.255.0 '
            'UT5_VFS_150651',
            'exit',
            'CSIM-EOS08_1611165 cli% setclienv csvtable 1\r',
            'CSIM-EOS08_1611165 cli% createvfs -fpg marktestfpg -wait '
            '127.0.0.2 255.255.255.\r',
            '0 UT5_VFS_XXXXXX\r',  # Don't match
            'VFS UT5_VFS_150651 already exists within FPG marktestfpg\r',
            'CSIM-EOS08_1611165 cli% exit\r',
            ''
        ]
        self.assertRaises(exceptions.SSHException,
                          ssh.HP3PARSSHClient.strip_input_from_output,
                          cmd, out)

# testing
# suite = unittest.TestLoader().
#     loadTestsFromTestCase(HP3ParFilePersonaClientTestCase)
# unittest.TextTestRunner(verbosity=2).run(suite)
