from tkinter import *
from ctypes import windll
from threading import Thread
from time import ctime,sleep
from tkinter import ttk
import pyaudio
import threading
import socket
import os

class Audio():    
    def __init__(self,conn=None):
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


    def recv(self,conn=None,FORMAT =pyaudio.paInt16,CHANNELS = 1,RATE = 48100,CHUNK = 500,
             output_device_index=None,call_back=None):
        
        stream = self.py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                    frames_per_buffer=CHUNK,output_device_index=output_device_index)
        self.stop_recv=False
        
        try:
            while True:
                if self.stop_recv == True:
                    try:
                        conn.close()
                    except:
                        pass
                    call_back()
                    break
                else:                
                    data = conn.recv(1000)
                    if not data:
                        raise 'Connection Close by client'
                        
                    stream.write(data)
                
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            call_back()
        
            
            
        finally:
            stream.close()            


    def send(self,conn=None,FORMAT =pyaudio.paInt16, CHANNELS=1, RATE = 48100,CHUNK = 500,
             input_device_index=None,call_back=None):
        
        self.stop_send=False
        conn=self.conn
        def callback(in_data, frame_count, time_info, status):
            nonlocal conn ,self,call_back
            try:
                conn.send(in_data)
                   
            except:
                self.stop_send==True
                
            status=0
            if self.stop_send==True:
                try:
                    conn.close()
                except:
                    pass
                call_back()
                status=2            
            return (None, status)


        # start Recording
        stream = self.py_audio.open(format=FORMAT,channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK, stream_callback=callback,
                                    input_device_index=input_device_index)        
        stream.start_stream()
        
            
    def audio_stream(self,FORMAT =pyaudio.paInt16, CHANNELS=2, RATE = 48100,CHUNK = 1000,
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

def custom_shape_canvas(parent=None,width=300,height=100,rad=50,padding=3,bg='red'):
    color=bg
    cornerradius=rad
    rad = 2*cornerradius
    parent.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,
                           padding+cornerradius,padding,width-padding-cornerradius,padding,
                           width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,
                           width-padding-cornerradius,height-padding,padding+cornerradius,height-padding),
                          fill=color, outline=color)

    parent.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color,
                      outline=color)
    parent.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90,
                      fill=color, outline=color)
    parent.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270,
                      extent=90, fill=color, outline=color)
    parent.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90,
                      fill=color, outline=color)


