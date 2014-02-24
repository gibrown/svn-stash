#    This file is part of svn-stash.

#    svn-stash is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    svn-stash is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with svn-stash.  If not, see <http://www.gnu.org/licenses/>.

import os,sys
import random
from datetime import datetime

HOME_DIR = os.path.expanduser("~")
CURRENT_DIR = os.getcwd()
SVN_STASH_DIR= HOME_DIR + "/.svn-stash"
COMMAND_DEFAULT="push"
TARGET_FILE_DEFAULT="all"
STASH_REGISTER_FILENAME = ".stashed_register"

class svn_stash_register:
	"""A class to register all stashes."""
	def __init__(self):
		self.stashes = [] #list of stashes in the current dir
		self.all_stashes = [] #list of all stashes in all directories
		self.load() #load register

	def load(self):
		try:
			create_stash_dir_if_any()
			current_dir = SVN_STASH_DIR + "/" + STASH_REGISTER_FILENAME
			with open(current_dir,"r") as f:
				for line in f:
					content = line.rstrip()
					content = content.split(" ")
					if len(content)>0:
						stash_id = content[0]
						if is_a_current_stash(stash_id):
							self.stashes.append(stash_id)
						self.all_stashes.append(stash_id)
				f.close()
		except IOError as e:
			print e
			print 'registerFile cannot be readed.'

	def write(self):
		try:
			create_stash_dir_if_any()
			current_dir = SVN_STASH_DIR + "/" + STASH_REGISTER_FILENAME
			with open(current_dir,"w") as f:
				content = []
				for stash_id in self.all_stashes:
					line = str(stash_id) + "\n"
					content.append(line)
				f.writelines(content)
				f.close()
		except IOError as e:
			print 'registerFile cannot be created.'

	def obtain_last_stash(self):
		length = len(self.stashes)
		if length>0:
			stash = svn_stash()
			stash_id = self.stashes[length-1]
			stash.load(stash_id)
			return stash
		return False

	def register_stash(self,stash): #stash must be a svn-stash instance
		stash_id = stash.key
		self.stashes.append(stash_id)
		self.all_stashes.append(stash_id)
		stash.write()
		print "create stash " + str(stash_id)

	def delete_stash(self,stash):
		stash_id = stash.key
		self.stashes.remove(stash_id)
		self.all_stashes.remove(stash_id)
		self.write()
		#Remove stash files
		stash.clear()
		print "delete stash " + str(stash_id)

