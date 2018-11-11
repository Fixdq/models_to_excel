# -*- encoding: utf-8 -*-
from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from account.models import User
from core.models import *
from core.wdecorators import get_object
from shop.models import *
from plan.models import PlanInfo
from utils import tool
from utils.qinius import *
import collections
import datetime
import json
from msg.models import MessageInfo
# Create your models here.


class ReportTemplate(Common):
    """总结模版"""
    title = models.CharField(u'标题', help_text=u'标题', max_length=256, default='', blank=True)
    # target = models.CharField(u'目标对象', help_text=u'目标对象', max_length=128, default='', blank=True)
    desc = models.CharField(u'简介', help_text=u'简介', max_length=256, default='', blank=True)
    tag = models.CharField(u'标签', help_text=u'标签', max_length=256, default='', blank=True)

    class Meta:
        db_table = 'report_template'
        verbose_name = '总结模版'


class ReportConfig(Common):
    """总结设置"""
    user = models.ForeignKey(User, verbose_name=u'所属用户', help_text=u'所属用户', null=True)
    five = models.BooleanField(u'五大项', help_text=u'五大项', default=True, blank=True)
    myself = models.BooleanField(u'自我总结', help_text=u'自我总结', default=False, blank=True)
    customer = models.BooleanField(u'顾客总结', help_text=u'顾客总结', default=False, blank=True)
    peixun = models.BooleanField(u'培训总结', help_text=u'培训总结', default=False, blank=True)
    qinggan = models.BooleanField(u'情感总结', help_text=u'情感总结', default=False, blank=True)
    huodong = models.BooleanField(u'活动总结', help_text=u'活动总结', default=False, blank=True)
    week = models.BooleanField(u'周会总结', help_text=u'周会总结', default=False, blank=True)
    qt_work = models.BooleanField(u'前台工作总结', help_text=u'前台工作总结', default=False, blank=True)

    REPORT_DAILY, REPORT_WEEK, REPORT_MONTH = 1, 2, 3
    REPORT_TYPE = ((REPORT_DAILY, u'日计划'), (REPORT_WEEK, u'周计划'), (REPORT_MONTH, u'月计划'))
    report_type = models.IntegerField(u'计划类型', help_text=u'计划类型', choices=REPORT_TYPE, default=REPORT_DAILY)

    POSITION_BEAUT, POSITION_ADVISER, POSITION_KEEPER, POSITION_MANAGER, POSITION_RECEPTIONIST, POSITION_CONDUCTOR = 1, 2, 3, 4, 5, 6
    # POSITION_BEAUT, POSITION_ADVISER, POSITION_KEEPER, POSITION_MANAGER, POSITION_RECEPTIONIST, POSITION_CONDUCTOR = 1, 2, 4, 8, 16, 32
    POSITION_TYPE = ((POSITION_BEAUT, u'美容师'), (POSITION_ADVISER, u'顾问'), (POSITION_KEEPER, u'店长'),
                     (POSITION_MANAGER, u'经理'), (POSITION_RECEPTIONIST, u'前台'), (POSITION_CONDUCTOR, u'总监'))
    position = models.IntegerField(u'员工类别', help_text=u'员工类别', default=POSITION_BEAUT, choices=POSITION_TYPE)

    def reset_flag(self):
        self.five = False
        self.myself = False
        self.customer = False
        self.peixun = False
        self.qinggan = False
        self.huodong = False
        self.qt_work = False
        self.week = False

    def get_model_choice(self):
        dic = collections.OrderedDict()
        dic['five'] = self.five
        dic['myself'] = self.myself
        dic['customer'] = self.customer
        dic['peixun'] = self.peixun
        dic['qinggan'] = self.qinggan
        dic['huodong'] = self.huodong
        dic['week'] = self.week
        dic['qt_work'] = self.qt_work
        return dic
        # return {'five': self.five, 'self': self._self, 'customer': self.customer, 'peixun': self.peixun,
        #         'qinggan': self.qinggan, 'huodong': self.huodong, 'week': self.week}

    class Meta:
        db_table = 'report_config'
        verbose_name = '总结设置'
        ordering = ['-create_time']