class Stream_gui():
    def __init__(self,parent=None):
        
        self.lab_x,self.lab_y=0,0
        windll.shcore.SetProcessDpiAwareness(True)
        self.Stream_win=Tk()
        
        height=((self.Stream_win.winfo_screenheight())//2)-300
        width=((self.Stream_win.winfo_screenwidth())//2)-400
        
        self.Stream_win.geometry(f'750x400+{width}+{height}')
        self.Stream_win.overrideredirect(True)



        self.Stream_win.config(bg='deep pink')

        self.frame = Canvas(self.Stream_win,bg='deep pink',bd=0,width=750,height=150,highlightthickness=0)
        back_col='cyan2'    
        self.frame.place(x=0,y=0)
        custom_shape_canvas(parent=self.frame,width=750,height=150,rad=40,padding=3,bg=back_col)

        self.local_stream=Button(self.frame,text=' Stream ',font=('bold',20,'bold italic')
                          ,bg='deep skyblue',bd=0,relief='flat',command=self.stream_button_command)
        self.local_stream.place(x=100,y=50)

        self.server_stream=Button(self.frame,text=' Server ',font=('bold',20,'bold italic')
                          ,bg='dodger blue',bd=0,relief='flat',command=self.server_button_command)
        self.server_stream.place(x=300,y=50)

        self.client_stream=Button(self.frame,text='  Client  ',font=('bold',20,'bold italic')
                          ,bg='cornflower blue',bd=0,relief='flat',command=self.client_button_command)
        self.client_stream.place(x=500,y=50)




        self.frame2 = Canvas(self.Stream_win,bg='deep pink',bd=0,width=620,height=250,highlightthickness=0)
        self.frame2.place(x=65,y=140)

        custom_shape_canvas(parent=self.frame2,width=620,height=250,rad=20,padding=3,bg=back_col)
        

        self.input_dev_choosen=ttk.Combobox(self.frame2, width = 30,font=('',13))
        self.input_dev_label=ttk.Label(self.frame2,text= ' Input Device   :',font=('',13,'bold italic'))

        self.output_dev_choosen=ttk.Combobox(self.frame2, width = 30,font=('',13))
        self.output_dev_label=ttk.Label(self.frame2,text='Output Device :',font=('',13,'bold italic'))

        self.start_local_stream_button=Button(self.frame2,text=' Start Process ',font=('bold',30,'bold italic')
                          ,bg='gold',bd=0,relief='flat',command=self.start_local_stream)
        

        self.ip_label=ttk.Label(self.frame2,text= 'IP  Address      :',font=('',13,'bold italic'))
        
        self.ip_address_var=StringVar()
        self.ip_address=ttk.Entry(self.frame2,font=('',13,'bold italic'),textvariable=self.ip_address_var,
                                  justify = 'right')


        self.port_var=StringVar()
        self.port_number=ttk.Entry(self.frame2,font=('',13,'bold italic'),textvariable=self.port_var,
                                  justify = 'left',width=8)

        self.start_server_stream_button=Button(self.frame2,text=' Start Server ',font=('bold',30,'bold italic')
                          ,bg='orange',bd=0,relief='flat',command=self.start_server_stream,width=13)
        

        self.start_client_stream_button=Button(self.frame2,text='Connect to Server',font=('bold',30,'bold italic')
                          ,bg='maroon2',bd=0,relief='flat',command=self.start_client_stream,width=15)
        
        




        self.Stream_win.bind('<B1-Motion>',self.move_Stream_win)
        self.Stream_win.bind('<Button-1>', self.bouble_click_Stream_win)
        self.Stream_win.bind("<Control-x>",lambda event: self.Stream_win.destroy())
        self.Stream_win.bind("<Control-X>",lambda event: self.Stream_win.destroy())
        self.Stream_win.wm_attributes('-transparentcolor', 'deep pink')
        self.Stream_win.wm_attributes('-topmost', True)

        self.frame2.config(height=0)
        self.Stream_win.update()

        #C_Audio_class___
        self.py_audio=Audio()

        self.ip='192.168.43.150'
        self.port=5000

        
        self.Stream_win.mainloop()

    def move_Stream_win(self,event=None):
        w=(self.Stream_win.winfo_geometry()).split('+')
        self.Stream_win.geometry(('+'+str((int(w[1])+event.x-self.lab_x)
                                          )+'+'+str((int(w[2])+event.y)-self.lab_y)))
    def bouble_click_Stream_win(self,event=None):
        self.lab_x=event.x
        self.lab_y=event.y
    #___________________________________Client________________________


    def client_button_command(self):
        if int(self.frame2['height']) > 0:
            if (self.start_client_stream_button['text']).strip()== 'Connect to Server':
                self.frame2_hide_show(status='hide',button='client')
                self.client_stream.config(bg='cornflower blue')

        else:
            self.client_stream.config(bg='maroon2')
            
            input_devices=self.py_audio.input_devices()
            input_devices_name=[]
            for index in input_devices:
                input_devices_name.append(input_devices[index])


            self.input_dev_choosen['values']=input_devices_name        
            self.input_dev_choosen['state']='readonly'        
            self.input_dev_label.place(x=30,y=20)         
            self.input_dev_choosen.place(x=200,y=20)
            self.input_dev_choosen.current(0)
            
            self.ip_label.place(x=30,y=70)
            self.ip_address.config(justify = 'left')
            self.ip_address.place(x=200,y=70)
            self.ip_address.focus_force()
            self.port_number.place(x=483,y=70)
            self.ip=self.get_lan_ip()
            self.ip_address_var.set(self.ip)
            self.port_var.set(self.port)
            
            self.start_client_stream_button.place(x=70,y=130)        
            self.frame2_hide_show(status='show',button='client')
            
    def start_client_stream(self):
        self.port_number.config(state='readonly')
        self.port=self.port_var.get()

        self.ip_address.config(state='readonly')
        self.ip=self.ip_address_var.get()
        
        self.input_dev_choosen['state']='disabled'
        current_input_dev=self.input_dev_choosen.get()
        input_devices=self.py_audio.input_devices()        
        input_devices_index=None
        for index in input_devices:
            if input_devices[index] ==current_input_dev:
                input_devices_index=index

        

        self.start_client_stream_button.config(text='Connecting....')
        self.py_audio.conn = socket.socket()
        try:
            self.py_audio.conn.connect((self.ip,int(self.port)))
            self.start_client_stream_button.config(text='  Connected.......')
            self.py_audio.send(input_device_index=input_devices_index,call_back=self.call_back_stop_client)
            
            
            self.start_client_stream_button.config(command=self.stop_client_stream)
            def on_enter(event):
                event.widget['fg']='red'
                event.widget['text']='  Disconnect.....'
            def on_leave(event):
                event.widget['fg']='black'
                event.widget['text']='  Connected.......'
                
                
            self.start_client_stream_button.bind("<Enter>",on_enter)
            self.start_client_stream_button.bind("<Leave>",on_leave)
            
        except Exception as e:
            for widget in self.frame2.winfo_children():
                widget.place_forget()
            text=''
            w=''
            for word in str(e).split():
                w+=' '+word
                if len(w) > 30:
                    text=text+w+'\n'
                    w=''
                
                
            text+=w
            l=Label(self.frame2,text=text,font=('',18,'bold italic'),fg='red',bg='cyan2')
            l.place(x=20,y=10)
            self.start_client_stream_button.place(x=70,y=140)
            def Try_Again():
                self.stop_client_stream()
                self.call_back_stop_client()
                self.client_button_command()
                
            self.start_client_stream_button.config(text='Try Again.....',command=Try_Again)
            
            


                




    def stop_client_stream(self):
        self.py_audio.stop_send=True
        self.start_client_stream_button.unbind("<Enter>")
        self.start_client_stream_button.unbind("<Leave>")
        self.start_client_stream_button.config(text='Disconnecting..')
                
        
    def call_back_stop_client(self):
        self.start_client_stream_button.config(text='Disconnected')
        self.client_stream.config(bg='cornflower blue')
        self.ip_address.config(state='normal')
        self.port_number.config(state='normal')                                
        self.start_client_stream_button.config(text='Connect to Server')
        self.start_client_stream_button.config(command=self.start_client_stream)
        self.frame2_hide_show(status='hide',button='client')
        
        
        
        
        
        
        
        

    #___________________________________Client________________________


    #+++++++++++++++++++++__Server___+++++++++++++++++++++++++++++++++++++++++++


    def server_button_command(self):
        if int(self.frame2['height']) > 0:
            if (self.start_server_stream_button['text']).strip()== 'Start Server':

                self.frame2_hide_show(status='hide',button='server')
                self.server_stream.config(bg='dodger blue')
                
            elif (self.start_server_stream_button['text']).strip()== 'Accepting...':
                self.stop_server_stream()
                self.call_back_stop_server_stream()
                

        else:
            self.server_stream.config(bg='orange')
            output_devices=self.py_audio.output_devices()
            output_devices_name=[]
            for index in output_devices:
                output_devices_name.append(output_devices[index])


            self.output_dev_choosen['values']=output_devices_name        
            self.output_dev_choosen['state']='readonly'        
            self.output_dev_label.place(x=30,y=20)         
            self.output_dev_choosen.place(x=200,y=20)
            self.output_dev_choosen.current(0)
            
            self.ip_label.place(x=30,y=70)
            self.ip_address.place(x=200,y=70)
            self.ip_address.config(state='readonly')

            
            self.port_number.place(x=483,y=70)
            self.ip=self.get_lan_ip()
            self.ip_address_var.set(self.ip)
            self.port_var.set(self.port)
            self.start_server_stream_button.place(x=120,y=130)        
            self.frame2_hide_show(status='show',button='server')
            
            
    def start_server_stream(self):
        self.start_server_stream_button.config(command='',text='Accepting...')
        self.port_number.config(state='readonly')
        self.port=self.port_var.get()

        self.sc = socket.socket()
        self.sc.bind(('',int(self.port)))
        print('Binding on loacalhost  : on port  '+str(self.port))            
        p=threading.Thread(target=self._listen_devices)
        p.start()

    def _listen_devices(self):
        try:
            self.sc.listen(1)
            connn, address = self.sc.accept()
            self.start_server_stream_button.config(text='connected..',fg='green2')

            self.output_dev_choosen['state']='readonly'
            current_output_dev=self.output_dev_choosen.get()
            output_devices=self.py_audio.output_devices()
            output_devices_index=None
            for index in output_devices:
                if output_devices[index] ==current_output_dev:
                    output_devices_index=index

            
            def on_enter(event):
                event.widget['bg']='orange red'
                event.widget['text']='Stop Stream.'
            def on_leave(event):
                event.widget['bg']='orange'
                event.widget['text']=' Streaming... '
                
                
            self.start_server_stream_button.config(text=' Streaming... ',fg='green2')
            self.start_server_stream_button.bind("<Enter>",on_enter)
            self.start_server_stream_button.bind("<Leave>",on_leave)
            self.start_server_stream_button.config(command=self.stop_server_stream)
            
            c=self.py_audio.recv(conn=connn,output_device_index=output_devices_index,
                                 call_back=self.call_back_stop_server_stream)
        except Exception as e:
            print(e)
            
            

    def stop_server_stream(self):
        self.py_audio.stop_recv=True

                                               
        
    def call_back_stop_server_stream(self):
        print('call_back_stop_server_stream_____call_back_stop_server_stream')
        self.start_server_stream_button.unbind("<Enter>")
        self.start_server_stream_button.unbind("<Leave>")
        self.start_server_stream_button.config(command='',text='Stopping....')
        self.port_number.config(state='normal')
        self.server_stream.config(bg='dodger blue')
        self.start_server_stream_button.config(text=' Start Server ',fg='black',bg='orange',
                                               command=self.start_server_stream)
        try:
            self.sc.close()
        except:
            pass
        self.frame2_hide_show(status='hide',button='server')
        
    #+++++++++++++++++++++__Server___+++++++++++++++++++++++++++++++++++++++++++



    def stream_button_command(self):
        if int(self.frame2['height']) > 0:
            if (self.start_local_stream_button['text']).strip()== 'Start Process':
                self.frame2_hide_show(status='hide',button='stream')
                self.local_stream.config(bg='deep skyblue')

        else:            
            input_devices=self.py_audio.input_devices()
            input_devices_name=[]
            for index in input_devices:
                input_devices_name.append(input_devices[index])
                
            
            
            output_devices=self.py_audio.output_devices()
            output_devices_name=[]
            for index in output_devices:
                output_devices_name.append(output_devices[index])

                
            
            self.input_dev_choosen['values']=input_devices_name        
            self.input_dev_choosen['state']='readonly'        
            self.input_dev_label.place(x=30,y=20)        
            self.input_dev_choosen.place(x=200,y=20)
            self.input_dev_choosen.current(0)

            self.output_dev_choosen['values']=output_devices_name        
            self.output_dev_choosen['state']='readonly'        
            self.output_dev_label.place(x=30,y=60)        
            self.output_dev_choosen.place(x=200,y=60)
            self.output_dev_choosen.current(0)
            self.start_local_stream_button.place(x=100,y=120)
            self.local_stream.config(bg='gold')
            self.frame2_hide_show(status='show',button='stream')
            


        

    def start_local_stream(self):
        print('starting')
        self.py_audio.stop_audio_stream=False
        self.input_dev_choosen['state']='disabled'
        self.output_dev_choosen['state']='disabled'
        self.start_local_stream_button.config(text='Starting..')
        self.Stream_win.update()

        current_input_dev=self.input_dev_choosen.get()
        current_output_dev=self.output_dev_choosen.get()

        input_devices=self.py_audio.input_devices()
        
        input_devices_index=None
        for index in input_devices:
            if input_devices[index] ==current_input_dev:
                input_devices_index=index
                        
        
        output_devices=self.py_audio.output_devices()
        output_devices_index=None
        for index in output_devices:
            if output_devices[index] ==current_output_dev:
                output_devices_index=index


        c=self.py_audio.audio_stream(output_device_index=output_devices_index
                                   ,input_device_index=input_devices_index)
        if c== True:
            self.start_local_stream_button.config(text=' Stop Process..')
            self.start_local_stream_button.config(command=self.stop_stream_command)
        else:
            self.start_local_stream_button.config(text=' Error: Check mlly')
            
    def stop_stream_command(self):
        self.py_audio.stop_audio_stream=True        
        self.input_dev_choosen['state']='readonly'
        self.output_dev_choosen['state']='readonly'
        self.start_local_stream_button.config(text=' Process stoped')
        sleep(0.1)    
        self.start_local_stream_button.config(text=' Start Process')
        self.start_local_stream_button.config(command=self.start_local_stream)
        self.frame2_hide_show(status='hide',button='stream')
        self.local_stream.config(bg='deep skyblue')



    def frame2_hide_show(self,status=None,button=None):
        if status=='hide':
            for i in range(250,0,-10):
                self.frame2.config(height=i)
                self.Stream_win.update()
                print(i)
            self.frame2.config(height=0)
            self.Stream_win.update()
            for widget in self.frame2.winfo_children():
                widget.place_forget()
                
            
            self.server_stream.config(state='normal')
            self.client_stream.config(state='normal')
            self.local_stream.config(state='normal')

        elif status=='show':

            
            if button =="stream":
                self.server_stream.config(state='disabled')
                self.client_stream.config(state='disabled')
            elif button =="server":
                self.local_stream.config(state='disabled')
                self.client_stream.config(state='disabled')
            elif button=="client":
                self.local_stream.config(state='disabled')
                self.server_stream.config(state='disabled')

            for i in range(0,250,8):
                self.frame2.config(height=i)
                self.Stream_win.update()
                print(i)

            self.frame2.config(height=250)
            self.Stream_win.update()
            
    def get_lan_ip(self):
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127.") and os.name != "nt":
            interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
            for ifname in interfaces:
                try:
                    ip = get_interface_ip(ifname)
                    break;
                except IOError:
                    pass
        return ip

            
        
    

        

        
            
            
        
root=Stream_gui()
