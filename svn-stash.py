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
from svn_stash_register import svn_stash_register,svn_stash,HOME_DIR,CURRENT_DIR,SVN_STASH_DIR,COMMAND_DEFAULT,TARGET_FILE_DEFAULT

def execute_stash_push(target_file,info):
	if len(info['files'])>0:
		#save the svn status into a stash
		stash = svn_stash()
		stash.push(target_file,info)
		register = svn_stash_register()
		register.register_stash(stash)
		register.write()
	else:
		print "nothing to stash in this directory."

def execute_stash_pop(target_file,info):
	#obtain last stash pop
	register = svn_stash_register()
	stash = register.obtain_last_stash()
	if stash:
		stash.pop()
		register.delete_stash(stash)
	else:
		print "there are not previous stashes."

def execute_stash_list(target_file,info):
	#obtain the list of stashes.
	register = svn_stash_register()
	for stash_id in register.stashes:
		print stash_id

def execute_stash_clear(target_file,info):
	#delete all stashes.
	register = svn_stash_register()
	marked_stashes = list(register.stashes)
	for stash in marked_stashes:
		current_stash = svn_stash()
		current_stash.load(stash)
		register.delete_stash(current_stash)

def execute_stash_show(target_file,info):
	#view all diffs of all stashes.
	register = svn_stash_register()
	for stash_id in register.stashes:
		current_stash = svn_stash()
		current_stash.load(stash_id)
		print current_stash

def execute_stash_help(target_file,info):
	b =  "\033[1m"
	end_b = "\033[0m"
	help_content = "SVN STASH\n"
	help_content += "\n" + b + "NAME" + end_b + "\n"
	help_content += "svn-stash - Stash the changes in a dirty working directory away\n"
	help_content += "\n"+ b + "SYNOPSIS" + end_b + "\n"
	help_content +=	"\tsvn stash list\n"
	help_content += "\tsvn stash show\n"
	help_content += "\tsvn stash push\n"
	help_content += "\tsvn stash pop\n"
	help_content += "\tsvn stash clear\n"
	help_content += "\tsvn stash help\n"
	help_content += "\n" + b + "DESCRIPTION" + end_b +"\n"
	help_content += "\tsvn-stash permits you to hide the changes that you don't want to commit just now. this can be more useful in some circumstances.\n"
	print help_content


#Parser order and file of the command
def execute_svn_stash(command,target_file,info):
	#print command+","+target_file
	if command == "push":
		execute_stash_push(target_file,info)
	elif command == "pop":
		execute_stash_pop(target_file,info)
	elif command == "list":
		execute_stash_list(target_file,info)
	elif command == "clear":
		execute_stash_clear(target_file,info)
	elif command == "show":
		execute_stash_show(target_file,info)
	elif command == "help":
		execute_stash_help(target_file,info)

#obtain the svn status files
def obtain_svn_status_files(dir):
	status_files = [] 
	flags = {}
	if dir == TARGET_FILE_DEFAULT:
		dir = "."
	status_list = os.popen('svn st "' + '" "'.join(dir) +'"').read()
	status_list = status_list.split("\n")
	for line in status_list:
		words = line.split()
		if len(words) > 1:
			elements = line.split()
			status = elements[0]
			filename = elements[1]
			if os.path.isdir(filename) and filename[:-1] != '/':
				filename = filename + "/"
			if status == "M" or status == "A" or status == "D":
				flags[filename] = status
				status_files.append(filename)
	return {'files': status_files, 'flags': flags}

def main(args):
	command = COMMAND_DEFAULT
	if len(args)>1:
		command = args[1]

	files = ["."]
	if len(args)>2:
		files = args[2:]

	info = obtain_svn_status_files(files)
	execute_svn_stash(command,TARGET_FILE_DEFAULT,info)


if __name__ == '__main__':
    main(sys.argv)
