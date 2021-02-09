from ansible.plugins.action import ActionBase

import pexpect
from pprint import pprint


class ActionModule(ActionBase):

    BYPASS_HOST_LOOP = True

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)
        pc = self._play_context
        print(["become", pc.become])
        print(["become_pass", pc.become_pass])
        print(["become_method", pc.become_method])
        print(["pc.become_user", pc.become_user])
        command = self._task.args.get('command', None)
        if pc.become and pc.become_method == "sudo":
            command = f'sudo {command}'
        script = self._task.args.get('script', None)
        pprint(["command", command])
        pprint(["script", script])

        console = pexpect.spawn(command)

        if pc.become and pc.become_method == "sudo":
            print("Sending sudo password")
            console.expect("password for.*:")
            console.send(pc.become_pass)
            console.send("\n")
            console.send("\n")

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
