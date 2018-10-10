from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from underlight_api.database import UnderlightDatabase

class PlayerDetails(Resource):
    @jwt_required
    def get(self, id):
        ident = get_jwt_identity()
        db = UnderlightDatabase.get()
        if id != ident:
            raise ValueError('Requesting details for acct %d but not permissioned' % id)
        pids = db.get_player_ids(id)
        return [db.get_player_info(pid) for pid in pids]
        