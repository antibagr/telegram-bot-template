from aiogram.utils.callback_data import CallbackData


menu_data = CallbackData("umd", "action", "s")
sign_up_data = CallbackData("sud", "r")
confirm_data = CallbackData("confd", "ctx")
accept_terms_data = CallbackData("atd", "a")
gender_data = CallbackData("gd", "g")
dropdown_menu_data = CallbackData("dmd", "cat", "s")
order_info_data = CallbackData("oid", "id", "role")
location_markup_data = CallbackData('lmd', 'ctx', 'sqid')
confirm_location_data = CallbackData('cld', 'coords', 'a')
cancel_data = CallbackData("cancld", "ctx")
offer_data = CallbackData('offd', 'order_id', 'action')
delivery_data = CallbackData('ded', 'order_id', 'checkpoint')
invalid_invite_link_data = CallbackData('iild', 'id', 'times', 'timestamp')
delivery_timer_data = CallbackData('dtd', 'order_id')
arbitration_data = CallbackData('ad', 'order_id')
