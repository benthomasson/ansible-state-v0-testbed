from ansible.plugins.action import ActionBase

import pexpect
from pprint import pprint


class ActionModule(ActionBase):

    BYPASS_HOST_LOOP = True

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)
        command = self._task.args.get('command', None)
        script = self._task.args.get('script', None)
        pprint(command)
        pprint(script)

        console = pexpect.spawn(command)

        logfile = None

        for line in script:
            line_type, line_value = list(line.items())[0]
            print(line_type, line_value)
            if line_type == "logfile":
                logfile = open(line_value, 'wb')
                console.logfile = logfile
            elif line_type == "expect":
                console.expect(line_value)
            elif line_type == "send":
                console.send(line_value)
            elif line_type == "interact":
                console.interact()

        if logfile:
            logfile.flush()
            logfile.close()
        return result