class ReportInfo(Common):
    """日报"""
    title = models.CharField(u'名称', help_text=u'名称', max_length=512, default='日报', blank=True)
    year = models.IntegerField(u'年份', default=0, blank=True)
    target_date = models.DateField(u'总结时间', help_text=u'总结时间', default=datetime.date.today)
    target_count = models.IntegerField(u'周/月编号', default=0, blank=True)
    employee = models.ForeignKey(Employee, verbose_name=u'员工', help_text=u'员工')
    shop = models.ForeignKey(ShopInfo, verbose_name=u'店铺', help_text=u'店铺')

    REPORT_DAILY, REPORT_WEEK, REPORT_MONTH = 1, 2, 3
    REPORT_TYPE = ((REPORT_DAILY, u'日总结'), (REPORT_WEEK, u'周总结'), (REPORT_MONTH, u'月总结'))
    report_type = models.IntegerField(u'总结类型', help_text=u'总结类型', choices=REPORT_TYPE, default=REPORT_DAILY)

    check = models.BooleanField(u'审核', default=False, blank=True)
    check_user = models.ForeignKey(User, verbose_name=u'审核用户', null=True, blank=True, related_name='dr_cu')
    check_comment = models.CharField(u'审核意见', max_length=1024, default='', blank=True)
    check_time = models.DateTimeField(u'审批时间', help_text=u'审批时间', default=None, null=True, blank=True)

    # 留言区
    check_report_user = models.CharField(u'留言人', max_length=1024, default='[]', blank=True)
    check_report_comment = models.CharField(u'留言', max_length=2048, default='[]', blank=True)
    check_report_now = models.CharField(u'留言时间', max_length=1024, help_text=u'审批时间', default='[]', null=True, blank=True)
    check_report_all = models.CharField(u'所有留言', max_length=2048, default='[]', blank=True)

    # 新加字段
    old_version = models.BooleanField(u'以前提交', default=True, blank=True)
    has_sub = models.BooleanField(u'是否提交', default=False, blank=True)

    def get_model_choice(self):
        report_config = get_object(ReportConfig, user=self.shop.user, report_type=self.report_type, position=self.employee.position, status=ReportConfig.STATUS_VALID)
        if report_config:
            return report_config.get_model_choice()
        return {}

    def get_check_user_position(self):
        if self.check_user.is_boss():
            return '老板'
        else:
            employee = get_object(Employee, user=self.check_user, shop=self.shop, status=Employee.STATUS_VALID)
            if employee:
                return employee.get_position_display()
        return ''

    def get_five_list(self):
        return ReportFive.objects.filter(report=self, status=ReportFive.STATUS_VALID)

    def get_myself_list(self):
        return ReportSelf.objects.filter(report=self, status=ReportSelf.STATUS_VALID)

    def get_customer_list(self):
        return ReportCustomer.objects.filter(report=self, status=ReportCustomer.STATUS_VALID).order_by('create_time')

    def get_peixun_list(self):
        return ReportPeiXun.objects.filter(report=self, status=ReportPeiXun.STATUS_VALID)

    def get_qinggan_list(self):
        return {'huodong': ReportQingGan.objects.filter(report=self, type=ReportQingGan.QG_HUODONG, status=ReportQingGan.STATUS_VALID),
                'xintai': ReportQingGan.objects.filter(report=self, type=ReportQingGan.QG_EMPLOYEE, status=ReportQingGan.STATUS_VALID)}

    def get_huodong_list(self):
        return ReportCustomerHuoDong.objects.filter(report=self, status=ReportCustomerHuoDong.STATUS_VALID)

    def get_week_list(self):
        return ReportWeekMeeting.objects.filter(report=self, status=ReportWeekMeeting.STATUS_VALID)

    def get_qt_work_list(self):
        return ReportQtWork.objects.filter(report=self, status=ReportQtWork.STATUS_VALID)

    def get_web_display_url(self):
        return reverse('web:report_detail', args=[self.shop_id, self.id])

####################################################################
    def get_other_list(self):
        return ReportOther.objects.filter(report=self, status=ReportOther.STATUS_VALID)

    def get_xinzhen_list(self):
        return ReportXingzheng.objects.filter(report=self, status=ReportXingzheng.STATUS_VALID)

    def get_toker_list(self):
        return ReportToker.objects.filter(report=self, status=ReportToker.STATUS_VALID)

    def get_peihe_list(self):
        return ReportPeihe.objects.filter(report=self, status=ReportPeihe.STATUS_VALID)

    def get_new_week_list(self):
        return ReportNewWeekMeeting.objects.filter(report=self, status=ReportNewWeekMeeting.STATUS_VALID)

    def get_new_month_list(self):
        return ReportNewMonthMeeting.objects.filter(report=self, status=ReportNewMonthMeeting.STATUS_VALID)

    def get_check_shop(self):
        return ReportCheckShop.objects.filter(report=self, status=ReportCheckShop.STATUS_VALID)

    def get_report_version_id(self):
        version = ReportVersion.objects.filter(report=self, status=ReportVersion.STATUS_VALID).first()
        if not version:
            return ''
        else:
            return version.id

    def get_report_version(self):
        version = ReportVersion.objects.filter(report=self, status=ReportVersion.STATUS_VALID).first()
        if not version:
            return ''
        else:
            return version.check_version

    def get_has_sub(self):
        msg_type = 3
        if self.report_type == ReportInfo.REPORT_DAILY:
            report_type = MessageInfo.MSG_SECOND_CREATE_DAILY_REPORT
        elif self.report_type == ReportInfo.REPORT_WEEK:
            report_type = MessageInfo.MSG_SECOND_CREATE_WEEK_REPORT
        else:
            report_type = MessageInfo.MSG_SECOND_CREATE_MONTH_REPORT
        msg = MessageInfo.objects.filter(target_id=self.id, msg_type_first=msg_type,
                                         msg_type_second=report_type,
                                         status=MessageInfo.STATUS_VALID)
        if msg:
            return True
        else:
            return False

    def get_really_sub(self):
        if self.old_version:
            return True
        else:
            if self.has_sub:
                return True
            else:
                return False


    @property
    def content(self):
        from report.serializers import ReportMapSerializer
        # 判断返回哪些模型字段
        model_list = ReportMapSerializer().model_map
        serializer_list = ReportMapSerializer().serializer_map
        data = {}
        report_config = get_object(ReportConfig,
                                   user=self.shop.user,
                                   report_type=self.report_type,
                                   position=self.employee.position,
                                   status=ReportConfig.STATUS_VALID)
        if not report_config:
            return {}

        choice_list = report_config.get_model_choice()
        for index, key in enumerate(choice_list):
            if key in model_list and choice_list[key]:
                data[key] = serializer_list[key](model_list[key].objects.filter(report=self, status=model_list[key].STATUS_VALID), many=True).data
        return data

    def save(self, *args, **kwargs):
        if self.year == 0:
            self.year = int(get_current_time(timezone.now()).strftime('%Y'))
        if self.target_count == 0:
            if self.report_type == self.REPORT_WEEK:
                self.target_count = int(get_current_time(timezone.now()).strftime('%W'))+1
            elif self.report_type == self.REPORT_MONTH:
                self.target_count = int(get_current_time(timezone.now()).strftime('%m'))
        return super(ReportInfo, self).save(*args, **kwargs)

    def get_leave_msg(self):
        user_list = eval(self.check_report_user)
        comment_list = eval(self.check_report_comment)
        time_list = eval(self.check_report_now)
        leave_msg_list = list()
        for num, item in enumerate(user_list):
            one_list = list()
            one_use = User.objects.filter(id=item, status=User.STATUS_VALID).first()
            if not one_use:
                continue
            one_list.append(one_use.nick)
            if one_use.is_boss:
                one_list.append('boss')
            else:
                emp = Employee.objects.filter(user=one_use, status=Employee.STATUS_VALID).first()
                if emp:
                    one_list.append(emp.get_position_display())
                else:
                    one_list.append('无职位')
            one_list.append(comment_list[num])
            one_list.append(time_list[num])
            leave_msg_list.append(one_list)

        return leave_msg_list

    class Meta:
        db_table = 'report_info'
        verbose_name = '总结信息'
        ordering = ['-create_time']


