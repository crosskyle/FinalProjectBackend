# Author: Kyle Cross
# Date: 7/13/17
# Description: A REST API that stores boat and slip data in a Google Cloud datastore

from google.appengine.ext import ndb
import webapp2
import json


class car(ndb.Model):
	id = ndb.StringProperty()
	email = ndb.StringProperty(required=True)
	make = ndb.StringProperty()
	model = ndb.StringProperty()
	year = ndb.IntegerProperty()


class carHandler(webapp2.RequestHandler):

	def post(self, email=None):
		req_body = json.loads(self.request.body)

		if email:
			new_car = car(email=email)

			if 'make' in req_body:
				new_car.make = req_body['make']

			if 'model' in req_body:
				new_car.model = req_body['model']

			if 'year' in req_body:
				new_car.year = req_body['year']

			new_car.put()
			new_car.id = str(new_car.key.urlsafe())
			new_car.put()

			car_dict = new_car.to_dict()
			car_dict['kind'] = new_car.key.kind()
			car_dict['self'] = '/cars/person/' + str(email) + '/car/' + new_car.key.urlsafe()

			self.response.write(json.dumps(car_dict))

		else:
			self.response.write('Provide the correct parameters.')
			self.abort(400)

	def get(self, email=None):
		car_data = car.query(car.email == email).fetch()
		car_dict = {
			"cars": []
		}

		for x in car_data:
			x_dict = x.to_dict()
			x_dict["kind"] = "car"
			x_dict["self"] = '/cars/person/' + str(email) + '/car/' + x.key.urlsafe()
			car_dict["cars"].append(x_dict)

		self.response.write(json.dumps(car_dict))


	def patch(self, email=None, car_id=None):
		print email, car_id

		if email and car_id:
			req_body = json.loads(self.request.body)
			car_entity = ndb.Key(urlsafe=car_id).get()

			if len(req_body) <= 3:

				if 'make' in req_body:
					car_entity.make = req_body['make']

				if 'model' in req_body:
					car_entity.model = req_body['model']

				if 'year' in req_body:
					car_entity.year = req_body['year']

				car_entity.put()

				car_dict = car_entity.to_dict()
				car_dict['kind'] = ndb.Key(urlsafe=car_id).kind()
				car_dict['self'] = '/cars/person/' + str(email) + '/car/' + car_entity.key.urlsafe()

				self.response.write(json.dumps(car_dict))

			else:
				self.response.write('Too many fields given')
				self.abort(400)
		else:
			self.response.write('Person\'s email and car id must be provided in parameters')
			self.abort(400)



class MainPage(webapp2.RequestHandler):

	def get(self):
		self.response.write("A REST API for storing car data.")


def handle_400(request, response, exception):
	response.set_status(400)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods


app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/cars/person/(.*)/car/(.*)', carHandler),
    ('/cars/person/(.*)', carHandler),
], debug=True)


app.error_handlers[400] = handle_400
