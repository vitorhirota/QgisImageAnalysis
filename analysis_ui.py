# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/analysis.ui'
#
# Created: Mon Jan 27 11:26:17 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AnalysisWidget(object):
    def setupUi(self, AnalysisWidget):
        AnalysisWidget.setObjectName(_fromUtf8("AnalysisWidget"))
        AnalysisWidget.resize(335, 205)
        AnalysisWidget.setMinimumSize(QtCore.QSize(0, 0))
        # AnalysisWidget.setFrameShape(QtGui.QFrame.StyledPanel)
        # AnalysisWidget.setFrameShadow(QtGui.QFrame.Raised)
        self.tabWidget = QtGui.QTabWidget(AnalysisWidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 5, 315, 161))
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_segm = QtGui.QWidget()
        self.tab_segm.setObjectName(_fromUtf8("tab_segm"))
        self.layoutWidget = QtGui.QWidget(self.tab_segm)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 291, 71))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.segm_raster_ipt = QtGui.QComboBox(self.layoutWidget)
        self.segm_raster_ipt.setObjectName(_fromUtf8("segm_raster_ipt"))
        self.gridLayout_3.addWidget(self.segm_raster_ipt, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.segm_clusters_ipt = QtGui.QSpinBox(self.layoutWidget)
        self.segm_clusters_ipt.setMinimum(1)
        self.segm_clusters_ipt.setMaximum(9999)
        self.segm_clusters_ipt.setObjectName(_fromUtf8("segm_clusters_ipt"))
        self.gridLayout_3.addWidget(self.segm_clusters_ipt, 1, 1, 1, 1)
        self.gridLayout_3.setColumnMinimumWidth(1, 150)
        self.tabWidget.addTab(self.tab_segm, _fromUtf8(""))
        self.tab_stats = QtGui.QWidget()
        self.tab_stats.setObjectName(_fromUtf8("tab_stats"))
        self.layoutWidget_5 = QtGui.QWidget(self.tab_stats)
        self.layoutWidget_5.setGeometry(QtCore.QRect(10, 10, 291, 71))
        self.layoutWidget_5.setObjectName(_fromUtf8("layoutWidget_5"))
        self.gridLayout_4 = QtGui.QGridLayout(self.layoutWidget_5)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.stats_segm_ipt = QtGui.QComboBox(self.layoutWidget_5)
        self.stats_segm_ipt.setObjectName(_fromUtf8("stats_segm_ipt"))
        self.gridLayout_4.addWidget(self.stats_segm_ipt, 1, 1, 1, 1)
        self.input_label = QtGui.QLabel(self.layoutWidget_5)
        self.input_label.setObjectName(_fromUtf8("input_label"))
        self.gridLayout_4.addWidget(self.input_label, 0, 0, 1, 1)
        self.segm_label_2 = QtGui.QLabel(self.layoutWidget_5)
        self.segm_label_2.setObjectName(_fromUtf8("segm_label_2"))
        self.gridLayout_4.addWidget(self.segm_label_2, 1, 0, 1, 1)
        self.stats_raster_ipt = QtGui.QComboBox(self.layoutWidget_5)
        self.stats_raster_ipt.setObjectName(_fromUtf8("stats_raster_ipt"))
        self.gridLayout_4.addWidget(self.stats_raster_ipt, 0, 1, 1, 1)
        self.gridLayout_4.setColumnMinimumWidth(1, 150)
        self.tabWidget.addTab(self.tab_stats, _fromUtf8(""))
        self.tab_class = QtGui.QWidget()
        self.tab_class.setObjectName(_fromUtf8("tab_class"))
        self.tabWidgetClf = QtGui.QTabWidget(self.tab_class)
        self.tabWidgetClf.setGeometry(QtCore.QRect(5, 0, 300, 125))
        self.tabWidgetClf.setStyleSheet(_fromUtf8(""))
        self.tabWidgetClf.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidgetClf.setObjectName(_fromUtf8("tabWidgetClf"))
        self.tab_class_ipt = QtGui.QWidget()
        self.tab_class_ipt.setObjectName(_fromUtf8("tab_class_ipt"))
        self.roi_class_field_label = QtGui.QLabel(self.tab_class_ipt)
        self.roi_class_field_label.setGeometry(QtCore.QRect(8, 65, 94, 26))
        self.roi_class_field_label.setObjectName(_fromUtf8("roi_class_field_label"))
        self.class_roi_ipt = QtGui.QComboBox(self.tab_class_ipt)
        self.class_roi_ipt.setGeometry(QtCore.QRect(140, 35, 150, 26))
        self.class_roi_ipt.setObjectName(_fromUtf8("class_roi_ipt"))
        self.class_roi_field = QtGui.QComboBox(self.tab_class_ipt)
        self.class_roi_field.setGeometry(QtCore.QRect(140, 65, 150, 26))
        self.class_roi_field.setObjectName(_fromUtf8("class_roi_field"))
        self.class_segm_ipt = QtGui.QComboBox(self.tab_class_ipt)
        self.class_segm_ipt.setGeometry(QtCore.QRect(140, 5, 150, 26))
        self.class_segm_ipt.setObjectName(_fromUtf8("class_segm_ipt"))
        self.roi_label = QtGui.QLabel(self.tab_class_ipt)
        self.roi_label.setGeometry(QtCore.QRect(8, 35, 60, 26))
        self.roi_label.setObjectName(_fromUtf8("roi_label"))
        self.segm_label = QtGui.QLabel(self.tab_class_ipt)
        self.segm_label.setGeometry(QtCore.QRect(8, 5, 113, 26))
        self.segm_label.setObjectName(_fromUtf8("segm_label"))
        self.tabWidgetClf.addTab(self.tab_class_ipt, _fromUtf8(""))
        self.tab_class_svm = QtGui.QWidget()
        self.tab_class_svm.setObjectName(_fromUtf8("tab_class_svm"))
        self.groupBox = QtGui.QGroupBox(self.tab_class_svm)
        self.groupBox.setGeometry(QtCore.QRect(170, 0, 111, 81))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.groupBox.setFlat(True)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.kgamma_label = QtGui.QLabel(self.groupBox)
        self.kgamma_label.setGeometry(QtCore.QRect(3, 20, 41, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.kgamma_label.setFont(font)
        self.kgamma_label.setObjectName(_fromUtf8("kgamma_label"))
        self.svm_kgamma_ipt = QtGui.QDoubleSpinBox(self.groupBox)
        self.svm_kgamma_ipt.setGeometry(QtCore.QRect(65, 20, 45, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.svm_kgamma_ipt.setFont(font)
        self.svm_kgamma_ipt.setDecimals(1)
        self.svm_kgamma_ipt.setSingleStep(0.1)
        self.svm_kgamma_ipt.setObjectName(_fromUtf8("svm_kgamma_ipt"))
        self.svm_kdegree_ipt = QtGui.QSpinBox(self.groupBox)
        self.svm_kdegree_ipt.setEnabled(False)
        self.svm_kdegree_ipt.setGeometry(QtCore.QRect(65, 40, 45, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.svm_kdegree_ipt.setFont(font)
        self.svm_kdegree_ipt.setProperty("value", 1)
        self.svm_kdegree_ipt.setObjectName(_fromUtf8("svm_kdegree_ipt"))
        self.kdegree_label = QtGui.QLabel(self.groupBox)
        self.kdegree_label.setGeometry(QtCore.QRect(3, 40, 41, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.kdegree_label.setFont(font)
        self.kdegree_label.setObjectName(_fromUtf8("kdegree_label"))
        self.kcoeff_label = QtGui.QLabel(self.groupBox)
        self.kcoeff_label.setGeometry(QtCore.QRect(3, 60, 65, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.kcoeff_label.setFont(font)
        self.kcoeff_label.setObjectName(_fromUtf8("kcoeff_label"))
        self.svm_kcoeff_ipt = QtGui.QDoubleSpinBox(self.groupBox)
        self.svm_kcoeff_ipt.setEnabled(False)
        self.svm_kcoeff_ipt.setGeometry(QtCore.QRect(65, 60, 45, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.svm_kcoeff_ipt.setFont(font)
        self.svm_kcoeff_ipt.setDecimals(1)
        self.svm_kcoeff_ipt.setSingleStep(0.1)
        self.svm_kcoeff_ipt.setObjectName(_fromUtf8("svm_kcoeff_ipt"))
        self.kernel_label = QtGui.QLabel(self.tab_class_svm)
        self.kernel_label.setGeometry(QtCore.QRect(11, 13, 41, 26))
        self.kernel_label.setObjectName(_fromUtf8("kernel_label"))
        self.svm_c_ipt = QtGui.QDoubleSpinBox(self.tab_class_svm)
        self.svm_c_ipt.setGeometry(QtCore.QRect(60, 50, 85, 24))
        self.svm_c_ipt.setDecimals(1)
        self.svm_c_ipt.setSingleStep(0.1)
        self.svm_c_ipt.setProperty("value", 1.0)
        self.svm_c_ipt.setObjectName(_fromUtf8("svm_c_ipt"))
        self.c_label = QtGui.QLabel(self.tab_class_svm)
        self.c_label.setGeometry(QtCore.QRect(11, 50, 16, 24))
        self.c_label.setObjectName(_fromUtf8("c_label"))
        self.svm_kernel_ipt = QtGui.QComboBox(self.tab_class_svm)
        self.svm_kernel_ipt.setGeometry(QtCore.QRect(60, 13, 85, 26))
        self.svm_kernel_ipt.setObjectName(_fromUtf8("svm_kernel_ipt"))
        self.svm_kernel_ipt.addItem(_fromUtf8(""))
        self.svm_kernel_ipt.addItem(_fromUtf8(""))
        self.svm_kernel_ipt.addItem(_fromUtf8(""))
        self.svm_kernel_ipt.addItem(_fromUtf8(""))
        self.tabWidgetClf.addTab(self.tab_class_svm, _fromUtf8(""))
        self.tabWidget.addTab(self.tab_class, _fromUtf8(""))
        self.cancel_btn = QtGui.QPushButton(AnalysisWidget)
        self.cancel_btn.setGeometry(QtCore.QRect(198, 170, 70, 32))
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setFlat(False)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.progressBar = QtGui.QProgressBar(AnalysisWidget)
        self.progressBar.setGeometry(QtCore.QRect(11, 176, 181, 20))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.ok_btn = QtGui.QPushButton(AnalysisWidget)
        self.ok_btn.setGeometry(QtCore.QRect(263, 170, 69, 32))
        self.ok_btn.setAutoDefault(True)
        self.ok_btn.setFlat(False)
        self.ok_btn.setObjectName(_fromUtf8("ok_btn"))

        self.retranslateUi(AnalysisWidget)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidgetClf.setCurrentIndex(0)
        self.svm_kernel_ipt.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(AnalysisWidget)

    def retranslateUi(self, AnalysisWidget):
        AnalysisWidget.setWindowTitle(_translate("AnalysisWidget", "Frame", None))
        self.label.setText(_translate("AnalysisWidget", "Raster Image", None))
        self.label_2.setText(_translate("AnalysisWidget", "Clusters", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_segm), _translate("AnalysisWidget", "Segmentation", None))
        self.input_label.setText(_translate("AnalysisWidget", "Raster Image", None))
        self.segm_label_2.setText(_translate("AnalysisWidget", "Segmented Image", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_stats), _translate("AnalysisWidget", "Statistics", None))
        self.roi_class_field_label.setText(_translate("AnalysisWidget", "ROI Class Field", None))
        self.roi_label.setText(_translate("AnalysisWidget", "ROI Layer", None))
        self.segm_label.setText(_translate("AnalysisWidget", "Segmented Image", None))
        self.tabWidgetClf.setTabText(self.tabWidgetClf.indexOf(self.tab_class_ipt), _translate("AnalysisWidget", "Inputs", None))
        self.groupBox.setTitle(_translate("AnalysisWidget", "Kernel Settings", None))
        self.kgamma_label.setText(_translate("AnalysisWidget", "Gamma", None))
        self.kdegree_label.setText(_translate("AnalysisWidget", "Degree", None))
        self.kcoeff_label.setText(_translate("AnalysisWidget", "Coefficient", None))
        self.kernel_label.setText(_translate("AnalysisWidget", "Kernel", None))
        self.c_label.setText(_translate("AnalysisWidget", "C", None))
        self.svm_kernel_ipt.setItemText(0, _translate("AnalysisWidget", "Linear", None))
        self.svm_kernel_ipt.setItemText(1, _translate("AnalysisWidget", "RBF", None))
        self.svm_kernel_ipt.setItemText(2, _translate("AnalysisWidget", "Poly", None))
        self.svm_kernel_ipt.setItemText(3, _translate("AnalysisWidget", "Sigmoid", None))
        self.tabWidgetClf.setTabText(self.tabWidgetClf.indexOf(self.tab_class_svm), _translate("AnalysisWidget", "SVM Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_class), _translate("AnalysisWidget", "Classification", None))
        self.cancel_btn.setText(_translate("AnalysisWidget", "Cancel", None))
        self.ok_btn.setText(_translate("AnalysisWidget", "OK", None))

