# -*- coding=utf-8 -*- 
#author:milkcandylmt mail:lhy.yh@qq.com
#2016-06-22

import  xdrlib ,sys
import xlrd
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
import os
import shutil
#import copy
from Selenium2Library import Selenium2Library
from Selenium2Library.keywords import *
import time

#直接调用action方法
from Selenium2Library.keywords._formelement import _FormElementKeywords

#异常处理
def tryExcept(func, *params, **paramMap):
    try:
        return func(*params, **paramMap)
    except Exception, e:
        return e
def isExcept(e, eType = Exception):
    return isinstance(e, eType)



#SMap_Ci 类用于 元素自检 根据xls文件的顺序进行检查 SYS模块主要为固定参数配置不检查、URL不检查
class SMap_Ci(object):
    def __init__(self):
        self.ci_rs={} #检查结果
        self.dr=_Basic()
        self.xlsobj=do_xls()
        #1、打开浏览器
        self.dr.my_open_browser(self.xlsobj.smap("SYS-URL")[0],self.xlsobj.smap("SYS-Browser")[0])
        #2、登录
        self.dr.D("Lgn-LOGIN_CODE")
        self.Ci_Engine()
    def Ci_Engine(self):
        for item in self.xlsobj.ci_keys:
            time.sleep(0.1)
            rv=None
            if item.endswith("-GOTO"):
                rv=tryExcept(self.dr.D,item)
            else:    
                rv=tryExcept(self.dr.visible_check,item)
            if isExcept(rv):
                self.ci_rs[item]="False"
                continue
            self.ci_rs[item]="True"

