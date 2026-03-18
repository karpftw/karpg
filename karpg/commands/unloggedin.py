"""
Custom unlogged-in commands for KARPG.

Replaces Evennia's default single-line `connect user pass` and
`create user pass` with multi-step prompted flows that suppress
terminal echo while passwords are being entered.
"""

from django.conf import settings

from evennia.utils import class_from_module, utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdConnect(COMMAND_DEFAULT_CLASS):
    """
    Log in to an existing account.

    Usage:
      connect
      connect <username>

    You will be prompted for your password. Characters will not echo
    while you type it.
    """

    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()"

    def func(self):
        session = self.caller
        address = session.address
        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        # Step 1: username (inline arg or prompt)
        username = self.args.strip()
        if not username:
            username = (yield "Username: ").strip()
        if not username:
            session.msg("No username given.")
            return

        # Step 2: password — suppress echo, prompt, restore echo
        session.msg("", options={"echo": False})
        password = (yield "Password: ").strip()
        session.msg("", options={"echo": True})

        if not password:
            session.msg("No password given.")
            return

        account, errors = Account.authenticate(
            username=username, password=password, ip=address, session=session
        )
        if account:
            session.sessionhandler.login(session, account)
        else:
            session.msg("|R%s|n" % "\n".join(errors))


class CmdCreate(COMMAND_DEFAULT_CLASS):
    """
    Create a new account.

    Usage:
      create
      create <username>

    You will be prompted to choose and confirm a password. Characters
    will not echo while you type it.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"

    def at_pre_cmd(self):
        if not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            self.msg("Registration is currently disabled.")
            return True
        return super().at_pre_cmd()

    def func(self):
        session = self.caller
        address = session.address
        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        # Step 1: username (inline arg or prompt)
        username = self.args.strip()
        if not username:
            username = (yield "Choose a username: ").strip()
        if not username:
            session.msg("No username given.")
            return

        non_normalized = username
        username = Account.normalize_username(username)
        if non_normalized != username:
            session.msg(
                "Note: your username was normalized to strip spaces and "
                "remove visually confusing characters."
            )

        # Step 2: password (echo suppressed)
        session.msg("", options={"echo": False})
        password = (yield "Choose a password: ").strip()
        session.msg("", options={"echo": True})

        if not password:
            session.msg("No password given.")
            return

        # Step 3: confirm password (echo suppressed)
        session.msg("", options={"echo": False})
        password2 = (yield "Confirm password: ").strip()
        session.msg("", options={"echo": True})

        if password != password2:
            session.msg("|RPasswords do not match. Please try again.|n")
            return

        account, errors = Account.create(
            username=username, password=password, ip=address, session=session
        )
        if account:
            session.msg(f"Account '|w{username}|n' created. Welcome!")
            session.msg(
                "You can now log in. Type: |wconnect %s|n" % username
            )
        else:
            session.msg("|R%s|n" % "\n".join(errors))
