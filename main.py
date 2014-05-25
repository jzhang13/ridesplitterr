#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from google.appengine.ext import db

import datetime


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Rides(db.Model):
	pickup_datetime = db.DateTimeProperty(required = True)
	location = db.StringProperty(required = True)
	destination = db.StringProperty(required = True)
	riders = db.ListProperty(str, default = None, required = True)
	numbers = db.ListProperty(str, default = None, required = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
    	self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)
    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		self.render("index.html")

class Browse(Handler):
	def get(self):
		rides = db.GqlQuery("select * from Rides order by pickup_datetime asc")
		self.render("browse.html", rides=rides)
	def post(self):
		create_ride = self.request.get("create_ride_button")
		join_ride = self.request.get("join_ride_button")
		if create_ride:
			self.create_ride()
		elif join_ride:
			self.join_ride()
		else:
			self.write("error")

	def create_ride(self):
		date_parts = self.request.get("date")
		time_parts = self.request.get("time")
		location = self.request.get("location")
		destination = self.request.get("destination")
		name = self.request.get("name")
		phone = self.request.get("phone")
		if date_parts and time_parts and location and destination and name and phone:
			date_parts_list = date_parts.split('-')
			time_parts_list = time_parts.split(':')
			if(date_parts_list < 1900):
				error = "invalid year"
				
			pickup_datetime = datetime.datetime(int(date_parts_list[0]), int(date_parts_list[1]), int(date_parts_list[2]), int(time_parts_list[0]), int(time_parts_list[1]))
			r = Rides(pickup_datetime=pickup_datetime, location=location, destination=destination)
			r.riders.append(name)
			r.numbers.append(phone)
			r.put()
			self.redirect('/browse')
		else:
			self.write("error")

	def join_ride(self):
		join_name = self.request.get("join_name")
		join_number = self.request.get("join_number")
		ride_id = self.request.get("get_ride_id")
		r = Rides.get_by_id(int(ride_id))
		r.riders.append(join_name)
		r.numbers.append(join_number)
		r.put()
		self.redirect('/browse')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/browse', Browse)],
                              debug=True)