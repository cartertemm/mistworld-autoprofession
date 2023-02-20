# MistWorld Auto Profession: An Add-on for nvda that that allows players of the Mistworld AudioGame to automatically use profession skills without screen reader spam when vitality is exausted
# Simply quits the game after "Lack of vitality" messages in case AFK


import ctypes
import os
import signal
import addonHandler
import globalPluginHandler
import speech
import scriptHandler
import speechViewer
import ui
import versionInfo
import winKernel
from appModuleHandler import processEntry32W
from eventHandler import FocusLossCancellableSpeechCommand


addonHandler.initTranslation()
PROCESS_NAME = "mw.exe"
VITALITY_GONE_MESSAGE = "lack of vitality"
BUILD_YEAR = getattr(versionInfo, 'version_year', 2021)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.oldSpeak = None
		self.enabled = False
		self.pid = None

	def terminate(self, *args, **kwargs):
		super().terminate(*args, **kwargs)
		self.disable(announce=False)

	def enable(self, announce=True):
		if not self.is_game_running():
			# Translators: spoken when the game is not running
			ui.message(_("Game does not appear to be running"))
			return
		if BUILD_YEAR >= 2021:
			self.oldSpeak = speech.speech.speak
			speech.speech.speak = self.patchedSpeak
		else:
			self.oldSpeak = speech.speak
			speech.speak = self.patchedSpeak
		self.enabled = True
		if announce:
			# Translators: spoken when the functionality is enabled
			self.oldSpeak([_("Automatic vitality patch enabled")])

	def disable(self, announce=True):
		if not self.is_game_running():
			# Translators: spoken when the game is not running
			self.oldSpeak([_("Game does not appear to be running")])
			return
		if BUILD_YEAR >= 2021:
			speech.speech.speak = self.oldSpeak
		else:
			speech.speak = self.oldSpeak
		self.enabled = False
		if announce:
			# Translators: spoken when the functionality is disabled
			self.oldSpeak([_("Automatic vitality patch disabled")])

	def getSequenceText(self, sequence):
		# courdacy of speech history
		return speechViewer.SPEECH_ITEM_SEPARATOR.join([x for x in sequence if isinstance(x, str)])

	def patchedSpeak(self, sequence, *args, **kwargs):
		self.oldSpeak(sequence, *args, **kwargs)
		text = self.getSequenceText(sequence).lstrip().rstrip()
		if text == VITALITY_GONE_MESSAGE:
			self.exit_game()
			self.disable(announce=False)
			# Translators: message spoken when use of the chosen profession skill has completed and the game is exiting
			self.oldSpeak([_("Skill complete! Now exiting the game.")])

	@scriptHandler.script(
		description="Toggles automatic quitting of Mistworld after vitality is used up (only available when the game is active)",
		gesture="KB:NVDA+SHIFT+\\",
	)
	def script_toggle(self, gesture):
		if self.enabled:
			self.disable(announce=True)
		else:
			self.enable(announce=True)

	def is_game_running(self):
		FSnapshotHandle = winKernel.kernel32.CreateToolhelp32Snapshot (2,0)
		FProcessEntry32 = processEntry32W()
		FProcessEntry32.dwSize = ctypes.sizeof(processEntry32W)
		ContinueLoop = winKernel.kernel32.Process32FirstW(FSnapshotHandle, ctypes.byref(FProcessEntry32))
		while ContinueLoop:
			if FProcessEntry32.szExeFile == PROCESS_NAME:
				self.pid = FProcessEntry32.th32ProcessID
				return True
			ContinueLoop = winKernel.kernel32.Process32NextW(FSnapshotHandle, ctypes.byref(FProcessEntry32))
		return False

	def exit_game(self):
		if not self.pid:
			if not self.is_game_running():
				return False
		# is_game_running() populates PID for us (if necessary)
		return os.kill(self.pid, signal.SIGTERM)

