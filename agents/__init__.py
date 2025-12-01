"""
Package for all agents in this project.
Currently exposes the Life Admin agent.
"""

from .life_admin.agent import root_agent, app  # re-export for convenience

__all__ = ["root_agent", "app"]
