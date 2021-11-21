from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os
from bibl_crawler import *

source_list = ["ndltd","ncl journal","wos","airiti","proquest","EBSCO"]

class modelGUI(Frame): #控制面板的class name
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid() #開啟視窗
        self.createWidgets() #介面
    
    def createWidgets(self):
        #輸入chrome driver位置
        self.flabel_1 = Label(self, text="driver位置")
        self.flabel_1.grid(row=1,column=0,sticky=E)
        #填空空格
        self.ftag_1= Entry(self,width=60)
        self.ftag_1.grid(row=1,column=1,sticky=W)
        #按鈕 打開資料夾路徑
        self.input_1  = Button(self, text = "選擇", command = self.ftag_1_input)
        self.input_1.grid(row=1,column=2,sticky=W)

        #搜尋平台選擇
        self.flabel_2 = Label(self,text="搜尋來源")
        self.flabel_2.grid(row=2,column=0,sticky=E)
        #下拉式選單
        self.ftag_2 = ttk.Combobox(self,values=source_list)
        self.ftag_2.grid(row=2,column=1,sticky=W)
        
        #匯入指令文字檔
        self.flabel_3 = Label(self,text="匯入指令(匯入格式:utf-8編碼,txt檔)")
        self.flabel_3.grid(row=3,column=0,sticky=E)
        #填空空格
        self.ftag_3 = Entry(self,width = 60)
        self.ftag_3.grid(row=3,column=1,sticky=W)
        #按鈕 打開資料夾路徑
        self.input_3 = Button(self,text = "選擇",command = self.ftag_3_input)
        self.input_3.grid(row=3,column=2,sticky=W)

        #指令匯入檔案提式文字
        self.flabel_3_1 = Label(self,text="提示: 指令匯入檔案類型:txt  編碼:utf-8   分行符號:\\t")
        self.flabel_3_1.grid(row=4,column=1,sticky=W)

        #儲存目的地
        self.flabel_4 = Label(self,text= "儲存資料夾位置")
        self.flabel_4.grid(row=5,column=0,sticky=E)
        #填空空格
        self.ftag_4 = Entry(self,width = 60)
        self.ftag_4.grid(row=5,column=1,sticky=W)
        #按鈕 打開資料夾路徑
        self.input_4 = Button(self,text="選擇",command=self.ftag_4_input)
        self.input_4.grid(row= 5, column=2,sticky=W)
        
        #開始執行程式按鈕
        self.main_prog_exe  = Button(self, text="開始", command = self.main_program)
        self.main_prog_exe.grid(row=10, column=1, sticky=W)


    def ftag_1_input(self): #輸入chrome driver路徑
        self.ask_open_driver(self.ftag_1)
    
    def ftag_3_input(self): #輸入指令文字檔路徑
        self.ask_open_file(self.ftag_3)
    
    def ftag_4_input(self): #輸入儲存資料夾路徑
        self.ask_save_dir(self.ftag_4)
    
    
    def ask_open_file(self, open_file_input): #詢問讀取檔名&位置(僅讀檔)
        options = {}
        options['filetypes'] = [("text","*.txt"),("xlsx","*.xlsx"),("allfiles","*")] #預設讀檔類型(第一個為預設，後續為可用選項)
        options['initialdir'] = os.getcwd() #起始資料夾為目前資料夾
        options['multiple'] = False #可否一次選擇多個檔案
        open_file_input.delete(0, 200)
        open_file_input.insert(END, filedialog.askopenfilename(**options))
    
    def ask_open_driver(self, open_file_input):
        options = {}
        options['filetypes'] = [("allfiles","*")]
        options['initialdir'] = os.getcwd() #起始資料夾為目前資料夾
        options['multiple'] = False #可否一次選擇多個檔案
        open_file_input.delete(0, 200)
        open_file_input.insert(END, filedialog.askopenfilename(**options))

    def ask_save_dir(self, save_dir_input): #詢問資料夾所在位置(讀/存)皆可用
        options = {}
        options['initialdir'] = os.getcwd()
        save_dir_input.delete(0, 200) 
        save_dir_input.insert(END, filedialog.askdirectory(**options))

    def main_program(self):
        #chrome driver位置
        driver_source = self.ftag_1.get()
        #搜尋來源
        source = self.ftag_2.get()
        #儲存位置
        target_dir = self.ftag_4.get()

        if source in source_list:
            print(self.ftag_3.get())
            #匯入指令
            input_data = open(self.ftag_3.get(),'r',encoding='utf-8-sig')
            input_code = [line.split('\t') for line in input_data.read().splitlines()]
            input_data.close()
            if source == source_list[0]:
                CRAWLER_NDLTD(driver_source,target_dir,input_code)
            elif source == source_list[1]:
                CRAWLER_NCL_JOURNAL(driver_source,target_dir,input_code)
            elif source == source_list[2]:
                CRAWLER_WOS(driver_source,target_dir,input_code)
            elif source == source_list[3]:
                CRAWLER_AITIRI(driver_source,target_dir,input_code)
            elif source == source_list[4]:
                CRAWLER_PROQUEST(driver_source,target_dir,input_code)
            elif source == source_list[5]:
                CRAWLER_EBSCO(driver_source,target_dir,input_code)
        else:
            print('輸入錯誤\n')
        
        return



if __name__ == '__main__':
    root = Tk()
    root.title("衍生著作書目搜尋")  #視窗title
    app = modelGUI(master=root)
    app.mainloop()