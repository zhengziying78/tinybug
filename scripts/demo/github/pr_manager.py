"""
Deprecated wrapper forwarding to the relocated GitHub PR manager.
"""

from temporal.github.pr_manager import *  # noqa: F401,F403
        print(f"⏰ Timeout reached after {timeout_seconds} seconds")
        return {
            'status': self.get_pr_status(pr_number, repo),
            'checks': self.get_pr_checks(pr_number, repo),
            'completed': False,
            'timeout': True
        }
