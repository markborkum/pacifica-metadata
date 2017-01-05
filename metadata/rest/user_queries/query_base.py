"""CherryPy Status Metadata proposalinfo base class."""
from metadata.orm import UserGroup, Proposals, ProposalParticipant


class QueryBase(object):
    """Retrieves a set of proposals for a given keyword set."""

    @staticmethod
    def format_user_block(user_entry):
        """Construct a dictionary from a given user instance in the metadata stack."""
        user_hash = user_entry.to_hash()
        proposal_xref = ProposalParticipant()
        where_exp = proposal_xref.where_clause({'person_id': user_entry.id})
        proposal_person_query = (
            ProposalParticipant.select().where(where_exp))

        proposals_id_list = [prop.proposal.id for prop in proposal_person_query]

        proposals = Proposals.select().where(Proposals.id << proposals_id_list)

        clean_proposals = {}
        for prop in proposals:
            info = prop.to_hash()
            info.pop('abstract')
            prop_id = prop.id
            clean_proposals[prop_id] = info

        return_block = {
            'person_id': user_hash.get('_id'),
            'first_name': user_hash.get('first_name'),
            'last_name': user_hash.get('last_name'),
            'network_id': user_hash.get('network_id'),
            'email_address': user_hash.get('email_address'),
            'last_updated': user_hash.get('updated'),
            'emsl_employee': False,
            'proposals': clean_proposals
        }

        usergroup_xref = UserGroup()
        where_exp = usergroup_xref.where_clause({'person_id': user_entry.id})
        groups = (UserGroup.select().where(where_exp))

        for group in groups:
            if group.person_id == user_entry.id:
                return_block['emsl_employee'] = True
                break

        return return_block

    @staticmethod
    def compose_help_block_message():
        """Assemble a block of relevant help text to be returned with an invalid request."""
        message = 'You must supply either a numeric person id (like "/userinfo/<person_id>")'
        message += ' or search for one using the form "/userinfo/search/<search_term_1>+<search_term_2>"'
        return message