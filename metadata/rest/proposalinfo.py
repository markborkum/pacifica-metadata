#!/usr/bin/python
"""Core interface for the proposalinfo metadata objects to interface with CherryPy."""
from metadata.rest.proposal_queries.proposal_lookup import ProposalLookup
from metadata.rest.proposal_queries.proposal_term_search import ProposalTermSearch
from metadata.rest.proposal_queries.proposal_user_search import ProposalUserSearch


# pylint: disable=too-few-public-methods
class ProposalInfoAPI(object):
    """ProposalInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.by_user_id = ProposalUserSearch()
        self.search = ProposalTermSearch()
        self.by_proposal_id = ProposalLookup()
