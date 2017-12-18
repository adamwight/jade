import json

import flask

from ... import util
from .... import errors, types


def configure(config, bp, trusted_clients, centralauth, state):

    @bp.route("/v1/judgements", methods=["GET"])
    def get_judgements(context):
        """Get all judgements."""
        if 'download_all' in flask.request.values:
            judgements_doc = state.judgements.get()
        else:
            judgements_doc = state.judgements.get_contexts()

        return flask.json.jsonify(judgements_doc)

    @bp.route("/v1/judgements/<string:context>", methods=["GET"])
    def get_context_judgements(context):
        """Get all judgements within a context."""
        if 'download_all' in flask.request.values:
            judgements_doc = state.judgements.get(context)
        else:
            judgements_doc = state.judgements.get_types(context)
        return flask.json.jsonify(judgements_doc)

    @bp.route("/v1/judgements/<string:context>/<string:type>", methods=["GET"])
    def get_entity_type_judgements(context, type_):
        """Get all judgements for a specific entity type."""
        judgements_doc = state.judgements.get(context, type_)
        return flask.json.jsonify(judgements_doc)

    @bp.route("/v1/judgements/<string:context>/<string:type>/<int:id>", methods=["GET"])  # noqa
    def get_entity_judgements(context, type_, id_):
        """Get all judgements for a specific entity."""
        judgements_doc = state.judgements.get(
            context, type_, id_)
        return flask.json.jsonify(judgements_doc)

    @bp.route("/v1/judgements/<string:context>/<string:type>/<int:id>/<string:schema>", methods=["GET"])  # noqa
    def get_entity_schema_judgements(context, type_, id_, schema):
        """Get all judgements for a specific entity schema."""
        judgements_doc = state.judgements.get(
            context, type_, id_, schema)
        return flask.json.jsonify(judgements_doc)

    @bp.route("/v1/judgements/<int:judgement_id>/preference", methods=["PUT"])
    @util.authorized_user_action(
        config, trusted_clients, centralauth, "set_judgement_preference")
    def set_judgement_preference(judgement_id, gu_id, request_values):
        """
        Set the preference bit for a specific judgement and returns the event.
        """
        preference = json.loads(request_values['preference'])
        if preference not in (True, False):
            raise errors.ParameterError(
                "'preference' must be either 'true' or 'false'")

        proto_event = types.events.JudgementPreferenceSet.proto(
            gu_id=gu_id, judgement_id=judgement_id, preference=preference)

        return util.execute_and_log_or_error(state, proto_event)

    @bp.route("/v1/judgements/", methods=["POST"])
    @util.authorized_user_action(
        config, trusted_clients, centralauth, "new_judgement")
    def new_judgement(gu_id, request_values):
        """Create a new judgement and return the event."""

        context = request_values['context']
        entity_type = request_values['entity_type']
        entity_id = request_values['entity_id']
        schema = request_values['schema']
        data = json.loads(request_values['data'])

        state.schemas.validate(schema, data)

        proto_event = types.events.NewJudgement.proto(
            gu_id=gu_id, context=context,
            entity=types.Entity(entity_type, entity_id),
            schema=request_values['schema'], data=data)

        return util.execute_and_log_or_error(state, proto_event)
