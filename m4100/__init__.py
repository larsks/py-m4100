import contextlib
import pexpect
import logging
import re

from .utils import parse_fixed_width_table, parse_dotted_table

LOG = logging.getLogger(__name__)

class CommandExecutionError(Exception):
    def __init__(self, *args, match=None, before=None):
        super().__init__(*args)
        self.match = match
        self.before = before


class Switch:
    prompt0 = re.compile(rb"\((?P<name>[^)]+)\) >")
    prompt1 = re.compile(rb"\((?P<name>[^)]+)\) (\((?P<mode>[^)]+)\))?#")
    re_error = [
        re.compile(b"invalid input", re.IGNORECASE),
        re.compile(b"vlan id not found", re.IGNORECASE),
    ]

    hostname = None
    mode = None

    def __init__(self, hostname, user="admin", password=None):
        self.user = user
        self.password = password
        self.hostname = hostname
        self.prompt = self.prompt0

        self.connect()

    def expect_prompt(self):
        self.expect(self.prompt)
        if self.child.match:
            groups = self.child.match.groupdict()
            self.hostname = (
                groups["name"].decode() if "name" in groups and groups["name"] else None
            )
            self.mode = (
                groups["mode"].decode() if "mode" in groups and groups["mode"] else None
            )
        else:
            self.hostname = None
            self.mode = None

    def expect(self, what):
        self.child.expect([what] + self.re_error)
        if self.child.match and self.child.match.re in self.re_error:
            raise CommandExecutionError(
                match=self.child.match, before=self.child.before
            )

    def connect(self):
        self.child = pexpect.spawn("ssh", args=["-l", self.user, self.hostname])
        self.login()
        self.expect_prompt()

    def login(self):
        if self.password is not None:
            self.expect("password:")
            self.child.sendline(self.password)

    def send_command(self, cmd):
        LOG.debug("send command: %s", cmd)
        self.child.sendline(cmd)
        self.expect_prompt()
        if self.child.before:
            return self.child.before.decode().splitlines()[1:-1]
        else:
            return ""

    def enable(self):
        self.prompt = self.prompt1
        LOG.info("enabled privileged mode")
        self.send_command("enable")
        self.enabled = 1

    def disable(self):
        LOG.info("disabled privileged mode")
        self.prompt = self.prompt0
        self.send_command("exit")
        self.enabled = 0

    @contextlib.contextmanager
    def vlan_database(self):
        self.send_command("vlan database")
        yield
        self.send_command("exit")

    @contextlib.contextmanager
    def configure(self):
        with self.context("configure"):
            yield

    @contextlib.contextmanager
    def interface(self, interface):
        with self.context(f"interface {interface}"):
            yield

    @contextlib.contextmanager
    def context(self, cmd):
        LOG.info("enter context %s", cmd)
        self.send_command(cmd)
        yield
        LOG.info("exit context %s", cmd)
        self.send_command("exit")

    def get_vlans(self):
        out = self.send_command("show vlan")
        return parse_fixed_width_table(out)

    def get_vlan(self, vid):
        out = self.send_command(f"show vlan {vid}")
        return parse_fixed_width_table(out)

    def get_hardware(self):
        out = self.send_command(r"show hardware | include \.\.\.")
        return parse_dotted_table(out)

    def get_sysinfo(self):
        out = self.send_command(r"show sysinfo | include \.\.\.")
        return parse_dotted_table(out)

    def get_ports(self):
        out = self.send_command("show port all")
        return parse_fixed_width_table(out)

    def get_port_status(self):
        out = self.send_command("show port status all")
        return parse_fixed_width_table(out)

    def get_version(self):
        out = self.send_command("show version")
        return parse_dotted_table(out)

    def get_interface_stats(self, interface):
        out = self.send_command(f"show interface {interface}")
        return parse_dotted_table(out)
