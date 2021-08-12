import pyaudio
import threading

class Audio():    
    def __init__(self,conn):
        self.py_audio= pyaudio.PyAudio()
        
        self.default_input=[]
        self.default_output=[]

        self.num_devides=0

        self.output={}
        self.input={}

        self.conn=conn

        self.stop_recv=False
        self.stop_send=False
        self.stop_audio_stream=False
        
        #__init_dev
        self.output_devices()
        self.input_devices()

    def output_devices(self):
        self.output={}
        
        info= self.py_audio.get_host_api_info_by_index(0)
        self.num_devides= info.get('deviceCount')

        l=0
        for i in range(0,self.num_devides):
                if self.py_audio.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
                    if l==0:
                        pass
                    else:                            
                        self.output[i]=self.py_audio.get_device_info_by_host_api_device_index(0,i).get('name')
                        if l==1:
                            self.default_output=[i,self.output[i]]
                    l+=1

        return self.output
    
    def input_devices(self):
        
        self.input={}
        
        info= self.py_audio.get_host_api_info_by_index(0)
        self.num_devides= info.get('deviceCount')
        l=0
        for i in range(0,self.num_devides):
                if self.py_audio.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
                    if l==0:
                        pass
                    else:
                        self.input[i]=self.py_audio.get_device_info_by_host_api_device_index(0,i).get('name')
                        if l==1:
                            self.default_input=[i,self.input[i]]
                    l+=1
                    

        return self.input


    def recv(self,conn=None,FORMAT =pyaudio.paInt16,CHANNELS = 1,RATE = 48100,CHUNK = 3000,
             output_device_index=None):

        if conn==None:
            conn=self.conn
        if output_device_index==None:
            output_device_index=self.default_output[0]
        
        stream = self.py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                    frames_per_buffer=CHUNK,output_device_index=output_device_index)
        self.stop_recv=False
        
        try:
            while True:
                if self.stop_recv == True:
                    break
                
                data = conn.recv(3000)
                stream.write(data)
                
        except Exception as e:
            print('Error : ',e)
            
            
        finally:
            stream.close()


    def send(self,conn=None,FORMAT =pyaudio.paInt16, CHANNELS=1, RATE = 48100,CHUNK = 3000,
             input_device_index=None):
        
        if conn==None:
            conn=self.conn
        if input_device_index==None:
            input_device_index=self.default_input[0]

        self.stop_send=False

        
        def callback(in_data, frame_count, time_info, status):
            nonlocal conn ,self
            conn.send(in_data)
            
            status=0
            if self.stop_send==True:
                status=2
            
            return (None, status)


        # start Recording
        stream = self.py_audio.open(format=FORMAT,channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK, stream_callback=callback,
                                    input_device_index=input_device_index)        
        stream.start_stream()
        
            
    def audio_stream(self,FORMAT =pyaudio.paInt16, CHANNELS=1, RATE = 48100,CHUNK = 3000,
             output_device_index=None,input_device_index=None):

        

        self.stop_audio_stream=False

        output_stream = self.py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                    frames_per_buffer=CHUNK,output_device_index=output_device_index)

        

        
        def callback(in_data, frame_count, time_info, status):
            nonlocal output_stream ,self
            output_stream.write(in_data)            
            status=0
            
            if self.stop_audio_stream ==True:
                output_stream.close()
                status=2
            
            return (None, status)


        # start Recording
        input_stream = self.py_audio.open(format=FORMAT,channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK, stream_callback=callback,
                                    input_device_index=input_device_index)        
        input_stream.start_stream()
        return True
        
        
        
        
        
    

        
import socket
import time

n=int(input('Enter 1 for Listen && 2 for send : '))
py=Audio('Mahadev')
print('Input_dev==',py.input_devices())
print('Output_dev==',py.output_devices())



if n==1:
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.bind(('',5000))
    print('Binding on loacalhost  : on port 8894')
    sc.listen(10)
    while True:
        conn, address = sc.accept()
        print("Connection has been established! |" + " IP " + address[0] + " | Port" + str(address[1]))
                
        p=threading.Thread(target=py.recv,kwargs={'conn': conn})
        p.start()
    
elif n==2:
    ip='192.168.43.150'
    port='5000'
    t=1000

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.connect((ip,int(port)))

        
    p=threading.Thread(target=py.send,kwargs={'conn': serversocket})
    p.start()

elif n==3:
    n=int(input('Enter Out_put Device  : '))
    i=int(input('Enter input_device  :  '))
    
    py.audio_stream()
    
else:
    print('Invalid ')

    
        


        
