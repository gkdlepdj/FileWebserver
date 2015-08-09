# coding: cp949
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib
import glob
import os 
import socket
import time 
import string,cgi
HOME_DIR = "D:\\local\\FileWebserver\\html_home"


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
    font-size: 14px;  
    font-weight: bold;
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

table th#thno {
   text-align: left;
   width: 10%%
}

table th#thname {
   text-align: left;
   width: 60%%
}

table th#thsize {
   text-align: right;
   width: 10%%
}

table th#thupdate {
   text-align: center;
   width: 20%%
}

table td#tdupdate {
   text-align: center;
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
    <th id='thno'>번호</th>
    <th id='thname'>이름</th>       
    <th id='thsize'>크기</th>
    <th id='thupdate'>최종수정일</th>
  </tr>
  %s  
</table>
</div>
</body>
</html>""" 
def byte_to_unit(n):
    if n > 1024*1024*1024:
        return "%.2fGB" % (float(n)/(1024*1024*1024))
    if n > 1024*1024:
        return "%.1fMB" % (float(n)/(1024*1024))
    if n > 1024:
        return "%.1fKB" % (float(n)/(1024))
    return "%dB" % n
def make_index(  path, abspath ):     

    # 정렬  디렉토리 알파벳 순서 + 파일 알파벳 순서 
    files = filter(os.path.isfile, glob.glob(abspath + "\\*"))
    files.sort()
    dirs = filter(os.path.isdir, glob.glob(abspath + "\\*"))
    dirs.sort()
    flist = dirs+files

    inslist = []
    insert_string ="<tr><td>{0}</td><td><a href='{1}'>{2}</a></td><td id='tdsize'>{3}</td><td id='tdupdate'>{4}</td></tr>"
    for i,f in  enumerate( flist ) : 
        file_name           = os.path.split(f)[1]
        urlpath             = (path+file_name) if path[-1]=='/' else (path + "/" + file_name)
        file_display_name   = '[ '+ file_name+' ]' if os.path.isdir(f) else file_name
        file_size           = byte_to_unit( os.path.getsize(f) )   
        file_update_time    = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime( os.stat(f).st_mtime )   )
        inslist.append( insert_string.format(i+1,urlpath,file_display_name,file_size,file_update_time) )
  
    ret = page_tpl % ( abspath.encode("cp949"),"\n".join(inslist))
    return ret

class MyHandler(BaseHTTPRequestHandler):
   
    def do_GET(self):
        try:
            print "self.path #==> : " + self.path
            if HOME_DIR[-1] == "\\":
                abspath = HOME_DIR[:-1] + self.path.replace("/","\\")
                
            else :
                abspath = HOME_DIR + self.path.replace("/","\\")
            print "abspath #==> : " + abspath            

            if os.path.isdir(abspath):
                page = make_index( self.path, abspath )
                # page = '<html><head></head><body>dir</body></html>'
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(page)
                return

            if self.path.endswith(".html"):
                f = open(abspath)
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if self.path.endswith(".css"):
                f = open(abspath)
                self.send_response(200)
                self.send_header('Content-type','text/css')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if os.path.isfile(abspath):
                f = open( abspath, 'rb' )
                self.send_response(200)
                self.send_header('Content-type','application/octet-stream')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            return # be sure not to fall into "except:" clause ?

        except IOError as e :
            # debug
            print e
            self.send_error(404,'File Not Found: %s' % self.path)

    # def do_POST(self):
    #     self.store_path = HOME_DIR+"\\upload.file"
    #     print "POST --- self.path #==> : " + self.path
    #     try:
    #         if self.path == '/':
    #             length = self.headers['content-length']
    #             data = self.rfile.read(int(length))
    #             with open(self.store_path, 'wb') as fh:
    #                 fh.write(data)
    #             self.send_response(200)
    #             self.end_headers()
    #             self.wfile.write("<HTML><HEAD></HEAD><BODY>POST OK.<BR><BR>");
    #             self.wfile.write( "File uploaded under name: " + os.path.split(self.store_path)[1] );
    #             self.wfile.write(  '<BR><A HREF=%s>back</A>' % ( "UPLOAD_PAGE")   )
    #             self.wfile.write("</BODY></HTML>");
    #     except Exception as e:
    #         print e
    #         self.send_error(404,'POST to "%s" failed: %s' % (self.path, str(e)) )


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
            fullname = os.path.join(HOME_DIR, filename)

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
            self.wfile.write(  '<BR><A HREF=%s>back</A>' % ( 'UPLOAD_PAGE,' )  )
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
    except socket.error, e:
        print "socket error: " + str(e)
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        os.exit(0)
    else:
        print 'started httpserver...'
        print "user can connect to " + local_server
        server.serve_forever()
        
    

if __name__ == '__main__':
    main()