class ReportFive(CommonAuto):
    """五大块"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')
    sale_cash_money = models.IntegerField(u'现金业绩', help_text=u'现金业绩', default=0, blank=True)
    self_sale_cash_money = models.IntegerField(u'个人现金业绩', help_text=u'个人现金业绩', default=0, blank=True)
    sale_cost_money = models.IntegerField(u'消耗业绩', help_text=u'消耗业绩', default=0, blank=True)
    sale_product_money = models.IntegerField(u'产品业绩', help_text=u'产品业绩', default=0, blank=True)
    sale_card_money = models.IntegerField(u'卡项业绩', help_text=u'卡项业绩', default=0, blank=True)
    sale_big_money = models.IntegerField(u'大项目业绩', help_text=u'大项目业绩', default=0, blank=True)
    sale_advantage = models.TextField(u'业绩优点', help_text=u'业绩优点', default='', blank=True)
    sale_disadvantage = models.TextField(u'业绩问题', help_text=u'业绩问题', default='', blank=True)
    sale_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # Monthly_consumption_amount = models.IntegerField(u'本月消耗金额', help_text=u'本月消耗金额', default=0, blank=True)
    # Cash_amount_this_month = models.IntegerField(u'本月消耗金额', help_text=u'本月消耗金额', default=0, blank=True)
    personal_cash_amount = models.IntegerField(u'个人现金金额', help_text=u'个人现金金额', default=0, blank=True)
    personal_consumption_amount = models.IntegerField(u'个人消耗金额', help_text=u'个人消耗金额', default=0, blank=True)
    cash_amount_group = models.IntegerField(u'组内现金金额', help_text=u'组内现金金额', default=0, blank=True)
    group_consumption_amount = models.IntegerField(u'组内消耗金额', help_text=u'组内消耗金额', default=0, blank=True)
    store_sales_aount = models.IntegerField(u'整店现金金额', help_text=u'整店现金金额', default=0, blank=True)
    store_consumption_amount = models.IntegerField(u'整店消耗金额', help_text=u'整店消耗金额', default=0, blank=True)
    mag_whole_store_amount = models.IntegerField(u'经理整店现金金额', help_text=u'经理整店现金金额', default=0, blank=True)
    mag_whole_store_consumption = models.IntegerField(u'经理整店消耗金额', help_text=u'经理整店消耗金额', default=0, blank=True)


    # 服务部分
    serve_count = models.IntegerField(u'服务人数', help_text=u'服务人数', default=0, blank=True)
    self_serve_count = models.IntegerField(u'个人服务人数', help_text=u'个人服务人数', default=0, blank=True)
    serve_reserve_count = models.IntegerField(u'预约人数', help_text=u'预约人数', default=0, blank=True)
    self_serve_reserve_count = models.IntegerField(u'个人预约人数', help_text=u'个人预约人数', default=0, blank=True)
    serve_new_count = models.IntegerField(u'新客人数', help_text=u'新客人数', default=0, blank=True)
    serve_project_count = models.IntegerField(u'项目个数', help_text=u'项目个数', default=0, blank=True)
    serve_advantage = models.TextField(u'服务优点', help_text=u'服务优点', default='', blank=True)
    serve_disadvantage = models.TextField(u'服务问题', help_text=u'服务问题', default='', blank=True)
    serve_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    #
    number_of_personal_services = models.IntegerField(u'个人服务人数', help_text=u'个人服务人数', default=0, blank=True)
    personal_number_of_projects = models.IntegerField(u'个人项目个数', help_text=u'个人项目个数', default=0, blank=True)
    group_service_times = models.IntegerField(u'组内服务人次', help_text=u'组内服务人次', default=0, blank=True)
    consul_project_nums = models.IntegerField(u'组内项目个数', help_text=u'组内项目个数', default=0, blank=True)
    store_service_number = models.IntegerField(u'整店服务人数', help_text=u'整店服务人数', default=0, blank=True)
    store_whole_items = models.IntegerField(u'整店项目个数', help_text=u'整店项目个数', default=0, blank=True)
    mag_whole_times = models.IntegerField(u'经理整店项目个数', help_text=u'经理整店项目个数', default=0, blank=True)
    mag_servies_people = models.IntegerField(u'经理整店服务人数', help_text=u'经理整店服务人数', default=0, blank=True)
    counter_reservation = models.IntegerField(u'反预约人数', help_text=u'反预约人数', default=0, blank=True)
    store_counter_reservation = models.IntegerField(u'整店反预约人数', help_text=u'整店反预约人数', default=0, blank=True)
    group_counter_reservation = models.IntegerField(u'组内反预约人数', help_text=u'组内反预约人数', default=0, blank=True)
    mag_store_counter_reservation = models.IntegerField(u'经理整店反预约人数', help_text=u'经理整店反预约人数', default=0, blank=True)

    # 拓客部分
    develop_new_count = models.IntegerField(u'老带新人数', help_text=u'老带新人数', default=0, blank=True)
    develop_activate_count = models.IntegerField(u'激活流失顾客人数', help_text=u'激活流失顾客人数', default=0, blank=True)
    develop_other_count = models.IntegerField(u'其他拓客人数', help_text=u'其他拓客人数', default=0, blank=True)
    develop_advantage = models.TextField(u'拓客优点', help_text=u'拓客优点', default='', blank=True)
    develop_disadvantage = models.TextField(u'拓客问题', help_text=u'拓客问题', default='', blank=True)
    develop_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)


    # personal_extension_guests = models.IntegerField(u'新版拓客人数', help_text=u'老带新人数', default=0, blank=True)

    # 行政部分
    rule_late_count = models.IntegerField(u'迟到数', help_text=u'迟到数', default=0, blank=True)
    rule_back_count = models.IntegerField(u'早退数', help_text=u'早退数', default=0, blank=True)
    rule_ill_count = models.IntegerField(u'事假病假数', help_text=u'事假病假数', default=0, blank=True)
    rule_health_count = models.IntegerField(u'卫生违规数', help_text=u'卫生违规数', default=0, blank=True)
    rule_refuse_count = models.IntegerField(u'违纪数', help_text=u'违纪数', default=0, blank=True)
    rule_advantage = models.TextField(u'行政优点', help_text=u'行政优点', default='', blank=True)
    rule_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    rule_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)

    # 其他部分
    other_content = models.TextField(u'工作内容', help_text=u'工作内容', default='', blank=True)
    other_result = models.TextField(u'工作结果', help_text=u'工作结果', default='', blank=True)
    other_advantage = models.TextField(u'优点', help_text=u'优点', default='', blank=True)
    other_disadvantage = models.TextField(u'问题', help_text=u'问题', default='', blank=True)
    other_correct = models.TextField(u'修正', help_text=u'修正', default='', blank=True)

    #####################################################
    customer_record = models.TextField(u'顾客记录', help_text=u'顾客记录', default='', blank=True)

    def get_report_money(self):
        return self.sale_cash_money + self.sale_product_money + self.sale_card_money + self.sale_big_money

    def get_yesterday_money(self):
        yesterday = self.report.target_date - datetime.timedelta(days=1)
        report = get_object(ReportInfo, employee=self.report.employee,
                            shop=self.report.shop,
                            report_type=self.report.report_type,
                            target_date=yesterday,
                            status=ReportInfo.STATUS_VALID)
        if report:
            five_list = report.get_five_list()
            if five_list.exists():
                return five_list[0].sale_cash_money
        return 0

    def last_money(self):
        lask_week = self.report.target_count - 1
        report = get_object(ReportInfo, employee=self.report.employee,
                            shop=self.report.shop,
                            report_type=self.report.report_type,
                            target_count=lask_week,
                            status=ReportInfo.STATUS_VALID)
        if report:
            five_list = report.get_five_list()
            if five_list.exists():
                return five_list[0].sale_cash_money
        return 0

    def last_month_money(self):
        lask_week = self.report.target_count - 1
        report = get_object(ReportInfo, employee=self.report.employee,
                            shop=self.report.shop,
                            report_type=self.report.report_type,
                            target_count=lask_week,
                            status=ReportInfo.STATUS_VALID)
        if report:
            five_list = report.get_five_list()
            if five_list.exists():
                return five_list[0].sale_cash_money
        return 0

    def get_plan_money(self):
        plan = get_object(PlanInfo, employee=self.report.employee,
                          shop=self.report.shop,
                          plan_type=self.report.report_type,
                          target_date=self.report.target_date,
                          status=PlanInfo.STATUS_VALID)
        if plan:
            five_list = plan.get_five_list()
            if five_list.exists():
                return five_list[0].sale_cash_money
        return 0

    def get_develop_count(self):
        return self.develop_new_count + self.develop_activate_count + self.develop_other_count

    def get_sale_advantage(self):
        return json.loads(self.sale_advantage, object_pairs_hook=collections.OrderedDict)

    def get_sale_disadvantage(self):
        return json.loads(self.sale_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_sale_correct(self):
        return json.loads(self.sale_correct, object_pairs_hook=collections.OrderedDict)

    def get_serve_advantage(self):
        return json.loads(self.serve_advantage, object_pairs_hook=collections.OrderedDict)

    def get_serve_disadvantage(self):
        return json.loads(self.serve_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_serve_correct(self):
        return json.loads(self.serve_correct, object_pairs_hook=collections.OrderedDict)

    def get_develop_advantage(self):
        return json.loads(self.develop_advantage, object_pairs_hook=collections.OrderedDict)

    def get_develop_disadvantage(self):
        return json.loads(self.develop_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_develop_correct(self):
        return json.loads(self.develop_correct, object_pairs_hook=collections.OrderedDict)

    def get_rule_advantage(self):
        return json.loads(self.rule_advantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_disadvantage(self):
        return json.loads(self.rule_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_correct(self):
        return json.loads(self.rule_correct, object_pairs_hook=collections.OrderedDict)

    def get_other_content(self):
        return json.loads(self.other_content, object_pairs_hook=collections.OrderedDict)

    def get_other_result(self):
        return json.loads(self.other_result, object_pairs_hook=collections.OrderedDict)

    def get_other_correct(self):
        return json.loads(self.other_correct, object_pairs_hook=collections.OrderedDict)

    def get_other_advantage(self):
        return json.loads(self.other_advantage, object_pairs_hook=collections.OrderedDict)

    def get_other_disadvantage(self):
        return json.loads(self.other_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_serve_percent(self):
        if self.serve_count > 0:
            return self.serve_reserve_count*100/self.serve_count
        return 0

    def get_rule_count(self):
        return self.rule_late_count + self.rule_back_count + self.rule_ill_count + self.rule_health_count + self.rule_refuse_count

    ######################################
    def get_customer_record(self):
        return json.loads(self.customer_record, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_five'
        verbose_name = '总结五大项'
        ordering = ['-create_time']


class ReportCustomer(CommonAuto):
    """顾客总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')
    name = models.CharField(u'姓名', help_text=u'姓名', max_length=512, default='', blank=True)
    result = models.CharField(u'服务结果', help_text=u'服务结果', max_length=1024, default='', blank=True)
    sale_money = models.IntegerField(u'销售结果', help_text=u'销售结果', default=0, blank=True)
    next_scheme = models.CharField(u'下次方案', help_text=u'下次方案', max_length=1024, default='', blank=True)

    class Meta:
        db_table = 'report_customer'
        verbose_name = '顾客总结'
        ordering = ['-create_time']


