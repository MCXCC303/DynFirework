class Validators:
    """表单验证类，包含所有表单通用的验证逻辑"""
    
    @staticmethod
    def is_not_empty(value, field_name="字段"):
        """检查字段是否为空
        
        参数:
            value: 字段值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
                valid: bool 是否有效
                message: str 错误消息，验证通过时为空字符串
        """
        if not value:
            return False, f"{field_name}不能为空"
        return True, ""
        
    @staticmethod
    def is_integer(value, field_name="字段"):
        """检查字段是否为整数
        
        参数:
            value: 字段值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            int(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是整数"
            
    @staticmethod
    def is_float(value, field_name="字段"):
        """检查字段是否为浮点数
        
        参数:
            value: 字段值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"
            
    @staticmethod
    def in_range(value, min_val, max_val, field_name="字段"):
        """检查字段是否在指定范围内
        
        参数:
            value: 字段值
            min_val: 最小值
            max_val: 最大值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            num = float(value)
            if num < min_val or num > max_val:
                return False, f"{field_name}必须在{min_val}和{max_val}之间"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"
            
    @staticmethod
    def is_positive(value, field_name="字段"):
        """检查字段是否为正数
        
        参数:
            value: 字段值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name}必须大于0"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"
            
    @staticmethod
    def is_non_negative(value, field_name="字段"):
        """检查字段是否为非负数
        
        参数:
            value: 字段值
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            num = float(value)
            if num < 0:
                return False, f"{field_name}不能为负数"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是数字"
            
    @staticmethod
    def validate_color(r, g, b, field_name="颜色"):
        """验证RGB颜色值
        
        参数:
            r: 红色分量
            g: 绿色分量
            b: 蓝色分量
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            r_val = int(r)
            g_val = int(g)
            b_val = int(b)
            
            if not (0 <= r_val <= 255 and 0 <= g_val <= 255 and 0 <= b_val <= 255):
                return False, f"{field_name}RGB值必须在0-255之间"
                
            return True, ""
        except ValueError:
            return False, f"{field_name}RGB值必须是整数"
            
    @staticmethod
    def validate_position(x, y, z, field_name="位置"):
        """验证坐标值
        
        参数:
            x: X坐标
            y: Y坐标
            z: Z坐标
            field_name: 字段名称，用于错误消息
            
        返回:
            tuple: (valid, message) 验证结果
        """
        try:
            float(x)
            float(y)
            float(z)
            return True, ""
        except ValueError:
            return False, f"{field_name}坐标必须是数字"

    @staticmethod
    def positive_number(value, field_name="数值"):
        """
        验证正数
        
        参数:
            value: 要验证的值
            field_name: 字段名称，用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name}必须大于0"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的数字"
    
    @staticmethod
    def positive_integer(value, field_name="整数"):
        """
        验证正整数
        
        参数:
            value: 要验证的值
            field_name: 字段名称，用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            num = int(value)
            if num <= 0:
                return False, f"{field_name}必须是正整数"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的整数"
    
    @staticmethod
    def number(value, field_name="数值"):
        """
        验证数字
        
        参数:
            value: 要验证的值
            field_name: 字段名称，用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的数字"
    
    @staticmethod
    def integer(value, field_name="整数"):
        """
        验证整数
        
        参数:
            value: 要验证的值
            field_name: 字段名称，用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            int(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的整数"
    
    @staticmethod
    def color_component(value, field_name="颜色分量"):
        """
        验证颜色分量(0-255)
        
        参数:
            value: 要验证的值
            field_name: 字段名称，用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            num = int(value)
            if num < 0 or num > 255:
                return False, f"{field_name}必须在0-255之间"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的整数"
            
    @staticmethod
    def angle(value, field_name="角度"):
        """
        验证角度值（可以是任意数字）
        
        参数:
            value: 要验证的值
            field_name: , 用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的数字"
            
    @staticmethod
    def positive_angle(value, field_name="角度"):
        """
        验证正角度值（必须大于0）
        
        参数:
            value: 要验证的值
            field_name: , 用于错误消息
            
        返回:
            (bool, str): (是否通过验证, 错误消息)
        """
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name}必须大于0"
            return True, ""
        except ValueError:
            return False, f"{field_name}必须是有效的数字" 