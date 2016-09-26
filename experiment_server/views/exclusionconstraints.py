from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from .webutils import WebUtils
from experiment_server.models.exclusionconstraints import ExclusionConstraint
import sqlalchemy.orm.exc


@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='exclusionconstraints', request_method="GET")
    def exclusionconstraints_GET(self):
        """ List all exclusionconstraints with GET method """
        return list(map(lambda _: _.as_dict(), ExclusionConstraint.all()))

    @view_config(route_name='exclusionconstraint', request_method="DELETE")
    def exclusioncontraints_DELETE_one(self):
        """ Find and delete one exclusionconstraint by id with destroy method """
        id = int(self.request.matchdict['id'])
        try:
            if (ExclusionConstraint.destroy(ExclusionConstraint.get(id)) == None):
                return "Delete exclusionconstraint ID:" + str(id) + " completed."
        except (sqlalchemy.orm.exc.UnmappedInstanceError):
            pass
            return "Delete exclusionconstraint ID:" + str(id) + " failed."
