from flask import Flask, request
import json

from app.documents.user import User
from app.documents.job import Job
from app.causeway_token import CausewayToken
from app.exceptions import ProcessingError, NonexistentDocumentException, BadTokenException, DocumentQuotaExceeded


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


def get_result(getter):
    try:
        return getter()
    except NonexistentDocumentException as e:
        return error(404, e)


def post_result(poster, check_token=True):
    if check_token:
        try:
            CausewayToken.parse(request.form['token']).save(request.form['payload'])
        except BadTokenException as e:
            return error(401, e)
        except DocumentQuotaExceeded as e:
            return error(402, e)
    try:
        poster()
        return success(201)
    except ProcessingError as e:
        return error(422, e)
    except NotImplementedError as e:
        return error(501, e)


def get_post_request_result(getter, poster, check_token=True):
    if request.method == 'GET':
        return get_result(getter)
    elif request.method == 'POST':
        return post_result(poster, check_token)


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
        "free_quota": app.config.server.free_quota,
        "description": app.config.server.description
    }
    return json.dumps(server_info)


@app.route('/token')
def request_id():
    """
    A unique ID which identifies a Causeway request.
    """
    try:
        return json.dumps(
            {'token': CausewayToken.new(
                user_id=request.form['user_id']).encoded.decode('utf-8')}
        )
    except NonexistentDocumentException as e:
        return error(401, e)


# JOBS


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    return get_post_request_result(
        getter=lambda: Job.BulkQuery(active_only=False).serialize(),
        poster=lambda: Job.new(request.form['payload'])
    )


@app.route('/jobs/active')
def active_jobs():
    return get_result(
        getter=lambda: Job.BulkQuery(active_only=True).serialize()
    )


@app.route('/jobs/<string:job_id>')
def job_by_id(job_id):
    return get_result(
        getter=lambda: Job.from_database(job_id).serialize()
    )


# BIDS


@app.route('/jobs/<string:job_id>/bids', methods=['GET', 'POST'])
def bids(job_id):
    return get_post_request_result(
        getter=lambda: Job.from_database(job_id).all_bids().serialize(),
        poster=lambda: Job.from_database(job_id).add_bid(request.form['payload'])
    )


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>')
def bid_by_id(job_id, bid_id):
    return get_result(
        getter=lambda: Job.from_database(job_id).get_bid(bid_id).serialize()
    )


# OFFERS


@app.route('/jobs/<string:job_id>/bids/<string:bid_id>/offer', methods=['GET', 'POST'])
@app.route('/jobs/<string:job_id>/offer')
def offer(job_id, bid_id):
    return get_post_request_result(
        getter=lambda: Job.from_database(job_id).bid_offered_to().serialize(),
        poster=lambda: Job.from_database(job_id).get_bid(bid_id).add_offer(request.form['payload'])
    )


# DELIVERY


@app.route('/jobs/<string:job_id>/delivery', methods=['GET', 'POST'])
def delivery(job_id):
    return get_post_request_result(
        getter=lambda: Job.from_database(job_id).get_delivery().serialize(),
        poster=lambda: Job.from_database(job_id).set_delivery(request.form['payload'])
    )


@app.route('/jobs/<string:job_id>/delivery/acceptance', methods=['POST'])
def accept_delivery(job_id):

    def block():
        job = Job.from_database(job_id)
        job.get_delivery().set_accept_delivery(request.form['payload'])
        job.finish()

    return post_result(
        poster=lambda: block()
    )


# DISPUTE


@app.route('/jobs/<string:job_id>/dispute', methods=['GET', 'POST'])
def dispute(job_id):
    return get_post_request_result(
        getter=lambda: Job.from_database(job_id).get_dispute().serialize(),
        poster=lambda: Job.from_database(job_id).set_dispute(request.form['payload'])
    )


@app.route('/jobs/<string:job_id>/dispute/resolution', methods=['POST'])
def resolve_dispute(job_id):
    return post_result(
        poster=lambda: Job.from_database(job_id).get_dispute().set_resolution(request.form['payload'])
    )


@app.route('/jobs/<string:job_id>/dispute/resolution/acceptance', methods=['POST'])
def accept_resolution(job_id):

    def block():
        job = Job.from_database(job_id)
        job.get_dispute().set_accept_resolution(request.form['payload'])
        job.finish()

    return post_result(
        poster=lambda: block()
    )


# USERS


@app.route('/users', methods=['GET', 'POST'])
def users():
    return get_post_request_result(
        getter=lambda: User.BulkQuery().serialize(),
        poster=lambda: User.new(request.form['payload']),
        check_token=False
    )


@app.route('/users/<string:user_id>')
def user_by_id(user_id):
    return get_result(
        getter=lambda: User.from_database(user_id).serialize()
    )


if __name__ == '__main__':
    app.run()
