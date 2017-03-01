from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class CodeGenerator:
	@classmethod
	def generate(cls, paramList):
		code = []
		code.append('var i = 0;')
		code.append(cls.generateCodeList(paramList))
		code.append('function* CodePicker(codeList) { for (var code of codeList) { var i = 0; while (i < code.span) { yield code.param; i++; } } }')
		code.append('var picker = CodePicker(codeList)')
		code.append('return function GoToMoon(state) {')
		code.append('var rocket = state.rocket')
		code.append('var moon = state.planetStates[1]')
		code.append(cls.generateLogCode())
		code.append('var controls = new Controls(picker.next().value);')
		code.append('i++;')
		code.append('return controls;')
		return code

	@classmethod
	def generateCodeList(cls, paramList):
		str = 'var codeList = ['
		for param in paramList:
			print(param)
			print(param['span'])
			str += '{{ span: {0}, param: {{ thrust: {1}, rcs: {{ pitch: {2}, yaw: {3}, roll: {4} }} }} }},'.\
				format(param['span'], param['thrust'], param['pitch'], param['yaw'], param['roll'])
		str += '];'
		return str
		
	@classmethod
	def generateLogCode(cls):
		str = ''
		str += 'console.log("state", '
		str += 'i, '
		str += 'rocket.mass, '
		str += 'rocket.position.x, rocket.position.y, rocket.position.z, '
		str += 'rocket.rotation.x, rocket.rotation.y, rocket.rotation.z, rocket.rotation.w, '
		str += 'rocket.velocity.x, rocket.velocity.y, rocket.velocity.z, '
		str += 'rocket.angularVelocity.x, rocket.angularVelocity.y, rocket.angularVelocity.z, '
		str += 'rocket.exploded, '
		str += 'rocket.fuel.mass, rocket.fuel.volume, '
		str += 'moon.mass, '
		str += 'moon.radius, '
		str += 'moon.position.x, moon.position.y, moon.position.z, '
		str += 'moon.rotation.x, moon.rotation.y, moon.rotation.z, '
		str += 'moon.velocity.x, moon.velocity.y, moon.velocity.z, '
		str += 'moon.angularVelocity.x, moon.angularVelocity.y, moon.angularVelocity.z'
		str += ');'
		return str

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
	def connect(self):
		self.driver = webdriver.Chrome()
		self.driver.get("http://hellospace.reaktor.com")

		time.sleep(10)	# TBD: ちゃんとした読み込み終了までのwaitに変える

		self.editor = EditorController(self.driver)
		self.ui = UIController(self.driver)

	def close(self):
		self.driver.close()

	def setCode(self, code):
		genCode = CodeGenerator.generate(code)
	
		self.editor.activate()
		self.editor.deleteAll()
		for str in genCode:
			self.editor.typeLine(str)

	def reset(self):
		self.ui.reset()

	def launch(self):
		self.ui.launch()



if __name__ == '__main__':
	controller = HelloSpaceController()
	controller.connect()

	code = [
		{ 'span': 100, 'thrust': 1.0, 'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0 },
		{ 'span': 100, 'thrust': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0 },
	]
	controller.setCode(code)

	controller.launch()
	time.sleep(10)

	controller.reset()
	time.sleep(1)

	controller.close()
