from flask import Flask, request
import json

from app.documents.user import User
from app.documents.job import Job
from app.causeway_request import CausewayRequest
from app.exceptions import ProcessingError, NonexistentDocumentException


app = Flask(__name__)
app.template_folder = 'json'


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


@app.route('/jobs/add', methods=['POST'])
def create_job():
    """
    Add a job.
    """
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
def show_active_jobs():
    """
    Active jobs registered with this server.
    Returns an error if no jobs are available.
    """
    try:
        return Job.BulkQuery(active_only=True).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/all')
def show_all_jobs():
    """
    Active jobs registered with this server.
    Returns an error if no jobs are available.
    """
    try:
        return Job.BulkQuery(active_only=False).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/<string:job_id>')
def show_job_by_id(job_id):
    """
    A job with the specified ID.
    Returns an error if not found.
    """
    try:
        return Job.from_database(job_id).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


# BIDS


@app.route('/jobs/<string:job_id>/bids/add', methods=['POST'])
def add_bid_to_job(job_id):
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


@app.route('/jobs/<string:job_id>/bids')
def job_bids(job_id):
    """
    All bids for a job.
    Returns an error if no bids are available.
    """
    try:
        return Job.from_database(job_id).all_bids().serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>')
def job_bid_by_id(job_id, bid_id):
    """
    A specific bid submitted to a job.
    Returns an error if bid does not exist.
    """
    try:
        return Job.from_database(job_id).get_bid(bid_id).serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


# OFFERS


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>/offer', methods=['POST'])
def create_offer_for_job(job_id, bid_id):
    """
    Award a job to a bidder. The URL should contain the 'id' parameter.
    Returns an error if the URL is invalid or the ID is invalid.
    """
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


@app.route('/jobs/<string:job_id>/offer')
def show_offer_for_job(job_id):
    """
    Get bid that the job was offered to.
    """
    try:
        return Job.from_database(job_id).bid_offered_to().serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


# DELIVERY


@app.route('/jobs/<string:job_id>/delivery/add', methods=['POST'])
def add_delivery(job_id):
    """
    Submit a delivery.
    """
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


@app.route('/jobs/<string:job_id>/delivery')
def show_delivery(job_id):
    """
    What a user submitted for a job delivery.
    Returns an error if no delivery has yet been submitted.
    """
    try:
        return Job.from_database(job_id).delivery.serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/<string:job_id>/delivery/accept', methods=['POST'])
def accept_delivery(job_id):
    """
    Accept a delivery.
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


@app.route('/jobs/<string:job_id>/dispute/add', methods=['POST'])
def add_dispute(job_id):
    """
    File a dispute.
    """
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


@app.route('/jobs/<string:job_id>/dispute')
def show_dispute(job_id):
    """
    Disputes that were filed for a job.
    Returns an error if no dispute was filed.
    """
    try:
        return Job.from_database(job_id).dispute.serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


@app.route('/jobs/<string:job_id>/dispute/resolution/add', methods=['POST'])
def resolve_dispute(job_id):
    """
    Cancel or finish a dispute.
    """
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


@app.route('/jobs/<string:job_id>/dispute/resolution/accept', methods=['POST'])
def accept_resolution(job_id):
    """
    Cancel or finish a dispute.
    """
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


@app.route('/users/add', methods=['POST'])
def add_user():
    """
    Add a user.
    """
    try:
        User.new(request.form['payload'])
        return success(201)
    except ProcessingError as e:
        return error(422, e)
    except NotImplementedError as e:
        return error(501, e)


@app.route('/users')
def users():
    """
    All users registered with a server.
    """
    try:
        return User.BulkQuery().serialize()
    except NonexistentDocumentException as e:
        return error(404, e)


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