class ReportSelf(CommonAuto):
    """总结：自我总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')
    self_lunli = models.IntegerField(u'伦理', help_text=u'伦理', default=0, blank=True)
    self_zhurenweng = models.IntegerField(u'主人翁', help_text=u'主人翁', default=0, blank=True)
    self_leguan = models.IntegerField(u'乐观', help_text=u'乐观', default=0, blank=True)
    self_peihe = models.IntegerField(u'配合', help_text=u'配合', default=0, blank=True)
    self_pinghe = models.IntegerField(u'平和', help_text=u'平和', default=0, blank=True)
    self_tongyi = models.IntegerField(u'统一', help_text=u'统一', default=0, blank=True)
    self_ganen = models.IntegerField(u'感恩', help_text=u'感恩', default=0, blank=True)
    self_renxing = models.IntegerField(u'韧性', help_text=u'韧性', default=0, blank=True)
    self_tashi = models.IntegerField(u'踏实', help_text=u'踏实', default=0, blank=True)
    self_renzhen = models.IntegerField(u'认真', help_text=u'认真', default=0, blank=True)

    self_manage = models.TextField(u'管理能力', help_text=u'管理能力', default='', blank=True)
    self_sale = models.TextField(u'销售能力', help_text=u'销售能力', default='', blank=True)

    class Meta:
        db_table = 'report_self'
        verbose_name = '自我总结'
        ordering = ['-create_time']


class ReportPeiXun(CommonAuto):
    """培训总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')
    content = models.CharField(u'培训内容', help_text=u'培训内容', max_length=1024, default='', blank=True)
    result = models.CharField(u'培训结果', help_text=u'培训结果', max_length=1024, default='', blank=True)
    suggest = models.CharField(u'培训建议', help_text=u'培训建议', max_length=1024, default='', blank=True)

    class Meta:
        db_table = 'report_peixun'
        verbose_name = '培训总结'


