from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

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
		self.editor.activate()
		self.editor.deleteAll()
		for str in code:
			self.editor.typeLine(str)

	def reset(self):
		self.ui.reset()

	def launch(self):
		self.ui.launch()



if __name__ == '__main__':
	controller = HelloSpaceController()
	controller.connect()

	code = [
		"return function GoToMoon(state) {",
		"return new Controls({ thrust: 1, rcs: { pitch: 0.01, yaw: 0.01 }})"
	]
	controller.setCode(code)

	controller.launch()
	time.sleep(5)

	controller.reset()
	time.sleep(1)

	controller.close()
