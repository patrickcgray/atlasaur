#!/usr/bin/python2.5
#
# Copyright 2009 Roman Nurik
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

import copy
import logging
import math
import sys
 
from google.appengine.ext import ndb
 
import geocell
import geomath
import util
 
DEBUG = False
if DEBUG:
    logging.getLogger().setLevel(logging.INFO)
 

def default_cost_function(num_cells, resolution):
   """The default cost function, used if none is provided by the developer."""
   return 1e10000 if num_cells > pow(geocell._GEOCELL_GRID_SIZE, 2) else 0
 
 
-  """A base model class for single-point geographically located entities."""
class GeoModel(object):
  """A model mixin for single-point geographically located entities.
 
   Attributes:
     location: A db.GeoPt that defines the single geographic point
         associated with this entity.
   """
  location = ndb.GeoPtProperty()
  location_geocells = ndb.StringProperty(repeated=True)
 
  def update_location(self):
     """Syncs underlying geocell properties with the entity's location."""
@@ -66,8 +66,8 @@
     else:
       self.location_geocells = []
 
  @classmethod
  def bounding_box_fetch(cls, query, bbox, max_results=1000,
                          cost_function=None):
     """Performs a bounding box fetch on the given query."""
 
@@ -101,7 +101,7 @@
     query_geocells = geocell.best_bbox_search_cells(bbox, cost_function)
 
     if query_geocells:
       for entity in query.filter(cls.location_geocells.IN(query_geocells)):
         if len(results) == max_results:
           break
         if (entity.location.lat >= bbox.south and
@@ -115,8 +115,9 @@
 
     return results
 

  @classmethod
  def proximity_fetch(cls, query, center, max_results=10, max_distance=0):
     """Performs a proximity/radius fetch on the given query.
 
     Fetches at most <max_results> entities matching the given query,"""
@@ -169,7 +170,7 @@
     def _merge_results_in_place(a, b):
       util.merge_in_place(a, b,
                         cmp_fn=lambda x, y: cmp(x[1], y[1]),
                         dup_fn=lambda x, y: x[0].key == y[0].key)
 
     sorted_edges = [(0,0)]
     sorted_edge_distances = [0]
@@ -183,8 +184,7 @@
 
       # Run query on the next set of geocells.
       cur_resolution = len(cur_geocells[0])
       temp_query = query.filter(cls.location_geocells.IN(cur_geocells_unique))
 
       # Update results and sort.
       new_results = temp_query.fetch(1000)