class ReportQingGan(CommonAuto):
    """情感文化总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')
    QG_HUODONG, QG_EMPLOYEE = 1, 2
    QG_TYPE = ((QG_HUODONG, u'活动情感总结'), (QG_EMPLOYEE, u'员工心态总结'))
    type = models.IntegerField(u'类型', choices=QG_TYPE, default=QG_HUODONG)

    time = models.CharField(u'活动时间', help_text=u'活动时间', max_length=1024, default='', blank=True)
    content = models.TextField(u'活动内容', help_text=u'活动内容', default='', blank=True)
    result = models.TextField(u'活动效果', help_text=u'活动效果', default='', blank=True)
    suggest = models.TextField(u'活动建议', help_text=u'活动建议', default='', blank=True)

    emp_time = models.CharField(u'沟通时间', help_text=u'沟通时间', max_length=1024, default='', blank=True)
    emp_target = models.TextField(u'沟通对象', help_text=u'沟通对象', default='', blank=True)
    emp_content = models.TextField(u'沟通重点', help_text=u'沟通重点', default='', blank=True)
    emp_result = models.TextField(u'沟通结果', help_text=u'沟通结果', default='', blank=True)
    emp_suggest = models.TextField(u'沟通建议', help_text=u'沟通建议', default='', blank=True)

    class Meta:
        db_table = 'report_qinggan'
        verbose_name = '情感文化规划'


class ReportCustomerHuoDong(CommonAuto):
    """顾客活动总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')

    time = models.CharField(u'活动时间', help_text=u'活动时间', max_length=1024, default='', blank=True)
    content = models.TextField(u'活动内容', help_text=u'活动内容', default='', blank=True)
    result = models.TextField(u'活动效果', help_text=u'活动效果', default='', blank=True)
    suggest = models.TextField(u'活动建议', help_text=u'活动建议', default='', blank=True)

    class Meta:
        db_table = 'report_customer_huodong'
        verbose_name = '顾客活动总结'


