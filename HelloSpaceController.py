from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from ThreadManager import *

class CodeGenerator:
	@classmethod
	def generate(cls, paramList):
		codestr = \
'''
var i = 0;
{0}

function* CodePicker(codeList) {{ for (var code of codeList) {{ var i = 0; while (i < code.span) {{ yield code.param; i++; }} }} }}
var picker = CodePicker(codeList);

return function GoToMoon(state) {{
	var rocket = state.rocket;
	var moon = state.planetStates[1];
{1}
	var controls = new Controls(picker.next().value);
	i++;
	return controls;
'''.format(cls.generateCodeList(paramList), cls.generateLogCode())
		return map(str.strip, codestr.splitlines())

	@classmethod
	def generateCodeList(cls, paramList):
		str = 'var codeList = ['
		for param in paramList:
			str += '{{ span: {0}, param: {{ thrust: {1}, rcs: {{ pitch: {2}, yaw: {3}, roll: {4} }} }} }},'.\
				format(param['span'], param['thrust'], param['pitch'], param['yaw'], param['roll'])
		str += '];'
		return str
		
	@classmethod
	def generateLogCode(cls):
		codestr = \
'''
console.log([
	"state",
	i, 
	rocket.mass,
	rocket.position.x, rocket.position.y, rocket.position.z, 
	rocket.rotation.x, rocket.rotation.y, rocket.rotation.z, rocket.rotation.w, 
	rocket.velocity.x, rocket.velocity.y, rocket.velocity.z, 
	rocket.angularVelocity.x, rocket.angularVelocity.y, rocket.angularVelocity.z, 
	rocket.exploded, 
	rocket.fuel.mass, rocket.fuel.volume, 
	moon.mass, 
	moon.radius, 
	moon.position.x, moon.position.y, moon.position.z, 
	moon.rotation.x, moon.rotation.y, moon.rotation.z, moon.rotation.w,
	moon.velocity.x, moon.velocity.y, moon.velocity.z, 
	moon.angularVelocity.x, moon.angularVelocity.y, moon.angularVelocity.z
].join(','));
'''
		return codestr.replace('\n', '').replace('\t', '')

class UIController:
	def __init__(self, driver):
		self.driver = driver
		self.resetElem = self.driver.find_element_by_id('reset')
		self.launchElem = self.driver.find_element_by_id('launch')

	def reset(self):
		self.resetElem.click()

	def launch(self):
		self.launchElem.click()


class EditorController:
	def __init__(self, driver):
		self.driver = driver
		self.editorElem = self.driver.find_element_by_id('editor')

	def activate(self):
		self.editorElem.click()
		return self

	def deleteAll(self):
		actions = ActionChains(self.driver)
		actions.move_to_element(self.editorElem)
		actions.key_down(Keys.COMMAND).\
			send_keys('a').\
			key_up(Keys.COMMAND).\
			perform()
		actions.send_keys(Keys.DELETE).perform()
		return self

	def typeLine(self, str):
		actions = ActionChains(self.driver)
		actions.move_to_element(self.editorElem)
		actions.send_keys(str).send_keys(Keys.ENTER).perform()
		return self


class HelloSpaceController:
	def __init__(self):
		self.param = None

	def connect(self):
		self.isReady = False
		self.q = Queue()
		self.thread = Thread(self.__run, self.q).start()
		self.q.put('connect')
		while not self.isReady:
			pass
		self.ticker = Ticker(0.01, self.q, 'tick').start()

	def close(self):
		self.ticker.stop()
		self.q.put('close')
		while self.isReady:
			pass
		self.thread.stop()

	def getLog(self):
		rawlog = self.driver.get_log('browser')
		if len(rawlog) == 0:
			return None

		log = rawlog[-1]['message']
		loglist = log[log.find('"') + 1 : log.rfind('"')].split(',')
		if loglist[0] != 'state':
			return None

		return {
			'frame': int(loglist[1]),
			'rocket': {
				'mass': float(loglist[2]),
				'position': list(map(float, loglist[3:6])),
				'rotation': list(map(float, loglist[6:10])),
				'velocity': list(map(float, loglist[10:13])),
				'angularVelocity': list(map(float, loglist[13:16])),
				'exploded': bool(loglist[16]),
				'fuel': {
					'mass': float(loglist[17]),
					'volume': float(loglist[18]),
				},
			},
			'planetState': {
				'mass': float(loglist[19]),
				'radius': float(loglist[20]),
				'position': list(map(float, loglist[21:24])),
				'rotation': list(map(float, loglist[24:28])),
				'velocity': list(map(float, loglist[28:31])),
				'anglarVelocity': list(map(float, loglist[31:34])),
			},
		}

	def setCode(self, code):
		self.q.put(['set_code', code])

	def reset(self):
		self.q.put('reset')

	def launch(self):
		self.q.put('launch')

	def __setCode(self, code):
		genCode = CodeGenerator.generate(code)
	
		self.editor.activate()
		self.editor.deleteAll()
		for str in genCode:
			self.editor.typeLine(str)

	def __reset(self):
		self.ui.reset()

	def __launch(self):
		self.ui.launch()

	def __connect(self):
		d = DesiredCapabilities.CHROME
		d['loggingPrefs'] = { 'browser' : 'ALL' }
		self.driver = webdriver.Chrome(desired_capabilities = d)
		self.driver.get("http://hellospace.reaktor.com")

		time.sleep(10)	# TBD: ちゃんとした読み込み終了までのwaitに変える

		self.editor = EditorController(self.driver)
		self.ui = UIController(self.driver)

		self.isReady = True

	def __close(self):
		self.driver.close()
		self.isReady = False
	
	def __run(self, arg):
		if arg == 'connect':
			self.__connect()
		elif arg == 'close':
			self.__close()
		elif arg == 'tick':
			param = self.getLog()
			if param != None:
				self.param = param
		elif arg[0] == 'set_code':
			self.__setCode(arg[1])
		elif arg == 'reset':
			self.__reset()
		elif arg == 'launch':
			self.__launch()


if __name__ == '__main__':
	controller = HelloSpaceController()
	controller.connect()

	code = [
		{ 'span': 100, 'thrust': 1.0, 'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0 },
		{ 'span': 100, 'thrust': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0 },
	]
	controller.setCode(code)

	controller.launch()

	for i in range(5):
		time.sleep(1)
		print(controller.param)

	controller.reset()
	time.sleep(1)

	controller.close()

	print('Fin')