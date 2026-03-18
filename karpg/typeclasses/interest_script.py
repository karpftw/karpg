"""
InterestScript

Global script (not attached to any object) that fires every 86400 seconds.
Applies 1% compound interest to all characters with bank_balance > 0,
capped at 50,000 GP.

Started from server/conf/at_server_startstop.py:at_server_start().
"""

from evennia.scripts.scripts import DefaultScript


class InterestScript(DefaultScript):

    def at_script_creation(self):
        self.key = "daily_interest"
        self.interval = 86400   # 24 hours in seconds
        self.persistent = True
        self.repeats = 0        # 0 = repeat forever

    def at_repeat(self):
        from world.economy import INTEREST_RATE, INTEREST_CAP
        import evennia

        chars = evennia.search_object(typeclass="typeclasses.characters.Character")
        for char in chars:
            bal = getattr(char.db, "bank_balance", 0) or 0
            if bal <= 0:
                continue
            headroom = INTEREST_CAP - bal
            if headroom <= 0:
                continue
            interest = min(int(bal * INTEREST_RATE), headroom)
            if interest > 0:
                char.db.bank_balance = bal + interest
                if char.sessions.count():
                    char.msg(
                        f"|gThe First Newhaven Bank has credited |w{interest:,} GP|g "
                        f"interest to your account. "
                        f"New balance: |w{char.db.bank_balance:,} GP|g.|n"
                    )
