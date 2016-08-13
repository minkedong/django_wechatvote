# -*- coding: utf-8 -*-
import json
from decimal import Decimal

class FieldVolidatorMixin(object):
    """
    参数验证
    """
    validate_key = [
        'exact_length',
        'max_length',
        'min_length',
        'exact_value',
        'max_value',
        'min_value',
    ]

    def validate_field(self, value, validators):
        for validator in validators:
            if hasattr(validator, '__call__'):
                if not self.func_validate(validator, value):
                    return False
            else:
                for vali_key,vali_value in validator.items():
                    if not self.general_validate(vali_key, vali_value, value):
                        return False
        return True

    def func_validate(self, func, value):
        return func(value)

    def general_validate(self, vali_key, vali_value, value):
        if vali_key not in self.validate_key:
            raise Exception('validate key %s is not valid' % vali_key)
        return getattr(self, '%s_validate' % vali_key)(vali_value, value)

    def exact_length_validate(self, vali_value, value):
        return int(vali_value) == len(value)

    def max_length_validate(self, vali_value, value):
        return int(vali_value) >= len(value)

    def min_length_validate(self, vali_value, value):
            return int(vali_value) <= len(value) 

    def exact_value_validate(self, vali_value, value):
        return vali_value == value

    def max_value_validate(self, vali_value, value):
        return vali_value >= value

    def min_value_validate(self, vali_value, value):
        return vali_value <= value



class FieldFormatorMixin(object):
    """
    参数format
    """
    format_key = [
        'int',
        'unicode',
        'decimal',
    ]
    TWOPLACES = Decimal(10) ** -2

    def format_field(self, value, formator):
        if formator not in self.format_key:
            raise Exception('format key %s is not valid' % formator)
        return getattr(self, '%s_format' % formator)(value)

    def int_format(self, value):
        try:
            return int(value)
        except Exception, e:
            raise Exception('format error')

    def unicode_format(self, value):
        try:
            return unicode(value)
        except Exception, e:
            raise Exception('format error')

    def decimal_format(self, value):
        try:
            return Decimal(value).quantize(self.TWOPLACES)
        except Exception, e:
            raise Exception('format error')

        

class ReqParameter(FieldFormatorMixin, FieldVolidatorMixin):
    """
    参数处理
    """
    METHODS = ['POST', 'GET'] # 暂时支持的方法
    # 常用字段规则
    # FIELD_USERNAME = {'fieldname':'username', 'formator':'unicode', 'validators':[lambda x:x.isdigit(),{'exact_length':11}], 'option':False}
    # FIELD_PASSWORD = {'fieldname':'password', 'formator':'unicode', 'validators':[{'min_length':6, 'max_length':14}], 'option':False}
    # FIELD_PASSWORD_REPEAT = {'fieldname':'password_repeat', 'formator':'unicode', 'validators':[{'min_length':6, 'max_length':14}], 'option':False}
    # FIELD_PASSWORD_ORIGIN = {'fieldname':'origin_password', 'formator':'unicode', 'validators':[{'min_length':6, 'max_length':14}], 'option':False}
    # FIELD_SMS = {'fieldname':'sms', 'formator':'unicode', 'validators':[lambda x:x.isdigit(),{'exact_length':6}]}

    def __init__(self, request, fields=[]):
        self.request = request
        self.fields = fields

    
    def get_method_item_value(self, method, fieldname, args_info, defaultvalue=None, option=False):
        item_value = None
        if method == 'POST':
            if self.request.POST.get(fieldname, None) is None:
                item_value = args_info.get(fieldname, None)
            else:
                item_value = self.request.POST.get(fieldname, None)

        elif method == 'GET':
            item_value = self.request.GET.get(fieldname, None)

        # 判断如果是非必要字段，给默认值
        if item_value is None and option:
            item_value = defaultvalue

        return item_value

    def get_args(self, method):
        if method not in self.METHODS:
            raise Exception('ReqParameter have not allow this method:%s' % method)

        valid, filedvalues = True, []

        try:
            args_info = json.loads(self.request.body)
        except Exception, e:
            args_info = {}

        for item in self.fields:
            # 字段参数
            fieldname = item.get('fieldname')
            formator = item.get('formator')
            validators = item.get('validators', [])
            option = item.get('option', False)
            defaultvalue = item.get('defaultvalue')
            if fieldname is None:
                raise Exception('fields arg must have key : fieldname')

            item_value = self.get_method_item_value(method, fieldname, args_info, defaultvalue, option)

            # 验证参数是否为必要参数
            if not option and item_value is None:
                valid = False
                break

            if option and item_value is None:
                # 如果是非必要参数，且前端没有传此值，则无需做各种验证及转换
                pass
            else:
                # 进行format
                if formator is not None:
                    try:
                        item_value = self.format_field(item_value, formator)
                    except Exception, e:
                        valid = False
                        break
                # 进行数据验证
                if not self.validate_field(item_value, validators):
                    valid = False
                    break

            filedvalues.append(item_value)

        return valid, filedvalues


    def get_post_args(self):
        return self.get_args('POST')


    def get_get_args(self):
        return self.get_args('GET')