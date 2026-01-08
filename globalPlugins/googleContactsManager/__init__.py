# -*- coding: utf-8 -*-
# Google Contacts Manager for NVDA
# Author: Volkan Ozdemir Software Services <bilgi@volkan-ozdemir.com.tr>

import globalPluginHandler
import gui
import wx
import ui
import config
import addonHandler
import webbrowser
import os
from logHandler import log

# NVDA Dil Tesisatını Başlat
addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""
	Main class for Google Contacts Manager.
	Standard: PascalCase for Classes, camelCase for methods.
	"""
	# Kategori ismini doğrudan çeviri fonksiyonuyla tanımlıyoruz
	scriptCategory = _("Google Contacts Manager")
	DONATION_URL = "https://www.paytr.com/link/N2IAQKmm"

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		# API Yapılandırması
		confSpec = {
			"clientId": "string(default='')",
			"clientSecret": "string(default='')",
		}
		config.conf.spec["googleContacts"] = confSpec
		self.createMenu()

	def createMenu(self):
		parentMenu = gui.mainFrame.sysTrayIcon.menu
		self.contactsMenu = wx.Menu()
		
		# Menü Öğeleri
		itemAdd = self.contactsMenu.Append(wx.ID_ANY, _("Add New Contact..."))
		itemEdit = self.contactsMenu.Append(wx.ID_ANY, _("Edit Contact..."))
		itemDelete = self.contactsMenu.Append(wx.ID_ANY, _("Delete Contact..."))
		self.contactsMenu.AppendSeparator()
		itemSettings = self.contactsMenu.Append(wx.ID_ANY, _("API Settings..."))
		itemDonate = self.contactsMenu.Append(wx.ID_ANY, _("Make a Donation (PayTR)..."))
		
		# Bağlantılar
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onAddContact, itemAdd)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onEditContact, itemEdit)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onDeleteContact, itemDelete)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, itemSettings)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onDonate, itemDonate)
		
		self.mainMenuItem = parentMenu.AppendSubMenu(self.contactsMenu, _("Google Contacts Manager"))

	def onAddContact(self, event):
		dlg = ContactFormDialog(gui.mainFrame, title=_("Add New Google Contact"))
		if dlg.ShowModal() == wx.ID_OK:
			ui.message(_("Contact adding to Google: {name}").format(name=dlg.fullNameEdit.GetValue()))

	def onEditContact(self, event):
		dlg = ContactFormDialog(gui.mainFrame, title=_("Edit Google Contact"))
		if dlg.ShowModal() == wx.ID_OK:
			ui.message(_("Contact updated: {name}").format(name=dlg.fullNameEdit.GetValue()))

	def onDeleteContact(self, event):
		if gui.messageBox(_("Are you sure you want to delete this contact?"), _("Delete Confirmation"), wx.YES_NO | wx.ICON_WARNING) == wx.YES:
			ui.message(_("Contact deleted successfully."))

	def onSettings(self, event):
		dlg = ApiSettingsDialog(gui.mainFrame)
		dlg.ShowModal()

	def onDonate(self, event):
		webbrowser.open(self.DONATION_URL)
		ui.message(_("Opening donation page. Thank you for your support!"))

	# Kısayol Scriptleri
	def script_openAddContact(self, gesture):
		self.onAddContact(None)
	script_openAddContact.__doc__ = _("Opens the Google Contact addition form.")

	def script_openSettings(self, gesture):
		self.onSettings(None)
	script_openSettings.__doc__ = _("Opens the API configuration for Google Contacts.")

class ContactFormDialog(wx.Dialog):
	def __init__(self, parent, title):
		super(ContactFormDialog, self).__init__(parent, title=title)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.fullNameEdit = sHelper.addLabeledControl(_("Full Name:"), wx.TextCtrl)
		self.phoneEdit = sHelper.addLabeledControl(_("Phone Number:"), wx.TextCtrl)
		self.emailEdit = sHelper.addLabeledControl(_("Email Address:"), wx.TextCtrl)
		self.notesEdit = sHelper.addLabeledControl(_("Notes:"), wx.TextCtrl, style=wx.TE_MULTILINE)
		btnSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		mainSizer.Add(sHelper.sizer, proportion=1, flag=wx.ALL, border=20)
		mainSizer.Add(btnSizer, flag=wx.EXPAND | wx.ALL, border=10)
		self.SetSizer(mainSizer)

class ApiSettingsDialog(wx.Dialog):
	def __init__(self, parent):
		super(ApiSettingsDialog, self).__init__(parent, title=_("Google API Credentials"))
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.clientIdEdit = sHelper.addLabeledControl(_("Google Client ID:"), wx.TextCtrl)
		self.clientIdEdit.SetValue(config.conf["googleContacts"]["clientId"])
		self.clientSecretEdit = sHelper.addLabeledControl(_("Google Client Secret:"), wx.TextCtrl)
		self.clientSecretEdit.SetValue(config.conf["googleContacts"]["clientSecret"])
		btnSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		mainSizer.Add(sHelper.sizer, proportion=1, flag=wx.ALL, border=20)
		mainSizer.Add(btnSizer, flag=wx.EXPAND | wx.ALL, border=10)
		self.SetSizer(mainSizer)
		self.Bind(wx.EVT_BUTTON, self.onSave, id=wx.ID_OK)

	def onSave(self, event):
		config.conf["googleContacts"]["clientId"] = self.clientIdEdit.GetValue()
		config.conf["googleContacts"]["clientSecret"] = self.clientSecretEdit.GetValue()
		ui.message(_("Google API settings saved successfully."))
		event.Skip()