class ReportWeekMeeting(CommonAuto):
    """周会执行"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')

    content = models.TextField(u'周会流程', help_text=u'周会流程', default='', blank=True)
    step = models.TextField(u'周会分工', help_text=u'周会分工', default='', blank=True)
    good = models.TextField(u'表彰重点', help_text=u'表彰重点', default='', blank=True)
    bad = models.TextField(u'问题重点', help_text=u'问题重点', default='', blank=True)
    peixun = models.TextField(u'培训重点', help_text=u'培训重点', default='', blank=True)
    correct = models.TextField(u'修正重点', help_text=u'修正重点', default='', blank=True)

    peixun_sale_content = models.TextField(u'销售培训内容', help_text=u'销售培训内容', default='', blank=True)
    peixun_sale_teacher = models.TextField(u'销售培训老师', help_text=u'销售培训老师', default='', blank=True)

    peixun_shoufa_content = models.TextField(u'手法培训内容', help_text=u'手法培训内容', default='', blank=True)
    peixun_shoufa_teacher = models.TextField(u'手法培训老师', help_text=u'手法培训老师', default='', blank=True)

    peixun_fanyuyue_content = models.TextField(u'反预约培训内容', help_text=u'反预约培训内容', default='', blank=True)
    peixun_fanyuyue_teacher = models.TextField(u'反预约培训老师', help_text=u'反预约培训老师', default='', blank=True)

    peixun_other_content = models.TextField(u'其他培训内容', help_text=u'其他培训内容', default='', blank=True)
    peixun_other_teacher = models.TextField(u'其他培训老师', help_text=u'其他培训老师', default='', blank=True)

    # def get_step(self):
    #     return json.loads(self.step, object_pairs_hook=collections.OrderedDict)

    def get_good(self):
        return json.loads(self.good, object_pairs_hook=collections.OrderedDict)

    def get_bad(self):
        return json.loads(self.bad, object_pairs_hook=collections.OrderedDict)

    def get_peixun(self):
        return json.loads(self.peixun, object_pairs_hook=collections.OrderedDict)

    def get_correct(self):
        return json.loads(self.correct, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_week_meeting'
        verbose_name = '周会执行'


class ReportQtWork(CommonAuto):
    """前台工作总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结')

    card_money = models.IntegerField(u'卡项业绩', help_text=u'卡项业绩', default=0, blank=True)
    card_desc = models.TextField(u'卡项明细', help_text=u'卡项明细', default='', blank=True)
    high_money = models.IntegerField(u'高端业绩', help_text=u'高端业绩', default=0, blank=True)
    high_desc = models.TextField(u'高端明细', help_text=u'高端明细', default='', blank=True)
    product_money = models.IntegerField(u'产品业绩', help_text=u'产品业绩', default=0, blank=True)
    product_desc = models.TextField(u'产品明细', help_text=u'产品明细', default='', blank=True)

    in_money = models.IntegerField(u'进', help_text=u'进', default=0, blank=True)
    out_money = models.IntegerField(u'销', help_text=u'销', default=0, blank=True)
    save_money = models.IntegerField(u'存', help_text=u'存', default=0, blank=True)

    all_money = models.IntegerField(u'总计费用', help_text=u'总计费用', default=0, blank=True)
    buy_something = models.TextField(u'采购', help_text=u'采购', default='', blank=True)

    rule_late_count = models.IntegerField(u'迟到数', help_text=u'迟到数', default=0, blank=True)
    rule_late_desc = models.CharField(u'迟到说明', help_text=u'迟到说明', max_length=1024, default='', blank=True)

    rule_back_count = models.IntegerField(u'早退数', help_text=u'早退数', default=0, blank=True)
    rule_back_desc = models.CharField(u'早退说明', help_text=u'早退说明', max_length=1024, default=0, blank=True)

    rule_ill_count = models.IntegerField(u'事假病假数', help_text=u'事假病假数', default=0, blank=True)
    rule_ill_desc = models.CharField(u'事假病假说明', help_text=u'事假病假说明', max_length=1024, default=0, blank=True)

    rule_health_count = models.IntegerField(u'卫生违规数', help_text=u'卫生违规数', default=0, blank=True)
    rule_health_desc = models.CharField(u'卫生违规说明', help_text=u'卫生违规说明', max_length=1024, default=0, blank=True)

    rule_refuse_count = models.IntegerField(u'违纪数', help_text=u'违纪数', default=0, blank=True)
    rule_refuse_desc = models.CharField(u'违纪说明', help_text=u'违纪说明', max_length=1024, default=0, blank=True)

    rule_other = models.CharField(u'其他', help_text=u'其他', max_length=256, default=0, blank=True)
    rule_other_desc = models.CharField(u'其他说明', help_text=u'其他说明', max_length=1024, default=0, blank=True)

    def get_buy_something(self):
        return json.loads(self.buy_something, object_pairs_hook=collections.OrderedDict)


    class Meta:
        db_table = 'report_qt_work'
        verbose_name = '前台工作总结'


