from flask import Flask, request
import json

from app.documents.user import User
from app.documents.job import Job
from app.causeway_request import CausewayRequest
from app.exceptions import ProcessingError, NonexistentDocumentException


app = Flask(__name__)


def error(status_code: int, exception: Exception):
    return json.dumps({'result': 'error',
                       'message': '{}: {}'.format(type(exception).__name__, str(exception))}), \
           status_code


def success(status_code: int, message: int = None):
    if message:
        success = {'result': 'success', 'message': message}
    else:
        success = {'result': 'success'}
    return json.dumps(success), status_code


# SERVICE


@app.route('/')
def info():
    """
    Information about the server and its status.
    """
    server_info = {
        "url": app.config.server.server_url,
        "causeway_version": app.config.server.causeway_version,
        "pricing_type": app.config.server.pricing_type,
        "free_data": app.config.server.free_data,
        "description": app.config.server.description
    }
    return json.dumps(server_info)


@app.route('/nonce')
def request_id():
    """
    A unique ID which identifies a Causeway request.
    """
    try:
        return CausewayRequest.new(user=request.form['user']).serialize()
    except NonexistentDocumentException as e:
        return error(401, e)


# JOBS


@app.route('/jobs', methods=['GET', 'POST'])
def create_job():
    """
    Add a job.
    """
    if request.method == 'GET':
        try:
            return Job.BulkQuery(active_only=False).serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
        except NonexistentDocumentException as e:
            return error(401, e)
        try:
            Job.new(request.form['payload'])
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


@app.route('/jobs/active')
def active_jobs():
    """
    Active jobs registered with this server.
    Returns an error if no jobs are available.
    """
    try:
        return Job.BulkQuery(active_only=True).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/<string:job_id>')
def job_by_id(job_id):
    """
    A job with the specified ID.
    Returns an error if not found.
    """
    try:
        return Job.from_database(job_id).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


# BIDS


@app.route('/jobs/<string:job_id>/bids', methods=['GET', 'POST'])
def bids(job_id):
    if request.method == 'GET':
        try:
            return Job.from_database(job_id).all_bids().serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
        except NonexistentDocumentException as e:
            return error(401, e)
        try:
            Job.from_database(job_id).add_bid(request.form['payload'])
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>')
def bid_by_id(job_id, bid_id):
    try:
        return Job.from_database(job_id).get_bid(bid_id).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


# OFFERS


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>/offer', methods=['GET', 'POST'])
@app.route('/jobs/<string:job_id>/offer')
def offer(job_id, bid_id):
    if request.method == 'GET':
        try:
            return Job.from_database(job_id).bid_offered_to().serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
        except NonexistentDocumentException as e:
            return error(401, e)
        try:
            Job.from_database(job_id).get_bid(bid_id).offer = request.form['payload']
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


# DELIVERY


@app.route('/jobs/<string:job_id>/delivery', methods=['GET', 'POST'])
def delivery(job_id):
    if request.method == 'GET':
        try:
            return Job.from_database(job_id).delivery.serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
        except NonexistentDocumentException as e:
            return error(401, e)
        try:
            Job.from_database(job_id).delivery = request.form['payload']
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


@app.route('/jobs/<string:job_id>/delivery/acceptance', methods=['POST'])
def accept_delivery(job_id):
    """
    :form-params
    """
    try:
        CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
    except NonexistentDocumentException as e:
        return error(401, e)
    try:
        job = Job.from_database(job_id)
        job.delivery.accept_delivery = request.form['payload']
        job.finish()
        return success(201)
    except ProcessingError as e:
        return error(422, e)
    except NotImplementedError as e:
        return error(501, e)


# DISPUTE


@app.route('/jobs/<string:job_id>/dispute', methods=['GET', 'POST'])
def dispute(job_id):
    if request.method == 'GET':
        try:
            return Job.from_database(job_id).dispute.serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
        except NonexistentDocumentException as e:
            return error(401, e)
        try:
            Job.from_database(job_id).dispute = request.form['payload']
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


@app.route('/jobs/<string:job_id>/dispute/resolution', methods=['POST'])
def resolve_dispute(job_id):
    try:
        CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
    except NonexistentDocumentException as e:
        return error(401, e)
    try:
        Job.from_database(job_id).dispute.resolution = request.form['payload']
        return success(201)
    except ProcessingError as e:
        return error(422, e)
    except NotImplementedError as e:
        return error(501, e)


@app.route('/jobs/<string:job_id>/dispute/resolution/acceptance', methods=['POST'])
def accept_resolution(job_id):
    try:
        CausewayRequest.validate(request.form['user'], request.form['nonce']).update(request.form['payload'])
    except NonexistentDocumentException as e:
        return error(401, e)
    try:
        job = Job.from_database(job_id)
        job.dispute.accept_resolution = request.form['payload']
        job.finish()
        return success(201)
    except ProcessingError as e:
        return error(422, e)
    except NotImplementedError as e:
        return error(501, e)


# USERS


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        try:
            return User.BulkQuery().serialize()
        except NonexistentDocumentException as e:
            return error(404, e)
    elif request.method == 'POST':
        try:
            User.new(request.form['payload'])
            return success(201)
        except ProcessingError as e:
            return error(422, e)
        except NotImplementedError as e:
            return error(501, e)


@app.route('/users/<string:user_id>')
def user_by_id(user_id):
    """
    Information on a specific user.
    """
    try:
        return User.from_database(user_id).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


if __name__ == '__main__':
    app.run()
