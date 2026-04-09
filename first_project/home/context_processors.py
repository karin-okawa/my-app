from households.models import UserHouseholdAccount

def current_household(request):
    """
    全テンプレートで現在選択中の家計簿を使えるようにするコンテキストプロセッサ
    """
    if not request.user.is_authenticated:
        return {'current_household': None, 'user_households': []}
    
    household_id = request.session.get('current_household_id')
    
    user_households = UserHouseholdAccount.objects.filter(
        user=request.user,
        status=1
    ).select_related('household_account')

    if not user_households.exists():
        return {'current_household': None, 'user_households': []}

    if household_id:
        household = user_households.filter(
            household_account_id=household_id
        ).first()
        if household:
            return {
                'current_household': household.household_account,
                'user_households': user_households,
            }

    first_household = user_households.first().household_account
    request.session['current_household_id'] = first_household.id
    return {
        'current_household': first_household,
        'user_households': user_households,
    }