#Basic 类基于Selenium2library拓展开发类
#致力于 实现元素整合到一个xls表格中
class _Basic(Selenium2Library):
    
    def __init__(self):
        Selenium2Library.__init__(self)
        self.driver=None
        self.xlsobj=do_xls()
        #self.my_open_browser()
    def my_open_browser(self,url="http://192.168.0.1",browser="chrome"):
        #自己的打开浏览器方法
        try:
            driver = self._current_browser()
        except RuntimeError, e:
            self.open_browser(url, browser)
            driver = self._current_browser()
        self.driver=driver
    def visible_check(self,locator=None,timeout=0.1):
        
        if len(self.smap(locator))>2 and self.smap(locator)[2]: #若节点带字典 则不点击
            return u"带字典节点 为不完整元素 不需要检查"
        
        if self.smap(locator)[1][0] == "a":
            if isExcept(self._element_find(self.smap(locator)[0], True, True, tag='a')):
                return False
            return True
        if self._is_visible(self.smap(locator)[0]):
            return True
        else:
            return False
    Set_dict={
        "text_field":"input_text",
        "button":"click_button",
        "goto":"go_to",
        "radio":"select_radio_button",
    }
    button_dict={
        "div":"click_element",
        "a":"click_link",
    }
    Get_dict={
        "text_field":"get_text",
        "value":"get_value",
    }
    
    #需要映射关系的节点元素
    value_set_list=["radio"]
    
    #描述性文件类型 并且带字典属性的节点列表
    discript_elem_dict=["radio"]
    
    
    def get_element_type(self,cmd=None):
    #获取类型 虚拟类型#则选择 #后面的
        rv=None
        if cmd[1]:
            tmp_list=cmd[1].split('#')
            if len(tmp_list) >1:
               rv=tmp_list[1]
            elif len(tmp_list)==1:
               rv=tmp_list[0]
        return rv
    
    #计算函数参数个数    
    def arg_count(self,func):
        arg=[] 
        for i in range(100):  # 
            try: 
                func(*arg) 
            except TypeError: 
                arg.append(1) 
            return len(arg)
    #actions 实现连串动作
    def action_multil(self,cmd=None):
        cmdlist=cmd.split("\n")
        for item in cmdlist:
            item_tmp=[]
            print item
            print item.split(" ")
            item_tmp=item.split(" ")
            if len(item_tmp) == 1:
                item_tmp.append("")
                item_tmp.append("")
            elif len(item_tmp) == 2:
                item_tmp.append("")
            if len(item_tmp) ==3:
                self.D(item_tmp[0],item_tmp[1],item_tmp[2])
    def D(self,cmd=None,act=None,value=None):
        #驱动动作 None Set Get
        funname=None
        cmd1=self.xlsobj.smap(cmd)
        while cmd1[0] in self.xlsobj.key_locator.keys():
            cmd1=self.xlsobj.smap(cmd1[0])
        type=self.get_element_type(cmd1)
        #print self.Set_dict[type]
        print "~~~~~~~~~~~~~~~~~~"
        print cmd1
        print "~~~~~~~~~~~~~~~~~~"
        # if isinstance(self.smap(cmd1[1])[2],dict) and type in self.discript_elem_dict:
            # return "discript_elem_dict no need to do any thing.."
        # if len(cmd1)>2 and cmd1[2]: #若节点带字典 则不做操作
            # return u"带字典节点 为描述性元素节点 不做任何操作"
            
        
        if type == "acts":
            return self.action_multil(cmd1[0])
        #当元素为 *-GOTO 时，act默认为Set
        if cmd.endswith("-GOTO"):
            act="Set"
        if cmd1 is None:
            return "locator cmd is None!"
        #func_key=self.Set_dict[type]
        if type and act == "Set":
            func_key=self.Set_dict[type]
            #以下几行处理不同元素虚拟类型调用的方法不同
            #例如div#button 方法调用click_button不可以，需要调用click_element
            tmp_listtype=cmd1[1].split("#")
            if len(tmp_listtype)>1:
                    dict_name=type+"_dict"
                    func_key=getattr(self,dict_name)[tmp_listtype[0]]
            func=getattr(self,func_key) #获取self对象的函数属性
            print func,cmd1[0],value
            if value:   #text_field填写
                if type in self.value_set_list:
                    value=cmd1[2][value]  #select_radio_button(cmd1[0],value)
                return func(cmd1[0],value)
            return func(cmd1[0])
        if type and act == "Get":
            func_key=self.Get_dict[type]
            func=getattr(self,func_key)
            return func(cmd1[0])
    def smap(self,scmd=""):
        #返回映射关系
        if scmd not in self.xlsobj.key_locator.keys():
            return False
        if self.xlsobj.key_locator[scmd][2] and isinstance(self.xlsobj.key_locator[scmd][2],list):  #字典字段 list转化为dict
            self.xlsobj.key_locator[scmd][2]=self.xlsobj.list2dict(self.xlsobj.key_locator[scmd][2].split(" "))
        return self.xlsobj.key_locator[scmd]
        
        