class MsgRecordCheck(Common):
    check_user = models.ForeignKey(User, verbose_name=u'审核用户', null=True, blank=True, related_name='check_user')
    user = models.ForeignKey(User, verbose_name=u'被审用户', null=True, blank=True, related_name='user')
    plan = models.ForeignKey(PlanInfo, verbose_name=u'计划', help_text=u'计划', null=True, blank=True, related_name='check_plan')
    report = models.ForeignKey(ReportInfo, verbose_name=u'总结', help_text=u'总结', null=True, blank=True, related_name='check_plan')
    plan_time = models.CharField(u'时间', help_text=u'时间', max_length=128, default='', blank=True)
    report_time = models.CharField(u'时间', help_text=u'时间', max_length=128, default='', blank=True)
    plan_msg = models.CharField(u'计划留言', help_text=u'计划留言', max_length=2048, default='', blank=True)
    report_msg = models.CharField(u'总结留言', help_text=u'总结留言', max_length=2048, default='', blank=True)
    priority = models.IntegerField(u'优先级', help_text=u'优先级', default=9, blank=True)

    def get_position(self):
        position = ''
        if self.check_user.is_boss():
            position = 'boss'
        else:
            emp = Employee.objects.filter(user=self.check_user, status=Employee.STATUS_VALID).first()
            if emp:
                if emp.position == 1:
                    position = 'beaut'
                elif emp.position == 2:
                    position = 'adviser'
                elif emp.position == 3:
                    position = 'keeper'
                elif emp.position == 4:
                    position = 'manager'
                elif emp.position == 5:
                    position = 'receptionist'
                elif emp.position == 6:
                    position = 'conductor'
        return position

    def plan_check(self):
        return True if self.plan else False

    def report_check(self):
        return True if self.report else False

    class Meta:
        db_table = 'all_leave_msg_new'
        verbose_name = '报表留言'
        ordering = ['priority']


#############################################
        # 新追加的模块

