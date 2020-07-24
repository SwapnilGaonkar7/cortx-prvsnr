import os
import pytest
import json
import logging


logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def env_level():
    return 'base'


@pytest.fixture(scope='module')
def script_name():
    return 'start-eos'


# TODO test=True case

# isolated is required since parametrization is used
@pytest.mark.isolated
@pytest.mark.mock_cmds({'': ['salt']})
@pytest.mark.parametrize("remote", [True, False], ids=['remote', 'local'])
@pytest.mark.parametrize("restart", [True, False], ids=['start', 'restart'])
def test_start_eos_commands(
    mhost, mlocalhost, ssh_config, remote, restart, mock_hosts, run_script
):
    remote = '--remote {}'.format(mhost.hostname) if remote else ''
    ssh_config = '--ssh-config {}'.format(ssh_config) if remote else ''
    with_sudo = '' # TODO

    res = run_script(
        "{} {} {} {}".format(
            ssh_config, with_sudo, remote, '--restart' if restart else ''
        ),
        mhost=(mlocalhost if remote else mhost)
    )
    assert res.rc == 0

    if restart:
        expected_lines = [
            "SALT-ARGS: * state.apply components.stop",
            "SALT-ARGS: * state.apply components.start"

        ]
    else:
        expected_lines = [
            "SALT-ARGS: * state.apply components.start"
        ]

    assert res.stdout.count('SALT-ARGS: ') == len(expected_lines)

    stdout_lines = [
        line for line in res.stdout.split(os.linesep) if 'SALT-ARGS' in line
    ]
    ind = stdout_lines.index(expected_lines[0])
    assert stdout_lines[ind:(ind + len(expected_lines))] == expected_lines