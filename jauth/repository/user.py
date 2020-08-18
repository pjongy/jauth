from tortoise import QuerySet

from jauth.model.user import User, UserType, UserStatus


def user_model_to_dict(row: User):
    user_dict = {
        'id': row.id,
        'email': row.email,
        'type': row.type,
        'status': row.status,
        'extra': row.extra,
        'is_email_verified': row.is_email_verified,
        'created_at': row.created_at,
        'modified_at': row.modified_at,
    }

    if row.type == UserType.EMAIL:
        user_dict['account'] = row.account

    if row.type != UserType.EMAIL:
        user_dict['third_party_user_id'] = row.third_party_user_id

    return user_dict


def _user_relational_query_set(query_set: QuerySet[User]) -> QuerySet[User]:
    return query_set


async def find_user_by_id(_id: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            id=_id
        ).order_by(
            'modified_at', 'created_at'
        )
    ).first()


async def find_user_by_account(account: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            account=account
        )
    ).first()


async def find_user_by_third_party_user_id(user_type: UserType, third_party_user_id: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            third_party_user_id=third_party_user_id,
            type=user_type,
            status=UserStatus.NORMAL,
        )
    ).first()


async def create_user(
    user_type: UserType,
    email: str,
    account: str = None,
    hashed_password: str = None,
    third_party_user_id: str = None,
    extra: dict = None
) -> User:
    if extra is None:
        extra = {}

    return await User.create(
        type=user_type,
        account=account,
        email=email,
        hashed_password=hashed_password,
        third_party_user_id=third_party_user_id,
        extra=extra,
    )


async def update_user(
    user_id: str,
    **kwargs
) -> int:
    return await User.filter(
        id=user_id
    ).update(
        **kwargs
    )
