import os, sys, re, shutil

#ArmaBriefingConversion
#https://github.com/firefly2442/ArmaBriefingConversion


#python run.py ./mymissions/ ./myconvertedmissions/

#these tags will be removed from the briefing.html file
html_tag_remove = ["<h2>", "</h2>", "<h6>", "</h6>", "<p>", "</p>", "<hr>", "<b>", "</b>"]
#these tags will be found and replaced from the briefing.html file
html_tag_find = ["<br>"]
html_tag_replace = ["<br/>"]

def parseBriefing(directory, output, briefing_names):
	#Open briefing.html for reading
	for briefing in briefing_names:
		if os.path.isfile(directory + "/" + briefing):
			with open(directory + "/" + briefing, "r") as briefingHTML:
				all_lines = briefingHTML.read()

	#remove any HTML tag specified above
	for tag in html_tag_remove:
		all_lines = all_lines.replace(tag, "")
	#replace any HTML tag specified above
	for i in range(0, len(html_tag_find)):
		all_lines = all_lines.replace(html_tag_find[i], html_tag_replace[i])

	#Python doesn't support variable length lookbehinds so we need to do
	#some trickery to get around possible spaces that could occur in the regexes
	all_lines = all_lines.replace('<a name = "', '<a name="')
	all_lines = all_lines.replace('<a name ="', '<a name="')
	all_lines = all_lines.replace('<a name= "', '<a name="')

	#This website is useful for developing regular expressions
	#http://gskinner.com/RegExr/

	#TODO: this title regex needs to be fixed so it works across multiple lines
	title = re.search(r'(?<=<title>)(.*)(?=<\/title>)', all_lines).group()
	#print "Title: " + title

	main = re.search(r'(?<=<a name="[M|m]ain">).*(?=\<a name="[P|p]lan">)', all_lines, re.DOTALL|re.MULTILINE)
	if main:
		main = cleanHTMLComments(main.group())
	else:
		main = "Empty main section.\n"
	
	plan = re.search(r'(?<=<a name="[P|p]lan">).*(?=\<a name="OBJ_1")', all_lines, re.DOTALL|re.MULTILINE)
	if plan:
		plan = cleanHTMLComments(plan.group())
		regex = re.compile(r'<a href="marker:(.*?)">(.*?)</a>', re.DOTALL|re.MULTILINE)
		plan = regex.sub(r"<marker name = '\1'>\2</marker>", plan)
		#TODO: optional
		# search and find MySection groups (may not exist)
		# add these as additional diary entries
	else:
		plan = "Empty plan section.\n"

	number_objs = len(re.findall(r'(?<=<a name="OBJ_)(\d)', all_lines))
	#print "Number objectives: " + str(number_objs)

	objs = []
	for i in range(1, number_objs+1):
		if "OBJ_"+str(i) in all_lines: #make sure the objective exists before searching for it
			objs.append(re.search(r'(?<=<a name="OBJ_' + str(i) + '"></a>).*', all_lines).group())
	
	number_debriefings = len(re.findall(r'(?<=<a name="[D|d]ebriefing:End)(\d)', all_lines))
	#print "Number endings: " + str(number_debriefings)

	debriefings = []
	for i in range(1, number_debriefings+1):
		if i < number_debriefings:
			debriefings.append(re.search(r'(<a name="[D|d]ebriefing:End' + str(i) + ')(.*)(?=\<a name="[D|d]ebriefing:[E|e]nd' + str(i+1) + ')', all_lines, re.DOTALL|re.MULTILINE).group())
		else: #last debrief, use special regex
			#TODO: this last one could have more than just the final debrief
			# what would be a good way to process this?
			debriefings.append(re.search(r'(<a name="[D|d]ebriefing:End' + str(i) + ')(.*)', all_lines, re.DOTALL|re.MULTILINE).group())

	briefingHTML.close()

	writeBriefingSQF(output, main, plan, objs)
	writeDebriefingHTML(output, title, debriefings)
	writeInitSQF(directory, output)

def writeInitSQF(directory, output):
	#copy the file over, if it exists already
	if os.path.isfile(directory + "/init.sqf"):
		shutil.copyfile(directory+"/init.sqf", output+"/init.sqf")
	#append to end of file, if the file doesn't exist it will be created
	with open(output + "/init.sqf", "a") as init:
		init.write("//auto-generated by ArmaBriefingConversion\n\n")
		init.write('[] execVM "briefing.sqf";')


def writeBriefingSQF(output, main, plan, objs):
	#Open briefing.sqf for writing
	briefingSQF = open(output + "/briefing.sqf", "w")

	briefingSQF.write("//auto-generated by ArmaBriefingConversion\n\n")

	briefingSQF.write('player createDiaryRecord ["Diary", ["Diary", "' + main + '"]];\n')
	briefingSQF.write('player createDiaryRecord ["Diary", ["Mission", "' + plan + '"]];\n')

	# go through objectives, need to be in reverse order so they display correctly
	# this is just a quirk of Arma
	briefingSQF.write('// tasks need to be in reversed order\n')
	for i in reversed(range(len(objs))):
		briefingSQF.write('objective'+str(i+1)+' = player createSimpleTask ["' + objs[i] + '"];\n')
		briefingSQF.write('objective'+str(i+1)+' setSimpleTaskDescription ["' + objs[i] + '", "' + objs[i] + '", "' + objs[i] + '"];\n')

	briefingSQF.close()



def writeDebriefingHTML(output, title, debriefings):
	#Open briefing.html for writing
	new_debrief = open(output + "/briefing.html", "w")

	new_debrief.write("<html><head><title>"+title+"</title></head><body>\n")
	new_debrief.write("<! --- Generated by ArmaBriefingConversion>\n\n")

	for entry in debriefings:
		new_debrief.write(entry+"\n")

	new_debrief.close()



def cleanHTMLComments(string):
	return re.sub(r'(<! ---)(.*?)>', '', string)



if len(sys.argv) <= 2:
	print "You didn't specify an input folder and output folder."
	sys.exit(0)
else:
	folder = sys.argv[1]
	output = sys.argv[2]

if not os.path.isdir(folder) or not os.path.isdir(output):
	print "The input or output locations are not folders."
	sys.exit(0)

#Check if output folder is empty, fail if not
if os.listdir(output):
	print "The output directory is not empty, clear it out first."
	sys.exit(0)

print "Recursively searching: " + folder

for root, dirnames, filenames in os.walk(folder):
	#print root
	#print dirnames
	#print filenames

	subsection = root[len(folder):]
	#print "Subsection: " + subsection

	briefing_names = ["briefing.html", "Briefing.html", "briefing.HTML", "Briefing.HTML"]

	for filename in filenames:
		if filename in briefing_names:
			print "Found briefing in: " + root
			parseBriefing(root, output+subsection, briefing_names)
		elif filename == "init.sqf":
			pass #do nothing, will be parsed later
		else:
			#print filename
			#copy file to appropriate directory
			shutil.copyfile(root + "/" + filename, output + subsection + "/" + filename)
	for dir in dirnames:
		#print "DIR: " + dir
		#create folder in appropriate directory
		os.makedirs(output + subsection + "/" + dir)
