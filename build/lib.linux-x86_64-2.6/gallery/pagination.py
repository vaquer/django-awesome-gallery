#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################
#                           vamosleones.cl                           #
######################################################################
# Copyright (c) 2009 Dale Ideas Ltda.                                #
# All rights reserved.                                               #
######################################################################
# THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF DALE IDEAS LTDA.    #
# The copyright notice above does not evidence any actual or         #
# intended publication of such source code.                          #
######################################################################
# ESTE ES CODIGO FUENTE PROPIETARIO NO PUBLICADO DE DALE IDEAS LTDA. #
# El aviso de copyright expuesto arriba no evidencia ninguna         #
# publicación real o prevista de tal código fuente.                  #
######################################################################
##
# Pagination Class - Contains all the function used in pagination
# 
# author: Roberto Alamos Moreno & Ed Vincent Geronilla<br />
# copyright: Copyright © 2010 Dale Ideas Ltda. <br />
# contact: ralamosm@daleideas.cl <br />
##

from django.core.paginator import Paginator, InvalidPage, Page

class UberPaginator(Paginator):
	def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
		super(UberPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
	
	def page(self, number):
		"Returns a Page object for the given 1-based page number. Modified to return an slightly modified Page object"
		try:
			number = self.validate_number(number)
		except:
			raise
		bottom = (number - 1) * self.per_page
		top = bottom + self.per_page
		if top + self.orphans >= self.count:
			top = self.count
		return UberPage(self.object_list[bottom:top], number, self)

class UberPage(Page):
	def __init__(self, object_list, number, paginator):
		self.neighborhood_len = 3
		super(UberPage, self).__init__(object_list, number, paginator)
	
	def neighborhood(self):
		# Neighborhood is trivial, near edges
		if self.number == 1:
			min_edge = 1
			max_edge = self.neighborhood_len
		elif self.number == self.paginator.num_pages:
			min_edge = self.paginator.num_pages - self.neighborhood_len
			max_edge = self.paginator.num_pages + 1
		else:
			# Neighbordhood is not trivial
			min_edge = self.number - self.neighborhood_len
			max_edge = self.number + self.neighborhood_len - 1
			
			if min_edge < 0:
				min_edge = 1
			if max_edge > self.paginator.num_pages:
				max_edge = self.paginator.num_pages
			
		nb = range(min_edge, max_edge + 1)
		
		# Get lower end
		lower_end = None
		if min_edge < 5:
			min_edge = 1
			nb = range(min_edge, max_edge + 1)
		else:
			lower_end = [1,2]
		
		# Get high end
		high_end = None
		if max_edge > (self.paginator.num_pages - 4):
			nb = range(min_edge, self.paginator.num_pages + 1)
		else:
			high_end = [self.paginator.num_pages - 1, self.paginator.num_pages]
		
		return { 'left': lower_end, 'center': nb, 'right': high_end }



class Pagination(Paginator):
	def __init__(self, page_list, num_per_page, current_page):
		#GLOBAL DECLARATION
		self.page_list = page_list #the list of items
		self.current_page = current_page #the current page of the
		self.object_list_prev = [] #output list previous
		self.object_list_cent = [] #output list center
		self.object_list_next = [] #output list next
		#NEXT PAGE DECLARATION
		self.p = Paginator(page_list, num_per_page)
		self.page_count = self.p.num_pages
		self.last_cur_page = self.page_count - current_page
		#COUNTERS
		self.ctr_start_0 = 0
		self.ctr_start_1 = 1
		self.ctr_start_9 = 9
		self.ctr_start_11 = 11
		self.ctr_last_min_4 = self.page_count - 4
		self.ctr_last_min_7 = self.page_count - 7
		self.ctr_last_min_9 = self.page_count - 9
		self.ctr_center_start = current_page - 3
		self.paginator = Paginator(page_list, num_per_page)
	def count(self):
		return self.paginator.count
		
	def page(self, cur_page):
		return self.paginator.page(cur_page)
		
	def num_pages(self):
		return self.paginator.num_pages	
			
	def prev_pages(self):
		while self.ctr_start_1 <= 11:
			self.object_list_prev.append(self.ctr_start_1)
			self.ctr_start_1 += 1
		if self.current_page >= 9:
			while self.ctr_start_11 > 2:
				self.object_list_prev.pop()
				self.ctr_start_11 -= 1
			return self.object_list_prev
		if self.current_page <= 4:
			while self.ctr_start_11 > 7:
				self.object_list_prev.pop()
				self.ctr_start_11 -= 1
			return self.object_list_prev
		if self.current_page >= 5 and self.current_page <= 9:
			while self.ctr_start_11 > (self.current_page + 3):
				self.object_list_prev.pop()
				self.ctr_start_11 -= 1
			return self.object_list_prev
	def next_pages(self):
		while self.ctr_last_min_9 <> self.page_count + 1:
			self.object_list_next.append(self.ctr_last_min_9)
			self.ctr_last_min_9 += 1
		if self.current_page <= self.ctr_last_min_7:
			self.object_list_next.reverse()
			while self.ctr_start_9 >= 2:
				self.object_list_next.pop()
				self.ctr_start_9 -= 1
			self.object_list_next.reverse()
			return self.object_list_next
		if self.current_page >= self.ctr_last_min_4:
			self.object_list_next.reverse()
			while self.ctr_start_9 > 7:
				self.object_list_next.pop()
				self.ctr_start_9 -= 1
			self.object_list_next.reverse()
			return self.object_list_next
		if self.current_page > self.ctr_last_min_7 and self.current_page < self.ctr_last_min_4:
			self.object_list_next.reverse()
			while self.ctr_start_9 > self.last_cur_page + 3:
				self.object_list_next.pop()
				self.ctr_start_9 -= 1
			self.object_list_next.reverse()
			return self.object_list_next
	def cent_pages(self):
		while self.ctr_start_0 <= 6:
			self.object_list_cent.append(self.ctr_center_start + self.ctr_start_0)
			self.ctr_start_0 += 1
		return self.object_list_cent
