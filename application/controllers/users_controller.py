"""
Handles all logic of the user api
"""
from flask_apispec import MethodResource
from flask_jwt_extended import jwt_required
from neomodel import exceptions
from webargs.flaskparser import use_args

from ..models.user import User
from ..responders import respond_with, no_content
from ..validators import users_validator


class UsersByIDController(MethodResource):
    """Access Users by id"""
    @jwt_required
    def get(self, object_id):
        """ get a single user """
        try:
            user = User.find_by(id_=object_id)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.update_args())
    def patch(self, params, object_id):
        """Logic for updating a user"""
        object_id = params.pop("id")
        try:
            user = User.find_by(id_=object_id)
            user.update(**params)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.update_args())
    def put(self, params, object_id):
        """Logic for updating a user"""
        object_id = params.pop("id")
        try:
            user = User.find_by(id_=object_id)
            if "password" in params:
                password = params.pop("password")
                old_password = params.pop("old_password", None)
                success = user.update_password(password, old_password)
                print(success)
                if not success:
                    return {"error": "old password is not correct"}, 422
            user.update(**params)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.delete_args())
    def delete(self, params, object_id):
        """Logic for deleting a user"""
        object_id = params["id"]
        try:
            user = User.find_by(id_=object_id)
            user.delete()
            return no_content()
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404


class UsersController(MethodResource):
    """ Controller for users """

    @jwt_required
    @use_args(users_validator.index_args())
    def get(self, params):  # pylint: disable=W0613
        """Logic for querying several users"""
        users = User.all()
        return {"users": respond_with(users)}, 200

    @use_args(users_validator.create_args())
    def post(self, params):
        """Logic for creating a user"""
        try:
            user = User(**params).save()
        except exceptions.UniqueProperty:
            return {"error": "Username or Email already taken"}, 409
        return respond_with(user), 200