class ReportOther(CommonAuto):
    """其他工作总结"""
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    work_content = models.TextField(u'工作内容', help_text=u'工作内容', default='', blank=True)
    work_advantage = models.TextField(u'工作优点', help_text=u'业绩优点', default='', blank=True)
    work_disadvantage = models.TextField(u'工作问题', help_text=u'业绩问题', default='', blank=True)
    work_correct = models.TextField(u'后期修正', help_text=u'修正方案', default='', blank=True)

    def get_work_advantage(self):
        return json.loads(self.work_advantage, object_pairs_hook=collections.OrderedDict)

    def get_work_disadvantage(self):
        return json.loads(self.work_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_work_correct(self):
        return json.loads(self.work_correct, object_pairs_hook=collections.OrderedDict)

    def get_work_content(self):
        return json.loads(self.work_content, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_other'
        verbose_name = '其他工作总结'
        ordering = ['create_time']


class ReportXingzheng(CommonAuto):
    '''行政工作总结'''
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    rule_all_count = models.IntegerField(u'违规总次数', help_text=u'违规总次数', default=0, blank=True)
    rule_late_count = models.IntegerField(u'迟到数', help_text=u'迟到数', default=0, blank=True)
    rule_back_count = models.IntegerField(u'早退数', help_text=u'早退数', default=0, blank=True)
    rule_ill_count = models.IntegerField(u'事假病假数', help_text=u'事假病假数', default=0, blank=True)
    rule_health_count = models.IntegerField(u'卫生违规数', help_text=u'卫生违规数', default=0, blank=True)
    rule_refuse_count = models.IntegerField(u'违纪数', help_text=u'违纪数', default=0, blank=True)
    rule_advantage = models.TextField(u'行政优点', help_text=u'行政优点', default='', blank=True)
    rule_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    rule_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)

    def get_rule_advantage(self):
        return json.loads(self.rule_advantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_disadvantage(self):
        return json.loads(self.rule_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_correct(self):
        return json.loads(self.rule_correct, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_xingzheng'
        verbose_name = '行政工作总结'
        ordering = ['create_time']


class ReportToker(CommonAuto):
    '''拓客总结'''
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    develop_new_count = models.IntegerField(u'服务人数', help_text=u'服务人数', default=0, blank=True)
    develop_activate_count = models.IntegerField(u'累积顾客人数', help_text=u'累积顾客人数', default=0, blank=True)
    develop_advantage = models.TextField(u'拓客优点', help_text=u'拓客优点', default='', blank=True)
    develop_disadvantage = models.TextField(u'拓客问题', help_text=u'拓客问题', default='', blank=True)
    develop_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # 新版字段
    personal_extension_guests = models.IntegerField(u'新版个人拓客人数', help_text=u'新版个人拓客人数', default=0, blank=True)
    personal_individual_guests = models.IntegerField(u'新版个人留客人数', help_text=u'新版个人留客人数', default=0, blank=True)
    stone_extension_guests = models.IntegerField(u'整店拓客人数', help_text=u'整店拓客人数', default=0, blank=True)
    stone_individual_guests = models.IntegerField(u'整店留客人数', help_text=u'整店留客人数', default=0, blank=True)
    group_extension_guests = models.IntegerField(u'整组拓客人数', help_text=u'整组拓客人数', default=0, blank=True)
    group_individual_guests = models.IntegerField(u'整组留客人数', help_text=u'整组留客人数', default=0, blank=True)
    mag_stone_extension_guests = models.IntegerField(u'经理整店拓客人数', help_text=u'经理整店拓客人数', default=0, blank=True)
    mag_stone_individual_guests = models.IntegerField(u'经理整店留客人数', help_text=u'经理整店留客人数', default=0, blank=True)






    def get_develop_advantage(self):
        return json.loads(self.develop_advantage, object_pairs_hook=collections.OrderedDict)

    def get_develop_disadvantage(self):
        return json.loads(self.develop_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_develop_correct(self):
        return json.loads(self.develop_correct, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_tuoke'
        verbose_name = '拓客总结'
        ordering = ['create_time']


class ReportPeihe(CommonAuto):
    '''主管总结'''
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    peihe_disadvantage = models.TextField(u'配合问题', help_text=u'拓客优点', default='', blank=True)
    peihe_correct = models.TextField(u'配合修正', help_text=u'拓客问题', default='', blank=True)
    peihe_advantage = models.TextField(u'配合优点', help_text=u'修正方案', default='', blank=True)

    def get_peihe_disadvantage(self):
        return json.loads(self.peihe_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_peihe_correct(self):
        return json.loads(self.peihe_correct, object_pairs_hook=collections.OrderedDict)

    def get_peihe_advantage(self):
        return json.loads(self.peihe_advantage, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_peihe'
        verbose_name = '主管配合总结'
        ordering = ['create_time']


class ReportNewWeekMeeting(CommonAuto):
    '''周会重点'''

    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    # 表彰
    week_good = models.TextField(u'表彰重点', help_text=u'表彰重点', default='', blank=True)
    # 行政
    week_rule_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    week_rule_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # 企业文化
    week_wenhua_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    week_wenhua_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # 销售培训
    week_peixun_xiaoshou = models.CharField(u'培训销售', max_length=512, default='', blank=True)
    week_peixun_xiaoshou_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)
    # 手法培训
    week_peixun_hand = models.CharField(u'培训手法', max_length=512, default='', blank=True)
    week_peixun_hand_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)
    # 其他培训
    week_peixun_other = models.CharField(u'其他', max_length=512, default='', blank=True)
    week_peixun_other_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)

    def get_good(self):
        return json.loads(self.week_good, object_pairs_hook=collections.OrderedDict)

    def get_rule_disadvantage(self):
        return json.loads(self.week_rule_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_correct(self):
        return json.loads(self.week_rule_correct, object_pairs_hook=collections.OrderedDict)

    def get_wenhua_disadvantage(self):
        return json.loads(self.week_wenhua_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_wenhua_correct(self):
        return json.loads(self.week_wenhua_correct, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_new_week_meeting'
        verbose_name = '新周会总结'
        ordering = ['create_time']


class ReportNewMonthMeeting(CommonAuto):
    '''月会重点'''

    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    # 表彰
    month_good = models.TextField(u'表彰重点', help_text=u'表彰重点', default='', blank=True)
    # 行政
    month_rule_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    month_rule_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # 企业文化
    month_wenhua_disadvantage = models.TextField(u'行政问题', help_text=u'行政问题', default='', blank=True)
    month_wenhua_correct = models.TextField(u'修正方案', help_text=u'修正方案', default='', blank=True)
    # 销售培训
    month_peixun_xiaoshou = models.CharField(u'培训销售', max_length=512, default='', blank=True)
    month_peixun_xiaoshou_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)
    # 手法培训
    month_peixun_hand = models.CharField(u'培训手法', max_length=512, default='', blank=True)
    month_peixun_hand_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)
    # 其他培训
    month_peixun_other = models.CharField(u'其他', max_length=512, default='', blank=True)
    month_peixun_other_teacher = models.CharField(u'培训老师', max_length=256, default='', blank=True)

    def get_good(self):
        return json.loads(self.month_good, object_pairs_hook=collections.OrderedDict)

    def get_rule_disadvantage(self):
        return json.loads(self.month_rule_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_rule_correct(self):
        return json.loads(self.month_rule_correct, object_pairs_hook=collections.OrderedDict)

    def get_wenhua_disadvantage(self):
        return json.loads(self.month_wenhua_disadvantage, object_pairs_hook=collections.OrderedDict)

    def get_wenhua_correct(self):
        return json.loads(self.month_wenhua_correct, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_new_month_meeting'
        verbose_name = '新月会总结'
        ordering = ['create_time']


class ReportCheckShop(CommonAuto):
    '''巡店总结'''
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    check_shop_title = models.CharField(u'店名', max_length=128, default='', blank=True)
    shop_disadvantage = models.TextField(u'店铺问题', help_text=u'拓客优点', default='', blank=True)
    shop_correct = models.TextField(u'店铺修正', help_text=u'拓客问题', default='', blank=True)
    shop_advantage = models.TextField(u'店铺优点', help_text=u'修正方案', default='', blank=True)

    def get_shop_correct(self):
        return json.loads(self.shop_correct, object_pairs_hook=collections.OrderedDict)

    def get_shop_advantage(self):
        return json.loads(self.shop_advantage, object_pairs_hook=collections.OrderedDict)

    def get_shop_disadvantage(self):
        return json.loads(self.shop_disadvantage, object_pairs_hook=collections.OrderedDict)

    class Meta:
        db_table = 'report_check_shop'
        verbose_name = '巡店总结'
        ordering = ['create_time']


class ReportVersion(CommonAuto):
    '''总结版本控制'''
    report = models.ForeignKey(ReportInfo, help_text=u'总结', verbose_name=u'总结', null=True, default=None, blank=True,
                               on_delete=models.SET_NULL)
    check_version = models.CharField(u'版本信息', help_text=u'版本信息', max_length=128, default='', blank=True)

    class Meta:
        db_table = 'report_version'
        verbose_name = '总结类别'
        ordering = ['-create_time']