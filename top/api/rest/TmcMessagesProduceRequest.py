'''
Created by auto_sdk on 2015.12.17
'''
from top.api.base import RestApi
class TmcMessagesProduceRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.messages = None

	def getapiname(self):
		return 'taobao.tmc.messages.produce'
