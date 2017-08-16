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
	color = ndb.StringProperty()


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

			if 'color' in req_body:
				new_car.color = req_body['color']

			new_car.put()
			new_car.id = str(new_car.key.urlsafe())
			new_car.put()

			car_dict = new_car.to_dict()
			car_dict['kind'] = new_car.key.kind()
			car_dict['self'] = '/cars/' + new_car.key.urlsafe()

			self.response.write(json.dumps(car_dict))

		else:
			self.response.write('Provide the correct parameters.')
			self.abort(400)


	def get(self, email=None):
		car_data = car.query(car.email == email).fetch()
		car_dict = {
			"kind": "collection",
			"cars": []
		}

		for x in car_data:
			x_dict = x.to_dict()
			x_dict["kind"] = "car"
			x_dict["self"] = '/cars/' + x.key.urlsafe()
			car_dict["cars"].append(x_dict)

		self.response.write(json.dumps(car_dict))


	def patch(self, car_id=None):

		if car_id:
			req_body = json.loads(self.request.body)
			car_entity = ndb.Key(urlsafe=car_id).get()

			if len(req_body) <= 4:

				if 'make' in req_body:
					car_entity.make = req_body['make']
				else:
					car_entity.make = None

				if 'model' in req_body:
					car_entity.model = req_body['model']
				else:
					car_entity.model = None

				if 'year' in req_body:
					car_entity.year = req_body['year']
				else:
					car_entity.year = None

				if 'color' in req_body:
					car_entity.color = req_body['color']
				else:
					car_entity.color = None

				car_entity.put()

				car_dict = car_entity.to_dict()
				car_dict['kind'] = ndb.Key(urlsafe=car_id).kind()
				car_dict['self'] = '/cars/' + car_entity.key.urlsafe()

				self.response.write(json.dumps(car_dict))

			else:
				self.response.write('Too many fields given')
				self.abort(400)
		else:
			self.response.write('Person\'s car id must be provided in parameters')
			self.abort(400)


	def delete(self, car_id=None):

		if car_id:
			ndb.Key(urlsafe=car_id).delete()
			self.response.set_status(204)



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
    ('/users/(.*)/cars', carHandler),
	('/cars/(.*)', carHandler),
], debug=True)


app.error_handlers[400] = handle_400
