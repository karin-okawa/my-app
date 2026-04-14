from households.models import UserHouseholdAccount  # 家計簿とユーザーの紐付けモデルのインポート


def current_household(request):
    """
    全テンプレートで現在選択中の家計簿を使えるようにするコンテキストプロセッサー
    """
    # 未ログインの場合は空のデータを返す
    if not request.user.is_authenticated:
        return {'current_household': None, 'user_households': []}

    # セッションから現在選択中の家計簿IDを取得する
    household_id = request.session.get('current_household_id')

    # ログインユーザーが参加中の家計簿一覧を取得する（関連モデルを一括取得）
    user_households = UserHouseholdAccount.objects.filter(
        user=request.user,
        status=1
    ).select_related('household_account')

    # 参加中の家計簿がない場合は空のデータを返す
    if not user_households.exists():
        return {'current_household': None, 'user_households': []}

    # セッションに家計簿IDがある場合はその家計簿を返す
    if household_id:
        household = user_households.filter(
            household_account_id=household_id
        ).first()
        if household:
            return {
                'current_household': household.household_account,
                'user_households': user_households,
            }

    # セッションにIDがない場合は最初の家計簿をデフォルトとして設定する
    first_household = user_households.first().household_account
    request.session['current_household_id'] = first_household.id
    return {
        'current_household': first_household,
        'user_households': user_households,
    }