class do_xls(object):
    def __init__(self):
        self.table_rows=[] #存放所有表格行（除表头）
        self.cmdstr=None
        self.key_locator={}
        self.cmddict={}
        self.find_cmddict={}  #查找的字典
        self.action_cmddict={} #动作字典
        self.table_rows=self.read_excel_table_byname_list()
        self.Key2Locator()
        self.urls_para() #带Key的url解析为 浏览器识别的格式
        self.ci_keys=[]
        self.key_list()
        self.element_all_smap()  #用于将 字典属性的列表 转化为字典
    #长度为偶数的列表 例如list=["a","1","b","2"] 转化为 {"a"："1","b"："2"}
    def list2dict(self,args):
        tmp_dict={}
        if len(args)%2 !=0:
            print u"list2dict()列表长度必须为偶数!"
            return
        j=0
        for i in range(0,len(args)/2):
            if j >= len(args):
                break
            tmp_dict[args[j]]=args[j+1]
            j+=2
        return tmp_dict    
    #除了SYS Lgn之外的所有点
    def key_list(self):
        for i in self.table_rows:
            if i[1].startswith("SYS-") or i[1].startswith("Lgn-"):
                continue
            self.ci_keys.append(i[1])
        
    def open_excel(self,file= 'test.xls'):
        try:
            data = xlrd.open_workbook(file)
            return data
        except Exception,e:
            print str(e)
    def read_excel_table_byname_list(self,file= 'ECOS-SMap.xls',colnameindex=0,by_name=u'ECOS'):
        data = self.open_excel(file)
        table = data.sheet_by_name(by_name)
        nrows = table.nrows #行数 
        colnames =  table.row_values(colnameindex) #某一行数据
        self.table_head=table.row_values(0)
        list =[]
        for rownum in range(1,nrows):
            row = table.row_values(rownum)
            if row:
                list.append(row)
        return list
    def cmd_combile(self):
        for item in self.table_rows:
            str_tmp=""
            if item[3]:
                str_tmp=item[3]
            
            if item[1].endswith("-URL") or item[1].endswith("-GOTO"):
                self.cmddict[item[1]]=item[6]
                continue
            if item[6] is None:
                str_tmp+=item[3]
                continue
            elif item[6]:
                if item[5]:
                    item[6]=item[5]+'='+item[6]
                str_tmp+="."+'_element_find("%s")'%item[6]
            self.cmddict[item[1]]=str_tmp
    def get_element_type_v2(self,cmd=None):
    #获取类型 虚拟类型#则选择 #后面的
        rv=None
        if cmd:
            tmp_list=cmd.split('#')
            if len(tmp_list) >1:
               rv=tmp_list[1]
            elif len(tmp_list)==1:
               rv=tmp_list[0]
        return rv
    # def get_element_type_v2(self,cmd=None):
        # if cmd:
            # return self.get_element_type(self.smap(cmd))
    #不需要 = 号的控件的列表    
    locator_no_need_eq=["radio"]
    
    #建立 关键字与定位器的 映射关系    
    def Key2Locator(self):
        #type=self.get_element_type(self.smap(""))
        for item in self.table_rows:
            print item[1]
            value=[]           
            str_tmp=""
            if item[6]:
                if item[5] and self.get_element_type_v2(item[4]) not in self.locator_no_need_eq:
                # and self.get_element_type(self.smap(item[1])) not in self.locator_no_need_eq
                #self.get_element_type(self.smap(item[1])) not in self.locator_no_need_eq 作用是locator_no_need_eq 列表的控件不需要带 = 号
                    str_tmp+="="
                if self.get_element_type_v2(item[4]) in self.locator_no_need_eq:
                    item[5]=""
                value.append(item[5]+str_tmp+item[6])
                value.append(item[4])
                value.append(item[7])
                self.key_locator[item[1]]=value
                    
                #print "value=",value
     #url从SMAP解析为浏览器可识别的模式
    def urls_para(self):
        for i in self.key_locator.keys():
            if i.endswith("-URL") or i.endswith("-GOTO"):
                 #print "i=",i
                 if i.startswith("SYS-"):
                    continue
                 self.key_locator[i][0]=self.url_para(self.key_locator[i][0])
    def url_para(self,url):
        urlstr_list=url.split("/")
        for item in urlstr_list:
            if item in self.key_locator.keys():
                url=url.replace(item,self.smap(item)[0])
        #print url
        return url
    def element_all_smap(self):
        for i in self.key_locator.keys():
            self.smap(i)
            
    #smap demo        
    # >>> x.smap("Net-Conntype")
    # [u'name=con-type', u'radio', {u'DHCP': u'dhcp', u'STATIC': u'static', u'_ATTRIB'
    # : u'id', u'PPPOE': u'adsl'}]
    def smap(self,scmd=""):
        #返回映射关系
        if scmd not in self.key_locator.keys():
            return False
        if self.key_locator[scmd][2] and isinstance(self.key_locator[scmd][2],dict) is not True:  #字典字段 list转化为dict
            self.key_locator[scmd][2]=self.list2dict(self.key_locator[scmd][2].split(" "))
        return self.key_locator[scmd]
if __name__=="__main__":
   #obj=_Basic()
   #obj.my_open_browser()
   #obj.D("Lgn-LOGIN_CODE")
   #obj.D("Lgn-Pwd","Set","admin")
   #print obj.D("Lgn-Pwd","Get")
   # obj.D("Lgn-Save","Set")
   #time.sleep(3)
   #obj.visible_check()
   #tables = obj.Key2Locator()
   #for i in obj.key_locator.items():
   #    print i
   test=SMap_Ci()
   print test.ci_rs