#!/usr/bin/python
# coding: cp949
# Copyright Jon Berg , turtlemeat.com
# Modified by nikomu @ code.google.com    
# Modified by gkdlepdj@mail.com 
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket 
import os # os. path
import urllib

page_tpl = """
<!DOCTYPE html>
<html>
<head>
    <title>FILE</title>
    <meta charset="euc-kr" />
<style type="text/css">  
div.list {
    margin: 100px 10%% 100px; 
            padding: 0px 0px 0px; 
    
}
table {
    width:100%%;
    font-family: '나눔고딕',NanumGothic;
    font-size: 12px;  
    border-collapse: collapse;
    border-spacing: 0;
}
table, th, td {
    border-bottom-style: solid;
    border-bottom-width: 1px;
    border-bottom-color: #cfcfcf;
    
}
th, td {
    padding: 5px;
    text-align: left;
}


table#t01 tr:nth-child(even) {
    background-color: white;
}
table#t01 tr:nth-child(odd) {
   background-color:#fbfbfb;
}
table td#tdsize {
   text-align: right;
}
table th#thsize {
   text-align: right;
} 
table#t01 th    {
    border-top-style: solid;
    border-top-width: 2px;
    border-top-color: #555555;
    background-color: #f0f0f0;
    color: black;
}
table#t01 tr:hover {
    background-color: #efac30;
}
</style>
</head>    
<body>
<div class='list'>
<p><h3>%s</h3></p>
<table id="t01" >
  <tr>
    <th>번호</th>
    <th>이름</th>       
    <th id = 'thsize'>크기</th>
    <th>최종수정일</th>
  </tr>
  %s  
</table>
</div>
</body>
</html>""" 

CWD = os.path.abspath('.')
## print CWD

# PORT = 8080     
UPLOAD_PAGE = 'upload.html' # must contain a valid link with address and port of the server     s

def byte_to_unit(n):
    if n > 1024*1024*1024:
        return "%.2fGB" % (float(n)/(1024*1024*1024))
    if n > 1024*1024:
        return "%.1fMB" % (float(n)/(1024*1024))
    if n > 1024:
        return "%.1fKB" % (float(n)/(1024))
    return "%dB" % n
def make_index( path,relpath):     
    abspath = os.path.abspath(relpath)
    flist = os.listdir( abspath )  #; print flist
    rellist = []
    for fname in flist :     
        relname = os.path.join( relpath, fname)
        relname = relname.encode("euckr")
        rellist.append(relname)

    inslist = []
    insert_string ="<tr><td>{0}</td><td><a href='{1}'>{2}</a></td><td id='tdsize'>{3}</td><td>{4}</td></tr>"
    for i,r in  enumerate( rellist ) : 
        n = os.path.getsize(r)
        filestat = os.stat(r)
        file_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime( filestat.st_mtime )   )
        file_size = byte_to_unit( n )   
        if os.path.isdir(r):
            file_display_name =  '[ '+os.path.split(r)[1]+' ]'
        else :
            file_display_name = os.path.split(r)[1] 
        if path[-1]=='/':
            urlpath = path +  os.path.split(r)[1] 
        else:
            urlpath = path + "/" + os.path.split(r)[1] 
        inslist.append( insert_string.format(i+1,urlpath,file_display_name,file_size,file_update_time) )
  
    ret = page_tpl % ( abspath.encode("cp949"),"\n".join(inslist))
    return ret

def localpath_to_urlpath(s):
    return s.replace("\\","/")
def urlpath_to_localpath(s):
    return s.replace("/","\\")
# -----------------------------------------------------------------------

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            print "self.path #==> : " + self.path
            mypath = '.' + urllib.url2pathname(self.path)
            # print "mypath    #==> : " + mypath
            # mypath = urlpath_to_localpath(mypath)
            # print "mypath    #==> : " + mypath
            mypath = mypath.decode("utf8")
            abspath = os.path.abspath( mypath )            
            print "mypath    #==> : " + mypath
            print "abspath   #==> : " + abspath

            if os.path.isdir(abspath):
                page = make_index( self.path,mypath )
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(page)
                return     

            if self.path.endswith(".html"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
                
            if self.path.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return

            #else : # default: just send the file     
            if os.path.isfile(abspath):   
                filepath = abspath
                f = open( os.path.join(CWD, filepath), 'rb' )
                self.send_response(200)
                self.send_header('Content-type',	'application/octet-stream')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            return # be sure not to fall into "except:" clause ?       
                
        except IOError as e :  
            # debug     
            print e
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        # global rootnode ## something remained in the orig. code     
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))     

            if ctype == 'multipart/form-data' :     

                # original version :     
                '''
                query=cgi.parse_multipart(self.rfile, pdict)
                upfilecontent = query.get('upfile')
                print "filecontent", upfilecontent[0]
                '''

                # using cgi.FieldStorage instead, see 
                # http://stackoverflow.com/questions/1417918/time-out-error-while-creating-cgi-fieldstorage-object     
                fs = cgi.FieldStorage( fp = self.rfile, 
                                       headers = self.headers, # headers_, 
                                       environ={ 'REQUEST_METHOD':'POST' } # all the rest will come from the 'headers' object,     
                                       # but as the FieldStorage object was designed for CGI, absense of 'POST' value in environ     
                                       # will prevent the object from using the 'fp' argument !     
                                     )
                ## print 'have fs'

            else: raise Exception("Unexpected POST request")
                
                
            fs_up = fs['upfile']
            filename = os.path.split(fs_up.filename)[1] # strip the path, if it presents     
            fullname = os.path.join(CWD, filename)

            # check for copies :     
            if os.path.exists( fullname ):     
                fullname_test = fullname + '.copy'
                i = 0
                while os.path.exists( fullname_test ):
                    fullname_test = "%s.copy(%d)" % (fullname, i)
                    i += 1
                fullname = fullname_test
                
            if not os.path.exists(fullname):
                with open(fullname, 'wb') as o:
                    # self.copyfile(fs['upfile'].file, o)
                    o.write( fs_up.file.read() )     


            self.send_response(200)
            self.end_headers()
            
            self.wfile.write("<HTML><HEAD></HEAD><BODY>POST OK.<BR><BR>");
            self.wfile.write( "File uploaded under name: " + os.path.split(fullname)[1] );
            self.wfile.write(  '<BR><A HREF=%s>back</A>' % ( UPLOAD_PAGE, )  )
            self.wfile.write("</BODY></HTML>");
            
            
        except Exception as e:
            # pass
            print e
            self.send_error(404,'POST to "%s" failed: %s' % (self.path, str(e)) )

def main():
    port =8080
    local_server = "http://%s:%d" % ( socket.gethostbyname(socket.gethostname()) , port )
    try:
        server = HTTPServer(('', port ), MyHandler)
        print 'started httpserver...' 
        print "user can connect to " + local_server
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

