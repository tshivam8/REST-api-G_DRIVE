from django.shortcuts import render
import csv
from django.http import QueryDict
import json
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
import os
from pathlib import Path



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class FileDeleteRet(APIView):
	parser_class = (FileUploadParser, )

	#retrieve
	def get(self, request, *args, **kwargs):
		fn = kwargs['fname']
		try:
			s=0
			e=0
			t=1
			pwd = os.path.dirname(BASE_DIR+r'/uploads/')
			with open('metadata.csv') as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=',')
				for row in csv_reader:
					try:

						if(row[0]==fn):
							s=row[1]
							e=row[2]
							break
					except:
						pass
			s=int(s)
			e=int(e)
			file_content=""
			if(e<s):
				e=e+4
			for i in range(s,e+1):

				if(i>4):
					i=i%4
				destination = open(pwd+"/node_"+str(i) +"/"+ fn+"_"+str(t), 'r')
				file_content = file_content + destination.read()
				t = t + 1

			return Response(file_content, status.HTTP_200_OK,content_type="application/octet-stream")
		except:
			return Response("requested object "+ fn + " is not found", status=404,content_type="text/plain")


		
		'''try:
			pwd = os.path.dirname(BASE_DIR+r'/uploads/')
			file = open(pwd + '/'+fn.strip("\"\"")).read()
			return Response(file, status.HTTP_200_OK,content_type="application/octet-stream")
		except:
			return Response("requested object "+ fn + " is not found", status=404,content_type="text/plain")'''
	#delete
	def delete(self,request,*args, **kwargs):
		try:
			fn = kwargs['fname'].strip("\"\"")
			#QueryDict(request.body)[" name"][11:].split("\r")[0]
			s=0
			e=0
			t=1
			
			pwd = os.path.dirname(BASE_DIR+r'/uploads/')
			
			with open('metadata.csv') as csv_file:

				csv_reader = csv.reader(csv_file, delimiter=',')

				for row in csv_reader:
					try:
						if(row[0]==fn):
							s=row[1]
							e=row[2]
							break
					except:
						pass
			
			s=int(s)
			e=int(e)
			if(e<s):
				e=e+4
			for i in range(s,e+1):
				if(i>4):
					i=i%4
				os.remove(pwd+"/node_"+str(i) +"/"+ fn+"_"+str(t))
				t = t + 1

			try:
				os.remove(pwd+'/'+fn)
			except:
				pass
			return Response('object '+fn +' deleted successfully', status.HTTP_200_OK,content_type="text/plain")
		except Exception as e:
			return Response(" Requested object "+ fn + " is not found to be deleted\n"+str(e), status=404,content_type="text/plain")

class FileUploadView(APIView):
	parser_class = (FileUploadParser, )

	#list
	def get(self, request, *args, **kwargs):
		pwd = os.path.dirname(BASE_DIR+r'/uploads/')
		#img_list =os.listdir(pwd)
		img_list=[f for f in os.listdir(pwd) if os.path.isfile(os.path.join(pwd, f))]
		l=list()
		for fi in img_list:
			d= dict()
			d["file_name"]=fi
			d["id"]=fi
			l.append(d)
		return Response(l, status.HTTP_200_OK,content_type="application/json")

	#upload
	def put(self, request, *args, **kwargs):
		f=request.FILES['file']
		pwd = os.path.dirname(BASE_DIR+r'/uploads/')
		my_file = Path(pwd+"/"+f.name.strip("\"\""))
		if my_file.is_file():
			return Response("File Already Exists", status=409,content_type="text/plain")

		destination = open(pwd+"/" + f.name, 'wb+')
		for chunk in f.chunks():
			destination.write(chunk)
		destination.close()
		
		np = open(BASE_DIR+"/node_pos.txt", "r")
		i=int(np.read())
		initial_node=i
		chunk = True
		t=1

		f.file.seek(0)
		while chunk:
			chunk = f.file.read(1024).strip().strip(b"\n")
			destination = open(pwd+"/node_"+str(i) +"/"+ f.name+"_"+str(t), 'wb+')
			destination.write(chunk+b'\n')
			destination.close()
			i=(i+1)%5
			if(i==0):
				i=1
			t=t+1
		
		np = open(BASE_DIR+"/node_pos.txt", "w")
		np.write(str(i))
		np.close()


		with open('metadata.csv','a') as newFile:
			newFileWriter = csv.writer(newFile)
			newFileWriter.writerow([f.name,initial_node,i-1])

		return Response(f.name, status.HTTP_200_OK,content_type="text/plain")

