class Validators:
    """提供通用的验证函数"""
    
    @staticmethod
    def positive_number(value, field_name):
        """验证正数"""
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name}必须大于0"
            return True, num
        except ValueError:
            return False, f"{field_name}必须是有效的数字"
    
    @staticmethod
    def number_in_range(value, field_name, min_val=None, max_val=None):
        """验证数值范围"""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False, f"{field_name}不能小于{min_val}"
            if max_val is not None and num > max_val:
                return False, f"{field_name}不能大于{max_val}"
            return True, num
        except ValueError:
            return False, f"{field_name}必须是有效的数字"
    
    @staticmethod
    def color_component(value, field_name):
        """验证颜色分量(0-255)"""
        try:
            num = int(value)
            if num < 0 or num > 255:
                return False, f"{field_name}必须在0-255范围内"
            return True, num
        except ValueError:
            return False, f"{field_name}必须是有效的整数" 