class svn_stash:
	"""A class to contain all information about stashes."""
	def __init__(self):
		self.files = {} #dictionary of files
		self.timestamp = datetime.now() #time of creation
		self.key = random.getrandbits(128) #unique identifier
		self.root_url = CURRENT_DIR

	def push(self,target_file,info):
		filename_list = info['files']
		flags = info['flags']
		filename_list = sorted(filename_list)
		filename_list.reverse()
		create_stash_dir_if_any()
		if target_file == "all":
			for filename in filename_list:
				self.push(filename,info)
		else:
			randkey = random.getrandbits(128) #unique identifier
			self.files[target_file] = randkey
			print "push " + target_file + "->" + str(randkey)
			if os.path.isfile(target_file) or os.path.isdir(target_file):
				result = os.popen("svn diff " + target_file + " > " + SVN_STASH_DIR + "/" + str(randkey) + ".stash.patch").read()
				result += os.popen("svn revert " + target_file).read()
				if flags[target_file] == 'A':
					if os.path.isfile(target_file):
						result += os.popen("rm " + target_file).read()
					if os.path.isdir(target_file):
						result += os.popen("rmdir " + target_file).read()
				if flags[target_file] == 'D':
					if os.path.isdir(target_file):
						result += os.popen("mkdir " + target_file).read()
			# print "push end: " + target_file + "->" +  ", ".join(filename_list)

	def pop(self):
		result = ""
		if os.path.exists(SVN_STASH_DIR):
			file_list = self.file_list
			for target_file in file_list:
				randkey  = self.files[target_file]
				filepath = SVN_STASH_DIR + "/" + str(randkey) + ".stash.patch"
				print 'pop: ' + target_file + "->" + filepath
				if os.path.isfile(filepath):
					if os.stat(filepath).st_size == 0 and not os.path.isdir(target_file):
						result  = os.popen("mkdir " + target_file).read()
						result  = os.popen("svn add " + target_file).read()
						# print "added dir " + target_file
					elif not os.path.isfile(target_file):
						result  = os.popen("touch " + target_file).read()
						result  = os.popen("patch -p0 <" + filepath).read()
						result  = os.popen("svn add " + target_file).read()
						# print "added file " + target_file
					else:
						result  = os.popen("svn patch " + target_file).read()
						print "patched file " + target_file
						# print "pop " + target_file
				else:
					print 'Patch file cannot be found: ' + target_file + "->" + filepath

	def write(self):
		#Create file for svn stash
		try:
			current_dir = SVN_STASH_DIR + "/" + str(self.key)
			with open(current_dir,"w") as f:
				content = []
				#add the first line with root url
				line = self.root_url + "\n"
				content.append(line)
				for target_file in self.files:
					line = target_file + " " + str(self.files[target_file]) + "\n"
					content.append(line)
				f.writelines(content)
				f.close()
		except IOError as e:
			print 'randFile cannot be created.'

   	def clear(self):
		result = ""
		if os.path.exists(SVN_STASH_DIR):
			for target_file in self.files:
				randkey  = self.files[target_file]
				filepath = SVN_STASH_DIR + "/" + str(randkey) + ".stash.patch"
				if os.path.isfile(filepath):
					result += os.popen("rm " + filepath).read()
				else:
					print 'randFile cannot be found.'
			filepath = SVN_STASH_DIR + "/" + str(self.key)
			if os.path.isfile(filepath):
				result += os.popen("rm " + filepath).read()
			else:
				print 'registerFile cannot be found.'

	def load(self,stash_id):
		try:
			current_dir = SVN_STASH_DIR + "/" + str(stash_id)
			with open(current_dir,"r") as f:
				is_first = True
				for line in f:
					content = line.rstrip()
					#if is the first line, then it is the root url
					if is_first:
						self.root_url = content
						is_first = False
					#it is stashed filename, otherwise
					else:
						content = content.split(" ")
						if len(content)>=2:
							self.files[content[0]] = content[1]
				self.key = stash_id
				f.close()
			self.file_list = self.files.keys()
			self.file_list = sorted(self.file_list)
		except IOError as e:
			print 'randFile cannot be readed.'

	def __str__(self):
		content = print_hr(70)
		content += "stash " + str(self.key)
		content += print_hr(70)
		content += "root in: <" + self.root_url + ">\n"
		for filename in self.file_list:
			try:
				real_dir =   self.files[filename] + ".stash.patch"
				current_dir = SVN_STASH_DIR + "/" + self.files[filename] + ".stash.patch"
				content += print_hr()
				content += "file " + real_dir
				content += print_hr()
				if os.stat(current_dir).st_size == 0:
					content += "Mkdir: " + filename + "\n"
				else:
					with open(current_dir,"r") as f:
						for line in f:
							content += line
						f.close()
			except IOError as e:
				content += 'randFile cannot be shown.\n'
		return content


########################
#Auxiliar functions    #
########################
#Create stash directory
def create_stash_dir_if_any():
	if not os.path.exists(SVN_STASH_DIR):
		os.makedirs(SVN_STASH_DIR)
	stash_register_file = SVN_STASH_DIR + "/" + STASH_REGISTER_FILENAME
	if not os.path.exists(stash_register_file):
		try:
			f = open(stash_register_file, "w")
		except IOError:
			print "registerFile cannot be created."

def print_hr(lng=30):
	return "\n" + ("-"*lng) + "\n"

def is_a_current_stash(stash_id):
	stash = svn_stash()
	stash.load(stash_id)
	current_dir_parts = CURRENT_DIR.split("/")
	stash_dir_parts = stash.root_url.split("/")
	stash_dir_parts = stash_dir_parts[:len(current_dir_parts)]
	stash_dir = "/".join(stash_dir_parts)
	if ".svn" in os.listdir(CURRENT_DIR):
		return stash_dir == CURRENT_DIR
	return False