# SeleniumSMap
也称为Smart Map。
Robot是个好用框架，毋庸置疑，但是Robot带来的是，对于程序员来说，不像在编程，这种感觉很痛苦。
但是它的库是很好的，例如S2L、SSH2Library，AppliumLibrary等自动化测试常用库。
一、基于Robot Framework的S2L拓展开发的SMAP，解决因为WEB改动频繁而影响的WEB自动化测试而思考出来的一个Idear。
xls文件存放所有页面元素信息。
通过调用_Basic类中的驱动函数 D() 来进行驱动页面操作。
例如obj.D("Lgn-Pwd","Set","test")
期望将元素操作归一化。
最终将在代码呈现的是简洁的关键字。
若页面元素有改动，则只需要改动xls表格即可，无需改动代码。

二、CI自检机制。
SMap_CI函数，根据xls记录的元素，自动打开WEB对元素进行自检，因此对xls元素的顺序与层次要求较高。
CI自检结果存放于成员变量ci_rs字典中

备注：
  本代码只是一个小demo，仅是一个解决思路。
  可能暂时无法解决所有的元素改动以及自检的问题，但是期望解决大部分。
 
