# rekjrc/context.py
def device_type(request):
    is_mobile = getattr(request.user_agent, 'is_mobile', False)
    is_tablet = getattr(request.user_agent, 'is_tablet', False)
    is_pc = getattr(request.user_agent, 'is_pc', False)
    return {
        'is_mobile': is_mobile,
        'is_tablet': is_tablet,
        'is_pc': is_pc,
    }
