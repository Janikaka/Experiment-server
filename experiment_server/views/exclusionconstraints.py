from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.exclusionconstraints import ExclusionConstraint


@view_defaults(renderer='json')
class ExclusionConstraints(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='exclusionconstraints', request_method="GET")
    def exclusionconstraints_GET(self):
        """ List all exclusionconstraints with GET method """
        return list(map(lambda _: _.as_dict(), ExclusionConstraint.all()))

    @view_config(route_name='exclusionconstraint', request_method="GET")
    def exclusionconstraints_GET_one(self):
        """ Find and return one configurationkey by id with GET method """
        exconst_id = self.request.swagger_data['id']
        exconstraint = ExclusionConstraint.get(exconst_id)
        if exconstraint is None:
            print_log(datetime.datetime.now(), 'GET', '/exclusionconstraints/'
                      + str(exconst_id), 'Get one exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        return exconstraint.as_dict()

    @view_config(route_name='exclusionconstraint', request_method="DELETE")
    def exclusioncontraints_DELETE_one(self):
        """ Find and delete one exclusionconstraint by id with destroy method """
        exconst_id = self.request.swagger_data['id']
        exconstraint = ExclusionConstraint.get(exconst_id)
        if not exconstraint:
            print_log(datetime.datetime.now(), 'DELETE', '/exclusionconstraints/'
                      + str(exconst_id), 'Delete exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        ExclusionConstraint.destroy(exconstraint)
        print_log(datetime.datetime.now(), 'DELETE', '/exclusionconstraints/'
                  + str(exconst_id), 'Delete exclusionconstraint', 'Succeeded')
        return self.createResponse(None, 200)
