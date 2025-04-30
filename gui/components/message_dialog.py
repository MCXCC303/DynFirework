from PyQt5.QtWidgets import QMessageBox

class MessageDialog:
    """消息对话框工具类，提供统一风格的消息弹窗"""
    
    @staticmethod
    def info(parent, title, message):
        """信息提示框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            message: 提示消息
            
        返回:
            int: 对话框返回值，通常为QMessageBox.Ok
        """
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Information)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setDefaultButton(QMessageBox.Ok)
        return dialog.exec_()
        
    @staticmethod
    def warning(parent, title, message):
        """警告提示框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            message: 警告消息
            
        返回:
            int: 对话框返回值，通常为QMessageBox.Ok
        """
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setDefaultButton(QMessageBox.Ok)
        return dialog.exec_()
        
    @staticmethod
    def error(parent, title, message):
        """错误提示框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            message: 错误消息
            
        返回:
            int: 对话框返回值，通常为QMessageBox.Ok
        """
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setDefaultButton(QMessageBox.Ok)
        return dialog.exec_()
        
    @staticmethod
    def question(parent, title, message):
        """确认对话框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            message: 询问消息
            
        返回:
            bool: 是否确认(Yes)
        """
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        return dialog.exec_() == QMessageBox.Yes
        
    @staticmethod
    def yes_no_cancel(parent, title, message):
        """是/否/取消对话框
        
        参数:
            parent: 父窗口
            title: 对话框标题
            message: 询问消息
            
        返回:
            str: "yes", "no", "cancel" 三者之一
        """
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Yes)
        
        result = dialog.exec_()
        if result == QMessageBox.Yes:
            return "yes"
        elif result == QMessageBox.No:
            return "no"
        else:
            return "cancel" 